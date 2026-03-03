import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# --- CONFIGURACIÓN BILINGÜE / BILINGUAL SETUP ---
LANG = 'ES'  # Toggle 'EN' / 'ES'

text = {
    'ES': {
        'title': 'Art. 35 (4-6): Ordenación y Límites de Crecimiento',
        'subtitle': 'Restricciones Morfológicas y Cuantitativas en Asentamientos Rurales',
        'legend_exist': 'Edificación Existente (Base de Cálculo)',
        'legend_new': 'Nueva Edificación (Max 25% de la existente)',
        'legend_road': 'Vial Rural Existente (Mantener)',
        'legend_road_ok': 'Conexión Interior (Permitido Ap. 4)',
        'legend_road_bad': 'Apertura de Nuevos Viales (Prohibido Ap. 4)',
        'ua_label': 'Unidad de Actuación (Ap. 5)',
        'math_rule': 'Regla del 25% (Ap. 6)',
        'math_desc': 'Si E_existente = 1000m² \n→ E_nueva ≤ 250m²'
    },
    'EN': {
        'title': 'Art. 35 (4-6): Ordering and Growth Limits',
        'subtitle': 'Morphological and Quantitative Restrictions in Rural Settlements',
        'legend_exist': 'Existing Buildings (Baseline)',
        'legend_new': 'New Buildings (Max 25% of existing)',
        'legend_road': 'Existing Rural Road (Maintain)',
        'legend_road_ok': 'Internal Connection (Allowed Para. 4)',
        'legend_road_bad': 'New Road Opening (Prohibited Para. 4)',
        'ua_label': 'Execution Unit (Para. 5)',
        'math_rule': 'The 25% Rule (Para. 6)',
        'math_desc': 'If E_existing = 1000m² \n→ E_new ≤ 250m²'
    }
}

# --- GENERACIÓN DE DATOS SIMULADOS ---
fig, ax = plt.subplots(figsize=(12, 8))

# 1. Fondo: Terreno Rústico
ax.set_facecolor('#f4f4f0') # Color "papel" o terreno claro

# 2. Viales Existentes (Líneas irregulares) - Ap. 4 "Mantener estructura"
roads_x = [10, 20, 40, 60, 80, 90]
roads_y = [50, 52, 48, 55, 50, 48]
ax.plot(roads_x, roads_y, color='gray', linewidth=10, alpha=0.4, solid_capstyle='round')
# Ramal existente
ax.plot([40, 45], [48, 20], color='gray', linewidth=8, alpha=0.4, solid_capstyle='round')
ax.plot([60, 65], [55, 80], color='gray', linewidth=8, alpha=0.4, solid_capstyle='round')

# 3. Edificaciones Existentes (Gris Oscuro) - Base del cálculo
# Representan la "trama consolidada"
existing_buildings = [
    patches.Rectangle((15, 55), 8, 8), patches.Rectangle((35, 55), 10, 6),
    patches.Rectangle((55, 60), 8, 8), patches.Rectangle((75, 52), 8, 8),
    patches.Rectangle((35, 25), 8, 8), patches.Rectangle((45, 30), 6, 6)
]

total_area_exist = 0
for p in existing_buildings:
    p.set_facecolor('#555555')
    p.set_edgecolor('black')
    ax.add_patch(p)
    total_area_exist += p.get_width() * p.get_height()

# 4. Nueva Edificación (Naranja) - Ap. 6 "Límite 25%"
# Diseñamos edificios nuevos pequeños que visualmente sean aprox 1/4 del área gris
new_buildings = [
    patches.Rectangle((42, 38), 6, 6), # Infill (colmatación)
    patches.Rectangle((62, 65), 5, 5)  # Ampliación pequeña
]

for p in new_buildings:
    p.set_facecolor('#ff9933') # Naranja seguridad
    p.set_edgecolor('black')
    p.set_hatch('///')
    ax.add_patch(p)

# 5. Viales Nuevos (Lo permitido vs Lo prohibido) - Ap. 4
# A. Permitido (Verde): Pequeña conexión interior para colmatar
ax.plot([45, 60], [25, 55], color='#66cc66', linewidth=4, linestyle='--')
ax.text(50, 40, '✓', color='green', fontsize=20, fontweight='bold')

# B. Prohibido (Rojo): Nuevo vial abriendo campo
ax.plot([80, 90], [50, 80], color='#cc6666', linewidth=4, linestyle=':')
ax.text(88, 70, '✗', color='red', fontsize=20, fontweight='bold')

# 6. Unidad de Actuación (Ap. 5)
# Un polígono punteado que delimita dónde se va a actuar
ua_polygon = patches.Polygon([(30, 15), (70, 15), (70, 75), (30, 75)],
                             closed=True, fill=False, edgecolor='#0066cc',
                             linestyle='--', linewidth=2)
ax.add_patch(ua_polygon)
ax.text(32, 17, text[LANG]['ua_label'], color='#0066cc', fontsize=10, style='italic', fontweight='bold')

# --- ANOTACIONES Y LEYENDA ---

# Títulos
ax.set_title(text[LANG]['title'], fontsize=16, fontweight='bold', pad=20)
ax.text(50, 95, text[LANG]['subtitle'], ha='center', fontsize=12, style='italic')

# Caja de Cálculo (La Matemática del Ap. 6)
props = dict(boxstyle='round', facecolor='white', alpha=0.9)
ax.text(5, 85, f"{text[LANG]['math_rule']}\n\n{text[LANG]['math_desc']}",
        fontsize=11, bbox=props, verticalalignment='top')

# Leyenda Personalizada
from matplotlib.lines import Line2D
custom_lines = [
    patches.Patch(facecolor='#555555', edgecolor='black', label=text[LANG]['legend_exist']),
    patches.Patch(facecolor='#ff9933', edgecolor='black', hatch='///', label=text[LANG]['legend_new']),
    Line2D([0], [0], color='#66cc66', lw=4, linestyle='--', label=text[LANG]['legend_road_ok']),
    Line2D([0], [0], color='#cc6666', lw=4, linestyle=':', label=text[LANG]['legend_road_bad']),
    Line2D([0], [0], color='#0066cc', lw=2, linestyle='--', label=text[LANG]['ua_label'])
]

ax.legend(handles=custom_lines, loc='lower right', framealpha=1)

# Ajustes finales
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')  # Ocultar ejes de coordenadas para aspecto de plano

plt.tight_layout()
plt.show()