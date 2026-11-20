# -*- coding: utf-8 -*-
"""
SciPy Urban Planning Optimizer for Tarea 4 (Replaces Galapagos).
Solves:
  1. Hard-constrained 2-floor buildability maximization (SLSQP + NonlinearConstraint)
  2. Sparse-data promoter profit optimization (PchipInterpolator + differential_evolution)
  3. Distribution-based stochastic/robust optimization (Monte Carlo + CVaR)
Generates a mobile-optimized SVG summary chart (fig4_scipy_promoter_opt.svg)
with in-memory RapidOCR collision verification (no PNG saved).
"""

import io
import json
import os
import re
import math
import numpy as np
from PIL import Image
from scipy.optimize import minimize, differential_evolution, NonlinearConstraint
from scipy.interpolate import PchipInterpolator
from scipy.stats import norm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# %% Global Configuration, Bilingual JSON Preamble & Fixed Statutory Constants
LANG = os.environ.get("PLOT_LANG", "EN")  # Toggle "EN" / "ES"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ.get("PLOT_OUT_DIR", SCRIPT_DIR)

LABELS_EN_JSON = r"""
{
  "title1": "1. Unknown Price Function Fitted from Sparse Comps\nSciPy PchipInterpolator + Epistemic Uncertainty",
  "xlabel1": "Plot Occupancy BCR / C_ocup (%)",
  "ylabel1": "Market Price (EUR / m2t)",
  "leg_band": "Market Uncertainty Band",
  "leg_pchip": "PCHIP Surrogate Price(BCR)",
  "leg_comps": "Observed Comps (5 pts)",
  "leg_cost": "Build Cost (1,400 EUR/m2t)",
  "title2": "2. Promoter Net Profit vs. BCR (10% Muni Cession)\nInterior Economic Peak vs. Boundary Buildability Max",
  "xlabel2": "Plot Occupancy BCR (%) along Np = 2 Frontier",
  "ylabel2": "Promoter Net Margin (M EUR)",
  "leg_p1090": "10th-90th Percentile Margin",
  "leg_mean": "Expected Net Margin E[Profit]",
  "leg_cvar": "Worst-20% CVaR Margin",
  "ann_pmax": "Profit Max (DE)\n{oc:.1f}% | FAR={ce:.3f}\n{prof:.1f}M EUR",
  "ann_ymax": "Max m2t (SLSQP)\n90% | FAR=0.895\n{prof:.1f}M EUR",
  "ocr": ["PCHIP", "Profit Max", "Max m2t", "90%"]
}
"""

LABELS_ES_JSON = r"""
{
  "title1": "1. Función de Precio Ajustada desde Testigos Dispersos\nInterpolación PCHIP + Incertidumbre Epistémica",
  "xlabel1": "Ocupación de Parcela BCR / C_ocup (%)",
  "ylabel1": "Precio de Mercado (EUR / m2c)",
  "leg_band": "Banda de Incertidumbre de Mercado",
  "leg_pchip": "Curva Sustituta PCHIP Precio(BCR)",
  "leg_comps": "Testigos Observados (5 ptos)",
  "leg_cost": "Coste Obra (1.400 EUR/m2c)",
  "title2": "2. Margen Neto del Promotor frente a BCR (10% Cesión PMS)\nÓptimo Económico Interior frente a Techo Máximo Normativo",
  "xlabel2": "Ocupación BCR (%) en Frontera Np = 2",
  "ylabel2": "Margen Neto Promotor (M EUR)",
  "leg_p1090": "Banda Percentil 10-90 Margen",
  "leg_mean": "Margen Neto Esperado E[Beneficio]",
  "leg_cvar": "Cola Pesimista CVaR 20%",
  "ann_pmax": "Máx Beneficio (DE)\n{oc:.1f}% | FAR={ce:.3f}\n{prof:.1f}M EUR",
  "ann_ymax": "Máx m2c (SLSQP)\n90% | FAR=0,895\n{prof:.1f}M EUR",
  "ocr": ["PCHIP", "Beneficio", "90%"]
}
"""

TXT = json.loads(LABELS_EN_JSON)
if LANG.upper() == "ES":
    TXT.update(json.loads(LABELS_ES_JSON))

S_BRUTA = 60000.0       # m2s (6 ha)
S_VIARIO = 6000.0       # m2s (10%)
R_CES = 0.45            # 45 m2s / 100 m2t
S_MIN_PLOT = 700.0      # m2s
NP_CAP = 2.0            # 2-floor cap
CE_BOUNDS = (0.40, 1.20)
OCUP_BOUNDS = (0.30, 0.90)
MUNI_SHARE = 0.10       # Ley 4/2017 Art. 44.c (10% urbanized plots to Council)


def sector_metrics(ce, c_ocup):
    """Compute core mass-balance quantities for (Ce, C_ocup)."""
    e_teorica = S_BRUTA * ce
    s_cesiones = R_CES * e_teorica
    s_neta = S_BRUTA - S_VIARIO - s_cesiones
    n_parcelas = math.floor(s_neta / S_MIN_PLOT)
    s_ocup_total = s_neta * c_ocup
    n_plantas_exact = e_teorica / max(1e-9, s_ocup_total)
    return {
        "Ce": float(ce),
        "C_ocup": float(c_ocup),
        "E_teorica": float(e_teorica),
        "S_cesiones": float(s_cesiones),
        "S_neta": float(s_neta),
        "N_parcelas": int(n_parcelas),
        "N_plantas_exact": float(n_plantas_exact),
    }


def make_svg_responsive(svg_path):
    """Ensure root <svg> scales cleanly on mobile screens via viewBox."""
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
    """Render figure to an in-memory buffer and check text readability + overlaps."""
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        print(f"[SKIP OCR] {label}: rapidocr_onnxruntime not available")
        return

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
                if ratio > 0.15:
                    overlaps.append((at, bt, round(ratio, 2)))

    print(f"[OCR CHECK] {label}: {len(detected_texts)} regions, missing={missing}, overlaps={overlaps}")


# %% 1. Case 1: Hard-Constrained Yield Optimization (SLSQP)
def solve_yield_slsqp():
    """Exact constrained optimization replacing Galapagos penalty tuning."""
    # x = [Ce, C_ocup]
    def neg_buildability(x):
        return -x[0]

    # Normalized constraint: (2 * S_neta * C_ocup - E_teorica) / S_BRUTA >= 0
    def floor_slack(x):
        ce, oc = x
        e_t = S_BRUTA * ce
        s_net = S_BRUTA - S_VIARIO - R_CES * e_t
        return (2.0 * s_net * oc - e_t) / S_BRUTA

    cons = NonlinearConstraint(floor_slack, lb=0.0, ub=np.inf)
    res = minimize(
        neg_buildability,
        x0=np.array([0.70, 0.70]),
        method="SLSQP",
        bounds=[CE_BOUNDS, OCUP_BOUNDS],
        constraints=[cons],
        options={"ftol": 1e-12, "maxiter": 500},
    )
    assert res.success, f"SLSQP failed: {res.message}"
    return sector_metrics(res.x[0], res.x[1])


# %% 2. Case 2: Unknown Price Curve from Sparse Comps (PCHIP + Differential Evolution)
OBS_OCUP = np.array([0.40, 0.50, 0.62, 0.75, 0.90])
OBS_PRICE = np.array([3400.0, 3200.0, 2820.0, 2420.0, 2100.0])  # Illustrative EUR/m2t market comps
price_surrogate = PchipInterpolator(OBS_OCUP, OBS_PRICE)

COST_BUILD_M2T = 1400.0    # EUR/m2t construction cost on promoter share
COST_URB_M2S = 50.0        # EUR/m2s sector urbanization cost (100% paid by promoter)


def promoter_profit_eur(ce, c_ocup, price_fn):
    """Net promoter profit (EUR) accounting for 10% municipal cession & 100% urb cost."""
    m = sector_metrics(ce, c_ocup)
    if m["N_plantas_exact"] > NP_CAP + 1e-6 or m["N_parcelas"] < 1:
        return -1e12
    e_prom = (1.0 - MUNI_SHARE) * m["E_teorica"]
    p_m2t = float(price_fn(np.clip(c_ocup, OBS_OCUP[0], OBS_OCUP[-1])))
    revenue = p_m2t * e_prom
    cost_const = COST_BUILD_M2T * e_prom
    cost_urb = COST_URB_M2S * S_BRUTA
    # Small plot-efficiency bonus/penalty: penalize >150 m2s wasted remainder
    rem = m["S_neta"] - m["N_parcelas"] * S_MIN_PLOT
    return revenue - cost_const - cost_urb - 200.0 * rem


def solve_profit_de():
    """Derivative-free global optimization over non-smooth discrete + surrogate objective."""
    def obj(x):
        return -promoter_profit_eur(x[0], x[1], price_surrogate)

    def height_constraint(x):
        ce, oc = x
        e_t = S_BRUTA * ce
        s_net = S_BRUTA - S_VIARIO - R_CES * e_t
        return (2.0 * s_net * oc - e_t) / S_BRUTA

    nlc = NonlinearConstraint(height_constraint, lb=0.0, ub=np.inf)
    res = differential_evolution(
        obj,
        bounds=[CE_BOUNDS, (0.40, 0.90)],
        constraints=(nlc,),
        seed=42,
        tol=1e-6,
        polish=False,
    )
    m = sector_metrics(res.x[0], res.x[1])
    m["Profit_MEUR"] = -res.fun / 1e6
    m["Price_EUR_m2t"] = float(price_surrogate(res.x[1]))
    return m


# %% 3. Case 3: Distribution Intuition (Monte Carlo + Expected Value & CVaR)
def solve_stochastic_frontier(n_draws=1000, seed=42):
    """Sample uncertain market price curves around sparse comps and optimize E[Profit] & CVaR."""
    rng = np.random.default_rng(seed)
    oc_grid = np.linspace(0.40, 0.90, 201)
    ce_grid = (1.8 * oc_grid) / (1.0 + 0.9 * oc_grid)
    e_grid = S_BRUTA * ce_grid
    e_prom_grid = (1.0 - MUNI_SHARE) * e_grid

    # Uncertainty grows at intermediate/unobserved occupancies + overall market shift
    base_p = price_surrogate(oc_grid)
    dist_to_obs = np.min(np.abs(oc_grid[:, None] - OBS_OCUP[None, :]), axis=1)
    sigma_p = 110.0 + 1800.0 * dist_to_obs  # EUR/m2t uncertainty

    # Correlated market shock + smooth slope shock
    market_shock = norm.rvs(loc=0.0, scale=140.0, size=(n_draws, 1), random_state=rng)
    slope_shock = norm.rvs(loc=0.0, scale=450.0, size=(n_draws, 1), random_state=rng)
    local_noise = norm.rvs(loc=0.0, scale=1.0, size=(n_draws, len(oc_grid)), random_state=rng) * sigma_p[None, :]

    p_samples = base_p[None, :] + market_shock + slope_shock * (oc_grid[None, :] - 0.65) + 0.35 * local_noise
    profit_samples = (p_samples - COST_BUILD_M2T) * e_prom_grid[None, :] - COST_URB_M2S * S_BRUTA

    mean_profit = np.mean(profit_samples, axis=0) / 1e6
    p10_profit = np.percentile(profit_samples, 10, axis=0) / 1e6
    p90_profit = np.percentile(profit_samples, 90, axis=0) / 1e6
    # CVaR (mean of worst 20% outcomes)
    k20 = max(1, int(0.20 * n_draws))
    cvar20 = np.mean(np.sort(profit_samples, axis=0)[:k20, :], axis=0) / 1e6

    idx_exp = int(np.argmax(mean_profit))
    idx_cvar = int(np.argmax(cvar20))
    return {
        "oc_grid": oc_grid,
        "ce_grid": ce_grid,
        "base_p": base_p,
        "sigma_p": sigma_p,
        "mean_profit": mean_profit,
        "p10_profit": p10_profit,
        "p90_profit": p90_profit,
        "cvar20": cvar20,
        "opt_exp": (float(oc_grid[idx_exp]), float(ce_grid[idx_exp]), float(mean_profit[idx_exp])),
        "opt_cvar": (float(oc_grid[idx_cvar]), float(ce_grid[idx_cvar]), float(cvar20[idx_cvar])),
    }


# %% 4. Mobile-First SVG Plot Generation
def build_fig4(yield_opt, profit_opt, stoch):
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
    plt.rcParams["svg.fonttype"] = "none"

    fig = plt.figure(figsize=(6.4, 8.6), facecolor="white")
    gs = fig.add_gridspec(2, 1, height_ratios=[0.95, 1.15], hspace=0.36)

    oc_pct = stoch["oc_grid"] * 100.0

    # --- Panel A: Sparse Comps + PCHIP Surrogate + Uncertainty ---
    ax1 = fig.add_subplot(gs[0])
    ax1.fill_between(oc_pct, stoch["base_p"] - 1.5 * stoch["sigma_p"], stoch["base_p"] + 1.5 * stoch["sigma_p"],
                     color="#DBEAFE", alpha=0.85, label=TXT["leg_band"])
    ax1.plot(oc_pct, stoch["base_p"], color="#2563EB", lw=2.2, label=TXT["leg_pchip"])
    ax1.plot(OBS_OCUP * 100.0, OBS_PRICE, "o", color="#0F172A", ms=7, zorder=6, label=TXT["leg_comps"])
    ax1.axhline(COST_BUILD_M2T, color="#DC2626", ls="--", lw=1.3, label=TXT["leg_cost"])

    ax1.set_xlim(38, 92)
    ax1.set_ylim(1200, 3800)
    ax1.set_xlabel(TXT["xlabel1"], fontsize=9, fontweight="bold", color="#0F172A")
    ax1.set_ylabel(TXT["ylabel1"], fontsize=9, fontweight="bold", color="#0F172A")
    ax1.set_title(TXT["title1"], fontsize=10.2, fontweight="bold", color="#0F172A", pad=8)
    ax1.grid(True, ls=":", color="#CBD5E1", alpha=0.8)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.legend(loc="upper right", fontsize=7.8, frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1")

    # --- Panel B: Promoter Net Margin Along 2-Floor Frontier ---
    ax2 = fig.add_subplot(gs[1])
    ax2.fill_between(oc_pct, stoch["p10_profit"], stoch["p90_profit"],
                     color="#DCFCE7", alpha=0.85, label=TXT["leg_p1090"])
    ax2.plot(oc_pct, stoch["mean_profit"], color="#15803D", lw=2.3, label=TXT["leg_mean"])
    ax2.plot(oc_pct, stoch["cvar20"], color="#7C3AED", lw=1.8, ls="--", label=TXT["leg_cvar"])

    # Mark key points
    y_oc = yield_opt["C_ocup"] * 100.0
    y_idx = int(np.argmin(np.abs(oc_pct - y_oc)))
    y_prof = float(stoch["mean_profit"][y_idx])

    p_oc = profit_opt["C_ocup"] * 100.0
    p_prof = profit_opt["Profit_MEUR"]

    c_oc, c_ce, c_val = stoch["opt_cvar"]
    c_oc_pct = c_oc * 100.0
    c_idx = int(np.argmin(np.abs(oc_pct - c_oc_pct)))
    c_prof = float(stoch["mean_profit"][c_idx])

    ax2.plot(p_oc, p_prof, "*", color="#D97706", ms=12, markeredgecolor="#0F172A", zorder=7)
    ax2.annotate(TXT["ann_pmax"].format(oc=p_oc, ce=profit_opt["Ce"], prof=p_prof),
                 (p_oc, p_prof), xytext=(12, -8), textcoords="offset points",
                 fontsize=7.8, fontweight="bold", color="#B45309",
                 bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#D97706"),
                 arrowprops=dict(arrowstyle="->", color="#D97706"), zorder=8)

    ax2.plot(y_oc, y_prof, "s", color="#DC2626", ms=8, markeredgecolor="white", zorder=7)
    ax2.annotate(TXT["ann_ymax"].format(prof=y_prof),
                 (y_oc, y_prof), xytext=(-88, 22), textcoords="offset points",
                 fontsize=7.8, fontweight="bold", color="#B91C1C",
                 bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#DC2626"),
                 arrowprops=dict(arrowstyle="->", color="#DC2626"), zorder=8)

    ax2.set_xlim(38, 92)
    ax2.set_ylim(20, 78)
    ax2.set_xlabel(TXT["xlabel2"], fontsize=9, fontweight="bold", color="#0F172A")
    ax2.set_ylabel(TXT["ylabel2"], fontsize=9, fontweight="bold", color="#0F172A")
    ax2.set_title(TXT["title2"], fontsize=10.2, fontweight="bold", color="#0F172A", pad=8)
    ax2.grid(True, ls=":", color="#CBD5E1", alpha=0.8)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(loc="lower left", fontsize=7.8, frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1")

    out_path = os.path.join(OUT_DIR, "fig4_scipy_promoter_opt.svg")
    fig.savefig(out_path, format="svg", bbox_inches="tight", facecolor="white")
    make_svg_responsive(out_path)
    verify_in_memory_ocr(fig, TXT["ocr"], "fig4_scipy")
    plt.close(fig)
    return out_path


# %% Main Entry Point
if __name__ == "__main__":
    y_opt = solve_yield_slsqp()
    print("=== 1. SciPy SLSQP (Hard-Constrained Max Buildability, Np <= 2) ===")
    print(f"  Ce*={y_opt['Ce']:.6f}, C_ocup*={y_opt['C_ocup']*100:.2f}%, "
          f"E={y_opt['E_teorica']:.2f} m2t, Plots={y_opt['N_parcelas']}, Np={y_opt['N_plantas_exact']:.6f}")

    p_opt = solve_profit_de()
    print("\n=== 2. SciPy Differential Evolution (PCHIP Comps + Discrete Plots + 10% Muni) ===")
    print(f"  Ce*={p_opt['Ce']:.4f}, C_ocup*={p_opt['C_ocup']*100:.2f}%, "
          f"E={p_opt['E_teorica']:.1f} m2t, Plots={p_opt['N_parcelas']}, "
          f"Price={p_opt['Price_EUR_m2t']:.0f} EUR/m2t, NetMargin={p_opt['Profit_MEUR']:.2f}M EUR")

    st = solve_stochastic_frontier()
    print("\n=== 3. SciPy Monte Carlo Robust Frontier (1,000 draws) ===")
    print(f"  Expected Profit Peak : C_ocup={st['opt_exp'][0]*100:.1f}%, Ce={st['opt_exp'][1]:.4f}, E[Profit]={st['opt_exp'][2]:.2f}M EUR")
    print(f"  Worst-20% CVaR Peak  : C_ocup={st['opt_cvar'][0]*100:.1f}%, Ce={st['opt_cvar'][1]:.4f}, CVaR20={st['opt_cvar'][2]:.2f}M EUR")

    svg_file = build_fig4(y_opt, p_opt, st)
    print("\nGenerated SVG:", svg_file)
