# %% Import libraries
import requests
import xml.etree.ElementTree as ET

# %% Function to fetch basic data
def get_catastro_data(ref):
    url = f"https://ovc.catastro.meh.es/OVCServWeb/OVCWcfCallejero/COVCCallejero.svc/json/Consulta_DNPRC?RefCat={ref}"
    print(url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return f"Error: {e}"


def parse_catastro_response(data):
    """Parse JSON response from Catastro API and extract land classification data."""
    if not data or 'consulta_dnprcResult' not in data:
        return None

    result = data['consulta_dnprcResult']

    # Extract basic information
    bi = result.get('bico', {}).get('bi', {})
    idbi = bi.get('idbi', {})
    dt = bi.get('dt', {})
    finca = result.get('bico', {}).get('finca', {})

    parsed = {
        'reference': {
            'country': idbi.get('cn'),
            'cadastral_ref': idbi.get('rc', {}),
        },
        'location': {
            'province': dt.get('np'),
            'municipality': dt.get('nm'),
            'address': bi.get('ldt'),
        },
        'plot': {
            'full_address': finca.get('ldt'),
            'surface': finca.get('dff', {}).get('ss'),
            'map_url': finca.get('infgraf', {}).get('igraf'),
        },
        'land_uses': []
    }

    # Extract land use classifications
    lspr = result.get('bico', {}).get('lspr', [])
    for subparcel in lspr:
        dspr = subparcel.get('dspr', {})
        parsed['land_uses'].append({
            'code': subparcel.get('cspr'),
            'class_code': dspr.get('ccc'),
            'description': dspr.get('dcc'),
            'surface': dspr.get('ssp'),
            'intensity': dspr.get('ip'),
        })

    return parsed


# %% Execution
if __name__ == "__main__":
    # %% Configuration
    from dotenv import load_dotenv
    from pprint import pprint
    import os

    load_dotenv()  # This line does what the plugin cannot do at runtime
    REF_CATASTRAL = os.getenv('REF_CATASTRAL')

    if not REF_CATASTRAL:
        raise ValueError("REF_CATASTRAL environment variable must be set")
    print(REF_CATASTRAL)
    #%% Ejemplo: Referencia catastral de un inmueble en Santa Cruz (El Toscal)
    # (Sustituye por una real de tu zona de estudio)
    LANG = 'ES'
    ref = REF_CATASTRAL
    data = get_catastro_data(REF_CATASTRAL)

    if data:
        parsed_data = parse_catastro_response(data)
        print("\n=== Raw Response ===")
        pprint(data)
        print("\n=== Parsed Data ===")
        pprint(parsed_data)

        if parsed_data:
            labels = {
                'ES': f"Datos para {REF_CATASTRAL}",
                'EN': f"Data for {REF_CATASTRAL}"
            }
            print(f"\n{labels[LANG]}")
    else:
        print("No encontrado" if LANG == 'ES' else "Not found")