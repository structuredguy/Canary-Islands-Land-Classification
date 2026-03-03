#%% Import libraries
import os

#%% Configuration
# Defines the output file for GstarCAD
output_filename = "../scr/Art35_Asentamiento_Rural.scr"

#%% GstarCAD Script Generation
# We use standard AutoCAD/GstarCAD command line syntax.
# Underscores (_) ensure the commands work regardless of the GstarCAD language version.

scr_content = """
_LAYER _MAKE "01_EXISTING_BUILDINGS" _COLOR 252 ""
_LAYER _MAKE "02_NEW_BUILDINGS_25PCT" _COLOR 30 "" 
_LAYER _MAKE "03_EXISTING_ROADS" _COLOR 8 ""
_LAYER _MAKE "04_ALLOWED_ROADS" _COLOR 3 ""
_LAYER _MAKE "05_PROHIBITED_ROADS" _COLOR 1 ""
_LAYER _MAKE "06_TEXT_LABELS" _COLOR 7 ""

; --- EXISTING ROADS (Irregular rural paths) ---
_CLAYER "03_EXISTING_ROADS"
_PLINE 10,50 20,52 40,48 60,55 80,50 90,48 ""
_PLINE 40,48 45,20 ""
_PLINE 60,55 65,80 ""

; --- EXISTING BUILDINGS (Base area for calculating the 25%) ---
_CLAYER "01_EXISTING_BUILDINGS"
_RECTANG 10,55 18,63
_RECTANG 30,55 40,61
_RECTANG 50,60 58,68
_RECTANG 70,52 78,60
_RECTANG 30,25 38,33

; --- NEW BUILDINGS (Max 25% growth, completely clear of roads) ---
_CLAYER "02_NEW_BUILDINGS_25PCT"
_RECTANG 50,35 56,41
_RECTANG 70,65 75,70

; --- ALLOWED ROADS (Internal connection - Art 35.4) ---
_CLAYER "04_ALLOWED_ROADS"
_PLINE 45,20 60,55 ""

; --- PROHIBITED ROADS (Opening new outward roads - Art 35.4) ---
_CLAYER "05_PROHIBITED_ROADS"
_PLINE 80,50 90,80 ""

; --- BILINGUAL TEXT LABELS ---
_CLAYER "06_TEXT_LABELS"
_TEXT 10,65 2 0 "Edificacion Existente / Existing Building"
_TEXT 50,43 2 0 "Crecimiento (Max 25%) / New Growth"
_TEXT 50,25 2 45 "Vial Permitido / Allowed Road"
_TEXT 82,65 2 70 "Vial Prohibido / Prohibited Road"

; --- VIEWPORT ADJUSTMENT ---
_ZOOM _EXTENTS
"""

#%% File Export
try:
    with open(output_filename, "w") as f:
        # We strip leading/trailing whitespace to avoid command line errors in CAD
        f.write(scr_content.strip())
    print(f"Success! The GstarCAD script has been saved to: {os.path.abspath(output_filename)}")
    print("To run it: Type 'SCRIPT' in GstarCAD and select this file.")
except Exception as e:
    print(f"Error saving script: {e}")