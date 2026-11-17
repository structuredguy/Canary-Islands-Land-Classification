# %% Import libraries
import os

# %% Configuration
output_filename = "Art35_Asentamiento_Rural_Fixed.scr"

# %% GstarCAD Script Generation
# En los scripts CAD, un string vacío ("") genera un salto de línea limpio (un 'Enter' puro).
# El guion (-) antes de los comandos fuerza el modo consola y suprime diálogos.

lines = [
    "FILEDIA 0",  # Suprime cuadros de diálogo de archivos
    "CMDDIA 0",  # Suprime cuadros de diálogo de comandos

    # --- CREACIÓN DE CAPAS ---
    # Sintaxis: _-LAYER -> _Make -> Nombre -> _Color -> Número -> Enter(por defecto) -> Enter(salir)
    "_-LAYER", "_Make", "01_EXISTING_BUILDINGS", "_Color", "252", "", "",
    "_-LAYER", "_Make", "02_NEW_BUILDINGS_25PCT", "_Color", "30", "", "",
    "_-LAYER", "_Make", "03_EXISTING_ROADS", "_Color", "8", "", "",
    "_-LAYER", "_Make", "04_ALLOWED_ROADS", "_Color", "3", "", "",
    "_-LAYER", "_Make", "05_PROHIBITED_ROADS", "_Color", "1", "", "",
    "_-LAYER", "_Make", "06_TEXT_LABELS", "_Color", "7", "", "",

    # --- VIALES EXISTENTES ---
    "_-LAYER", "_Set", "03_EXISTING_ROADS", "",
    "_PLINE", "10,50", "20,52", "40,48", "60,55", "80,50", "90,48", "",
    "_PLINE", "40,48", "45,20", "",
    "_PLINE", "60,55", "65,80", "",

    # --- EDIFICACIONES EXISTENTES ---
    "_-LAYER", "_Set", "01_EXISTING_BUILDINGS", "",
    "_RECTANG", "10,55", "18,63",
    "_RECTANG", "30,55", "40,61",
    "_RECTANG", "50,60", "58,68",
    "_RECTANG", "70,52", "78,60",
    "_RECTANG", "30,25", "38,33",

    # --- NUEVAS EDIFICACIONES (Cumpliendo regla del 25%) ---
    "_-LAYER", "_Set", "02_NEW_BUILDINGS_25PCT", "",
    "_RECTANG", "50,35", "56,41",
    "_RECTANG", "70,65", "75,70",

    # --- VIALES PERMITIDOS (Conexión interior Art. 35.4) ---
    "_-LAYER", "_Set", "04_ALLOWED_ROADS", "",
    "_PLINE", "45,20", "60,55", "",

    # --- VIALES PROHIBIDOS (Apertura al exterior Art. 35.4) ---
    "_-LAYER", "_Set", "05_PROHIBITED_ROADS", "",
    "_PLINE", "80,50", "90,80", "",

    # --- ETIQUETAS DE TEXTO ---
    "_-LAYER", "_Set", "06_TEXT_LABELS", "",
    "_TEXT", "10,65", "2", "0", "Edificacion Existente / Existing Building",
    "_TEXT", "50,43", "2", "0", "Crecimiento (Max 25%) / New Growth",
    "_TEXT", "50,25", "2", "45", "Vial Permitido / Allowed Road",
    "_TEXT", "82,65", "2", "70", "Vial Prohibido / Prohibited Road",

    # --- RESTAURAR VARIABLES Y ENCUADRE ---
    "FILEDIA 1",
    "CMDDIA 1",
    "_ZOOM", "_EXTENTS"
]

# Unimos la lista con saltos de línea.
# Añadimos un salto al final (\n) para asegurar que el último comando (ZOOM) se ejecute.
scr_content = "\n".join(lines) + "\n"

# %% File Export
try:
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(scr_content)
    print(f"Éxito. Script regenerado correctamente en: {os.path.abspath(output_filename)}")
except Exception as e:
    print(f"Error guardando el script: {e}")