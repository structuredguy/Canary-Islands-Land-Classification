#%%
import requests
import json
from urllib.parse import urljoin

class CatastroAPI:
    def __init__(self):
        # Base URLs for the two main services described in the document
        # [cite: 730] Service for Address and Data
        self.base_url_callejero = "http://ovc.catastro.meh.es/OVCServWeb/OVCWcfCallejero/COVCCallejero.svc/json/"
        # [cite: 757] Service for Coordinates
        self.base_url_coords = "http://ovc.catastro.meh.es/OVCServWeb/OVCWcfCallejero/COVCCoordenadas.svc/json/"

    def _get(self, base_url, endpoint, params):
        """Helper to make the request and return JSON."""
        url = urljoin(base_url, endpoint)
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Connection error: {str(e)}"}

    def get_data_by_refcat(self, ref_cat):
        """
        2.1.6 Consulta de DATOS CATASTRALES por Referencia Catastral [cite: 540]
        Endpoint: Consulta_DNPRC [cite: 737, 801]
        """
        params = {
            "RefCat": ref_cat, # [cite: 552] 14 or 20 characters
            "Provincia": "",   # Optional
            "Municipio": ""    # Optional
        }
        # Note: The document example uses 'Consulta_DNPRC' [cite: 801]
        return self._get(self.base_url_callejero, "Consulta_DNPRC", params)

    def get_data_by_address(self, prov, muni, sigla, calle, num):
        """
        2.1.5 Consulta de DATOS CATASTRALES por Localización [cite: 207]
        Endpoint: Consulta_DNPLOC [cite: 736]
        """
        params = {
            "Provincia": prov,   # [cite: 229]
            "Municipio": muni,   # [cite: 230]
            "Sigla": sigla,      #  Type of way (e.g., CL, AV, PZ) - See Anexo II
            "Calle": calle,      # [cite: 232]
            "Numero": num,       # [cite: 233]
            # Optional blocks [cite: 235-238]
            "Bloque": "",
            "Escalera": "",
            "Planta": "",
            "Puerta": ""
        }
        return self._get(self.base_url_callejero, "Consulta_DNPLOC", params)

    def get_ref_by_coordinates(self, lat, lon, srs="EPSG:4326"):
        """
        2.2.1 Localización de referencia catastral por coordenadas [cite: 582]
        Endpoint: Consulta_RCCOOR [cite: 758]
        """
        params = {
            "SRS": srs,             # [cite: 586] EPSG:4326 is WGS84 (Google Maps standard)
            "Coordenada_X": lon,    #  Longitude for Geo SRS
            "Coordenada_Y": lat     #  Latitude for Geo SRS
        }
        return self._get(self.base_url_coords, "Consulta_RCCOOR", params)

#%% --- Execution Examples ---

api = CatastroAPI()

#%% --- 1. Query by Cadastral Reference (RefCat)
print("--- 1. Query by Cadastral Reference (RefCat) ---")
# Example RefCat from Document [cite: 807]
ref_cat = "2749704YJ0624N0001DI"
data_ref = api.get_data_by_refcat(ref_cat)
# Parsing the obscure keys (Keys like 'pc1', 'pc2' are defined in schema [cite: 274])
print(json.dumps(data_ref, indent=2))

#%% --- 2. Query by Address (Santa Cruz example)
print("\n--- 2. Query by Address (Santa Cruz example) ---")
# Using the address logic discussed previously
# Sigla 'CL' = Calle
data_addr = api.get_data_by_address(
    prov="SANTA CRUZ DE TENERIFE",
    muni="SANTA CRUZ DE TENERIFE",
    sigla="CL",
    calle="CASTILLO",
    num="10"
)
print(json.dumps(data_addr, indent=2))

#%% --- 3. Reverse Geocoding (Lat/Lon -> RefCat)
print("\n--- 3. Reverse Geocoding (Lat/Lon -> RefCat) ---")
# Coords for El Toscal area approximately
lat, lon = 28.469, -16.254
data_geo = api.get_ref_by_coordinates(lat, lon)
print(json.dumps(data_geo, indent=2))