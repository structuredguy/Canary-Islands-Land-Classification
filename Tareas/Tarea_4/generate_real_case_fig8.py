# -*- coding: utf-8 -*-
"""
Generates fig8_real_sc_tenerife_case.svg tying Tarea 4 to real Santa Cruz PGO-13 data:
  - Panel 1: Grafcan OrtoExpress aerial tile over UA-1 (SSU 5.13 Residencial El Tablero, 6.83 ha)
             with PGO-13 EDIF/ZUSO overlays (C-2 2F, C-3/C-4/C-5, P private yards, PZ/AJ public).
  - Panel 2: Sector land-budget comparison (Real UA-1 6.83 ha & SSU 5.20 6.03 ha vs. Tarea 4 Model 6.00 ha).
Verified in-memory via RapidOCR (no PNG saved to disk).
"""

import io
import json
import os
import re
import urllib.request
import numpy as np
import geopandas as gpd
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# %% 0. Paths, Bilingual JSON Preamble & Local SIPU Source
LANG = os.environ.get("PLOT_LANG", "EN")  # Toggle "EN" / "ES"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ.get("PLOT_OUT_DIR", SCRIPT_DIR)
SVG_PATH = os.path.join(OUT_DIR, "fig8_real_sc_tenerife_case.svg")
SIPU_DIR = r"C:\dev\QGIS-testing\data\Santa Cruz de Tenerife\140613-pgo-sct-sipu\02SIST"

LABELS_EN_JSON = r"""
{
  "title1": "1. Real Santa Cruz Case: UA-1 (SSU 5.13 El Tablero, 6.83 ha)\nGrafcan OrtoExpress + PGO-13 Mixed 2F/3-5F VPO Zoning",
  "leg_perim": "UA-1 Perimeter (6.83 ha)",
  "leg_c2": "C-2: 2-Floor Residential (4.6%)",
  "leg_c35": "C-3 to C-5: 3-5F Blocks (19.5%)",
  "leg_p": "P: Private Communal Yards (8.6%)",
  "leg_pub": "PZ/AJ/A-D: Public Cessions (38.7%)",
  "title2": "2. Land Budget Gap: SG Buffers, Grid Boulevards & Extra EL/D/I vs. Model",
  "xlabel2": "Share of Gross Sector Area (%)",
  "ylabels2": [
    "UA-1 El Tablero\n(6.83 ha, Built)",
    "SSU 5.20 Llano Moro\n(6.03 ha, Raw)",
    "Tarea 4 Mixed VPO\n(6.00 ha, Model)"
  ],
  "bar_net": "Net Residential Plots (%)",
  "bar_pub": "Public EL/D/I Cessions (%)",
  "bar_roads": "Roads & Pedestrian (%)",
  "bar_other": "Unzoned / Local Streets (%)",
  "ocr": ["El Tablero", "6.83 ha", "32.5%", "28.7%", "Llano Moro"]
}
"""

LABELS_ES_JSON = r"""
{
  "title1": "1. Caso Real Santa Cruz: UA-1 (SSU 5.13 El Tablero, 6,83 ha)\nOrtoExpress Grafcan + Zonificación Mixta 2P/3-5P VPO (PGO-13)",
  "leg_perim": "Perímetro UA-1 (6,83 ha)",
  "leg_c2": "C-2: Residencial 2 Plantas (4,6%)",
  "leg_c35": "C-3 a C-5: Bloques 3-5P (19,5%)",
  "leg_p": "P: Patios Mancomunados (8,6%)",
  "leg_pub": "PZ/AJ/A-D: Cesiones Públicas (38,7%)",
  "title2": "2. Brecha de Suelo: SG, Viario Real y Exceso EL/D/I frente al Modelo",
  "xlabel2": "Porcentaje de la Superficie Bruta (%)",
  "ylabels2": [
    "UA-1 El Tablero\n(6,83 ha, Ejec.)",
    "SSU 5.20 Llano Moro\n(6,03 ha, Bruto)",
    "Tarea 4 VPO Mixta\n(6,00 ha, Modelo)"
  ],
  "bar_net": "Parcelas Netas Residenciales (%)",
  "bar_pub": "Cesiones Públicas EL/D/I (%)",
  "bar_roads": "Viario y Peatonal (%)",
  "bar_other": "Sin Zonif. / Viario Local (%)",
  "ocr": ["El Tablero", "6,83 ha", "32.5%", "28.7%", "Llano Moro"]
}
"""

TXT = json.loads(LABELS_EN_JSON)
if LANG.upper() == "ES":
    TXT.update(json.loads(LABELS_ES_JSON))


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
    """Render in-memory PNG buffer for RapidOCR check (never written to disk)."""
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
                if ratio > 0.15:
                    overlaps.append((at, bt, round(ratio, 2)))

    print(f"[OCR CHECK] {label}: {len(detected_texts)} regions, missing={missing}, overlaps={overlaps}")


# %% 1. Load Santa Cruz PGO-13 Layers & Fetch Grafcan OrtoExpress Tile
if __name__ == "__main__":
    ges = gpd.read_file(os.path.join(SIPU_DIR, "GES.shp"))
    edif = gpd.read_file(os.path.join(SIPU_DIR, "EDIF.shp"))
    ed_z = edif[~edif["ETIPLAN"].astype(str).str.startswith(("AE.", "AOU", "AMB"))].copy()

    ua1 = ges[(ges["TXTPLAN"].str.contains("5.13", na=False)) & (ges["ETIPLAN"] == "UA-1")].iloc[0]
    geom = ua1.geometry
    minx, miny, maxx, maxy = geom.bounds
    cx, cy = (minx + maxx) / 2.0, (miny + maxy) / 2.0
    half = max(maxx - minx, maxy - miny) * 0.56
    bx1, by1, bx2, by2 = cx - half, cy - half, cx + half, cy + half

    wms_url = (
        f"https://idecan1.grafcan.es/ServicioWMS/OrtoExpress?"
        f"SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=ortoexpress&STYLES="
        f"&SRS=EPSG:32628&BBOX={bx1},{by1},{bx2},{by2}&WIDTH=1000&HEIGHT=1000&FORMAT=image/jpeg"
    )
    orto_img = Image.open(io.BytesIO(urllib.request.urlopen(wms_url, timeout=20).read()))

    ied = ed_z[ed_z.intersects(geom)].copy()
    ied["geometry"] = ied.geometry.intersection(geom)
    ied = ied[~ied.is_empty].copy()

    def map_group(code):
        if code == "C-2":
            return "C-2 (2F)"
        if code in ("C-3", "C-4", "Ce-4.1", "C-5"):
            return "C-3..C-5 (3-5F)"
        if code == "P":
            return "Private Yard (P)"
        if code in ("PZ", "AJ", "A-D"):
            return "Public EL/D/I"
        return "Other"

    ied["grp"] = ied["ETIPLAN"].astype(str).apply(map_group)

    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
    plt.rcParams["svg.fonttype"] = "none"

    fig = plt.figure(figsize=(6.4, 9.4), facecolor="white")
    gs = fig.add_gridspec(2, 1, height_ratios=[1.35, 0.85], hspace=0.28)

    # --- Panel A: Aerial Orthophoto + PGO-13 Zoning Overlay ---
    ax1 = fig.add_subplot(gs[0])
    ax1.imshow(orto_img, extent=[bx1, bx2, by1, by2], origin="upper")

    palette = {
        "C-2 (2F)": ("#F59E0B", 0.55),
        "C-3..C-5 (3-5F)": ("#EF4444", 0.45),
        "Private Yard (P)": ("#A855F7", 0.42),
        "Public EL/D/I": ("#22C55E", 0.35),
    }
    for grp, (col, alp) in palette.items():
        sub = ied[ied["grp"] == grp]
        if len(sub):
            sub.plot(ax=ax1, facecolor=col, edgecolor=col, alpha=alp, lw=0.9, zorder=3)

    gpd.GeoSeries([geom]).boundary.plot(ax=ax1, color="#FACC15", lw=2.5, zorder=5)

    legend_handles = [
        Patch(facecolor="none", edgecolor="#FACC15", lw=2.2, label=TXT["leg_perim"]),
        Patch(facecolor="#F59E0B", alpha=0.65, label=TXT["leg_c2"]),
        Patch(facecolor="#EF4444", alpha=0.55, label=TXT["leg_c35"]),
        Patch(facecolor="#A855F7", alpha=0.55, label=TXT["leg_p"]),
        Patch(facecolor="#22C55E", alpha=0.50, label=TXT["leg_pub"]),
    ]
    ax1.legend(handles=legend_handles, loc="lower left", fontsize=7.2, frameon=True,
               facecolor="#0F172A", edgecolor="#94A3B8", labelcolor="white")
    ax1.set_xlim(bx1, bx2)
    ax1.set_ylim(by1, by2)
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.set_title(TXT["title1"], fontsize=9.6, fontweight="bold", color="#0F172A", pad=8)

    # --- Panel B: Real Tenerife Sectors vs. Tarea 4 Theoretical Sector ---
    ax2 = fig.add_subplot(gs[1])
    labels = TXT["ylabels2"]
    net_res = np.array([32.5, 25.9, 57.8])      # Net residential land %
    pub_ces = np.array([38.7, 37.9, 32.2])      # EL/D/I public parks, plazas, schools %
    roads = np.array([28.7, 22.3, 10.0])        # Roads & pedestrian %
    other_sg = np.array([0.1, 13.9, 0.0])       # Remainder / rounding

    y = np.arange(len(labels))
    h = 0.52
    ax2.barh(y, net_res, height=h, color="#2563EB", label=TXT["bar_net"])
    ax2.barh(y, pub_ces, left=net_res, height=h, color="#16A34A", label=TXT["bar_pub"])
    ax2.barh(y, roads, left=net_res + pub_ces, height=h, color="#64748B", label=TXT["bar_roads"])
    ax2.barh(y, other_sg, left=net_res + pub_ces + roads, height=h, color="#CBD5E1", label=TXT["bar_other"])

    for idx in range(len(labels)):
        ax2.text(net_res[idx] / 2.0, y[idx], f"{net_res[idx]:.1f}%", va="center", ha="center",
                 color="white", fontsize=8.5, fontweight="bold")
        ax2.text(net_res[idx] + pub_ces[idx] / 2.0, y[idx], f"{pub_ces[idx]:.1f}%", va="center", ha="center",
                 color="white", fontsize=8.5, fontweight="bold")
        ax2.text(net_res[idx] + pub_ces[idx] + roads[idx] / 2.0, y[idx], f"{roads[idx]:.1f}%", va="center", ha="center",
                 color="white", fontsize=8.5, fontweight="bold")
        if other_sg[idx] > 5.0:
            ax2.text(net_res[idx] + pub_ces[idx] + roads[idx] + other_sg[idx] / 2.0, y[idx], f"{other_sg[idx]:.1f}%",
                     va="center", ha="center", color="#0F172A", fontsize=8.0, fontweight="bold")

    ax2.set_yticks(y)
    ax2.set_yticklabels(labels, fontsize=8.3, fontweight="bold", color="#0F172A")
    ax2.invert_yaxis()
    ax2.set_xlim(0, 102)
    ax2.set_xlabel(TXT["xlabel2"], fontsize=8.8, fontweight="bold", color="#0F172A")
    ax2.set_title(TXT["title2"], fontsize=9.1, fontweight="bold", color="#0F172A", pad=8)
    ax2.grid(True, axis="x", ls=":", color="#CBD5E1", alpha=0.8)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2, fontsize=7.4,
               frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1")

    fig.savefig(SVG_PATH, format="svg", bbox_inches="tight", facecolor="white")
    make_svg_responsive(SVG_PATH)
    verify_in_memory_ocr(fig, TXT["ocr"], "fig8_real_sc")
    plt.close(fig)
    print(f"Generated SVG: {SVG_PATH}")
