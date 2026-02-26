import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. The Enhanced Dataset
data = {
    'Era': ['1960s\n(Migration)', '2000s\n(Bubble)', '2010s\n(Stagnation)'],
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

# Calculations
df['Total_Land_Consumed'] = df['Land_Paved_Ha'] + df['Land_Zoned_Empty_Ha']
df['Real_Demand'] = df['Delta_Population'] / df['Household_Size']
df['Useful_Housing'] = df[['Delta_Housing_Units', 'Real_Demand']].min(axis=1)
df['Speculation_Waste'] = (df['Delta_Housing_Units'] - df['Useful_Housing']).clip(lower=0)

# The Ratios for Chart 3
df['EDY_Score'] = df['Useful_Housing'] / df['Total_Land_Consumed']
df['Raw_Density'] = df['Delta_Housing_Units'] / df['Total_Land_Consumed']

# 2. Visualization Setup (1 Row, 3 Columns)
plt.style.use('seaborn-v0_8-whitegrid')
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))

# --- CHART 1: The Social Bulk ---
eras = df['Era']
ax1.bar(eras, df['Useful_Housing'], label='Useful Housing', color='#2ca02c')
ax1.bar(eras, df['Speculation_Waste'], bottom=df['Useful_Housing'], label='Speculative Waste', color='#d62728',
        hatch='//')
ax1.set_ylabel('Housing Units (Millions)', fontweight='bold')
ax1.set_title('1. The Social Bulk (Homes Built)', fontsize=14, fontweight='bold')

ax1_twin = ax1.twinx()
ax1_twin.plot(eras, df['Household_Size'], color='black', marker='o', linewidth=2, label='Persons/Household')
ax1_twin.set_ylim(2.0, 4.0)

lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax1_twin.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', fontsize=9)

# --- CHART 2: The Physical Footprint (Stacked Land) ---
ax2.bar(eras, df['Land_Paved_Ha'], label='Paved (Urbanizable → Urbano)', color='#7f7f7f')
ax2.bar(eras, df['Land_Zoned_Empty_Ha'], bottom=df['Land_Paved_Ha'], label='Zoned/Empty (Rústico → Urbanizable)',
        color='#bcbd22', hatch='..')
ax2.set_ylabel('Hectares Consumed', fontweight='bold')
ax2.set_title('2. The Physical Footprint (Land)', fontsize=14, fontweight='bold')
ax2.legend(loc='upper left', fontsize=9)

# --- CHART 3: The Efficiency Ratios (Derived from 1 & 2) ---
ax3.plot(eras, df['Raw_Density'], color='#1f77b4', marker='s', linestyle='--', linewidth=3, markersize=8,
         label='Raw Density (Total Homes / Ha)')
ax3.plot(eras, df['EDY_Score'], color='#9467bd', marker='D', linestyle='-', linewidth=3, markersize=8,
         label='EDY (Useful Homes / Ha)')
ax3.set_ylabel('Efficiency Score (Homes per Hectare)', fontweight='bold')
ax3.set_title('3. The Resulting Efficiency', fontsize=14, fontweight='bold')
ax3.legend(loc='upper right', fontsize=9)

# Presentation Formatting
plt.tight_layout()
# plt.show()

# 3. Save the File
plt.savefig('../img/EffectiveDemographicYield_EN.png')

