#%% Import libraries
import pandas as pd
import os

#%% Configuration
# Generará el archivo Excel en tu Escritorio de Windows 11
desktop_path = os.path.join(os.path.join(os.environ['OneDriveCommercial']), "Desktop")
output_file = os.path.join(desktop_path, "Catastro_Data_Dictionary.xlsx")

#%% Data Definition (Bilingual EN/ES)
# Estructura del diccionario de datos extraída de la Sede Electrónica del Catastro
data = [
    {
        "Endpoint": "ConsultaProvincia",
        "Method": "GET/POST",
        "Inputs (ES / EN)": "Ninguno / None",
        "Required": "N/A",
        "Outputs (Keys)": "cuprov, cpine, p",
        "Description": "Listado de PROVINCIAS / List of PROVINCES."
    },
    {
        "Endpoint": "ConsultaMunicipio",
        "Method": "GET/POST",
        "Inputs (ES / EN)": "Provincia, Municipio",
        "Required": "Provincia",
        "Outputs (Keys)": "cumun, nm, carto, cd, cmc, cp, cm",
        "Description": "Listado de MUNICIPIOS de una provincia / List of MUNICIPALITIES in a province."
    },
    {
        "Endpoint": "ConsultaVia",
        "Method": "GET/POST",
        "Inputs (ES / EN)": "Provincia, Municipio, TipoVia, NomVia",
        "Required": "Provincia, Municipio",
        "Outputs (Keys)": "cuca, cv, tv, nv, cp, cm, ecine, esine, nucine, vine, sine, deine",
        "Description": "Listado de VÍAS de un municipio / List of STREETS in a municipality."
    },
    {
        "Endpoint": "ConsultaNumero",
        "Method": "GET/POST",
        "Inputs (ES / EN)": "Provincia, Municipio, TipoVia, NomVia, Numero",
        "Required": "Todos / All",
        "Outputs (Keys)": "cunum, pc1, pc2, pnp, plp",
        "Description": "Listado de NÚMEROS de una vía / List of NUMBERS in a street."
    },
    {
        "Endpoint": "ConsultaDNPLOC",
        "Method": "GET/POST",
        "Inputs (ES / EN)": "Provincia, Municipio, TipoVia, NomVia, Numero, Bloque, Escalera, Planta, Puerta",
        "Required": "Provincia, Municipio, TipoVia, NomVia, Numero",
        "Outputs (Keys)": "rc, dt, debi, finca, lcons, lspr",
        "Description": "Consulta de datos por localización / Data query by physical location."
    },
    {
        "Endpoint": "ConsultaDNPRC",
        "Method": "GET/POST",
        "Inputs (ES / EN)": "RefCat, Provincia, Municipio",
        "Required": "RefCat",
        "Outputs (Keys)": "rc, dt, debi, finca, lcons, lspr",
        "Description": "Consulta de datos por Referencia Catastral / Data query by Cadastral Reference."
    },
    {
        "Endpoint": "ConsultaRCCOOR",
        "Method": "GET/POST",
        "Inputs (ES / EN)": "SRS, Coordenada_X, Coordenada_Y",
        "Required": "Todos / All",
        "Outputs (Keys)": "pc1, pc2, geo (xcen, ycen, srs), ldt",
        "Description": "Referencia catastral por coordenadas / Cadastral reference by coordinates."
    }
]

#%% DataFrame Generation and Export
df_dictionary = pd.DataFrame(data)

try:
    # Escribe el archivo en formato Excel
    df_dictionary.to_excel(output_file, index=False, sheet_name="Catastro_Dictionary")
    print(f"Data Dictionary successfully saved to: {output_file}")
except Exception as e:
    print(f"Error saving file. Ensure 'openpyxl' is installed (pip install openpyxl). Error: {e}")