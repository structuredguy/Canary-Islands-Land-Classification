# %% Import libraries
import requests
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt

# %% Configuration
LANG = 'ES'  # Switch to 'EN' for English

labels = {
    'ES': {
        'title': 'Planeamiento Vigente - Grafcan (WMS)',
        'x_axis': 'Longitud (WGS84)',
        'y_axis': 'Latitud (WGS84)',
        'loading': 'Solicitando imagen a Grafcan WMS...',
        'error': 'Error al conectar con Grafcan WMS. Código:',
        'xml_warn': 'El servidor devolvió un XML en lugar de imagen. Revisa las capas en GetCapabilities.'
    },
    'EN': {
        'title': 'Current Planning - Grafcan (WMS)',
        'x_axis': 'Longitude (WGS84)',
        'y_axis': 'Latitude (WGS84)',
        'loading': 'Requesting image from Grafcan WMS...',
        'error': 'Error connecting to Grafcan WMS. Code:',
        'xml_warn': 'Server returned XML instead of image. Check layers in GetCapabilities.'
    }
}

# %% Grafcan WMS API Request
# Endpoint oficial de WMS para Planeamiento (Fíjate que es idecan2 y ServicioWMS)
wms_url = "https://idecan2.grafcan.es/ServicioWMS/Planeamiento"

# Bounding Box (BBOX) centrado en la zona baja del Barranco de Santos
bbox_str = "-16.255,28.460,-16.245,28.470"

# Parámetros estándar WMS 1.1.1
params = {
    "SERVICE": "WMS",
    "VERSION": "1.1.1",
    "REQUEST": "GetMap",
    "LAYERS": "Planeamiento",  # Capa raíz del servicio
    "STYLES": "",
    "BBOX": bbox_str,
    "SRS": "EPSG:4326",
    "WIDTH": "1200",
    "HEIGHT": "800",
    "FORMAT": "image/png",
    "TRANSPARENT": "true"
}

print(labels[LANG]['loading'])

try:
    response = requests.get(wms_url, params=params)

    if response.status_code == 200:
        # Validar que el WMS devolvió una imagen y no un error XML camuflado
        if 'image' in response.headers.get('Content-Type', ''):
            img = Image.open(BytesIO(response.content))

            # %% Plotting
            fig, ax = plt.subplots(figsize=(12, 8))

            # Para matplotlib.imshow, extent es [xmin, xmax, ymin, ymax]
            min_x, min_y, max_x, max_y = map(float, bbox_str.split(','))

            ax.imshow(img, extent=[min_x, max_x, min_y, max_y])

            ax.set_title(labels[LANG]['title'], fontsize=14, fontweight='bold')
            ax.set_xlabel(labels[LANG]['x_axis'])
            ax.set_ylabel(labels[LANG]['y_axis'])

            plt.grid(True, linestyle='--', alpha=0.4, color='white')
            plt.tight_layout()
            plt.show()
        else:
            print(labels[LANG]['xml_warn'])
            print(response.text[:500])  # Muestra el inicio del error XML
    else:
        print(f"{labels[LANG]['error']} {response.status_code}")

except Exception as e:
    print(f"Excepción de conexión: {e}")