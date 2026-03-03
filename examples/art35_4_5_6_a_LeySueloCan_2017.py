#%% Import libraries
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Polygon, LineString, box

#%% Configuration & Bilingual Labels
LANG = 'ES' # Toggle 'EN' / 'ES'

labels = {
    'ES': {
        'title': 'Ordenación de Asentamiento Rural (Art. 35.4 - 35.6)',
        'zone_2_3': 'Área Consolidada (Ocupación $\ge$ 2/3)',
        'exist_bldg': 'Edificabilidad Materializada ($E_{existente}$)',
        'new_bldg': 'Nueva Edificabilidad Máxima (25% $E_{existente}$)',
        'exist_road': 'Viario Estructural Mantenido (Apt. 4)',
        'new_road': 'Viario de Colmatación Interior (Apt. 4)',
        'ua': 'Límite Unidad de Actuación (Apt. 5)',
        'axis_x': 'Eje X (metros)',
        'axis_y': 'Eje Y (metros)'
    },
    'EN': {
        'title': 'Rural Settlement Planning (Art. 35.4 - 35.6)',
        'zone_2_3': 'Consolidated Area (Occupation $\ge$ 2/3)',
        'exist_bldg': 'Existing Buildability ($E_{existing}$)',
        'new_bldg': 'Max New Buildability (25% $E_{existing}$)',
        'exist_road': 'Maintained Structural Road (Sect. 4)',
        'new_road': 'Internal Infill Road (Sect. 4)',
        'ua': 'Action Unit Boundary (Sect. 5)',
        'axis_x': 'X Axis (meters)',
        'axis_y': 'Y Axis (meters)'
    }
}

#%% Data Generation: Spatial Modeling of the Law
# 1. Unidad de Actuación (Apt. 5)
ua_poly = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])

# 2. Área con Ocupación >= 2/3 (Apt. 6)
# Zona fuertemente antropizada dentro del asentamiento
zone_consolidated = Polygon([(10, 10), (90, 10), (90, 60), (10, 60)])

# 3. Edificabilidad Existente
bldg_1 = box(15, 15, 35, 35) # Area = 400
bldg_2 = box(45, 15, 65, 35) # Area = 400
bldg_3 = box(15, 40, 35, 55) # Area = 300
exist_bldgs = gpd.GeoDataFrame(geometry=[bldg_1, bldg_2, bldg_3])
total_existing_area = exist_bldgs.area.sum() # Total = 1100

# 4. Nueva Edificabilidad (Límite del 25% - Apt. 6)
# Max allowed = 1100 * 0.25 = 275
new_bldg = box(70, 40, 70 + 16.58, 40 + 16.58) # Area ~ 275
new_bldg_gdf = gpd.GeoDataFrame(geometry=[new_bldg])

# 5. Red Viaria (Apt. 4)
existing_road = LineString([(-10, 5), (110, 5)]) # Vía que se mantiene
colmatation_road = LineString([(78, 5), (78, 38)]) # Vía nueva estrictamente para acceso interior

#%% Plotting
fig, ax = plt.subplots(figsize=(10, 8))

# Plot backgrounds and boundaries
gpd.GeoSeries([ua_poly]).plot(ax=ax, facecolor='none', edgecolor='black', linewidth=2, linestyle='-.', label=labels[LANG]['ua'])
gpd.GeoSeries([zone_consolidated]).plot(ax=ax, facecolor='moccasin', edgecolor='orange', alpha=0.4, label=labels[LANG]['zone_2_3'])

# Plot buildings
exist_bldgs.plot(ax=ax, facecolor='dimgray', edgecolor='black', label=labels[LANG]['exist_bldg'])
new_bldg_gdf.plot(ax=ax, facecolor='crimson', edgecolor='darkred', hatch='//', label=labels[LANG]['new_bldg'])

# Plot roads
gpd.GeoSeries([existing_road]).plot(ax=ax, color='black', linewidth=4, label=labels[LANG]['exist_road'])
gpd.GeoSeries([colmatation_road]).plot(ax=ax, color='blue', linewidth=3, linestyle='--', label=labels[LANG]['new_road'])

# Styling
ax.set_title(labels[LANG]['title'], fontsize=14, fontweight='bold')
ax.set_xlabel(labels[LANG]['axis_x'])
ax.set_ylabel(labels[LANG]['axis_y'])

# Custom legend to handle different geometry types neatly
handles, legend_labels = ax.get_legend_handles_labels()
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2)

plt.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()
plt.savefig('../img/art35_4_5_6_a_LeySueloCan_2017.png', dpi=300)
plt.show()