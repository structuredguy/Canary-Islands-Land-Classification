# %% Import libraries
import requests
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import box

# %% Configuration and Bilingual Setup
LANG = 'ES'  # Toggle 'EN' / 'ES'

labels = {
    'ES': {
        'title': 'Clasificación de Suelo (Ley 4/2017) - API Grafcan',
        'x_axis': 'Longitud (WGS84)',
        'y_axis': 'Latitud (WGS84)',
        'legend_title': 'Clase de Suelo',
        'annotation': 'Cauce Barranco',
        'error_msg': 'Error al conectar con Grafcan. Código de estado:'
    },
    'EN': {
        'title': 'Land Classification (Law 4/2017) - Grafcan API',
        'x_axis': 'Longitude (WGS84)',
        'y_axis': 'Latitude (WGS84)',
        'legend_title': 'Land Class',
        'annotation': 'Ravine Channel',
        'error_msg': 'Error connecting to Grafcan. Status code:'
    }
}

# %% Grafcan WFS API Request
# Endpoint oficial del servicio WFS de Planeamiento de IDECanarias
wfs_url = "https://idecan1.grafcan.es/ServicioWFS/Planeamiento"

# Bounding Box (BBOX) centrado en la zona baja del Barranco de Santos / Toscal
# Formato: min_lon, min_lat, max_lon, max_lat
bbox = "-16.255,28.460,-16.245,28.470"

# Parámetros para la petición WFS
# La capa 'planeamiento:clasificacion' contiene las clases de suelo vigentes
params = {
    "service": "WFS",
    "version": "2.0.0",
    "request": "GetFeature",
    "typeName": "planeamiento:clasificacion",
    "outputFormat": "application/json",
    "srsName": "EPSG:4326",  # Solicitamos WGS84 para visualización directa
    "bbox": f"{bbox},urn:ogc:def:crs:EPSG:4326"
}

print(f"Solicitando datos a Grafcan WFS para BBOX: {bbox}...")

try:
    response = requests.get(wfs_url, params=params)

    if response.status_code == 200:
        # Cargar el JSON directamente en GeoPandas
        gdf = gpd.read_file(response.text)
        print(f"Se han descargado {len(gdf)} polígonos de clasificación.")

        # Filtrar columnas útiles (Grafcan suele usar 'clase' o 'descripcion')
        # Aquí asumimos que la columna clave se llama 'clase_suelo' o similar
        # gdf.head() te permitirá ver la estructura exacta de atributos devuelta

    else:
        print(f"{labels[LANG]['error_msg']} {response.status_code}")
        gdf = None

except Exception as e:
    print(f"Excepción: {e}")
    gdf = None

# %% Plotting
if gdf is not None and not gdf.empty:
    fig, ax = plt.subplots(figsize=(12, 8))

    # Si la capa real de Grafcan usa un nombre de columna distinto para la clase,
    # cámbialo aquí (ej. 'CLASE', 'TIPO', 'CATEGORIA')
    columna_clase = 'clase' if 'clase' in gdf.columns else gdf.columns[0]

    # Dibujar el mapa
    gdf.plot(
        column=columna_clase,
        ax=ax,
        cmap='Set2',
        edgecolor='black',
        linewidth=0.5,
        legend=True,
        legend_kwds={'title': labels[LANG]['legend_title'], 'bbox_to_anchor': (1.05, 1), 'loc': 'upper left'}
    )

    # Anotación bilingüe señalando el área central
    center_x = -16.250
    center_y = 28.465
    ax.annotate(
        labels[LANG]['annotation'],
        xy=(center_x, center_y),
        xytext=(center_x + 0.002, center_y + 0.002),
        arrowprops=dict(facecolor='black', arrowstyle='->'),
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8)
    )

    # Configuración de ejes bilingüe
    ax.set_title(labels[LANG]['title'], fontsize=14, fontweight='bold')
    ax.set_xlabel(labels[LANG]['x_axis'])
    ax.set_ylabel(labels[LANG]['y_axis'])

    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()
else:
    print("No se generó el gráfico porque el GeoDataFrame está vacío o falló la conexión.")