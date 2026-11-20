# -*- coding: utf-8 -*-
"""
Non-Linear Quantile Regression & Promoter Profit Optimizer (Tarea 4).
Replaces ad-hoc Gaussian noise with spreadsheet-driven quartile curves:
  1. Reads (or initializes) market_price_quantiles_sim.xlsx (Quartile_Summary + Simulated_Raw_Comps).
  2. Fits joint non-crossing 4-parameter logistic quantile curves Q25(Ce), Q50(Ce), Q75(Ce)
     via SciPy SLSQP (Chamberlain minimum-distance grouped estimator) and cross-checks against
     raw-sample pinball loss optimization.
  3. Uses Quantile Equivariance + closed-form Asymmetric Split-Normal reconstruction to compute
     exact Q25, Q50, Q75, Skew-Adjusted E[Profit], and Downside CVaR25 without Monte Carlo noise,
     plus Differential Evolution check with discrete 700 m2s plot quantization.
  4. Outputs mobile-first SVG (fig5_quantile_profit_opt.svg) verified in-memory via RapidOCR.
"""

import io
import json
import os
import re
import math
import numpy as np
import pandas as pd
from PIL import Image
from scipy.optimize import minimize, differential_evolution
from scipy.stats import norm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from adjustText import adjust_text

# %% 0. Paths, Bilingual JSON Preamble & Statutory Sector Constants
LANG = os.environ.get("PLOT_LANG", "EN")  # Toggle "EN" / "ES"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ.get("PLOT_OUT_DIR", SCRIPT_DIR)
XLSX_PATH = os.path.join(SCRIPT_DIR, "market_price_quantiles_sim.xlsx")
SVG_PATH = os.path.join(OUT_DIR, "fig5_quantile_profit_opt.svg")

LABELS_EN_JSON = r"""
{
  "title1": "1. Non-Linear Logistic Quantile Regression on Spreadsheet Comps",
  "xlabel1": "Gross FAR (Ce, m2t / m2s) on 2-Floor Frontier",
  "ylabel1": "Market Price (EUR/m2t)",
  "xlabel1_top": "Corresponding Lot Coverage BCR (%)",
  "leg_iqr": "Fitted IQR Band (Q25-Q75)",
  "leg_q75": "Q75 Upper Quartile Fit",
  "leg_mean": "Skew-Adjusted E[P]",
  "leg_q50": "Q50 Median Fit",
  "leg_q25": "Q25 Lower Quartile Fit",
  "leg_comps": "Excel Quartiles (Q25, Q50, Q75)",
  "leg_cost": "Build Cost (1,400 EUR/m2t)",
  "title2": "2. Promoter Net Profit via Quantile Equivariance (10% Muni Cession)",
  "xlabel2": "Gross FAR (Ce, m2t / m2s) along 2-Floor Frontier",
  "ylabel2": "Net Margin (M EUR)",
  "leg_pi_iqr": "Profit IQR Band (Q25-Q75)",
  "leg_pi_75": "Q75 Upside Profit",
  "leg_pi_mean": "Expected Profit E[Pi] (Right-Skewed)",
  "leg_pi_50": "Q50 Median Profit",
  "leg_pi_25": "Q25 Lower Quartile Profit",
  "leg_pi_cvar": "Worst-25% CVaR Profit",
  "max_m2t": "Max m2t",
  "ocr": ["Q75", "Q50", "CVaR25", "Max m2t", "1,400 EUR"]
}
"""

LABELS_ES_JSON = r"""
{
  "title1": "1. Regresión Cuantílica Logística No Lineal sobre Testigos",
  "xlabel1": "Gross FAR (Ce, m2c / m2s) en Frontera de 2 Plantas",
  "ylabel1": "Precio de Mercado (EUR/m2c)",
  "xlabel1_top": "Ocupación Equivalente BCR (%)",
  "leg_iqr": "Banda IQR Ajustada (Q25-Q75)",
  "leg_q75": "Ajuste Cuartil Superior Q75",
  "leg_mean": "Media Asimétrica E[P]",
  "leg_q50": "Ajuste Mediana Q50",
  "leg_q25": "Ajuste Cuartil Inferior Q25",
  "leg_comps": "Cuartiles Excel (Q25, Q50, Q75)",
  "leg_cost": "Coste Obra (1.400 EUR/m2c)",
  "title2": "2. Beneficio Neto por Equivarianza Cuantílica (10% Cesión PMS)",
  "xlabel2": "Gross FAR (Ce, m2c / m2s) en Frontera de 2 Plantas",
  "ylabel2": "Margen Neto (M EUR)",
  "leg_pi_iqr": "Banda IQR Margen (Q25-Q75)",
  "leg_pi_75": "Margen Alcista Q75",
  "leg_pi_mean": "Margen Esperado E[Pi] (Asimetría +)",
  "leg_pi_50": "Margen Mediano Q50",
  "leg_pi_25": "Margen Inferior Q25",
  "leg_pi_cvar": "Cola Pesimista CVaR25",
  "max_m2t": "Máx m2c",
  "ocr": ["Q75", "Q50", "CVaR25", "Máx m2c", "1.400 EUR"]
}
"""

TXT = json.loads(LABELS_EN_JSON)
if LANG.upper() == "ES":
    TXT.update(json.loads(LABELS_ES_JSON))

S_BRUTA = 60000.0       # m2s (6 ha)
S_VIARIO = 6000.0       # m2s (10%)
R_CES = 0.45            # 45 m2s / 100 m2t
S_MIN_PLOT = 700.0      # m2s
NP_CAP = 2.0            # 2-floor statutory cap
MUNI_SHARE = 0.10       # Ley 4/2017 Art. 44.c (10% lucrative cession)
COST_BUILD_M2T = 1400.0 # EUR/m2t
COST_URB_M2S = 50.0     # EUR/m2s (100% borne by promoter)
REM_PENALTY_M2S = 200.0 # EUR/m2s plot-remainder inefficiency weight

Z_75 = float(norm.ppf(0.75))
PHI_Z75 = float(norm.pdf(Z_75))


def oc_to_ce(c_ocup):
    """Bijection on Np = 2 frontier: C_ocup -> Ce_max."""
    return (1.8 * c_ocup) / (1.0 + 0.9 * c_ocup)


def ce_to_oc(ce):
    """Inverse bijection on Np = 2 frontier: Ce -> C_ocup."""
    return ce / (1.8 - 0.9 * ce)


def build_simulated_spreadsheet(xlsx_path, seed=2026):
    """Create illustrative Excel workbook with market price quartiles across constructabilities."""
    oc_vals = np.array([0.35, 0.45, 0.52, 0.60, 0.70, 0.80, 0.90])
    ce_vals = np.round(oc_to_ce(oc_vals), 4)
    n_comps = np.array([18, 24, 31, 29, 26, 22, 19], dtype=int)
    q25_vals = np.array([3120.0, 3010.0, 2840.0, 2600.0, 2340.0, 2130.0, 1940.0])
    q50_vals = np.array([3480.0, 3310.0, 3090.0, 2810.0, 2510.0, 2260.0, 2060.0])
    q75_vals = np.array([4150.0, 3820.0, 3470.0, 3080.0, 2700.0, 2390.0, 2160.0])
    notes = [
        "Detached luxury villas + large pool/garden (strong right-skew)",
        "Low-density detached villas",
        "Semi-detached chalets pareados",
        "Grouped townhouses (adossados)",
        "Compact row houses",
        "High-occupancy patio houses",
        "Max-density 2-floor commodity units (compressed margin)",
    ]

    iqr = q75_vals - q25_vals
    bowley = ((q75_vals - q50_vals) - (q50_vals - q25_vals)) / iqr

    df_summary = pd.DataFrame({
        "C_ocup": oc_vals,
        "Ce_2floor": ce_vals,
        "n_comps": n_comps,
        "Q25_EUR_m2t": q25_vals,
        "Q50_EUR_m2t": q50_vals,
        "Q75_EUR_m2t": q75_vals,
        "IQR_EUR_m2t": iqr,
        "Bowley_Skew": np.round(bowley, 3),
        "Typology_Note": notes,
    })

    # Also build simulated raw comparable sales whose empirical quartiles closely match df_summary
    rng = np.random.default_rng(seed)
    raw_rows = []
    cid = 1
    for i in range(len(ce_vals)):
        m = q50_vals[i]
        sig_m = (m - q25_vals[i]) / Z_75
        sig_p = (q75_vals[i] - m) / Z_75
        ni = int(n_comps[i])
        # Stratified quantile grid inside [0.04, 0.96] so bucket empirical quartiles align cleanly
        probs = np.linspace(0.04, 0.96, ni)
        rng.shuffle(probs)
        prices = np.empty(ni)
        for j, u in enumerate(probs):
            if u < 0.5:
                prices[j] = m + sig_m * norm.ppf(u)
            else:
                prices[j] = m + sig_p * norm.ppf(u)
        prices = np.round(np.clip(prices, 1450.0, 5800.0), 0)
        for p_val in prices:
            raw_rows.append({
                "Comp_ID": f"CMP-{cid:03d}",
                "C_ocup": float(oc_vals[i]),
                "Ce_2floor": float(ce_vals[i]),
                "Price_EUR_m2t": float(p_val),
            })
            cid += 1
    df_raw = pd.DataFrame(raw_rows)

    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        df_summary.to_excel(writer, sheet_name="Quartile_Summary", index=False)
        df_raw.to_excel(writer, sheet_name="Simulated_Raw_Comps", index=False)


# %% 1. Joint Non-Crossing Non-Linear Quantile Regression (Logistic Sigmoid)
def logistic_decay(ce, low, high, slope, midpoint):
    """4-parameter non-linear decreasing price curve with saturation asymptotes."""
    z = np.clip(slope * (ce - midpoint), -40.0, 40.0)
    return low + (high - low) / (1.0 + np.exp(z))


def fit_joint_nonlinear_quantiles(df_sum):
    """
    Fit Q25(Ce), Q50(Ce), Q75(Ce) jointly using SciPy SLSQP on grouped quantiles
    (Chamberlain minimum-distance estimator) with strict non-crossing constraints.
    """
    ce_obs = df_sum["Ce_2floor"].to_numpy(dtype=float)
    w_obs = df_sum["n_comps"].to_numpy(dtype=float)
    targets = [
        df_sum["Q25_EUR_m2t"].to_numpy(dtype=float),
        df_sum["Q50_EUR_m2t"].to_numpy(dtype=float),
        df_sum["Q75_EUR_m2t"].to_numpy(dtype=float),
    ]
    ce_grid = np.linspace(ce_obs.min(), ce_obs.max(), 60)

    def pseudo_huber_loss(params):
        total = 0.0
        for idx, y_obs in enumerate(targets):
            pred = logistic_decay(ce_obs, *params[4 * idx : 4 * idx + 4])
            r = (pred - y_obs) / 50.0
            total += float(np.sum(w_obs * (np.sqrt(1.0 + r * r) - 1.0)))
        return total

    def non_crossing_margin(params):
        f25 = logistic_decay(ce_grid, *params[0:4])
        f50 = logistic_decay(ce_grid, *params[4:8])
        f75 = logistic_decay(ce_grid, *params[8:12])
        min_gap = 40.0
        return np.concatenate([(f50 - f25 - min_gap) / 100.0, (f75 - f50 - min_gap) / 100.0])

    x0 = np.array([
        1700.0, 3250.0, 10.0, 0.72,
        1800.0, 3650.0, 9.5, 0.72,
        1800.0, 4500.0, 9.0, 0.69,
    ])
    bounds = [
        (1200.0, 2600.0), (2700.0, 5500.0), (2.0, 28.0), (0.45, 0.88),
    ] * 3
    cons = {"type": "ineq", "fun": non_crossing_margin}
    res = minimize(
        pseudo_huber_loss,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=[cons],
        options={"maxiter": 1200, "ftol": 1e-11},
    )
    assert res.success, f"Joint quantile fit failed: {res.message}"
    return {
        "params_25": res.x[0:4],
        "params_50": res.x[4:8],
        "params_75": res.x[8:12],
        "ce_obs": ce_obs,
        "targets": targets,
    }


def fit_raw_pinball_check(df_raw, init_fit):
    """Cross-check: minimize exact check/pinball loss over simulated raw transactions."""
    ce_raw = df_raw["Ce_2floor"].to_numpy(dtype=float)
    y_raw = df_raw["Price_EUR_m2t"].to_numpy(dtype=float)
    taus = [0.25, 0.50, 0.75]
    inits = [init_fit["params_25"], init_fit["params_50"], init_fit["params_75"]]
    bounds = [(1200.0, 2600.0), (2700.0, 5500.0), (2.0, 28.0), (0.45, 0.88)]

    raw_params = {}
    for tau, p0 in zip(taus, inits):
        def pinball_obj(theta):
            u = y_raw - logistic_decay(ce_raw, *theta)
            # Smooth small epsilon corner for Powell/Nelder-Mead robustness
            loss = np.where(u >= 0.0, tau * u, (tau - 1.0) * u)
            return float(np.mean(loss))

        r = minimize(pinball_obj, p0, method="Nelder-Mead", options={"maxiter": 2000, "xatol": 1e-5, "fatol": 1e-5})
        raw_params[tau] = r.x
    return raw_params


# %% 2. Quantile Equivariance + Closed-Form Split-Normal Profit Metrics
def eval_profit_curves(ce_grid, fit):
    """
    Evaluate continuous and discrete-remainder net profits across quantiles.
    Because profit is linear-increasing in price P, quantiles transform identically
    by quantile equivariance without Monte Carlo sampling error.
    """
    p25 = logistic_decay(ce_grid, *fit["params_25"])
    p50 = logistic_decay(ce_grid, *fit["params_50"])
    p75 = logistic_decay(ce_grid, *fit["params_75"])

    # Two-piece split half-normal matching exact (Q25, Q50, Q75) at every Ce
    sig_m = np.maximum(1.0, (p50 - p25) / Z_75)
    sig_p = np.maximum(1.0, (p75 - p50) / Z_75)
    p_mean = p50 + (sig_p - sig_m) / math.sqrt(2.0 * math.pi)
    p_cvar25 = p50 - sig_m * (PHI_Z75 / 0.25)

    e_teorica = S_BRUTA * ce_grid
    e_prom = (1.0 - MUNI_SHARE) * e_teorica
    s_neta = S_BRUTA - S_VIARIO - R_CES * e_teorica
    n_plots = np.floor(s_neta / S_MIN_PLOT)
    rem = s_neta - n_plots * S_MIN_PLOT

    def price_to_profit_meur(price_arr, with_rem=True):
        rem_cost = REM_PENALTY_M2S * rem if with_rem else 0.0
        return ((price_arr - COST_BUILD_M2T) * e_prom - COST_URB_M2S * S_BRUTA - rem_cost) / 1e6

    return {
        "ce": ce_grid,
        "oc": ce_to_oc(ce_grid),
        "p25": p25,
        "p50": p50,
        "p75": p75,
        "p_mean": p_mean,
        "p_cvar25": p_cvar25,
        "pi_25": price_to_profit_meur(p25, with_rem=False),
        "pi_50": price_to_profit_meur(p50, with_rem=False),
        "pi_75": price_to_profit_meur(p75, with_rem=False),
        "pi_mean": price_to_profit_meur(p_mean, with_rem=False),
        "pi_cvar25": price_to_profit_meur(p_cvar25, with_rem=False),
        "pi_50_disc": price_to_profit_meur(p50, with_rem=True),
        "pi_mean_disc": price_to_profit_meur(p_mean, with_rem=True),
        "n_plots": n_plots,
    }


def optimize_discrete_de(fit, target="pi_mean"):
    """Global DE over Ce on [ce_min, ce_max] including discrete 700 m2s plot remainder."""
    ce_lo = float(fit["ce_obs"].min())
    ce_hi = float(fit["ce_obs"].max())

    def neg_obj(x):
        ce_val = float(x[0])
        p25 = float(logistic_decay(ce_val, *fit["params_25"]))
        p50 = float(logistic_decay(ce_val, *fit["params_50"]))
        p75 = float(logistic_decay(ce_val, *fit["params_75"]))
        sig_m = max(1.0, (p50 - p25) / Z_75)
        sig_p = max(1.0, (p75 - p50) / Z_75)
        if target == "pi_mean":
            p_eff = p50 + (sig_p - sig_m) / math.sqrt(2.0 * math.pi)
        elif target == "pi_cvar25":
            p_eff = p50 - sig_m * (PHI_Z75 / 0.25)
        elif target == "pi_75":
            p_eff = p75
        elif target == "pi_25":
            p_eff = p25
        else:
            p_eff = p50
        e_t = S_BRUTA * ce_val
        e_prom = (1.0 - MUNI_SHARE) * e_t
        s_net = S_BRUTA - S_VIARIO - R_CES * e_t
        n_pl = math.floor(s_net / S_MIN_PLOT)
        rem = s_net - n_pl * S_MIN_PLOT
        prof = ((p_eff - COST_BUILD_M2T) * e_prom - COST_URB_M2S * S_BRUTA - REM_PENALTY_M2S * rem) / 1e6
        return -prof

    res = differential_evolution(neg_obj, bounds=[(ce_lo, ce_hi)], seed=42, tol=1e-7, polish=True)
    ce_star = float(res.x[0])
    oc_star = float(ce_to_oc(ce_star))
    s_net = S_BRUTA - S_VIARIO - R_CES * S_BRUTA * ce_star
    return {
        "Ce": ce_star,
        "C_ocup": oc_star,
        "N_parcelas": int(math.floor(s_net / S_MIN_PLOT)),
        "Profit_MEUR": -float(res.fun),
    }


# %% 3. Mobile-Optimized SVG Visualization + In-Memory RapidOCR Verification
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
    """Render in-memory raster and check RapidOCR readability and zero overlaps."""
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


def build_fig5(df_sum, fit, curves):
    """Create mobile-first 2-panel SVG comparing quartile price fit and profit optima."""
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
    plt.rcParams["svg.fonttype"] = "none"

    fig = plt.figure(figsize=(6.4, 9.2), facecolor="white")
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.15], hspace=0.44)

    ce = curves["ce"]
    ce_obs = df_sum["Ce_2floor"].to_numpy(dtype=float)
    q25_obs = df_sum["Q25_EUR_m2t"].to_numpy(dtype=float)
    q50_obs = df_sum["Q50_EUR_m2t"].to_numpy(dtype=float)
    q75_obs = df_sum["Q75_EUR_m2t"].to_numpy(dtype=float)

    # --- Panel A: Non-Linear Quantile Regression of Price vs. Constructability ---
    ax1 = fig.add_subplot(gs[0])
    ax1.fill_between(ce, curves["p25"], curves["p75"], color="#DBEAFE", alpha=0.80, label=TXT["leg_iqr"])
    ax1.plot(ce, curves["p75"], color="#0284C7", lw=1.7, ls="--", label=TXT["leg_q75"])
    ax1.plot(ce, curves["p_mean"], color="#D97706", lw=1.6, ls="-.", label=TXT["leg_mean"])
    ax1.plot(ce, curves["p50"], color="#1D4ED8", lw=2.3, label=TXT["leg_q50"])
    ax1.plot(ce, curves["p25"], color="#1E3A8A", lw=1.7, ls=":", label=TXT["leg_q25"])

    # Spreadsheet quartile whisker stems
    for x_i, l_i, m_i, h_i in zip(ce_obs, q25_obs, q50_obs, q75_obs):
        ax1.plot([x_i, x_i], [l_i, h_i], color="#0F172A", lw=1.4, zorder=5)
    ax1.scatter(ce_obs, q75_obs, marker="^", s=34, color="#0284C7", edgecolor="#0F172A", lw=0.6, zorder=6)
    ax1.scatter(ce_obs, q50_obs, marker="o", s=38, color="#0F172A", zorder=6, label=TXT["leg_comps"])
    ax1.scatter(ce_obs, q25_obs, marker="v", s=34, color="#1E3A8A", edgecolor="#0F172A", lw=0.6, zorder=6)
    ax1.axhline(COST_BUILD_M2T, color="#DC2626", ls="--", lw=1.2, label=TXT["leg_cost"])

    ax1.set_xlim(0.45, 0.92)
    ax1.set_ylim(1250, 4450)
    ax1.set_xlabel(TXT["xlabel1"], fontsize=9, fontweight="bold", color="#0F172A")
    ax1.set_ylabel(TXT["ylabel1"], fontsize=9, fontweight="bold", color="#0F172A")
    ax1.set_title(TXT["title1"], fontsize=10.0, fontweight="bold", color="#0F172A", pad=24)
    ax1.grid(True, ls=":", color="#CBD5E1", alpha=0.85)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # Secondary top axis for corresponding Building Coverage Ratio BCR (%)
    ax1_top = ax1.twiny()
    ax1_top.set_xlim(ax1.get_xlim())
    oc_ticks = np.array([0.35, 0.45, 0.60, 0.75, 0.90])
    ax1_top.set_xticks(oc_to_ce(oc_ticks))
    ax1_top.set_xticklabels([f"{int(v*100)}%" for v in oc_ticks], fontsize=8, color="#475569")
    ax1_top.set_xlabel(TXT["xlabel1_top"], fontsize=8.2, color="#475569", labelpad=5)
    ax1_top.spines["right"].set_visible(False)

    ax1.legend(loc="upper right", fontsize=7.3, frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1")

    # --- Panel B: Quantile-Equivariant Net Profit Frontier ---
    ax2 = fig.add_subplot(gs[1])
    ax2.fill_between(ce, curves["pi_25"], curves["pi_75"], color="#DCFCE7", alpha=0.80, label=TXT["leg_pi_iqr"])
    ax2.plot(ce, curves["pi_75"], color="#0D9488", lw=1.7, ls="--", label=TXT["leg_pi_75"])
    ax2.plot(ce, curves["pi_mean"], color="#D97706", lw=2.3, label=TXT["leg_pi_mean"])
    ax2.plot(ce, curves["pi_50"], color="#15803D", lw=2.1, ls="-.", label=TXT["leg_pi_50"])
    ax2.plot(ce, curves["pi_25"], color="#166534", lw=1.6, ls=":", label=TXT["leg_pi_25"])
    ax2.plot(ce, curves["pi_cvar25"], color="#7C3AED", lw=1.9, ls="--", label=TXT["leg_pi_cvar"])

    # Mark exact continuous optima for each criterion
    specs = [
        ("Q75", curves["pi_75"], "#0D9488", (0.50, 74.5)),
        ("E[Pi]", curves["pi_mean"], "#D97706", (0.48, 63.0)),
        ("Q50", curves["pi_50"], "#15803D", (0.68, 59.5)),
        ("CVaR25", curves["pi_cvar25"], "#7C3AED", (0.69, 43.0)),
    ]
    texts = []
    for lbl, arr, col, txt_pos in specs:
        k = int(np.argmax(arr))
        x_k = float(ce[k])
        y_k = float(arr[k])
        ax2.plot(x_k, y_k, "o", color=col, ms=7.5, markeredgecolor="#0F172A", lw=0.8, zorder=7)
        t = ax2.text(
            txt_pos[0],
            txt_pos[1],
            f"{lbl}: FAR={x_k:.3f} | {y_k:.1f}M",
            fontsize=7.6,
            fontweight="bold",
            color=col,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=col, alpha=0.95),
            zorder=8,
        )
        texts.append(t)

    # Also mark statutory max yield boundary Gross FAR = 0.895
    y_max_e = float(curves["pi_50"][-1])
    x_max_e = float(ce[-1])
    ax2.plot(x_max_e, y_max_e, "s", color="#DC2626", ms=7.5, markeredgecolor="white", zorder=7)
    t_bnd = ax2.text(
        0.74,
        33.5,
        f"{TXT['max_m2t']}: FAR={x_max_e:.3f} | {y_max_e:.1f}M",
        fontsize=7.5,
        fontweight="bold",
        color="#B91C1C",
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#DC2626", alpha=0.95),
        zorder=8,
    )
    texts.append(t_bnd)

    # Draw clean leader arrows from labels to exact optima
    targets_xy = []
    for _, arr, _, _ in specs:
        k = int(np.argmax(arr))
        targets_xy.append((float(ce[k]), float(arr[k])))
    targets_xy.append((x_max_e, y_max_e))

    adjust_text(
        texts,
        x=[pt[0] for pt in targets_xy],
        y=[pt[1] for pt in targets_xy],
        ax=ax2,
        expand=(1.15, 1.25),
        force_text=(0.35, 0.55),
        force_points=(0.45, 0.65),
    )
    for t, (tx, ty), col in zip(texts, targets_xy, [s[2] for s in specs] + ["#DC2626"]):
        px, py = t.get_position()
        ax2.annotate(
            "",
            xy=(tx, ty),
            xytext=(px, py),
            arrowprops=dict(arrowstyle="->", color=col, lw=1.0, shrinkA=6, shrinkB=4),
            zorder=6,
        )

    ax2.set_xlim(0.45, 0.92)
    ax2.set_ylim(18, 82)
    ax2.set_xlabel(TXT["xlabel2"], fontsize=9, fontweight="bold", color="#0F172A")
    ax2.set_ylabel(TXT["ylabel2"], fontsize=9, fontweight="bold", color="#0F172A")
    ax2.set_title(TXT["title2"], fontsize=10.0, fontweight="bold", color="#0F172A", pad=8)
    ax2.grid(True, ls=":", color="#CBD5E1", alpha=0.85)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(loc="lower left", fontsize=7.2, frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1")

    fig.savefig(SVG_PATH, format="svg", bbox_inches="tight", facecolor="white")
    make_svg_responsive(SVG_PATH)
    verify_in_memory_ocr(fig, TXT["ocr"], "fig5_quantile_profit")
    plt.close(fig)


# %% Main Entry Point
if __name__ == "__main__":
    if not os.path.exists(XLSX_PATH):
        build_simulated_spreadsheet(XLSX_PATH)
        print(f"Created simulated quartile spreadsheet: {XLSX_PATH}")

    df_summary = pd.read_excel(XLSX_PATH, sheet_name="Quartile_Summary")
    df_raw = pd.read_excel(XLSX_PATH, sheet_name="Simulated_Raw_Comps")

    fit = fit_joint_nonlinear_quantiles(df_summary)
    raw_check = fit_raw_pinball_check(df_raw, fit)

    print("=== 1. Joint Non-Crossing Logistic Quantile Fit (vs Excel Quartiles) ===")
    for lbl, p_key, col, tau in [
        ("Q25", "params_25", "Q25_EUR_m2t", 0.25),
        ("Q50", "params_50", "Q50_EUR_m2t", 0.50),
        ("Q75", "params_75", "Q75_EUR_m2t", 0.75),
    ]:
        pred = logistic_decay(fit["ce_obs"], *fit[p_key])
        mae_grp = float(np.mean(np.abs(pred - df_summary[col].to_numpy())))
        pred_raw = logistic_decay(fit["ce_obs"], *raw_check[tau])
        diff_raw = float(np.mean(np.abs(pred - pred_raw)))
        L, U, k, c0 = fit[p_key]
        print(f"  {lbl}: L={L:.0f}, U={U:.0f}, k={k:.2f}, c0={c0:.3f} | MAE vs Sheet={mae_grp:.1f} EUR | Raw-Pinball Delta={diff_raw:.1f} EUR")

    ce_grid = np.linspace(float(fit["ce_obs"].min()), float(fit["ce_obs"].max()), 501)
    curves = eval_profit_curves(ce_grid, fit)

    print("\n=== 2. Optimal Constructability & Profit Shift Across Quantile Criteria ===")
    for name, arr in [
        ("CVaR25 (Downside Risk)", curves["pi_cvar25"]),
        ("Q25    (Bear Market)", curves["pi_25"]),
        ("Q50    (Median Market)", curves["pi_50"]),
        ("E[Pi]  (Skew-Adjusted)", curves["pi_mean"]),
        ("Q75    (Luxury Tail)", curves["pi_75"]),
    ]:
        k = int(np.argmax(arr))
        ce_k = float(curves["ce"][k])
        oc_k = float(curves["oc"][k])
        print(f"  {name}: Ce*={ce_k:.4f} (C_ocup={oc_k*100:.1f}%), Peak={arr[k]:.2f}M EUR")

    print("\n=== 3. Differential Evolution Check (w/ Discrete 700 m2s Plot Remainder) ===")
    for crit in ["pi_cvar25", "pi_25", "pi_50", "pi_mean", "pi_75"]:
        de_res = optimize_discrete_de(fit, target=crit)
        print(f"  DE[{crit:9s}]: Ce*={de_res['Ce']:.4f} (Ocup={de_res['C_ocup']*100:.1f}%), "
              f"Plots={de_res['N_parcelas']}, NetMargin={de_res['Profit_MEUR']:.2f}M EUR")

    build_fig5(df_summary, fit, curves)
    print(f"\nGenerated SVG: {SVG_PATH}")
