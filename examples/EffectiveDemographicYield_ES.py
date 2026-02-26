import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# %% Configuración de Idioma (Language Configuration)
# Choose 'en' for English or 'es' for Spanish
LANGUAGE = 'es'

# %% Traducciones (Translations)
texts = {
    'eras': {
        'en': ['1960s\n(Migration)', '2000s\n(Bubble)', '2010s\n(Stagnation)'],
        'es': ['Años 60\n(Migración)', 'Años 2000\n(Burbuja)', 'Años 2010\n(Estancamiento)']
    },
    'useful_housing_label': {'en': 'Useful Housing', 'es': 'Vivienda Útil'},
    'speculative_waste_label': {'en': 'Speculative Waste', 'es': 'Residuo Especulativo'},
    'housing_units_ylabel': {'en': 'Housing Units (Millions)', 'es': 'Unidades de Vivienda (Millones)'},
    'chart1_title': {'en': '1. The Social Bulk (Homes Built)', 'es': '1. El Volumen Social (Viviendas Construidas)'},
    'persons_per_household_label': {'en': 'Persons/Household', 'es': 'Personas/Hogar'},
    'land_paved_label': {'en': 'Paved (Urbanizable → Urbano)', 'es': 'Pavimentado (Urbanizable → Urbano)'},
    'land_zoned_empty_label': {'en': 'Zoned/Empty (Rústico → Urbanizable)', 'es': 'Zonificado/Vacío\n(Rústico → Urbanizable)'},
    'hectares_consumed_ylabel': {'en': 'Hectares Consumed', 'es': 'Hectáreas Consumidas'},
    'chart2_title': {'en': '2. The Physical Footprint (Land)', 'es': '2. La Huella Física (Suelo)'},
    'raw_density_label': {'en': 'Raw Density (Total Homes / Ha)', 'es': 'Densidad Bruta (Total Viviendas / Ha)'},
    'edy_score_label': {'en': 'EDY (Useful Homes / Ha)', 'es': 'RDU (Viviendas Útiles / Ha)'},
    'efficiency_score_ylabel': {'en': 'Efficiency Score (Homes per Hectare)', 'es': 'Puntuación de Eficiencia (Viviendas por Hectárea)'},
    'chart3_title': {'en': '3. The Resulting Efficiency', 'es': '3. La Eficiencia Resultante'},
}


# %% 1. The Enhanced Dataset
data = {
    'Era': texts['eras'][LANGUAGE],
    'Delta_Housing_Units': [2_900_000, 5_500_000, 450_000],
    'Delta_Population': [3_400_000, 5_800_000, 300_000],
    'Household_Size': [3.4, 2.7, 2.5],

    # Total Land is now split into the two Spanish legal phases:
    # 1. Paved (Urbanizable -> Urbano): Actually bulldozed and built.
    # 2. Zoned (Rústico -> Urbanizable): Legally reclassified for speculation, often sitting empty.
    'Land_Paved_Ha': [35_000, 70_000, 8_000],
    'Land_Zoned_Empty_Ha': [5_000, 50_000, 2_000]
}

df = pd.DataFrame(data)

# %% Calculations
df['Total_Land_Consumed'] = df['Land_Paved_Ha'] + df['Land_Zoned_Empty_Ha']
df['Real_Demand'] = df['Delta_Population'] / df['Household_Size']
df['Useful_Housing'] = df[['Delta_Housing_Units', 'Real_Demand']].min(axis=1)
df['Speculation_Waste'] = (df['Delta_Housing_Units'] - df['Useful_Housing']).clip(lower=0)

# The Ratios for Chart 3
df['EDY_Score'] = df['Useful_Housing'] / df['Total_Land_Consumed']
df['Raw_Density'] = df['Delta_Housing_Units'] / df['Total_Land_Consumed']

# %% 2. Visualization Setup (1 Row, 3 Columns)
plt.style.use('seaborn-v0_8-whitegrid')
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))

# --- CHART 1: The Social Bulk ---
eras = df['Era']
ax1.bar(eras, df['Useful_Housing'], label=texts['useful_housing_label'][LANGUAGE], color='#2ca02c')
ax1.bar(eras, df['Speculation_Waste'], bottom=df['Useful_Housing'], label=texts['speculative_waste_label'][LANGUAGE], color='#d62728',
        hatch='//')
ax1.set_ylabel(texts['housing_units_ylabel'][LANGUAGE], fontweight='bold')
ax1.set_title(texts['chart1_title'][LANGUAGE], fontsize=14, fontweight='bold')

ax1_twin = ax1.twinx()
ax1_twin.plot(eras, df['Household_Size'], color='black', marker='o', linewidth=2, label=texts['persons_per_household_label'][LANGUAGE])
ax1_twin.set_ylim(2.0, 4.0)

lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax1_twin.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', fontsize=9)

# --- CHART 2: The Physical Footprint (Stacked Land) ---
ax2.bar(eras, df['Land_Paved_Ha'], label=texts['land_paved_label'][LANGUAGE], color='#7f7f7f')
ax2.bar(eras, df['Land_Zoned_Empty_Ha'], bottom=df['Land_Paved_Ha'], label=texts['land_zoned_empty_label'][LANGUAGE],
        color='#bcbd22', hatch='..')
ax2.set_ylabel(texts['hectares_consumed_ylabel'][LANGUAGE], fontweight='bold')
ax2.set_title(texts['chart2_title'][LANGUAGE], fontsize=14, fontweight='bold')
ax2.legend(loc='upper left', fontsize=9)

# --- CHART 3: The Efficiency Ratios (Derived from 1 & 2) ---
ax3.plot(eras, df['Raw_Density'], color='#1f77b4', marker='s', linestyle='--', linewidth=3, markersize=8,
         label=texts['raw_density_label'][LANGUAGE])
ax3.plot(eras, df['EDY_Score'], color='#9467bd', marker='D', linestyle='-', linewidth=3, markersize=8,
         label=texts['edy_score_label'][LANGUAGE])
ax3.set_ylabel(texts['efficiency_score_ylabel'][LANGUAGE], fontweight='bold')
ax3.set_title(texts['chart3_title'][LANGUAGE], fontsize=14, fontweight='bold')
ax3.legend(loc='upper right', fontsize=9)

# %% Presentation Formatting
plt.tight_layout()
#plt.show()
# %%
plt.savefig('../img/EffectiveDemographicYield_ES.png')
