# -*- coding: utf-8 -*-
"""
Sensitivity of Promoter Profit Optimum to Variable Build Cost C_build(Ce).
Compares:
  1. Constant baseline (1,400 EUR/m2t)
  2. Decreasing cost (spec + facade-to-volume + scale economies)
  3. U-shaped cost (economies up to ~70% occupancy, then basement garage inflection)
Generates mobile-optimized fig6_cost_curve_sensitivity.svg (RapidOCR verified).
"""

import io
import json
import os
import re
import math
import numpy as np
import pandas as pd
from PIL import Image
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
SVG_PATH = os.path.join(OUT_DIR, "fig6_cost_curve_sensitivity.svg")

LABELS_EN_JSON = r"""
{
  "models": {
    "const": "Constant (1,400)",
    "dec": "Decreasing (Facade+Scale)",
    "ushape": "U-Shape (+Basement >72%)"
  },
  "tags": {
    "const": "Const",
    "dec": "Dec",
    "ushape": "U-Shape"
  },
  "garage_box": "Garage\nthreshold\n(BCR>72%)",
  "title1": "1. How Build Cost Varies with Gross FAR (Np = 2)",
  "xlabel1": "Gross FAR (Ce, m2t / m2s) on 2-Floor Frontier",
  "ylabel1": "Hard Build Cost (EUR/m2t)",
  "title2": "2. Shift in Optimal Gross FAR* Under Cost Curves",
  "xlabel2": "Gross FAR (Ce, m2t / m2s) on 2-Floor Frontier",
  "ylabel2": "Expected Net Margin E[Pi] (M EUR)",
  "ocr": ["Const:", "Dec:", "U-Shape:", "Garage"]
}
"""

LABELS_ES_JSON = r"""
{
  "models": {
    "const": "Constante (1.400)",
    "dec": "Decreciente (Envolvente+Escala)",
    "ushape": "Forma en U (+Sótano BCR>72%)"
  },
  "tags": {
    "const": "Const",
    "dec": "Decrec",
    "ushape": "En U"
  },
  "garage_box": "Umbral\ngaraje\n(BCR>72%)",
  "title1": "1. Variación del Coste Constructivo con Gross FAR (Np = 2)",
  "xlabel1": "Gross FAR (Ce, m2c / m2s) en Frontera de 2 Plantas",
  "ylabel1": "Coste de Construcción (EUR/m2c)",
  "title2": "2. Desplazamiento del Óptimo Gross FAR* según Curva de Costes",
  "xlabel2": "Gross FAR (Ce, m2c / m2s) en Frontera de 2 Plantas",
  "ylabel2": "Margen Neto Esperado E[Pi] (M EUR)",
  "ocr": ["Const:", "Decrec:", "En U:", "garaje"]
}
"""

TXT = json.loads(LABELS_EN_JSON)
if LANG.upper() == "ES":
    _es = json.loads(LABELS_ES_JSON)
    for _k, _v in _es.items():
        if isinstance(_v, dict) and isinstance(TXT.get(_k), dict):
            TXT[_k].update(_v)
        else:
            TXT[_k] = _v

Z_75 = float(norm.ppf(0.75))


def build_cost_models(ce, oc):
    """Return three realistic hard build-cost regimes (EUR/m2t) along Np = 2 frontier."""
    c_const = np.full_like(ce, 1400.0)
    # Detached luxury villas (high facade/floor + pools/finishes) -> compact attached townhouses
    c_dec = 1240.0 + 500.0 / (1.0 + np.exp(9.0 * (ce - 0.62)))
    # Surface parking saturates above ~72% occupancy, forcing excavated basement stalls
    basement_share = 1.0 / (1.0 + np.exp(-22.0 * (oc - 0.72)))
    c_ushape = c_dec + 260.0 * basement_share
    return {
        "const": c_const,
        "dec": c_dec,
        "ushape": c_ushape,
    }


def make_svg_responsive(svg_path):
    """Make SVG scale cleanly on mobile screens via viewBox."""
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
    """Render in-memory PNG buffer for RapidOCR collision check (never written to disk)."""
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


# %% 1. Run Comparison & Generate SVG
if __name__ == "__main__":
    df_sum = pd.read_excel(XLSX_PATH, sheet_name="Quartile_Summary")
    fit = qpo.fit_joint_nonlinear_quantiles(df_sum)

    ce = np.linspace(float(df_sum["Ce_2floor"].min()), float(df_sum["Ce_2floor"].max()), 501)
    oc = qpo.ce_to_oc(ce)
    p25 = qpo.logistic_decay(ce, *fit["params_25"])
    p50 = qpo.logistic_decay(ce, *fit["params_50"])
    p75 = qpo.logistic_decay(ce, *fit["params_75"])
    p_mean = p50 + (((p75 - p50) / Z_75) - ((p50 - p25) / Z_75)) / math.sqrt(2.0 * math.pi)
    e_prom = (1.0 - qpo.MUNI_SHARE) * qpo.S_BRUTA * ce

    models = build_cost_models(ce, oc)
    colors = {
        "const": "#64748B",
        "dec": "#0284C7",
        "ushape": "#DC2626",
    }
    styles = {
        "const": "--",
        "dec": "-",
        "ushape": "-.",
    }

    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
    plt.rcParams["svg.fonttype"] = "none"

    fig = plt.figure(figsize=(6.4, 8.6), facecolor="white")
    gs = fig.add_gridspec(2, 1, height_ratios=[0.9, 1.15], hspace=0.40)

    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])

    texts = []
    targets_xy = []
    label_offsets = {
        "const": (0.49, 63.0),
        "dec": (0.67, 61.0),
        "ushape": (0.68, 50.0),
    }

    print("=== Variable Build Cost Sensitivity (Skew-Adjusted Expected Net Profit) ===")
    for key, c_arr in models.items():
        name = TXT["models"][key]
        pi_mean = ((p_mean - c_arr) * e_prom - qpo.COST_URB_M2S * qpo.S_BRUTA) / 1e6
        k = int(np.argmax(pi_mean))
        ce_k = float(ce[k])
        oc_k = float(oc[k])
        pi_k = float(pi_mean[k])
        pi_end = float(pi_mean[-1])
        print(f"  {name:32s}: Ce*={ce_k:.3f} (Oc={oc_k*100:.1f}%), Cost*={c_arr[k]:.0f} EUR/m2t, Peak={pi_k:.2f}M, At Ce=0.895={pi_end:.2f}M")

        ax1.plot(ce, c_arr, color=colors[key], ls=styles[key], lw=2.1, label=name)
        ax2.plot(ce, pi_mean, color=colors[key], ls=styles[key], lw=2.2, label=name)
        ax2.plot(ce_k, pi_k, "o", color=colors[key], ms=7.5, markeredgecolor="#0F172A", lw=0.8, zorder=7)

        lx, ly = label_offsets[key]
        short_tag = TXT["tags"][key]
        t = ax2.text(
            lx,
            ly,
            f"{short_tag}: Ce={ce_k:.3f} | {pi_k:.1f}M",
            fontsize=7.6,
            fontweight="bold",
            color=colors[key],
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=colors[key], alpha=0.95),
            zorder=8,
        )
        texts.append(t)
        targets_xy.append((ce_k, pi_k, colors[key]))

    # Top panel styling
    ax1.axvline(0.785, color="#94A3B8", ls=":", lw=1.1)
    ax1.text(0.793, 1555, TXT["garage_box"], fontsize=7.5, color="#475569",
             bbox=dict(boxstyle="round,pad=0.16", fc="white", ec="#CBD5E1", alpha=0.92))
    ax1.set_xlim(0.46, 0.91)
    ax1.set_ylim(1150, 1820)
    ax1.set_xlabel(TXT["xlabel1"], fontsize=9, fontweight="bold", color="#0F172A")
    ax1.set_ylabel(TXT["ylabel1"], fontsize=9, fontweight="bold", color="#0F172A")
    ax1.set_title(TXT["title1"], fontsize=10.0, fontweight="bold", color="#0F172A", pad=8)
    ax1.grid(True, ls=":", color="#CBD5E1", alpha=0.85)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.legend(loc="upper right", fontsize=7.6, frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1")

    # Bottom panel styling & collision avoidance
    adjust_text(
        texts,
        x=[pt[0] for pt in targets_xy],
        y=[pt[1] for pt in targets_xy],
        ax=ax2,
        expand=(1.15, 1.25),
        force_text=(0.35, 0.55),
        force_points=(0.45, 0.65),
    )
    for t, (tx, ty, col) in zip(texts, targets_xy):
        px, py = t.get_position()
        ax2.annotate(
            "",
            xy=(tx, ty),
            xytext=(px, py),
            arrowprops=dict(arrowstyle="->", color=col, lw=1.0, shrinkA=6, shrinkB=4),
            zorder=6,
        )

    ax2.set_xlim(0.46, 0.91)
    ax2.set_ylim(14, 68)
    ax2.set_xlabel(TXT["xlabel2"], fontsize=9, fontweight="bold", color="#0F172A")
    ax2.set_ylabel(TXT["ylabel2"], fontsize=9, fontweight="bold", color="#0F172A")
    ax2.set_title(TXT["title2"], fontsize=10.0, fontweight="bold", color="#0F172A", pad=8)
    ax2.grid(True, ls=":", color="#CBD5E1", alpha=0.85)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(loc="lower left", fontsize=7.6, frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1")

    fig.savefig(SVG_PATH, format="svg", bbox_inches="tight", facecolor="white")
    make_svg_responsive(SVG_PATH)
    verify_in_memory_ocr(fig, TXT["ocr"], "fig6_cost_sensitivity")
    plt.close(fig)
    print(f"\nGenerated SVG: {SVG_PATH}")
