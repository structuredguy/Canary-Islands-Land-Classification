#%% Import libraries
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point

#%% Configuration & Bilingual Labels
LANG = 'ES' # Toggle EN/ES

labels = {
    'ES': {
        'title': 'Auditoría Art. 35: Delimitación Teórica de Asentamiento Rural',
        'buildings': 'Edificaciones (Catastro)',
        'core': 'Núcleo Principal (>= 10 viviendas)',
        'buffer': 'Buffer 200m (Apt. 2)',
        'isolated': 'Edificación Aislada Integrada',
        'axis_x': 'Longitud (UTM)',
        'axis_y': 'Latitud (UTM)'
    },
    'EN': {
        'title': 'Art. 35 Audit: Theoretical Rural Settlement Delimitation',
        'buildings': 'Buildings (Cadastre)',
        'core': 'Main Core (>= 10 homes)',
        'buffer': '200m Buffer (Sect. 2)',
        'isolated': 'Integrated Isolated Building',
        'axis_x': 'Longitude (UTM)',
        'axis_y': 'Latitude (UTM)'
    }
}

#%% Data Generation (Simulating Cadastral Footprints)
# En un caso real, descargaríamos esto vía WFS de la capa "Building" de INSPIRE Catastro
# Aquí simulamos un clúster central (núcleo) y edificaciones dispersas.
# Coordenadas proyectadas (ej. EPSG:32628 - UTM Huso 28N para Canarias) para medir en metros.

# 12 casas juntas (Cumple Apt. 1: >= 10 viviendas)
core_points = [Point(500 + i*15, 500 + j*15) for i in range(4) for j in range(3)]

# Casas aisladas
isolated_points = [
    Point(650, 550), # A 150m (Dentro del buffer)
    Point(750, 400), # A > 200m (Fuera del asentamiento)
    Point(350, 600)  # A 150m (Dentro del buffer)
]

all_buildings = gpd.GeoDataFrame(geometry=core_points + isolated_points, crs="EPSG:32628")

#%% Geoprocessing: The 200m Rule (Art 35.2)
# 1. Definir el núcleo
core_gdf = gpd.GeoDataFrame(geometry=core_points, crs="EPSG:32628")
core_hull = core_gdf.union_all().convex_hull # Envolvente convexa del núcleo

# 2. Aplicar el buffer de 200 metros al núcleo
# Esto traza la distancia máxima permitida para incorporar casas aisladas
buffer_200m = gpd.GeoDataFrame(geometry=[core_hull.buffer(200)], crs="EPSG:32628")

# 3. Evaluar qué casas aisladas entran en el asentamiento
isolated_gdf = gpd.GeoDataFrame(geometry=isolated_points, crs="EPSG:32628")
buildings_in_settlement = gpd.sjoin(isolated_gdf, buffer_200m, predicate='within')

#%% Plotting the Application of the Law
fig, ax = plt.subplots(figsize=(10, 8))

# Dibujar el Buffer (El área de influencia legal de 200m)
buffer_200m.plot(ax=ax, facecolor='lightgreen', edgecolor='green', alpha=0.3,
                 label=labels[LANG]['buffer'], linestyle='--')

# Dibujar la envolvente del núcleo
gpd.GeoSeries([core_hull]).plot(ax=ax, facecolor='none', edgecolor='blue', linewidth=2)

# Dibujar las casas
all_buildings.plot(ax=ax, color='gray', markersize=20, label=labels[LANG]['buildings'])
core_gdf.plot(ax=ax, color='blue', markersize=30, label=labels[LANG]['core'])
buildings_in_settlement.plot(ax=ax, color='red', markersize=30, label=labels[LANG]['isolated'])

ax.set_title(labels[LANG]['title'], fontsize=14, fontweight='bold')
ax.set_xlabel(labels[LANG]['axis_x'])
ax.set_ylabel(labels[LANG]['axis_y'])

# Leyenda manual para claridad
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label=labels[LANG]['core']),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label=labels[LANG]['isolated']),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=10, label='Excluido (>200m)'),
    Line2D([0], [0], color='green', lw=2, linestyle='--', label=labels[LANG]['buffer'])
]
ax.legend(handles=legend_elements, loc='upper right')

plt.grid(True, linestyle=':', alpha=0.6)
plt.axis('equal') # Mantener proporción de metros
plt.savefig('../img/art35_LeySueloCan_2017.png', dpi=300)
plt.show()