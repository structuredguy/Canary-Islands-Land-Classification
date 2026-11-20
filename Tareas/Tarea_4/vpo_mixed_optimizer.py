# -*- coding: utf-8 -*-
"""
Mixed Subsidized Housing (VPO) + Free-Market Optimizer (Tarea 4 + Tarea 3).
Models the 3D decision space (Ce, C_ocup_M, C_ocup_V) when 40% of total sector
buildability E_teorica (10% Municipal PMS + 30% Private VPO) is reserved for VPO
under RDL 7/2015 Art. 20.1.b (vs 30% Canary floor in Ley 4/2017 Art. 138).

Compares:
  1. 0% VPO Baseline (10% Muni market-rate equivalent)
  2. 40% VPO under strict Np <= 2 cap on both zones
  3. 40% VPO under Tarea 3 mixed typology (Np_M <= 2 villas + 5-floor VPO towers)

Generates mobile-optimized fig7_vpo_mixed_opt.svg (RapidOCR verified).
"""

import io
import json
import os
import re
import math
import numpy as np
import pandas as pd
from PIL import Image
from scipy.optimize import differential_evolution
from scipy.stats import norm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from adjustText import adjust_text

import quantile_profit_optimizer as qpo

# %% 0. Paths, Bilingual JSON Preamble & Constants
LANG = os.environ.get("PLOT_LANG", "EN")  # Toggle "EN" / "ES"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ.get("PLOT_OUT_DIR", SCRIPT_DIR)
XLSX_PATH = os.path.join(SCRIPT_DIR, "market_price_quantiles_sim.xlsx")
SVG_PATH = os.path.join(OUT_DIR, "fig7_vpo_mixed_opt.svg")

LABELS_EN_JSON = r"""
{
  "title1": "1. Unified Cost Surface (Includes VPO Underground Garage >70%)\nEven With Garage Cost, BCR_V=90% Preserves High-Margin Market Land",
  "xlabel1": "Market Lot Coverage BCR_M (%)",
  "ylabel1": "VPO Lot Coverage BCR_V (%)",
  "cbar1": "E[Profit] (M EUR)",
  "garage_line": "VPO Garage Threshold (70%)",
  "opt_ann": "Optimum: BCR_M={oc_m:.1f}%, BCR_V=90%\nGross FAR*={ce:.3f} | {prof:.1f}M",
  "title2": "2. Regime Shift Under Single Unified Construction Cost Curve",
  "xlabel2": "Total Sector Gross FAR (Ce, m2t / m2s)",
  "ylabel2": "Expected Margin (M EUR)",
  "leg_0": "0% VPO (Market Baseline)",
  "leg_2f": "40% VPO | 2F + Garage (BCR_V=90%)",
  "leg_5f": "40% VPO | 5F Tower + Garage",
  "tag_0": "No VPO",
  "tag_5f": "5F VPO",
  "tag_2f": "2F VPO",
  "ocr": ["Optimum", "54.7", "44.7", "47.1", "Garage"]
}
"""

LABELS_ES_JSON = r"""
{
  "title1": "1. Superficie de Coste Unificada (Incluye Garaje VPO >70%)\nAun con Sótano, BCR_V=90% Preserva el Suelo Libre de Alto Margen",
  "xlabel1": "Ocupación Zona Libre BCR_M (%)",
  "ylabel1": "Ocupación Zona VPO BCR_V (%)",
  "cbar1": "E[Beneficio] (M EUR)",
  "garage_line": "Umbral Garaje VPO (70%)",
  "opt_ann": "Óptimo: BCR_M={oc_m:.1f}%, BCR_V=90%\nGross FAR*={ce:.3f} | {prof:.1f}M",
  "title2": "2. Cambio de Régimen bajo Curva Única de Coste Constructivo",
  "xlabel2": "Gross FAR Total del Sector (Ce, m2c / m2s)",
  "ylabel2": "Margen Esperado (M EUR)",
  "leg_0": "0% VPO (Referencia Libre)",
  "leg_2f": "40% VPO | 2P + Garaje (BCR_V=90%)",
  "leg_5f": "40% VPO | Torre 5P + Garaje",
  "tag_0": "Sin VPO",
  "tag_5f": "VPO 5P",
  "tag_2f": "VPO 2P",
  "ocr": ["Óptimo", "54.7", "44.7", "47.1", "Garaje"]
}
"""

TXT = json.loads(LABELS_EN_JSON)
if LANG.upper() == "ES":
    TXT.update(json.loads(LABELS_ES_JSON))

Z_75 = float(norm.ppf(0.75))

P_VPO_CAP = 1680.0       # Regulated VPO module sale price (EUR/m2t)
VPO_TOTAL_SHARE = 0.40   # 40% of total E_teorica (10% Muni PMS + 30% Promoter VPO)
MKT_SHARE = 0.60         # 60% of total E_teorica (Free-market promoter)
VPO_PROM_SHARE = 0.30    # 30% of total E_teorica (Promoter VPO)


def unified_build_cost(oc, np_floors, is_vpo=False):
    """
    Single physical hard-cost function (EUR/m2t) shared across all typologies:
      1. Envelope compactness & scale economies via net intensity (oc * Np)
      2. Elevator / seismic structural step for multi-family >= 3 floors
      3. Common underground garage (+250 EUR/m2t) when surface parking saturates
         (oc > 70%) OR collective density requires basements (Np >= 3)
      4. Market luxury finish correlation at low density (VPO at statutory basic spec)
    """
    e_net = oc * np_floors
    c_env = 1120.0 + 420.0 / (1.0 + np.exp(3.2 * (e_net - 1.15)))
    c_hgt = 90.0 / (1.0 + np.exp(-6.0 * (np_floors - 2.6)))
    trig_oc = 1.0 / (1.0 + np.exp(-24.0 * (oc - 0.70)))
    trig_np = 1.0 / (1.0 + np.exp(-6.0 * (np_floors - 2.6)))
    c_gar = 250.0 * max(trig_oc, trig_np)
    c_spec = 0.0 if is_vpo else (220.0 / (1.0 + np.exp(8.0 * (oc - 0.55))))
    return float(c_env + c_hgt + c_gar + c_spec)


def build_price_fn(fit):
    """Return calibrated skew-adjusted market price E[P(C_ocup_M)]."""
    ce_lo = float(fit["ce_obs"].min())
    ce_hi = float(fit["ce_obs"].max())

    def market_expected_price(oc_m):
        ce_eq = np.clip(qpo.oc_to_ce(oc_m), ce_lo, ce_hi)
        p25 = qpo.logistic_decay(ce_eq, *fit["params_25"])
        p50 = qpo.logistic_decay(ce_eq, *fit["params_50"])
        p75 = qpo.logistic_decay(ce_eq, *fit["params_75"])
        return p50 + (((p75 - p50) / Z_75) - ((p50 - p25) / Z_75)) / math.sqrt(2.0 * math.pi)

    return market_expected_price


def coupled_ce_max(oc_m, oc_v, np_m=2.0, np_v=2.0, vpo_share=0.40):
    """Closed-form 2-zone frontier constructability Ce_max(C_ocup_M, C_ocup_V)."""
    mkt_share = 1.0 - vpo_share
    denom = 0.45 + (mkt_share / (np_m * oc_m)) + (vpo_share / (np_v * oc_v))
    return 0.90 / denom


def solve_scenario(p_mkt_fn, vpo_share, np_v_cap, oc_v_bounds, label):
    """Solve 3D (Ce, C_ocup_M, C_ocup_V) sector optimization via Differential Evolution."""
    vpo_prom = max(0.0, vpo_share - qpo.MUNI_SHARE)
    mkt_share = (1.0 - qpo.MUNI_SHARE) - vpo_prom

    def neg_profit(x):
        ce, oc_m, oc_v = x
        e_t = qpo.S_BRUTA * ce
        s_net = qpo.S_BRUTA - qpo.S_VIARIO - qpo.R_CES * e_t
        e_mkt = mkt_share * e_t
        e_vpo_tot = vpo_share * e_t
        e_vpo_prom = vpo_prom * e_t

        if vpo_share > 0.0:
            s_vpo_min = e_vpo_tot / (oc_v * np_v_cap)
            s_mkt_avail = s_net - s_vpo_min
        else:
            # 10% municipal cession is market-rate equivalent at same density
            s_mkt_avail = (1.0 - qpo.MUNI_SHARE) * s_net
        if s_mkt_avail < qpo.S_MIN_PLOT:
            return 1e12
        np_mkt = e_mkt / (s_mkt_avail * oc_m)
        if np_mkt > qpo.NP_CAP + 1e-6:
            return 1e12

        pm = float(p_mkt_fn(oc_m))
        cm = unified_build_cost(oc_m, 2.0, is_vpo=False)
        cv = unified_build_cost(oc_v, np_v_cap, is_vpo=True)
        profit_eur = (pm - cm) * e_mkt + (P_VPO_CAP - cv) * e_vpo_prom - qpo.COST_URB_M2S * qpo.S_BRUTA
        return -profit_eur / 1e6

    res = differential_evolution(
        neg_profit,
        bounds=[(0.40, 1.20), (0.35, 0.90), oc_v_bounds],
        seed=42,
        tol=1e-6,
        polish=True,
    )
    ce, oc_m, oc_v = res.x
    e_t = qpo.S_BRUTA * ce
    s_net = qpo.S_BRUTA - qpo.S_VIARIO - qpo.R_CES * e_t
    s_vpo = (vpo_share * e_t) / (oc_v * np_v_cap) if vpo_share > 0.0 else 0.0
    s_mkt = (s_net - s_vpo) if vpo_share > 0.0 else (1.0 - qpo.MUNI_SHARE) * s_net
    return {
        "label": label,
        "Ce": float(ce),
        "oc_M": float(oc_m),
        "oc_V": float(oc_v),
        "np_V": float(np_v_cap),
        "C_mkt": unified_build_cost(oc_m, 2.0, is_vpo=False),
        "C_vpo": unified_build_cost(oc_v, np_v_cap, is_vpo=True) if vpo_share > 0.0 else 0.0,
        "S_net": float(s_net),
        "S_mkt": float(s_mkt),
        "S_vpo": float(s_vpo),
        "E_mkt": float(mkt_share * e_t),
        "E_vpo_tot": float(vpo_share * e_t),
        "Profit_MEUR": -float(res.fun),
    }


def make_svg_responsive(svg_path):
    """Make SVG width 100% with mobile-friendly max-width while preserving viewBox."""
    with open(svg_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(
        r'(<svg[^>]*?)\s+width="[^"]+"\s+height="[^"]+"',
        r'\1 width="100%" style="max-width:680px;height:auto;display:block;margin:auto;"',
        content,
        count=1,
    )
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(content)


def verify_in_memory_ocr(fig, required_tokens, label):
    """Render in-memory PNG buffer for RapidOCR check (no PNG saved on disk)."""
    from rapidocr_onnxruntime import RapidOCR

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=180, bbox_inches="tight", facecolor="white")
    buf.seek(0)
    img_arr = np.array(Image.open(buf).convert("RGB"))
    buf.close()

    ocr = RapidOCR()
    result, _ = ocr(img_arr)
    detected_texts = []
    boxes = []
    if result:
        for item in result:
            box, text, conf = item
            detected_texts.append((text, float(conf)))
            xs = [p[0] for p in box]
            ys = [p[1] for p in box]
            boxes.append((min(xs), min(ys), max(xs), max(ys), text))

    joined = " | ".join(t for t, _ in detected_texts)
    missing = [tok for tok in required_tokens if tok.lower() not in joined.lower()]
    overlaps = []
    for i in range(len(boxes)):
        ax1, ay1, ax2, ay2, at = boxes[i]
        area_a = max(1.0, (ax2 - ax1) * (ay2 - ay1))
        for j in range(i + 1, len(boxes)):
            bx1, by1, bx2, by2, bt = boxes[j]
            ix1, iy1 = max(ax1, bx1), max(ay1, by1)
            ix2, iy2 = min(ax2, bx2), min(ay2, by2)
            if ix2 > ix1 and iy2 > iy1:
                inter = (ix2 - ix1) * (iy2 - iy1)
                area_b = max(1.0, (bx2 - bx1) * (by2 - by1))
                ratio = inter / min(area_a, area_b)
                if ratio > 0.10:
                    overlaps.append((at, bt, round(ratio, 2)))

    print(f"[OCR CHECK] {label}: {len(detected_texts)} regions, missing={missing}, overlaps={overlaps}")


# %% 1. Build 2-Panel Mobile SVG (Coupled 2D Slice + Regime Comparison)
def build_fig7(p_mkt_fn, res_base, res_2f, res_5f):
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
    plt.rcParams["svg.fonttype"] = "none"

    fig = plt.figure(figsize=(6.4, 8.8), facecolor="white")
    gs = fig.add_gridspec(2, 1, height_ratios=[1.05, 1.05], hspace=0.40)

    # --- Panel A: 2D Coupled Frontier Surface E[Pi](C_ocup_M, C_ocup_V) for Strict Np <= 2 ---
    ax1 = fig.add_subplot(gs[0])
    oc_m_grid = np.linspace(0.35, 0.90, 90)
    oc_v_grid = np.linspace(0.35, 0.90, 90)
    OM, OV = np.meshgrid(oc_m_grid, oc_v_grid)
    CE_MAT = coupled_ce_max(OM, OV, np_m=2.0, np_v=2.0, vpo_share=VPO_TOTAL_SHARE)

    PI_MAT = np.zeros_like(CE_MAT)
    for i in range(OM.shape[0]):
        for j in range(OM.shape[1]):
            ce_val = float(CE_MAT[i, j])
            om_val = float(OM[i, j])
            ov_val = float(OV[i, j])
            e_t = qpo.S_BRUTA * ce_val
            pm = float(p_mkt_fn(om_val))
            cm = unified_build_cost(om_val, 2.0, is_vpo=False)
            cv = unified_build_cost(ov_val, 2.0, is_vpo=True)
            PI_MAT[i, j] = ((pm - cm) * MKT_SHARE * e_t + (P_VPO_CAP - cv) * VPO_PROM_SHARE * e_t - qpo.COST_URB_M2S * qpo.S_BRUTA) / 1e6

    cf = ax1.contourf(OM * 100.0, OV * 100.0, PI_MAT, levels=16, cmap="YlGnBu")
    cs = ax1.contour(OM * 100.0, OV * 100.0, CE_MAT, levels=[0.50, 0.60, 0.67, 0.75], colors="#0F172A", linestyles="--", linewidths=1.0)
    ax1.clabel(cs, fmt="FAR=%.2f", fontsize=7.5, inline=True)
    ax1.axhline(70.0, color="#DC2626", ls=":", lw=1.2)
    ax1.text(63.0, 66.2, TXT["garage_line"], fontsize=7.3, fontweight="bold", color="#B91C1C",
             bbox=dict(boxstyle="round,pad=0.14", fc="white", ec="none", alpha=0.82))

    cbar = fig.colorbar(cf, ax=ax1, pad=0.02)
    cbar.set_label(TXT["cbar1"], fontsize=8.2, fontweight="bold", color="#0F172A")
    cbar.ax.tick_params(labelsize=7.5)

    # Mark strict 2-floor optimum on corner BCR_V = 90%
    ax1.plot(res_2f["oc_M"] * 100.0, res_2f["oc_V"] * 100.0, "*", color="#F59E0B", ms=13, markeredgecolor="#0F172A", zorder=8)
    ax1.annotate(
        TXT["opt_ann"].format(oc_m=res_2f["oc_M"] * 100.0, ce=res_2f["Ce"], prof=res_2f["Profit_MEUR"]),
        xy=(res_2f["oc_M"] * 100.0, res_2f["oc_V"] * 100.0),
        xytext=(48.0, 74.0),
        fontsize=7.6,
        fontweight="bold",
        color="#B45309",
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#F59E0B", alpha=0.95),
        arrowprops=dict(arrowstyle="->", color="#F59E0B", lw=1.2),
        zorder=9,
    )

    ax1.set_xlim(35, 90)
    ax1.set_ylim(35, 91)
    ax1.set_xlabel(TXT["xlabel1"], fontsize=8.8, fontweight="bold", color="#0F172A")
    ax1.set_ylabel(TXT["ylabel1"], fontsize=8.8, fontweight="bold", color="#0F172A")
    ax1.set_title(TXT["title1"], fontsize=9.1, fontweight="bold", color="#0F172A", pad=8)

    # --- Panel B: Expected Profit vs Gross FAR Across 3 Regimes ---
    ax2 = fig.add_subplot(gs[1])
    oc_m_sweep = np.linspace(0.35, 0.90, 301)

    # Curve 1: 0% VPO
    ce_0 = qpo.oc_to_ce(oc_m_sweep)
    pi_0 = np.array([
        ((float(p_mkt_fn(om)) - unified_build_cost(om, 2.0, False)) * 0.90 * qpo.S_BRUTA * ce - qpo.COST_URB_M2S * qpo.S_BRUTA) / 1e6
        for om, ce in zip(oc_m_sweep, ce_0)
    ])

    # Curve 2: 40% VPO, Np <= 2 (fixing BCR_V = 90% optimal corner; includes underground garage)
    ce_2f = coupled_ce_max(oc_m_sweep, res_2f["oc_V"], np_m=2.0, np_v=2.0, vpo_share=VPO_TOTAL_SHARE)
    cv_2f = unified_build_cost(res_2f["oc_V"], 2.0, is_vpo=True)
    pi_2f = np.array([
        ((float(p_mkt_fn(om)) - unified_build_cost(om, 2.0, False)) * MKT_SHARE * qpo.S_BRUTA * ce
         + (P_VPO_CAP - cv_2f) * VPO_PROM_SHARE * qpo.S_BRUTA * ce - qpo.COST_URB_M2S * qpo.S_BRUTA) / 1e6
        for om, ce in zip(oc_m_sweep, ce_2f)
    ])

    # Curve 3: 40% VPO, Tarea 3 5-Floor Towers (includes elevator core + common underground garage)
    ce_5f = coupled_ce_max(oc_m_sweep, res_5f["oc_V"], np_m=2.0, np_v=5.0, vpo_share=VPO_TOTAL_SHARE)
    cv_5f = unified_build_cost(res_5f["oc_V"], 5.0, is_vpo=True)
    pi_5f = np.array([
        ((float(p_mkt_fn(om)) - unified_build_cost(om, 2.0, False)) * MKT_SHARE * qpo.S_BRUTA * ce
         + (P_VPO_CAP - cv_5f) * VPO_PROM_SHARE * qpo.S_BRUTA * ce - qpo.COST_URB_M2S * qpo.S_BRUTA) / 1e6
        for om, ce in zip(oc_m_sweep, ce_5f)
    ])

    ax2.plot(ce_0, pi_0, color="#64748B", ls="--", lw=2.0, label=TXT["leg_0"])
    ax2.plot(ce_2f, pi_2f, color="#DC2626", ls="-", lw=2.2, label=TXT["leg_2f"])
    ax2.plot(ce_5f, pi_5f, color="#0284C7", ls="-.", lw=2.2, label=TXT["leg_5f"])

    peaks = [
        (res_base, "#475569", TXT["tag_0"], (0.475, 58.5)),
        (res_5f, "#0284C7", TXT["tag_5f"], (0.745, 53.0)),
        (res_2f, "#DC2626", TXT["tag_2f"], (0.630, 30.0)),
    ]
    for r, col, tag, pos in peaks:
        ax2.plot(r["Ce"], r["Profit_MEUR"], "o", color=col, ms=7.5, markeredgecolor="#0F172A", lw=0.8, zorder=7)
        ax2.annotate(
            f"{tag}: FAR={r['Ce']:.3f} ({r['Profit_MEUR']:.1f}M)",
            xy=(r["Ce"], r["Profit_MEUR"]),
            xytext=pos,
            fontsize=8.0,
            fontweight="bold",
            color=col,
            bbox=dict(boxstyle="round,pad=0.22", fc="white", ec=col, alpha=0.96),
            arrowprops=dict(arrowstyle="->", color=col, lw=1.1, shrinkB=4),
            zorder=9,
        )

    ax2.set_xlim(0.46, 0.96)
    ax2.set_ylim(16, 64)
    ax2.set_xlabel(TXT["xlabel2"], fontsize=8.8, fontweight="bold", color="#0F172A")
    ax2.set_ylabel(TXT["ylabel2"], fontsize=8.8, fontweight="bold", color="#0F172A")
    ax2.set_title(TXT["title2"], fontsize=9.8, fontweight="bold", color="#0F172A", pad=8)
    ax2.grid(True, ls=":", color="#CBD5E1", alpha=0.85)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(loc="lower left", fontsize=7.5, frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1")

    fig.savefig(SVG_PATH, format="svg", bbox_inches="tight", facecolor="white")
    make_svg_responsive(SVG_PATH)
    verify_in_memory_ocr(fig, TXT["ocr"], "fig7_vpo_mixed")
    plt.close(fig)


# %% Main Entry Point
if __name__ == "__main__":
    df_sum = pd.read_excel(XLSX_PATH, sheet_name="Quartile_Summary")
    fit = qpo.fit_joint_nonlinear_quantiles(df_sum)
    p_mkt_fn = build_price_fn(fit)

    res_base = solve_scenario(p_mkt_fn, 0.0, 2.0, (0.35, 0.90), "0% VPO Baseline")
    res_2f = solve_scenario(p_mkt_fn, VPO_TOTAL_SHARE, 2.0, (0.35, 0.90), "40% VPO Strict Np<=2")
    res_5f = solve_scenario(p_mkt_fn, VPO_TOTAL_SHARE, 5.0, (0.35, 0.55), "40% VPO Tarea3 5F Towers")

    print("=== Mixed Market + 40% VPO (Single Unified Physical Build Cost) ===")
    for r in [res_base, res_2f, res_5f]:
        print(
            f"  {r['label']:26s} | Ce*={r['Ce']:.4f} | oc_M={r['oc_M']*100:.1f}% | "
            f"oc_V={r['oc_V']*100:.1f}% (NpV={r['np_V']:.0f}) | "
            f"C_mkt={r['C_mkt']:.0f}, C_vpo={r['C_vpo']:.0f} EUR/m2t | "
            f"S_mkt={r['S_mkt']:.0f}, S_vpo={r['S_vpo']:.0f} m2s | E[Pi]={r['Profit_MEUR']:.2f}M EUR"
        )

    build_fig7(p_mkt_fn, res_base, res_2f, res_5f)
    print(f"\nGenerated SVG: {SVG_PATH}")
