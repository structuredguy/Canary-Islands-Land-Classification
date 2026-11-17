#%% Import libraries
import duckdb
import json
import pandas as pd
from pprint import pprint
import os
print(os.getcwd())
#%% Configuration
LANG = 'ES' # Toggle 'EN' / 'ES'

labels = {
    'ES': {
        'main_title': '--- DATOS GENERALES DEL INMUEBLE ---',
        'units_title': '--- UNIDADES CONSTRUCTIVAS (Aplanadas con DuckDB) ---'
    },
    'EN': {
        'main_title': '--- GENERAL REAL ESTATE DATA ---',
        'units_title': '--- CONSTRUCTION UNITS (Flattened with DuckDB) ---'
    }
}

#%% Data Input
# Your JSON payload
json_payload = """
{
  "consulta_dnprcResult": {
    "control": { "cudnp": 1, "cucons": 3 },
    "bico": {
      "bi": {
        "idbi": { "cn": "UR", "rc": { "pc1": "2749704", "pc2": "YJ0624N", "car": "0001", "cc1": "D", "cc2": "I" } },
        "dt": { "np": "VALENCIA", "nm": "GODELLETA", "locs": { "lous": { "lourb": { "dir": { "cv": "57", "tv": "CL", "nv": "GUAYANA-MOJONERA", "pnp": "3" }, "dp": "46388" } } } },
        "ldt": "CL GUAYANA-MOJONERA 3 46388 GODELLETA (VALENCIA)",
        "debi": { "luso": "Residencial", "sfc": "94", "cpt": "100,000000", "ant": "1976" }
      },
      "finca": {
        "ldt": "CL GUAYANA-MOJONERA 3  GODELLETA (VALENCIA)",
        "ltp": "Parcela construida sin división horizontal",
        "dff": { "ss": "839" },
        "infgraf": { "igraf": "https://www1.sedecatastro.gob.es/Cartografia/mapa.aspx?del=46&mun=138&refcat=2749704YJ0624N" }
      },
      "lcons": [
        { "lcd": "VIVIENDA", "dt": { "lourb": { "loint": { "es": "1", "pt": "00", "pu": "00" } } }, "dfcons": { "stl": "58" }, "dvcons": { "dtip": "VIVIENDA UNIFAMILIAR" } },
        { "lcd": "ALMACEN", "dt": { "lourb": { "loint": { "es": "1", "pt": "00" } } }, "dfcons": { "stl": "19" }, "dvcons": { "dtip": "ANEJOS DE VIVIENDA Y LOCALES EN ESTRUCTURA" } },
        { "lcd": "APARCAMIENTO", "dt": { "lourb": { "loint": { "es": "1", "pt": "00" } } }, "dfcons": { "stl": "17" }, "dvcons": { "dtip": "ANEJOS DE VIVIENDA Y LOCALES EN ESTRUCTURA" } }
      ]
    }
  }
}
"""

# Write to a temporary file for DuckDB to ingest
temp_file = os.path.join('output', 'temp_catastro.json')
with open(temp_file, 'w', encoding='utf-8') as f:
    f.write(json_payload)

#%% Conexión a archivo físico
import duckdb

# En lugar de ':memory:', define una ruta local
db_path = r"db/catastro_local.duckdb"
con = duckdb.connect(db_path)

# Cuando el script termine, el archivo catastro_local.duckdb quedará en tu disco.
#%% 1. Extraer datos generales (Sin desenrollar arrays)
query_general = f"""
SELECT 
    consulta_dnprcResult.bico.bi.idbi.rc.pc1 || consulta_dnprcResult.bico.bi.idbi.rc.pc2 AS RefCat,
    consulta_dnprcResult.bico.bi.ldt AS Address,
    consulta_dnprcResult.bico.bi.debi.luso AS Main_Use,
    consulta_dnprcResult.bico.bi.debi.ant AS Year_Built,
    consulta_dnprcResult.bico.finca.dff.ss AS Plot_Surface_m2
FROM read_json_auto('{temp_file}');
"""
print(query_general)
df_general = con.execute(query_general).df()
print(df_general)
#%% 2. Desenrollar (UNNEST) el array de unidades constructivas (lcons)
# Esto es donde DuckDB brilla, convirtiendo el JSON anidado en filas
query_units = f"""
WITH unnested_data AS (
    SELECT UNNEST(consulta_dnprcResult.bico.lcons) AS unit
    FROM read_json_auto('{temp_file}')
)
SELECT 
    unit.lcd AS Constructive_Use,
    unit.dfcons.stl AS Surface_m2,
    unit.dvcons.dtip AS Typology,
    unit.dt.lourb.loint.es AS Stair,
    unit.dt.lourb.loint.pt AS Floor
FROM unnested_data;
"""
print(query_units)
df_units = con.execute(query_units).df()

#%% Output Results
print(f"\n{labels[LANG]['main_title']}")
print(df_general.to_string(index=False))

print(f"\n{labels[LANG]['units_title']}")
print(df_units.to_string(index=False))

# Clean up
os.remove(temp_file)