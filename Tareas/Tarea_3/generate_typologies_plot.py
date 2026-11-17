# -*- coding: utf-8 -*-
"""
Sector Urbanistico: Distribucion Completa de Tipologias y Cesiones
Ajustado para DNI terminado en 4 -> Edificabilidad bruta e = 1,0 m2c/m2s.
Visualizacion integrada que combina:
1. Suelo Dotacional Publico (EL/D/I 24.000 m2s - Dominio Publico)
2. Viario Publico a ceder (7.000 m2s)
3. Residencial Unifamiliar Libre (Baja densidad, 2-3 plantas, jardines privados)
4. Residencial Plurifamiliar Protegido (VPO 40%, 5 plantas en torre con jardin PRIVADO comunitario)
5. Parcela Lucrativa Municipal (10% Cesion Legal = 2.900 m2s / 6.000 m2c, VPO Publica / PMS)
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

# Parametros urbanisticos ajustados a DNI (terminacion 4 -> e = 1,0 m2c/m2s)
S_SECTOR = 60000.0         # 6 hectareas = 60.000 m2s
E_BRUTA = 1.0              # Edificabilidad ajustada: 0,8 + 0,2 = 1,0 m2c/m2s
E_TOTAL = S_SECTOR * E_BRUTA  # 60.000 m2c

S_VIARIO = 7000.0          # 7.000 m2s
S_DOTACIONAL = E_TOTAL * 0.40  # 24.000 m2s (Art. 138.1.A.c Ley 4/2017)
S_LUCRATIVA = S_SECTOR - S_VIARIO - S_DOTACIONAL  # 29.000 m2s

# Reparto de suelo y edificabilidad lucrativa:
# 1. Cesion 10% al Ayuntamiento (Art. 44.c Ley 4/2017):
S_MUNICIPIO = S_LUCRATIVA * 0.10  # 2.900 m2s
E_MUNICIPIO = E_TOTAL * 0.10      # 6.000 m2c (VPO Publica / Patrimonio Municipal de Suelo)

# 2. Suelo y edificabilidad para Promotores (90%):
S_PROMOTOR = S_LUCRATIVA * 0.90   # 26.100 m2s
E_PROMOTOR = E_TOTAL * 0.90       # 54.000 m2c

# Reserva de Vivienda Protegida (40% de edificabilidad residencial):
# Total VPO sector = 24.000 m2c (40%). Total Libre = 36.000 m2c (60%).
# Si el municipio aporta su 10% a VPO publica (6.000 m2c), el promotor aporta 18.000 m2c VPO privada.
E_VPO_TOTAL = E_TOTAL * 0.40      # 24.000 m2c
E_VPO_MUNICIPAL = E_MUNICIPIO     # 6.000 m2c
E_VPO_PRIVADA = 18000.0           # 18.000 m2c
E_LIBRE_PROMOTOR = 36000.0        # 36.000 m2c

output_dir = os.path.dirname(os.path.abspath(__file__))

fig = plt.figure(figsize=(16, 15))
gs = GridSpec(3, 1, height_ratios=[1.25, 0.9, 1.0], figure=fig)

ax1 = fig.add_subplot(gs[0])  # Sector Cuadrado
ax2 = fig.add_subplot(gs[1])  # Sector Franja Alargada
ax3 = fig.add_subplot(gs[2])  # Analisis Juridico y Seccion de Alturas

# Paleta cromatica
C_PARK = '#8FBC8F'           # Espacio libre dotacional PUBLICO
C_ROAD = '#D3D3D3'           # Viario publico
C_ROAD_LINE = '#888888'
C_UNI_PARCEL = '#EBF5FB'     # Parcela unifamiliar libre
C_UNI_BLD = '#2980B9'        # Huella unifamiliar libre (2 plantas B+1)
C_UNI_POOL = '#5DADE2'       # Piscina privada
C_MULTI_PARCEL = '#FADBD8'   # Parcela plurifamiliar VPO privada
C_MULTI_BLD = '#C0392B'      # Bloques plurifamiliares VPO privada (5 plantas B+4)
C_PRIV_GARDEN = '#D5F5E3'    # Jardin PRIVADO comunitario de copropietarios
C_MUN_PARCEL = '#FCF3CF'     # Parcela municipal 10% (2.900 m2s)
C_MUN_BLD = '#D4AC0D'        # Edificio municipal (Patrimonio Municipal de Suelo / VPO Publica)

# ==============================================================================
# SUBPLOT 1: SECTOR CUADRADO (AJUSTADO A e = 1,0 m2c/m2s)
# ==============================================================================
W_sq, H_sq = 250.0, 240.0
ax1.set_xlim(-10, W_sq + 15)
ax1.set_ylim(-10, H_sq + 15)
ax1.set_aspect('equal')
ax1.set_title("Opcion A: Sector Cuadrado (250 m x 240 m = 60.000 m2s) [Ajuste DNI -> e = 1,0 m2c/m2s]\n"
              "Unifamiliar Libre (36.000 m2c) + VPO Privada (18.000 m2c) + Parcela Municipal 10% (2.900 m2s / 6.000 m2c)",
              fontsize=11, fontweight='bold', pad=10)

# Perimetro sector
rect_sector_sq = patches.Rectangle((0, 0), W_sq, H_sq, linewidth=1.5, edgecolor='#222222', facecolor='none', linestyle='--')
ax1.add_patch(rect_sector_sq)

# 1. Dotacional / Espacio Libre Publico (100m x 240m = 24.000 m2s)
W_park_sq = 100.0
rect_park_sq = patches.Rectangle((0, 0), W_park_sq, H_sq, facecolor=C_PARK, edgecolor='#2E7D32', linewidth=1.2, alpha=0.9)
ax1.add_patch(rect_park_sq)
ax1.text(W_park_sq / 2, H_sq / 2,
         "ESPACIO LIBRE DOTACIONAL PUBLICO (EL/D/I)\n24.000 m2s (0 m2c lucrativa)\n"
         "[DOMINIO PUBLICO - ABIERTO A LA CIUDAD]\n"
         "Reserva legal 0,40 m2s/m2c (Art. 138 Ley 4/2017)",
         ha='center', va='center', fontsize=8, fontweight='bold', color='#1B5E20',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9, edgecolor='#2E7D32'))

# 2. Viario (Avenida de 14m x 240m = 3.360 m2s + 2 calles secundarias de 13.38m = 3.640 m2s -> 7.000 m2s)
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

# 3. Manzana Norte (Block 3, Area = 136m x 77.24m = 10.504 m2s)
# Subdividida en:
# - Parcela Municipal del 10% (2.900 m2s): anchura = 2.900 / 77.235 = 37.55 m en el extremo este
# - Parcela Plurifamiliar VPO Privada: los restantes 98.45 m x 77.24 m = 7.604 m2s
W_mun_sq = S_MUNICIPIO / H_b3  # 37.547 m
W_vpo_sq = W_res - W_mun_sq    # 98.453 m

# 3A. Macro-parcela VPO Privada (98.45m x 77.24m)
rect_vpo_sq = patches.Rectangle((X_res_start, Y_s2 + H_street), W_vpo_sq, H_b3,
                                facecolor=C_PRIV_GARDEN, edgecolor='#922B21', linewidth=1.2)
ax1.add_patch(rect_vpo_sq)

# Torres VPO privadas (2 bloques de 5 plantas B+4 = 18.000 m2c)
t1 = patches.Rectangle((X_res_start + 10, Y_s2 + H_street + 14), 36, 24, facecolor=C_MULTI_BLD, edgecolor='#641E16', linewidth=1.0)
t2 = patches.Rectangle((X_res_start + 52, Y_s2 + H_street + 14), 36, 24, facecolor=C_MULTI_BLD, edgecolor='#641E16', linewidth=1.0)
ax1.add_patch(t1)
ax1.add_patch(t2)
ax1.text(X_res_start + 28, Y_s2 + H_street + 26, "Torre VPO-1\n5 Pl. (B+4)", ha='center', va='center', fontsize=6.5, fontweight='bold', color='white')
ax1.text(X_res_start + 70, Y_s2 + H_street + 26, "Torre VPO-2\n5 Pl. (B+4)", ha='center', va='center', fontsize=6.5, fontweight='bold', color='white')

ax1.text(X_res_start + W_vpo_sq / 2, Y_s2 + H_street + H_b3 - 12,
         "COMPLEJO PLURIFAMILIAR VPO PRIVADA (18.000 m2c)\n"
         "Fondo verde = Jardin y Plaza PRIVADA Comunitaria\n"
         "[PROPIEDAD PRIVADA: NO confundible con Parque publico]",
         ha='center', va='center', fontsize=6.5, fontweight='bold', color='#78281F',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9, edgecolor='#C0392B'))

# 3B. Parcela Municipal de Cesion Obligatoria (10% = 2.900 m2s)
X_mun_sq = X_res_start + W_vpo_sq
rect_mun_sq = patches.Rectangle((X_mun_sq, Y_s2 + H_street), W_mun_sq, H_b3,
                                facecolor=C_MUN_PARCEL, edgecolor='#B7950B', linewidth=1.5, hatch='//')
ax1.add_patch(rect_mun_sq)

# Edificio Municipal (6.000 m2c en 5 plantas)
bld_mun_sq = patches.Rectangle((X_mun_sq + 4, Y_s2 + H_street + 14), W_mun_sq - 8, 28,
                               facecolor=C_MUN_BLD, edgecolor='#7D6608', linewidth=1.2)
ax1.add_patch(bld_mun_sq)
ax1.text(X_mun_sq + W_mun_sq / 2, Y_s2 + H_street + 28, "EDIFICIO MUNICIPAL\n(VPO Publica / PMS)\n6.000 m2c (5 Pl.)",
         ha='center', va='center', fontsize=6.5, fontweight='bold', color='white')
ax1.text(X_mun_sq + W_mun_sq / 2, Y_s2 + H_street + H_b3 - 14,
         "PARCELA MUNICIPAL\n2.900 m2s (10% Suelo)",
         ha='center', va='center', fontsize=6, fontweight='bold', color='#7D6608',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9, edgecolor='#B7950B'))

# 4. Manzanas Sur y Central: UNIFAMILIAR LIBRE (36.000 m2c)
# 36 parcelas unifamiliares de ~513 m2s
unifam_blocks = [
    {'y0': 0.0, 'h': H_b1, 'rows': 2, 'cols': 9},
    {'y0': Y_s1 + H_street, 'h': H_b2, 'rows': 2, 'cols': 9}
]
for blk in unifam_blocks:
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
            p_patch = patches.Rectangle((px, py), pw, ph, facecolor=C_UNI_PARCEL, edgecolor='#7FB3D5', linewidth=0.6)
            ax1.add_patch(p_patch)
            bw, bh = pw * 0.65, ph * 0.65
            bx, by = px + 1.5, py + (ph - bh) / 2
            b_patch = patches.Rectangle((bx, by), bw, bh, facecolor=C_UNI_BLD, edgecolor='#1B4F72', linewidth=0.7, alpha=0.85)
            ax1.add_patch(b_patch)
            sw, sh = pw * 0.20, ph * 0.35
            sx, sy = px + pw - sw - 1.2, py + (ph - sh) / 2
            pool_patch = patches.Rectangle((sx, sy), sw, sh, facecolor=C_UNI_POOL, edgecolor='#2980B9', linewidth=0.5)
            ax1.add_patch(pool_patch)

ax1.text(X_res_start + W_res / 2, H_b1 / 2, "ZONA UNIFAMILIAR LIBRE SUR: 18 Parcelas de ~513 m2s (2 Pl. B+1 con Jardin y Piscina Privada)",
         ha='center', va='center', fontsize=7.5, fontweight='bold', color='#154360',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.85, edgecolor='none'))
ax1.text(X_res_start + W_res / 2, Y_s1 + H_street + H_b2 / 2, "ZONA UNIFAMILIAR LIBRE CENTRAL: 18 Parcelas de ~513 m2s (36.000 m2c Renta Libre)",
         ha='center', va='center', fontsize=7.5, fontweight='bold', color='#154360',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.85, edgecolor='none'))

ax1.set_xlabel("Anchura (metros)", fontsize=8.5)
ax1.set_ylabel("Profundidad (metros)", fontsize=8.5)

# ==============================================================================
# SUBPLOT 2: SECTOR FRANJA ALARGADA (AJUSTADO A e = 1,0 m2c/m2s)
# ==============================================================================
W_st, H_st = 600.0, 100.0
ax2.set_xlim(-15, W_st + 15)
ax2.set_ylim(-15, H_st + 20)
ax2.set_aspect('equal')
ax2.set_title("Opcion B: Sector Franja Alargada (600 m x 100 m = 60.000 m2s) [e = 1,0 m2c/m2s]\n"
              "Parques Terminales (24.000 m2s), Cluster VPO Privada + Parcela Municipal (2.900 m2s) y Corredor Unifamiliar Libre",
              fontsize=11, fontweight='bold', pad=10)

rect_sector_st = patches.Rectangle((0, 0), W_st, H_st, linewidth=1.5, edgecolor='#222222', facecolor='none', linestyle='--')
ax2.add_patch(rect_sector_st)

H_spine = S_VIARIO / W_st  # 11.6667 m
Y_spine = (H_st - H_spine) / 2.0  # 44.1667 m
rect_spine = patches.Rectangle((0, Y_spine), W_st, H_spine, facecolor=C_ROAD, edgecolor=C_ROAD_LINE, linewidth=1.0)
ax2.add_patch(rect_spine)

# Parques terminales: 24.000 m2s total = 12.000 m2s en cada extremo
L_park_st = (S_DOTACIONAL / 2.0) / (H_st - H_spine)  # 135.849 m
# Oeste
rect_pw_n = patches.Rectangle((0, Y_spine + H_spine), L_park_st, Y_spine, facecolor=C_PARK, edgecolor='#2E7D32', linewidth=0.8, alpha=0.85)
rect_pw_s = patches.Rectangle((0, 0), L_park_st, Y_spine, facecolor=C_PARK, edgecolor='#2E7D32', linewidth=0.8, alpha=0.85)
ax2.add_patch(rect_pw_n)
ax2.add_patch(rect_pw_s)
ax2.text(L_park_st / 2, H_st / 2, "PARQUE PUBLICO OESTE\n(EL/D/I: 12.000 m2s)\n[Dominio Publico]", ha='center', va='center', fontsize=6.5, fontweight='bold', color='#1B5E20')

# Este
rect_pe_n = patches.Rectangle((W_st - L_park_st, Y_spine + H_spine), L_park_st, Y_spine, facecolor=C_PARK, edgecolor='#2E7D32', linewidth=0.8, alpha=0.85)
rect_pe_s = patches.Rectangle((W_st - L_park_st, 0), L_park_st, Y_spine, facecolor=C_PARK, edgecolor='#2E7D32', linewidth=0.8, alpha=0.85)
ax2.add_patch(rect_pe_n)
ax2.add_patch(rect_pe_s)
ax2.text(W_st - L_park_st / 2, H_st / 2, "PARQUE PUBLICO ESTE\n(EL/D/I: 12.000 m2s)\n[Dominio Publico]", ha='center', va='center', fontsize=6.5, fontweight='bold', color='#1B5E20')

X_luc_start = L_park_st
L_luc = W_st - 2 * L_park_st  # 328.302 m

# 1. Parcela Municipal del 10% (2.900 m2s) en banda sur del acceso oeste
L_mun_st = S_MUNICIPIO / Y_spine  # 65.657 m
rect_mun_st = patches.Rectangle((X_luc_start, 0), L_mun_st, Y_spine, facecolor=C_MUN_PARCEL, edgecolor='#B7950B', linewidth=1.2, hatch='//')
ax2.add_patch(rect_mun_st)

b_mun_st = patches.Rectangle((X_luc_start + 6, 10), L_mun_st - 12, 24, facecolor=C_MUN_BLD, edgecolor='#7D6608', linewidth=1.0)
ax2.add_patch(b_mun_st)
ax2.text(X_luc_start + L_mun_st / 2, 22, "EDIFICIO MUNICIPAL (5 Pl.)\n6.000 m2c (10% Cesion)", ha='center', va='center', fontsize=6.5, fontweight='bold', color='white')
ax2.text(X_luc_start + L_mun_st / 2, 38, "PARCELA MUNICIPAL (2.900 m2s)", ha='center', fontsize=6, fontweight='bold', color='#7D6608')

# 2. Cluster VPO Privada en banda norte enfrente
L_vpo_st_n = 95.0
rect_vpo_st_n = patches.Rectangle((X_luc_start, Y_spine + H_spine), L_vpo_st_n, Y_spine, facecolor=C_PRIV_GARDEN, edgecolor='#922B21', linewidth=1.0)
ax2.add_patch(rect_vpo_st_n)

b1_n = patches.Rectangle((X_luc_start + 8, Y_spine + H_spine + 10), 38, 24, facecolor=C_MULTI_BLD, edgecolor='#641E16', linewidth=1.0)
b2_n = patches.Rectangle((X_luc_start + 50, Y_spine + H_spine + 10), 38, 24, facecolor=C_MULTI_BLD, edgecolor='#641E16', linewidth=1.0)
ax2.add_patch(b1_n)
ax2.add_patch(b2_n)
ax2.text(X_luc_start + 27, Y_spine + H_spine + 22, "Bloque VPO 1 (5 Pl.)", ha='center', va='center', fontsize=6.5, fontweight='bold', color='white')
ax2.text(X_luc_start + 69, Y_spine + H_spine + 22, "Bloque VPO 2 (5 Pl.)", ha='center', va='center', fontsize=6.5, fontweight='bold', color='white')
ax2.text(X_luc_start + L_vpo_st_n / 2, H_st * 0.95, "Complejo VPO Privada (Jardin Privado Comunitario)", ha='center', fontsize=6, fontweight='bold', color='#78281F')

# 3. Corredor Unifamiliar Libre
X_uni_n_start = X_luc_start + L_vpo_st_n
L_uni_n = L_luc - L_vpo_st_n
N_uni_n = 19
W_p_n = L_uni_n / N_uni_n

for i in range(N_uni_n):
    px = X_uni_n_start + i * W_p_n
    py = Y_spine + H_spine
    p_patch = patches.Rectangle((px, py), W_p_n, Y_spine, facecolor=C_UNI_PARCEL, edgecolor='#7FB3D5', linewidth=0.5)
    ax2.add_patch(p_patch)
    b_patch = patches.Rectangle((px + 1.5, py + 4), W_p_n - 3, Y_spine * 0.55, facecolor=C_UNI_BLD, edgecolor='#1B4F72', linewidth=0.5, alpha=0.85)
    ax2.add_patch(b_patch)

X_uni_s_start = X_luc_start + L_mun_st
L_uni_s = L_luc - L_mun_st
N_uni_s = 21
W_p_s = L_uni_s / N_uni_s

for i in range(N_uni_s):
    px = X_uni_s_start + i * W_p_s
    py = 0.0
    p_patch = patches.Rectangle((px, py), W_p_s, Y_spine, facecolor=C_UNI_PARCEL, edgecolor='#7FB3D5', linewidth=0.5)
    ax2.add_patch(p_patch)
    b_patch = patches.Rectangle((px + 1.5, py + 6), W_p_s - 3, Y_spine * 0.55, facecolor=C_UNI_BLD, edgecolor='#1B4F72', linewidth=0.5, alpha=0.85)
    ax2.add_patch(b_patch)

ax2.text(X_uni_n_start + L_uni_n / 2, H_st * 0.95, "Corredor Unifamiliar Libre Norte (19 Parcelas - 2 Pl. B+1)", ha='center', fontsize=6.5, fontweight='bold', color='#154360')
ax2.text(X_uni_s_start + L_uni_s / 2, 5, "Corredor Unifamiliar Libre Sur (21 Parcelas - 2 Pl. B+1 con Jardin)", ha='center', fontsize=6.5, fontweight='bold', color='#154360')

ax2.set_xlabel("Longitud (metros)", fontsize=8.5)
ax2.set_ylabel("Anchura (metros)", fontsize=8.5)

# ==============================================================================
# SUBPLOT 3: ACLARACION JURIDICA DE PARQUES Y BALANCE DE CESIONES
# ==============================================================================
ax3.set_xlim(0, 100)
ax3.set_ylim(0, 100)
ax3.axis('off')
ax3.set_title("Distincion Juridica Fundamental: Parques Dotacionales Publicos vs Jardines Privados de Manzana\n"
              "y Destino Legal del 10% de Cesion al Ayuntamiento (Ajustado a e = 1,0 m2c/m2s)",
              fontsize=11, fontweight='bold', pad=8)

box_pub = patches.FancyBboxPatch((2, 8), 30, 84, boxstyle="round,pad=1.0", facecolor='#EAFAF1', edgecolor='#27AE60', linewidth=1.5)
ax3.add_patch(box_pub)
ax3.text(17, 86, "ESPACIO LIBRE DOTACIONAL (EL/D/I)\n[DOMINIO PUBLICO]", ha='center', fontsize=8, fontweight='bold', color='#145A32')

txt_pub = (
    "* Superficie: 24.000 m2s (0,40 x 60.000 m2c).\n"
    "* Regimen: DOMINIO PUBLICO MUNICIPAL.\n"
    "* Destino: Parque urbano, plazas y zonas\n"
    "  verdes abiertas a toda la ciudadania.\n"
    "* Conservacion: Municipal / Entidad de\n"
    "  Conservacion Urbanistica.\n"
    "* Estatus: CESION OBLIGATORIA GRATUITA\n"
    "  segun Art. 138.1.A.c Ley 4/2017.\n"
    "* Inconfundible: NUNCA puede sustituirse\n"
    "  por jardines privados interiores."
)
ax3.text(4, 76, txt_pub, ha='left', va='top', fontsize=6.8, color='#196F3D', linespacing=1.2)

box_priv = patches.FancyBboxPatch((35, 8), 30, 84, boxstyle="round,pad=1.0", facecolor='#FADBD8', edgecolor='#C0392B', linewidth=1.5)
ax3.add_patch(box_priv)
ax3.text(50, 86, "JARDIN PRIVADO DEL COMPLEJO\n[PROPIEDAD PRIVADA]", ha='center', fontsize=8, fontweight='bold', color='#78281F')

txt_priv = (
    "* Superficie: ~5.000 m2s en parcela.\n"
    "* Regimen: PROPIEDAD PRIVADA COMUN\n"
    "  (Regimen de Propiedad Horizontal).\n"
    "* Uso: Exclusivo de los residentes/copropietarios\n"
    "  del bloque plurifamiliar (recinto vallado).\n"
    "* Conservacion: A cargo exclusivo de los\n"
    "  propietarios en cuota de comunidad.\n"
    "* Dotaciones: Piscina privada, juegos, solarium.\n"
    "* Regla legal: Forma parte del suelo lucrativo;\n"
    "  NO computa como cesion publica al municipio."
)
ax3.text(37, 76, txt_priv, ha='left', va='top', fontsize=6.8, color='#641E16', linespacing=1.2)

box_mun = patches.FancyBboxPatch((68, 8), 30, 84, boxstyle="round,pad=1.0", facecolor='#FEF9E7', edgecolor='#D4AC0D', linewidth=1.5)
ax3.add_patch(box_mun)
ax3.text(83, 86, "PARCELA MUNICIPAL DEL 10%\n[PATRIMONIO DE SUELO - PMS]", ha='center', fontsize=8, fontweight='bold', color='#7D6608')

txt_mun = (
    "* Superficie: 2.900 m2s (10% suelo lucrativo).\n"
    "* Edificabilidad: 6.000 m2c (10% aprovechamiento).\n"
    "* Base legal: Art. 44.c Ley 4/2017 y TRLSRU.\n"
    "* Destino legal obligatorio (Art. 299.3):\n"
    "  Afecto prioritariamente a la construccion de\n"
    "  Vivienda Protegida (VPO Publica / Alquiler social).\n"
    "* Representacion grafica: Se materializa en\n"
    "  parcela urbanizada independiente de 2.900 m2s\n"
    "  o en 5 parcelas de 500 m2s + 400 m2s en metalico."
)
ax3.text(70, 76, txt_mun, ha='left', va='top', fontsize=6.8, color='#7D6608', linespacing=1.2)

legend_elements = [
    patches.Patch(facecolor=C_PARK, edgecolor='#2E7D32', label='Parque Dotacional Publico (24.000 m2s - Dominio Publico)'),
    patches.Patch(facecolor=C_ROAD, edgecolor=C_ROAD_LINE, label='Viario Publico a Ceder (7.000 m2s)'),
    patches.Patch(facecolor=C_UNI_BLD, edgecolor='#1B4F72', label='Vivienda Unifamiliar Libre (2-3 Pl. B+1, 36.000 m2c)'),
    patches.Patch(facecolor=C_MULTI_BLD, edgecolor='#641E16', label='Vivienda Plurifamiliar VPO Privada (5 Pl. B+4 en Torre)'),
    patches.Patch(facecolor=C_PRIV_GARDEN, edgecolor='#922B21', label='Jardin y Plaza PRIVADA Comunitaria de Copropietarios'),
    patches.Patch(facecolor=C_MUN_PARCEL, edgecolor='#B7950B', hatch='//', label='Parcela Municipal 10% (2.900 m2s / 6.000 m2c - VPO Publica)')
]
fig.legend(handles=legend_elements, loc='lower center', ncol=3, fontsize=8, frameon=True, bbox_to_anchor=(0.5, 0.005))

plt.tight_layout(rect=[0, 0.035, 1, 1])
out_svg = os.path.join(output_dir, 'sector_shapes_typologies.svg')
fig.savefig(out_svg, format='svg', bbox_inches='tight')
fig.savefig(os.path.join(output_dir, 'sector_shapes_typologies.pdf'), format='pdf', bbox_inches='tight')
plt.close(fig)
print(f"Grafico integrado e=1.0 guardado con exito en: {out_svg}")
