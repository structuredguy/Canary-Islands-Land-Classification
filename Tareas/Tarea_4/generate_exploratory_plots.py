# -*- coding: utf-8 -*-
"""
Exploratory Visuals for Tarea 4: Urban Planning Sector Optimization
Generates three mobile-optimized SVG charts (Samsung Galaxy S22 portrait format)
and runs an in-memory RapidOCR + bounding-box collision check without saving PNGs.
"""

import io
import os
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
from PIL import Image

# %% Global Style Configuration (Mobile-First Typography)
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.edgecolor"] = "#334155"
plt.rcParams["axes.linewidth"] = 0.9
plt.rcParams["svg.fonttype"] = "none"  # Keep crisp selectable SVG text

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Colorblind-safe, high-contrast palette
C_ROAD = "#94A3B8"
C_CESS = "#10B981"
C_NET = "#2563EB"
C_DEFICIT = "#EF4444"
C_FEASIBLE = "#DCFCE7"
C_UNFEAS = "#FEE2E2"
C_WALL = "#E2E8F0"
C_GOLD = "#D97706"
C_DARK = "#0F172A"
C_MUTED = "#475569"


def make_svg_responsive(svg_path):
    """Ensure root <svg> scales cleanly on mobile screens via viewBox."""
    with open(svg_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Replace fixed width/height pt attributes with width="100%" while preserving viewBox
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
    low_conf = [(t, c) for t, c in detected_texts if c < 0.70]

    # Check pairwise bounding-box IoU for genuine overlaps
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
                overlap_ratio = inter / min(area_a, area_b)
                if overlap_ratio > 0.15:
                    overlaps.append((at, bt, round(overlap_ratio, 2)))

    print(f"[OCR CHECK] {label}: {len(detected_texts)} text regions, "
          f"missing={missing}, low_conf={len(low_conf)}, overlaps={overlaps}")


# %% FIGURE 1: Problem Structure (Land Split + 4 Scenario Massing Profiles)
def build_fig1():
    fig = plt.figure(figsize=(6.4, 9.0), facecolor="white")
    gs = fig.add_gridspec(2, 1, height_ratios=[0.95, 1.45], hspace=0.34)

    # --- Panel A: Land Mass-Balance Comparison (Group A vs Group B) ---
    ax1 = fig.add_subplot(gs[0])
    ax1.set_xlim(0, 62000)
    ax1.set_ylim(-0.55, 1.85)
    ax1.set_yticks([1.05, 0.15])
    ax1.set_yticklabels(["Group A\nCe = 1.0\n(60,000 m2c)", "Group B\nCe = 0.6\n(36,000 m2c)"],
                        fontsize=9.5, fontweight="bold", color=C_DARK)
    ax1.set_xlabel("Sector Land Area (m2s)  |  Total S_bruta = 60,000 m2s (6 ha)",
                   fontsize=9, fontweight="bold", color=C_DARK)
    ax1.set_title("1. How Buildability (Ce) Shrinks Net Land\n"
                  "Cessions = 0.45 x E_teorica  |  Roads = 10% Fixed",
                  fontsize=11, fontweight="bold", color=C_DARK, pad=10)
    ax1.grid(axis="x", linestyle=":", color="#CBD5E1", alpha=0.8)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    groups = [
        {"y": 1.05, "road": 6000, "cess": 27000, "net": 27000, "plots": "38 plots\n(rem 400 m2s)"},
        {"y": 0.15, "road": 6000, "cess": 16200, "net": 37800, "plots": "54 plots\n(exact 0 rem)"},
    ]
    bar_h = 0.52
    for g in groups:
        y = g["y"]
        ax1.barh(y, g["road"], height=bar_h, left=0, color=C_ROAD, edgecolor="white", lw=1.2)
        ax1.barh(y, g["cess"], height=bar_h, left=g["road"], color=C_CESS, edgecolor="white", lw=1.2)
        ax1.barh(y, g["net"], height=bar_h, left=g["road"] + g["cess"], color=C_NET, edgecolor="white", lw=1.2)

        ax1.text(g["road"] / 2, y, "6k\n10%", ha="center", va="center",
                 fontsize=8, fontweight="bold", color="white")
        ax1.text(g["road"] + g["cess"] / 2, y, f"Cessions\n{g['cess']:,} m2s",
                 ha="center", va="center", fontsize=8.5, fontweight="bold", color="white")
        ax1.text(g["road"] + g["cess"] + g["net"] / 2, y,
                 f"Net: {g['net']:,} m2s\n{g['plots']}",
                 ha="center", va="center", fontsize=8.5, fontweight="bold", color="white")

    legend_handles = [
        patches.Patch(color=C_ROAD, label="Viario (10%)"),
        patches.Patch(color=C_CESS, label="Public Cessions (45 m2s/100 m2c)"),
        patches.Patch(color=C_NET, label="Net Lucrative Land (>=700 m2s/plot)"),
    ]
    ax1.legend(handles=legend_handles, loc="upper center", bbox_to_anchor=(0.5, 1.02),
               ncol=2, frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1", fontsize=8)

    # --- Panel B: 2x2 Massing Profiles on Representative Plot (S1..S4) ---
    ax2_outer = fig.add_subplot(gs[1])
    ax2_outer.axis("off")
    ax2_outer.set_title("2. Vertical Massing Across the 4 Scenarios\n"
                        "Dashed Red Line = 2-Floor Cap (Np = 2)",
                        fontsize=11, fontweight="bold", color=C_DARK, pad=14)

    sub_gs = gs[1].subgridspec(2, 2, wspace=0.22, hspace=0.35)
    scenarios = [
        {"id": "S1: Ce=1.0, Ocup=90%", "ocup": 0.90, "exact": 2.47, "ceil": 3, "plots": 38, "ok": False, "loss": "-19% lost"},
        {"id": "S2: Ce=1.0, Ocup=50%", "ocup": 0.50, "exact": 4.44, "ceil": 5, "plots": 38, "ok": False, "loss": "-55% lost"},
        {"id": "S3: Ce=0.6, Ocup=90%", "ocup": 0.90, "exact": 1.06, "ceil": 2, "plots": 54, "ok": True,  "loss": "0% lost"},
        {"id": "S4: Ce=0.6, Ocup=50%", "ocup": 0.50, "exact": 1.90, "ceil": 2, "plots": 54, "ok": True,  "loss": "0% lost"},
    ]

    for idx, sc in enumerate(scenarios):
        ax = fig.add_subplot(sub_gs[idx // 2, idx % 2])
        ax.set_xlim(-0.08, 1.08)
        ax.set_ylim(-0.3, 6.45)
        ax.set_xticks([])
        ax.set_yticks([0, 1, 2, 3, 4, 5])
        ax.tick_params(axis="y", labelsize=8, colors=C_MUTED)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)

        # Plot ground base (width = 1.0 represents 100% of plot)
        ax.add_patch(patches.Rectangle((0.0, -0.18), 1.0, 0.18,
                                       facecolor="#CBD5E1", edgecolor=C_DARK, lw=0.8))

        # Centered building footprint width = sc["ocup"]
        w = sc["ocup"]
        x0 = (1.0 - w) / 2.0
        full_floors = int(np.floor(sc["exact"]))
        frac = sc["exact"] - full_floors

        # Draw each floor
        for fl in range(full_floors):
            above_cap = fl >= 2
            fc = "#FCA5A5" if above_cap else "#93C5FD"
            ec = "#B91C1C" if above_cap else "#1D4ED8"
            ax.add_patch(patches.Rectangle((x0, fl), w, 0.92,
                                           facecolor=fc, edgecolor=ec, lw=1.0))
        if frac > 0.01:
            fl = full_floors
            above_cap = fl >= 2
            fc = "#FECACA" if above_cap else "#BFDBFE"
            ec = "#B91C1C" if above_cap else "#1D4ED8"
            # Partial top floor (proportional width representing partial floor)
            pw = w * frac
            px0 = (1.0 - pw) / 2.0
            ax.add_patch(patches.Rectangle((px0, fl), pw, 0.92,
                                           facecolor=fc, edgecolor=ec, lw=1.0, hatch="//" if above_cap else None))

        # 2-floor cap line
        ax.axhline(2.0, color=C_DEFICIT, linestyle="--", linewidth=1.6, zorder=10)

        # Status badge cleanly above maximum 5th floor (y=5.75)
        badge_col = "#15803D" if sc["ok"] else "#B91C1C"
        badge_bg = "#DCFCE7" if sc["ok"] else "#FEE2E2"
        ax.set_title(sc["id"], fontsize=9, fontweight="bold", color=C_DARK, pad=5)
        ax.text(0.5, 5.75,
                f"{sc['exact']:.2f} -> {sc['ceil']} fl | {sc['plots']} plots  ({sc['loss']})",
                ha="center", va="center", fontsize=7.6, fontweight="bold", color=badge_col,
                bbox=dict(boxstyle="round,pad=0.22", fc=badge_bg, ec=badge_col, lw=0.9))

    out_path = os.path.join(OUT_DIR, "fig1_problem_and_scenarios.svg")
    fig.savefig(out_path, format="svg", bbox_inches="tight", facecolor="white")
    make_svg_responsive(out_path)
    verify_in_memory_ocr(fig, ["60,000", "38 plots", "54 plots", "2.47", "4.44", "1.06", "1.90"], "fig1")
    plt.close(fig)


# %% FIGURE 2: Constrained Parameter Space & Solution Pathways (Np <= 2)
def build_fig2():
    fig, ax = plt.subplots(figsize=(6.4, 7.6), facecolor="white")

    ocup = np.linspace(0.30, 1.15, 400)
    # Boundary: N_exact = Ce / ((0.9 - 0.45*Ce)*ocup) = k  => Ce = (0.9*k*ocup)/(1 + 0.45*k*ocup)
    def ce_bound(oc, k):
        return (0.9 * k * oc) / (1.0 + 0.45 * k * oc)

    ce_2 = ce_bound(ocup, 2.0)

    # Shaded regions
    ax.fill_between(ocup * 100, 0.25, np.minimum(ce_2, 1.28),
                    where=(ocup <= 1.0), color=C_FEASIBLE, alpha=0.85, zorder=1)
    ax.fill_between(ocup * 100, np.minimum(ce_2, 1.28), 1.28,
                    where=(ocup <= 1.0), color=C_UNFEAS, alpha=0.55, zorder=1)
    ax.axvspan(100, 116, color=C_WALL, alpha=0.9, zorder=2)

    # Assignment parameter requirement bands
    ax.axvspan(61, 84, color="#F1F5F9", alpha=0.75, zorder=1)
    ax.axvline(61, color="#64748B", ls=":", lw=1.0, zorder=3)
    ax.axvline(84, color="#64748B", ls=":", lw=1.0, zorder=3)
    ax.axvline(100, color=C_DARK, ls="-", lw=1.8, zorder=4)
    ax.axhline(0.90, color="#64748B", ls=":", lw=1.0, zorder=3)
    ax.axhline(1.20, color=C_GOLD, ls="--", lw=1.3, zorder=3)

    # Floor contour lines
    for k, ls, lw, col in [
        (1.0, "-.", 1.1, "#047857"),
        (2.0, "-",  2.4, "#15803D"),
        (3.0, "--", 1.1, "#B91C1C"),
        (4.0, "--", 1.1, "#991B1B"),
        (5.0, "--", 1.0, "#7F1D1D"),
    ]:
        y_k = ce_bound(ocup[ocup <= 1.0], k)
        ax.plot(ocup[ocup <= 1.0] * 100, y_k, linestyle=ls, linewidth=lw, color=col, zorder=5)

    # Contour curve labels placed cleanly at x = 34% or x = 96%
    ax.text(33, ce_bound(0.33, 1.0) - 0.045, "Np=1", fontsize=8, fontweight="bold", color="#047857")
    ax.text(33, ce_bound(0.33, 2.0) + 0.025, "Np=2 Limit", fontsize=8.5, fontweight="bold", color="#15803D")
    ax.text(33, ce_bound(0.33, 3.0) + 0.025, "Np=3", fontsize=8, fontweight="bold", color="#B91C1C")
    ax.text(33, ce_bound(0.33, 4.0) + 0.025, "Np=4", fontsize=8, fontweight="bold", color="#991B1B")
    ax.text(33, ce_bound(0.33, 5.0) + 0.025, "Np=5", fontsize=8, fontweight="bold", color="#7F1D1D")

    # Region captions
    ax.text(72.5, 1.225, "Ley 4/2017 Cap (Ce <= 1.20)", fontsize=8, fontweight="bold",
            color=C_GOLD, ha="center", va="bottom")
    ax.text(108, 0.78, "Physical\nWall\n(>100%)", fontsize=8.5, fontweight="bold",
            color=C_DARK, ha="center", va="center")
    ax.text(72.5, 0.42, "FEASIBLE\n(Np <= 2)", fontsize=10, fontweight="bold",
            color="#166534", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#15803D", alpha=0.9))

    # Plot 4 scenarios + target solutions
    pts = [
        ("S1", 90, 1.00, "#DC2626", "o", (-14, 9)),
        ("S2", 50, 1.00, "#DC2626", "o", (-16, 9)),
        ("S3", 90, 0.60, "#15803D", "o", (-14, -15)),
        ("S4", 50, 0.60, "#15803D", "o", (-14, -15)),
        ("Wall\n(111%)", 111.1, 1.00, "#475569", "X", (-8, -26)),
        ("Fix B1\n(0.895)", 90, 0.895, "#2563EB", "D", (8, -4)),
        ("Fix B2\n(0.621)", 50, 0.621, "#2563EB", "D", (-38, 8)),
        ("Fix C\n(85%,0.85)", 85, 0.85, "#7C3AED", "*", (-56, -20)),
    ]
    for label, px, py, col, mk, offset in pts:
        ms = 11 if mk == "*" else 8
        ax.plot(px, py, marker=mk, markersize=ms, color=col, markeredgecolor="white",
                markeredgewidth=1.0, zorder=10)
        ax.annotate(label, (px, py), xytext=offset, textcoords="offset points",
                    fontsize=8, fontweight="bold", color=col,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85),
                    zorder=11)

    # Solution Arrows from S1 & S2
    arrow_kw = dict(arrowstyle="-|>,head_length=0.5,head_width=0.3", lw=1.6, zorder=8)
    # Path A: S1 -> Wall (impossible)
    ax.annotate("", xy=(109.5, 1.00), xytext=(91.5, 1.00),
                arrowprops={**arrow_kw, "color": "#64748B", "ls": "--"})
    # Path B1: S1 -> Fix B1
    ax.annotate("", xy=(90, 0.908), xytext=(90, 0.985),
                arrowprops={**arrow_kw, "color": "#2563EB"})
    # Path B2: S2 -> Fix B2
    ax.annotate("", xy=(50, 0.635), xytext=(50, 0.985),
                arrowprops={**arrow_kw, "color": "#2563EB"})
    # Path C: S2 -> Fix C (Combined)
    ax.annotate("", xy=(83.6, 0.856), xytext=(51.5, 0.992),
                arrowprops={**arrow_kw, "color": "#7C3AED"})

    ax.set_xlim(30, 116)
    ax.set_ylim(0.30, 1.28)
    ax.set_xlabel("Plot Occupancy Coefficient C_ocup (%)", fontsize=9.5, fontweight="bold", color=C_DARK)
    ax.set_ylabel("Gross Building Coefficient Ce (m2c / m2s)", fontsize=9.5, fontweight="bold", color=C_DARK)
    ax.set_title("Feasible Design Space Under 2-Floor Cap (Np <= 2)\n"
                 "Why Occupancy Alone Fails for Ce = 1.0 & Solution Paths",
                 fontsize=11, fontweight="bold", color=C_DARK, pad=10)
    ax.grid(True, linestyle=":", color="#CBD5E1", alpha=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Legend below plot for clean mobile reading
    leg_items = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#DC2626", markersize=8, label="S1, S2 (Unfeasible Np=2)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#15803D", markersize=8, label="S3, S4 (Feasible Np<=2)"),
        Line2D([0], [0], marker="D", color="w", markerfacecolor="#2563EB", markersize=7, label="Reduce Ce Only (Fix B)"),
        Line2D([0], [0], marker="*", color="w", markerfacecolor="#7C3AED", markersize=10, label="Combined Fix (C_ocup + Ce)"),
    ]
    ax.legend(handles=leg_items, loc="upper center", bbox_to_anchor=(0.5, -0.11),
              ncol=2, frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1", fontsize=8.5)

    out_path = os.path.join(OUT_DIR, "fig2_feasible_space_2floors.svg")
    fig.savefig(out_path, format="svg", bbox_inches="tight", facecolor="white")
    make_svg_responsive(out_path)
    verify_in_memory_ocr(fig, ["Feasible", "Np=2", "S1", "S2", "S3", "S4", "111%"], "fig2")
    plt.close(fig)


# %% FIGURE 3: Discrete Plot Staircase & Materializable vs Unbuilt Deficit
def build_fig3():
    fig = plt.figure(figsize=(6.4, 8.6), facecolor="white")
    gs = fig.add_gridspec(2, 1, height_ratios=[1.05, 1.0], hspace=0.40)

    # --- Panel A: Discrete Plot Count Staircase vs Ce ---
    ax1 = fig.add_subplot(gs[0])
    ce_grid = np.linspace(0.40, 1.20, 801)
    s_neta = 54000.0 - 27000.0 * ce_grid
    n_exact = s_neta / 700.0
    n_floor = np.floor(n_exact)

    ax1.plot(ce_grid, n_exact, color="#94A3B8", ls="--", lw=1.4, label="Continuous S_neta / 700")
    ax1.step(ce_grid, n_floor, where="post", color=C_NET, lw=2.2, label="Discrete Plots floor(S_neta / 700)")

    # Key operating points
    pts_a = [
        (0.60, 54, "Ce=0.6 -> 54.00\n(Exact 0 rem)", (10, 10), "#15803D"),
        (0.895, 42, "Fix B1 (0.895)\n-> 42 plots", (-62, -26), "#7C3AED"),
        (1.00, 38, "Ce=1.0 -> 38.57\n(38 + 400 m2s rem)", (-78, -28), "#DC2626"),
    ]
    for cx, cy, txt, off, col in pts_a:
        ax1.plot(cx, cy, "o", color=col, markersize=7, markeredgecolor="white", zorder=6)
        ax1.annotate(txt, (cx, cy), xytext=off, textcoords="offset points",
                     fontsize=8, fontweight="bold", color=col,
                     arrowprops=dict(arrowstyle="->", color=col, lw=0.9),
                     bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=col, alpha=0.92),
                     zorder=7)

    ax1.set_xlim(0.40, 1.20)
    ax1.set_ylim(26, 65)
    ax1.set_xlabel("Gross Building Coefficient Ce (m2c / m2s)", fontsize=9, fontweight="bold", color=C_DARK)
    ax1.set_ylabel("Resulting Plots (N_parcelas)", fontsize=9, fontweight="bold", color=C_DARK)
    ax1.set_title("1. Discrete Plot Staircase: S_min = 700 m2s Quantization\n"
                  "Higher Ce Reduces Net Land and Plot Count",
                  fontsize=10.5, fontweight="bold", color=C_DARK, pad=8)
    ax1.grid(True, ls=":", color="#CBD5E1", alpha=0.8)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.legend(loc="upper right", fontsize=8, frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1")

    # --- Panel B: Buildability Materialized vs Deficit under Np = 2 ---
    ax2 = fig.add_subplot(gs[1])
    labels = ["S1\n(1.0, 90%)", "S2\n(1.0, 50%)", "S3\n(0.6, 90%)", "S4\n(0.6, 50%)", "Fix C\n(0.85, 85%)"]
    built = np.array([48.6, 27.0, 36.0, 36.0, 51.0])     # in 1,000 m2c
    deficit = np.array([11.4, 33.0, 0.0, 0.0, 0.0])      # unbuilt / TAU / subsoil gap
    x = np.arange(len(labels))
    w = 0.56

    ax2.bar(x, built, width=w, color=C_NET, edgecolor="white", label="Built in 2 Floors (E_mat)")
    ax2.bar(x, deficit, width=w, bottom=built, color="#FCA5A5", edgecolor="#DC2626",
            hatch="///", lw=1.1, label="Unbuilt Deficit (TAU / Subsoil)")

    for i in range(len(labels)):
        ax2.text(x[i], built[i] / 2.0, f"{built[i]:.1f}k", ha="center", va="center",
                 fontsize=8.5, fontweight="bold", color="white")
        if deficit[i] > 0:
            pct = int(round(100 * deficit[i] / (built[i] + deficit[i])))
            ax2.text(x[i], built[i] + deficit[i] + 2.0, f"-{deficit[i]:.1f}k\n(-{pct}%)",
                     ha="center", va="bottom", fontsize=8, fontweight="bold", color="#B91C1C")
        else:
            ax2.text(x[i], built[i] + 2.0, "100%\nOK",
                     ha="center", va="bottom", fontsize=8, fontweight="bold", color="#15803D")

    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=8.5, fontweight="bold", color=C_DARK)
    ax2.set_ylim(0, 72)
    ax2.set_ylabel("Floor Area (x1,000 m2c)", fontsize=9, fontweight="bold", color=C_DARK)
    ax2.set_title("2. Theoretical vs Materialized Floor Area (Np = 2)\n"
                  "Combined Fix (0.85, 85%) Builds 51.0k m2c in 2 Floors",
                  fontsize=10.5, fontweight="bold", color=C_DARK, pad=8)
    ax2.grid(axis="y", ls=":", color="#CBD5E1", alpha=0.8)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(loc="upper right", fontsize=8, frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1")

    out_path = os.path.join(OUT_DIR, "fig3_discrete_and_deficits.svg")
    fig.savefig(out_path, format="svg", bbox_inches="tight", facecolor="white")
    make_svg_responsive(out_path)
    verify_in_memory_ocr(fig, ["54", "38", "48.6k", "27.0k", "51.0k", "-19%", "-55%"], "fig3")
    plt.close(fig)


if __name__ == "__main__":
    build_fig1()
    build_fig2()
    build_fig3()
    print("Generated all 3 SVG figures in:", OUT_DIR)
