# -*- coding: utf-8 -*-
"""
Sector Urbanistico: Comparativa de Geometrias y Analisis de Superficies
Ajustado para DNI terminado en 4 -> Coeficiente de Edificabilidad ajustado e = 1,0 m2c/m2s.
Calculo y visualizacion de superficies fisicas (m2s) vs juridicas/edificables (m2c)
conforme a la Ley 4/2017 del Suelo de Canarias y Decreto 183/2018.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec

# Configuracion general de matplotlib
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#444444'
plt.rcParams['axes.linewidth'] = 0.8

# Parametros normativos ajustados al DNI (terminacion en 4: par -> sumar mitad = 2 al decimal -> e = 1,0)
S_SECTOR = 60000.0       # Superficie total del sector: 6 ha = 60.000 m2s
E_BRUTA = 1.0            # Edificabilidad ajustada por DNI (terminacion 4): 0,8 + 0,2 = 1,0 m2c/m2s
E_TOTAL = S_SECTOR * E_BRUTA  # 60.000 m2c

S_VIARIO = 7000.0        # Viario a ceder: 7.000 m2s
# Reserva dotacional minima segun Ley 4/2017 art. 138.1.A.c: 40 m2s por cada 100 m2c (0,40 m2s/m2c)
S_DOTACIONAL = E_TOTAL * 0.40  # 24.000 m2s

S_LUCRATIVA = S_SECTOR - S_VIARIO - S_DOTACIONAL  # 29.000 m2s
E_NETA = E_TOTAL / S_LUCRATIVA  # ~2.06897 m2c/m2s

PARCELA_MIN = 500.0      # Parcela minima: 500 m2s
OCUP_MAX = 0.60          # Ocupacion maxima de parcela: 60%

# Reparto legal de aprovechamiento: 90% Promotores, 10% Municipio
CUOTA_PROMOTOR = 0.90
CUOTA_MUNICIPIO = 0.10

S_PROMOTOR = S_LUCRATIVA * CUOTA_PROMOTOR    # 26.100 m2s
E_PROMOTOR = E_TOTAL * CUOTA_PROMOTOR        # 54.000 m2c

S_MUNICIPIO = S_LUCRATIVA * CUOTA_MUNICIPIO  # 2.900 m2s
E_MUNICIPIO = E_TOTAL * CUOTA_MUNICIPIO      # 6.000 m2c

# Analisis de parcelacion minima y restos
N_PROM_COMPLETAS = int(S_PROMOTOR // PARCELA_MIN)  # 52 parcelas
RESTO_PROM = S_PROMOTOR % PARCELA_MIN             # 100 m2s

N_MUN_COMPLETAS = int(S_MUNICIPIO // PARCELA_MIN)  # 5 parcelas
RESTO_MUN = S_MUNICIPIO % PARCELA_MIN             # 400 m2s

output_dir = os.path.dirname(os.path.abspath(__file__))

# %% FIGURA 1: COMPARATIVA DE GEOMETRIAS DEL SECTOR (CUADRADO VS FRANJA ALARGADA)
fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), gridspec_kw={'height_ratios': [1.3, 0.9]})

# Colores para usos del suelo
C_PARK = '#8FBC8F'        # Espacios libres / dotacional (Dark Sea Green)
C_ROAD = '#D3D3D3'        # Viario publico (Light Gray)
C_ROAD_LINE = '#888888'   # Bordes viario
C_PROM_BG = '#E6F0FA'     # Parcela promotor (Azul suave)
C_PROM_BLD = '#4682B4'    # Huella construida promotor 60% (Steel Blue)
C_MUN_BG = '#FFF2CC'      # Parcela ayuntamiento (Amarillo suave)
C_MUN_BLD = '#D4AC0D'     # Huella construida ayuntamiento 60% (Dorado)
C_REMAINDER = '#FADBD8'   # Resto / Compensacion (Rojo suave)

# --- SUBPLOT 1: SECTOR APROXIMADAMENTE CUADRADO (250m x 240m = 60.000 m2s) ---
W_sq, H_sq = 250.0, 240.0
ax1.set_xlim(-10, W_sq + 15)
ax1.set_ylim(-10, H_sq + 15)
ax1.set_aspect('equal')
ax1.set_title("Opcion A: Sector Cuadrado (250 m x 240 m = 60.000 m2s) [Ajuste DNI terminacion 4 -> e = 1,0 m2c/m2s]\n"
              "Distribucion de Suelo Fisico: Parque (24.000 m2s), Viario (7.000 m2s) y Lucrativo (29.000 m2s)",
              fontsize=11, fontweight='bold', pad=12)

# Perimetro sector
rect_sector_sq = patches.Rectangle((0, 0), W_sq, H_sq, linewidth=1.5, edgecolor='#222222', facecolor='none', linestyle='--')
ax1.add_patch(rect_sector_sq)

# 1. Espacio Libre / Dotacional (100m x 240m = 24.000 m2s)
W_park_sq = 100.0
rect_park_sq = patches.Rectangle((0, 0), W_park_sq, H_sq, facecolor=C_PARK, edgecolor='#2E7D32', linewidth=1.2, alpha=0.85)
ax1.add_patch(rect_park_sq)
ax1.text(W_park_sq / 2, H_sq / 2,
         "ESPACIOS LIBRES Y DOTACIONES (EL/D/I)\nSuperficie Suelo: 24.000 m2s\nEdificabilidad Lucrativa: 0 m2c\n(Reserva legal min. 0,40 m2s/m2c x 60.000 m2c)",
         ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1B5E20',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.85, edgecolor='#2E7D32'))

# 2. Viario (Avenida central N-S de 14m x 240m = 3.360 m2s + 2 calles E-W de 13.38m x 136m = 3.640 m2s -> Total 7.000 m2s)
W_ave = 14.0
rect_ave = patches.Rectangle((W_park_sq, 0), W_ave, H_sq, facecolor=C_ROAD, edgecolor=C_ROAD_LINE, linewidth=1.0)
ax1.add_patch(rect_ave)

X_res_start = W_park_sq + W_ave  # 114.0 m
W_res = W_sq - X_res_start       # 136.0 m

H_street = 3640.0 / (2 * W_res)  # 13.3824 m
H_b1 = 68.0
Y_s1 = H_b1
H_b2 = 68.0
Y_s2 = Y_s1 + H_street + H_b2
H_b3 = H_sq - (Y_s2 + H_street)   # 77.235 m

rect_s1 = patches.Rectangle((X_res_start, Y_s1), W_res, H_street, facecolor=C_ROAD, edgecolor=C_ROAD_LINE, linewidth=0.8)
rect_s2 = patches.Rectangle((X_res_start, Y_s2), W_res, H_street, facecolor=C_ROAD, edgecolor=C_ROAD_LINE, linewidth=0.8)
ax1.add_patch(rect_s1)
ax1.add_patch(rect_s2)

ax1.text(W_park_sq + W_ave / 2, H_sq * 0.15, "VIARIO PUBLICO: 7.000 m2s",
         ha='center', va='center', rotation=90, fontsize=8, fontweight='bold', color='#424242',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='#888888'))

# 3. Parcelas en bloques residenciales (Total lucrativo = 29.000 m2s)
# 52 parcelas promotor + 5 parcelas municipio = 57 parcelas completas + resto 500 m2s (100 prom / 400 ayto)
blocks_sq = [
    {'y0': 0.0, 'h': H_b1, 'rows': 2, 'cols': 9, 'role': 'promotor'},               # 18 parcelas
    {'y0': Y_s1 + H_street, 'h': H_b2, 'rows': 2, 'cols': 9, 'role': 'promotor'},   # 18 parcelas
    {'y0': Y_s2 + H_street, 'h': H_b3, 'rows': 2, 'cols': 11, 'role': 'mixed'}      # 22 parcelas (16 promotor + 5 municipio + 1 resto)
]

for b_idx, blk in enumerate(blocks_sq):
    y_base = blk['y0']
    h_tot = blk['h']
    rows = blk['rows']
    cols = blk['cols']
    pw = W_res / cols
    ph = h_tot / rows
    
    for r in range(rows):
        for c in range(cols):
            px = X_res_start + c * pw
            py = y_base + r * ph
            
            is_mun = False
            if blk['role'] == 'mixed' and c >= 8:
                # 5 parcelas municipio (cols 8, 9 en fila 0 y 1, col 10 fila 0)
                if not (r == 1 and c == 10):
                    is_mun = True
            
            bg_col = C_MUN_BG if is_mun else C_PROM_BG
            edge_col = '#B7950B' if is_mun else '#2980B9'
            
            p_rect = patches.Rectangle((px, py), pw, ph, facecolor=bg_col, edgecolor=edge_col, linewidth=0.6)
            ax1.add_patch(p_rect)
            
            scale = np.sqrt(OCUP_MAX)
            bw = pw * scale
            bh = ph * scale
            bx = px + (pw - bw) / 2
            by = py + (ph - bh) / 2
            
            b_col = C_MUN_BLD if is_mun else C_PROM_BLD
            b_rect = patches.Rectangle((bx, by), bw, bh, facecolor=b_col, edgecolor='none', alpha=0.75)
            ax1.add_patch(b_rect)

ax1.text(X_res_start + W_res / 2, H_b1 / 2, "Manzana Sur: 18 Parcelas Promotor (~513 m2s c/u con 60% huella)",
         ha='center', va='center', fontsize=7.5, color='#1A5276', fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.75, edgecolor='none'))
ax1.text(X_res_start + W_res / 2, Y_s1 + H_street + H_b2 / 2, "Manzana Central: 18 Parcelas Promotor (~513 m2s c/u)",
         ha='center', va='center', fontsize=7.5, color='#1A5276', fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.75, edgecolor='none'))
ax1.text(X_res_start + W_res * 0.35, Y_s2 + H_street + H_b3 / 2, "Manzana Norte:\n16 Parcelas Promotor",
         ha='center', va='center', fontsize=7.5, color='#1A5276', fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.75, edgecolor='none'))
ax1.text(X_res_start + W_res * 0.86, Y_s2 + H_street + H_b3 / 2, "5 Parcelas\nMunicipio\n(10% Legal)",
         ha='center', va='center', fontsize=7.5, color='#7D6608', fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.85, edgecolor='#B7950B'))

ax1.set_xlabel("Anchura del Sector (metros)", fontsize=9)
ax1.set_ylabel("Profundidad del Sector (metros)", fontsize=9)


# --- SUBPLOT 2: SECTOR FRANJA ALARGADA (600m x 100m = 60.000 m2s) ---
W_st, H_st = 600.0, 100.0
ax2.set_xlim(-15, W_st + 15)
ax2.set_ylim(-15, H_st + 20)
ax2.set_aspect('equal')
ax2.set_title("Opcion B: Sector Franja Alargada (600 m x 100 m = 60.000 m2s) [e = 1,0 m2c/m2s]\n"
              "Desarrollo Lineal: Parques Terminales (24.000 m2s), Espina Central (7.000 m2s) y Suelo Lucrativo (29.000 m2s)",
              fontsize=11, fontweight='bold', pad=12)

rect_sector_st = patches.Rectangle((0, 0), W_st, H_st, linewidth=1.5, edgecolor='#222222', facecolor='none', linestyle='--')
ax2.add_patch(rect_sector_st)

H_spine = S_VIARIO / W_st  # 11.6667 m
Y_spine = (H_st - H_spine) / 2.0  # 44.1667 m
rect_spine = patches.Rectangle((0, Y_spine), W_st, H_spine, facecolor=C_ROAD, edgecolor=C_ROAD_LINE, linewidth=1.0)
ax2.add_patch(rect_spine)
ax2.text(W_st / 2, H_st / 2, "EJE VIARIO CENTRAL: 600 m x 11,67 m = 7.000 m2s (0 m2c)",
         ha='center', va='center', fontsize=8, fontweight='bold', color='#424242',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='#888888'))

# Parques terminales: 24.000 m2s en total -> 12.000 m2s en cada extremo
L_park_st = (S_DOTACIONAL / 2.0) / (H_st - H_spine)  # 135.849 m

# Parque Oeste
rect_pw_n = patches.Rectangle((0, Y_spine + H_spine), L_park_st, Y_spine, facecolor=C_PARK, edgecolor='#2E7D32', linewidth=1.0, alpha=0.85)
rect_pw_s = patches.Rectangle((0, 0), L_park_st, Y_spine, facecolor=C_PARK, edgecolor='#2E7D32', linewidth=1.0, alpha=0.85)
ax2.add_patch(rect_pw_n)
ax2.add_patch(rect_pw_s)
ax2.text(L_park_st / 2, H_st / 2, "PARQUE OESTE\n(EL/D/I: 12.000 m2s)", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#1B5E20')

# Parque Este
rect_pe_n = patches.Rectangle((W_st - L_park_st, Y_spine + H_spine), L_park_st, Y_spine, facecolor=C_PARK, edgecolor='#2E7D32', linewidth=1.0, alpha=0.85)
rect_pe_s = patches.Rectangle((W_st - L_park_st, 0), L_park_st, Y_spine, facecolor=C_PARK, edgecolor='#2E7D32', linewidth=1.0, alpha=0.85)
ax2.add_patch(rect_pe_n)
ax2.add_patch(rect_pe_s)
ax2.text(W_st - L_park_st / 2, H_st / 2, "PARQUE ESTE\n(EL/D/I: 12.000 m2s)", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#1B5E20')

# Lucrativo central: longitud = 328.30 m
X_luc_start = L_park_st
L_luc = W_st - 2 * L_park_st  # 328.302 m
N_parcels_side = 29  # 29 al norte + 29 al sur = 58 parcelas
W_parcel_st = L_luc / N_parcels_side  # 11.32 m
H_parcel_st = Y_spine  # 44.17 m -> 500 m2s exactos!

for side, y0 in [('sur', 0.0), ('norte', Y_spine + H_spine)]:
    for i in range(N_parcels_side):
        px = X_luc_start + i * W_parcel_st
        py = y0
        
        # 5 parcelas al municipio
        is_mun = (side == 'norte' and i >= N_parcels_side - 5)
        bg_col = C_MUN_BG if is_mun else C_PROM_BG
        edge_col = '#B7950B' if is_mun else '#2980B9'
        
        p_rect = patches.Rectangle((px, py), W_parcel_st, H_parcel_st, facecolor=bg_col, edgecolor=edge_col, linewidth=0.5)
        ax2.add_patch(p_rect)
        
        scale = np.sqrt(OCUP_MAX)
        bw = W_parcel_st * scale
        bh = H_parcel_st * scale
        bx = px + (W_parcel_st - bw) / 2
        by = py + (H_parcel_st - bh) / 2
        
        b_col = C_MUN_BLD if is_mun else C_PROM_BLD
        b_rect = patches.Rectangle((bx, by), bw, bh, facecolor=b_col, edgecolor='none', alpha=0.75)
        ax2.add_patch(b_rect)

ax2.text(X_luc_start + L_luc * 0.45, H_st * 0.82, "Banda Residencial Norte: 24 Parcelas Promotor + 5 Municipio (Frontal al vial)",
         ha='center', va='center', fontsize=7.5, color='#1A5276', fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='none'))
ax2.text(X_luc_start + L_luc * 0.45, H_st * 0.18, "Banda Residencial Sur: 29 Parcelas Promotor (500 m2s con Huella 60%)",
         ha='center', va='center', fontsize=7.5, color='#1A5276', fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='none'))

ax2.set_xlabel("Longitud del Sector (metros)", fontsize=9)
ax2.set_ylabel("Anchura (metros)", fontsize=9)

legend_elements = [
    patches.Patch(facecolor=C_PARK, edgecolor='#2E7D32', label='Suelo Dotacional EL/D/I (24.000 m2s / 0 m2c)'),
    patches.Patch(facecolor=C_ROAD, edgecolor=C_ROAD_LINE, label='Viario Publico a Ceder (7.000 m2s / 0 m2c)'),
    patches.Patch(facecolor=C_PROM_BG, edgecolor='#2980B9', label='Parcela Promotor (52 parcelas + resto 100 m2s)'),
    patches.Patch(facecolor=C_PROM_BLD, edgecolor='none', label='Huella Edificable Promotor (60% Ocupacion)'),
    patches.Patch(facecolor=C_MUN_BG, edgecolor='#B7950B', label='Parcela Municipio (10% Legal = 5 parcelas + resto 400 m2s)'),
    patches.Patch(facecolor=C_MUN_BLD, edgecolor='none', label='Huella Edificable Municipio (60% Ocupacion)')
]
fig1.legend(handles=legend_elements, loc='lower center', ncol=3, fontsize=8.5, frameon=True, bbox_to_anchor=(0.5, 0.01))

plt.tight_layout(rect=[0, 0.05, 1, 1])
fig1_path = os.path.join(output_dir, 'sector_shapes_comparison.svg')
fig1.savefig(fig1_path, format='svg', bbox_inches='tight')
fig1.savefig(os.path.join(output_dir, 'sector_shapes_comparison.pdf'), format='pdf', bbox_inches='tight')
plt.close(fig1)
print(f"Figura 1 guardada correctamente en: {fig1_path}")

# %% FIGURA 2: SUELO FISICO (m2s) vs EDIFICABILIDAD JURIDICA (m2c) Y ANALISIS DEL REDONDEO
fig2 = plt.figure(figsize=(15, 11))
gs = GridSpec(2, 2, height_ratios=[1.0, 1.1], width_ratios=[1.1, 1.0], figure=fig2)

ax_bar = fig2.add_subplot(gs[0, 0])
ax_parcel = fig2.add_subplot(gs[0, 1])
ax_legal = fig2.add_subplot(gs[1, :])

# --- PANEL 1: BALANCE GLOBAL DEL SECTOR: FISICO (m2s) vs EDIFICABLE (m2c) ---
categories = ['Viario Publico', 'Dotacional\n(EL/D/I)', 'Lucrativo\nPromotor (90%)', 'Lucrativo\nMunicipio (10%)', 'TOTAL SECTOR']
x_indices = np.arange(len(categories))
width = 0.35

suelo_vals = [S_VIARIO, S_DOTACIONAL, S_PROMOTOR, S_MUNICIPIO, S_SECTOR]
edif_vals = [0.0, 0.0, E_PROMOTOR, E_MUNICIPIO, E_TOTAL]

b1 = ax_bar.bar(x_indices - width/2, suelo_vals, width, label='Superficie de Suelo Fisica (m2s)', color='#3498DB', edgecolor='#1B4F72', alpha=0.9)
b2 = ax_bar.bar(x_indices + width/2, edif_vals, width, label='Edificabilidad Juridica (m2c)', color='#E67E22', edgecolor='#7E5109', alpha=0.9)

ax_bar.set_title("Balance General (e = 1,0 m2c/m2s): Suelo Fisico (m2s) vs Techo Edificable (m2c)", fontsize=11, fontweight='bold')
ax_bar.set_xticks(x_indices)
ax_bar.set_xticklabels(categories, fontsize=8)
ax_bar.set_ylabel("Metros Cuadrados (m2)", fontsize=9)
ax_bar.grid(axis='y', linestyle=':', alpha=0.6)
ax_bar.legend(fontsize=8, loc='upper left')

for rect in b1:
    h = rect.get_height()
    if h > 0:
        ax_bar.annotate(f"{int(h):,} m2s".replace(',', '.'),
                        xy=(rect.get_x() + rect.get_width() / 2, h),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=7, fontweight='bold', color='#1B4F72')
for rect in b2:
    h = rect.get_height()
    if h > 0:
        ax_bar.annotate(f"{int(h):,} m2c".replace(',', '.'),
                        xy=(rect.get_x() + rect.get_width() / 2, h),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=7, fontweight='bold', color='#7E5109')

# --- PANEL 2: ANATOMIA DE PARCELA TIPO (500 m2s -> 1.034,48 m2c en 4 PLANTAS) ---
ax_parcel.set_title("Anatomia de Parcela Tipo (e = 1,0): 500 m2s -> 1.034,48 m2c en 4 Plantas\n"
                    "Ocupacion Max. 60% (300 m2s) -> Obliga a 4 Plantas (PB + 3)", fontsize=10.5, fontweight='bold')
ax_parcel.set_xlim(-10, 110)
ax_parcel.set_ylim(-10, 110)
ax_parcel.axis('off')

# Diagrama en planta
ax_parcel.text(25, 102, "PLANTA: Suelo Fisico (500 m2s)", ha='center', fontsize=8.5, fontweight='bold', color='#2C3E50')
p_base = patches.Rectangle((5, 45), 40, 50, facecolor='#EAECEE', edgecolor='#2C3E50', linewidth=1.5)
ax_parcel.add_patch(p_base)
ax_parcel.text(25, 48, "Parcela: 500 m2s", ha='center', fontsize=7, color='#5D6D7E')

footprint = patches.Rectangle((10, 55), 30, 35, facecolor='#5DADE2', edgecolor='#2874A6', linewidth=1.2)
ax_parcel.add_patch(footprint)
ax_parcel.text(25, 72, "Huella Max. 60%\n300 m2s", ha='center', va='center', fontsize=8, fontweight='bold', color='#154360')
ax_parcel.text(25, 96, "Retranqueo / Jardin (40% = 200 m2s)", ha='center', fontsize=7, color='#27AE60')

# Diagrama en alzado vertical: 4 Plantas para agotar 1.034,48 m2c
ax_parcel.text(80, 102, "SECCION: 4 Plantas (1.034 m2c)", ha='center', fontsize=8.5, fontweight='bold', color='#2C3E50')

f0 = patches.Rectangle((60, 42), 40, 11, facecolor='#F39C12', edgecolor='#B9770E', linewidth=1.0)
f1 = patches.Rectangle((60, 54), 40, 11, facecolor='#E67E22', edgecolor='#AF601A', linewidth=1.0)
f2 = patches.Rectangle((60, 66), 40, 11, facecolor='#D35400', edgecolor='#A04000', linewidth=1.0)
f3 = patches.Rectangle((66, 78), 28, 11, facecolor='#BA4A00', edgecolor='#873600', linewidth=1.0)
ax_parcel.add_patch(f0)
ax_parcel.add_patch(f1)
ax_parcel.add_patch(f2)
ax_parcel.add_patch(f3)

ax_parcel.text(80, 47, "Planta Baja: 300 m2c", ha='center', va='center', fontsize=6.5, fontweight='bold', color='white')
ax_parcel.text(80, 59, "Planta 1: 300 m2c", ha='center', va='center', fontsize=6.5, fontweight='bold', color='white')
ax_parcel.text(80, 71, "Planta 2: 300 m2c", ha='center', va='center', fontsize=6.5, fontweight='bold', color='white')
ax_parcel.text(80, 83, "Planta 3: 134,5 m2c", ha='center', va='center', fontsize=6.5, fontweight='bold', color='white')

ax_parcel.annotate('', xy=(103, 42), xytext=(103, 89), arrowprops=dict(arrowstyle='<->', color='#333333', lw=1.2))
ax_parcel.text(105, 65, "4 Plantas\n(1.034,5 m2c)", ha='left', va='center', fontsize=7.5, fontweight='bold', color='#900C3F')
ax_parcel.text(80, 32, "Ratio Neta: 2,069 m2c/m2s\nMinimo legal: 4 plantas", ha='center', fontsize=7.5, color='#333333')

# --- PANEL 3: ANALISIS DEL DNI TERMINACION 4 Y REPARTO LEGAL ---
ax_legal.set_title("Analisis Aritmetico y Juridico Ajustado a DNI (e = 1,0 m2c/m2s): Reparto de Aprovechamiento y Restos",
                   fontsize=11, fontweight='bold', pad=10)
ax_legal.set_xlim(0, 100)
ax_legal.set_ylim(0, 100)
ax_legal.axis('off')

box_err = patches.FancyBboxPatch((2, 10), 45, 80, boxstyle="round,pad=1.5", facecolor='#FADBD8', edgecolor='#C0392B', linewidth=1.5)
ax_legal.add_patch(box_err)
ax_legal.text(24.5, 84, "CALCULO ERRADO POR RESTA DIRECTA", ha='center', fontsize=8.5, fontweight='bold', color='#922B21')

err_text = (
    "1. Suelo lucrativo total: 29.000 m2s\n"
    "2. Division global: 29.000 / 500 = 58 parcelas exactas.\n"
    "3. Promotor (90% = 26.100 m2s):\n"
    "   26.100 / 500 = 52,2 -> Asigna 52 parcelas.\n"
    "4. 'Resta errada':\n"
    "   58 - 52 = 6 parcelas al Ayuntamiento.\n\n"
    "ERROR JURIDICO:\n"
    "- 6 parcelas = 3.000 m2s (10,34% del sector).\n"
    "- El Ayto. solo tiene derecho a 2.900 m2s (10,00%).\n"
    "- Exceso municipal ilegal no pagado: +100 m2s.\n"
    "- Se priva al promotor de su resto legal de 100 m2s."
)
ax_legal.text(4, 78, err_text, ha='left', va='top', fontsize=7.2, color='#641E16', linespacing=1.2)

box_ok = patches.FancyBboxPatch((52, 10), 46, 80, boxstyle="round,pad=1.5", facecolor='#D4EFDF', edgecolor='#229954', linewidth=1.5)
ax_legal.add_patch(box_ok)
ax_legal.text(75, 84, "SOLUCION LEGAL EXACTA (LEY 4/2017)", ha='center', fontsize=8.5, fontweight='bold', color='#196F3D')

ok_text = (
    "1. DERECHO EXACTO DEL PROMOTOR (90%): 26.100 m2s\n"
    "   - 52 parcelas minimas (26.000 m2s) + RESTO DE 100 m2s.\n"
    "   - El resto de 100 m2s SE ADICIONA a las 52 parcelas\n"
    "     del promotor (haciendolas de 501,9 m2s de media).\n\n"
    "2. DERECHO EXACTO DEL MUNICIPIO (10%): 2.900 m2s\n"
    "   - Corresponden 5 parcelas de 500 m2s (2.500 m2s)\n"
    "     + RESTO DE 400 m2s (o 827,6 m2c).\n"
    "   - El resto de 400 m2s se compensa en metalico (Art. 44.c y\n"
    "     285.1.d Ley 4/2017) o se destina a parcela unica de 2.900 m2s.\n\n"
    "3. NUMERO MINIMO DE PLANTAS: 4 plantas obligatorias\n"
    "   (60.000 m2c / 17.400 m2s ocupadas = 3,45 -> 4 plantas)."
)
ax_legal.text(54, 78, ok_text, ha='left', va='top', fontsize=7.2, color='#145A32', linespacing=1.2)

plt.tight_layout()
fig2_path = os.path.join(output_dir, 'physical_vs_buildable_areas.svg')
fig2.savefig(fig2_path, format='svg', bbox_inches='tight')
fig2.savefig(os.path.join(output_dir, 'physical_vs_buildable_areas.pdf'), format='pdf', bbox_inches='tight')
plt.close(fig2)
print(f"Figura 2 guardada correctamente en: {fig2_path}")
