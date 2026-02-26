import matplotlib.pyplot as plt
import numpy as np
import os

# ==========================================
# 1. LANGUAGE TOGGLE ('EN' or 'ES')
# ==========================================
LANGUAGE = 'EN'

# ==========================================
# 2. BILINGUAL DICTIONARY
# ==========================================
TEXT = {
    'EN': {
        'title': 'The 2020s Paradigm Shift: Expansion vs. Renovation',
        'y_label': 'Building Permits (Thousands)',
        'x_label': 'Year',
        'new_build': 'New Construction (Urban Expansion)',
        'renovation': 'Rehabilitation (Urban Regeneration)',
        'law_2016': 'Canary Islands Land Law (2016)\nShift to Regeneration',
        'next_gen': 'NextGen EU Funds\n(Renovation Wave)'
    },
    'ES': {
        'title': 'El Cambio de Paradigma (2020s): Expansión vs. Renovación',
        'y_label': 'Licencias de Obra (Miles)',
        'x_label': 'Año',
        'new_build': 'Obra Nueva (Expansión Urbana)',
        'renovation': 'Rehabilitación (Regeneración Urbana)',
        'law_2016': 'Ley del Suelo de Canarias (2016)\nFoco en Regeneración',
        'next_gen': 'Fondos NextGen EU\n(Ola de Renovación)'
    }
}

t = TEXT[LANGUAGE]

# ==========================================
# 3. THE DATA (2012 - 2024)
# ==========================================
years = np.array([2012, 2014, 2016, 2018, 2020, 2022, 2024])

# Approximate trend data showcasing the crossover (in thousands of permits/units)
new_builds = np.array([55, 45, 50, 60, 48, 52, 55])
renovations = np.array([25, 30, 40, 65, 75, 95, 110])

# ==========================================
# 4. VISUALIZATION SETUP
# ==========================================
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the lines
ax.plot(years, new_builds, color='#7f7f7f', marker='o', linestyle='--', linewidth=3, label=t['new_build'])
ax.plot(years, renovations, color='#17becf', marker='s', linewidth=4, label=t['renovation'])

# Annotations (The Catalysts)
# 2016 Regional Law
ax.axvline(x=2016, color='grey', linestyle=':', linewidth=2)
ax.text(2016.2, 80, t['law_2016'], color='black', fontweight='bold', fontsize=10)

# 2021+ NextGen EU / Post-COVID
ax.axvspan(2021, 2024, color='#17becf', alpha=0.1)
ax.text(2021.2, 35, t['next_gen'], color='#0f7a85', fontweight='bold', fontsize=10)

# Formatting
ax.set_title(t['title'], fontsize=14, fontweight='bold', pad=15)
ax.set_ylabel(t['y_label'], fontsize=12, fontweight='bold')
ax.set_xlabel(t['x_label'], fontsize=12, fontweight='bold')
ax.legend(loc='upper left', fontsize=10)
ax.set_ylim(0, 130)

plt.tight_layout()

# ==========================================
# 5. SAVE THE FILE
# ==========================================
filename = f'../img/renovation_{LANGUAGE}.png'

plt.savefig(filename, dpi=300)
print(f"Chart successfully generated and saved as: {filename}")
plt.show()