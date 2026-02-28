#%% Import libraries
import pandas as pd

#%% Configuración de visualización de Pandas
# Elimina el límite de columnas
pd.set_option('display.max_columns', None)
# Amplía el ancho virtual de la consola para evitar saltos de línea
pd.set_option('display.width', 1000)