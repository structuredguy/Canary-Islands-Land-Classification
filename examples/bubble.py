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
        'title': 'The 2000s Bubble: Housing Starts vs. Demographic Need',
        'y_label': 'Housing Units (Thousands)',
        'x_label': 'Year',
        'starts': 'Housing Starts (Concrete Poured)',
        'demand': 'Real Demographic Demand (New Households)',
        'waste': 'Speculative Waste (The Bubble)',
        'law_1998': '1998 Land Law\n"Todo Urbanizable"',
        'euro': 'Euro Adoption\n(Cheap Credit)'
    },
    'ES': {
        'title': 'La Burbuja de los 2000: Viviendas Iniciadas vs. Necesidad Demográfica',
        'y_label': 'Unidades de Vivienda (Miles)',
        'x_label': 'Año',
        'starts': 'Viviendas Iniciadas (Ladrillo Puesto)',
        'demand': 'Demanda Demográfica Real (Nuevos Hogares)',
        'waste': 'Desperdicio Especulativo (La Burbuja)',
        'law_1998': 'Ley del Suelo 1998\n"Todo Urbanizable"',
        'euro': 'Adopción del Euro\n(Crédito Barato)'
    }
}

t = TEXT[LANGUAGE]

# ==========================================
# 3. THE DATA (1996 - 2010)
# ==========================================
years = np.array([1996, 1998, 2000, 2002, 2004, 2006, 2008, 2010])

# Approximate historical data for Spain (in thousands)
housing_starts = np.array([300, 450, 550, 600, 700, 850, 350, 100])
real_demand = np.array([250, 280, 320, 350, 380, 400, 300, 150])

# ==========================================
# 4. VISUALIZATION SETUP
# ==========================================
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the lines
ax.plot(years, housing_starts, color='#d62728', marker='o', linewidth=3, label=t['starts'])
ax.plot(years, real_demand, color='#2ca02c', marker='s', linestyle='--', linewidth=3, label=t['demand'])

# Fill the "Speculative Waste" gap
ax.fill_between(years, real_demand, housing_starts, where=(housing_starts > real_demand),
                interpolate=True, color='#d62728', alpha=0.2, label=t['waste'])

# Annotations (The Catalysts)
# 1998 Law
ax.axvline(x=1998, color='grey', linestyle=':', linewidth=2)
ax.text(1998.2, 750, t['law_1998'], color='black', fontweight='bold', fontsize=10)

# 2002 Euro
ax.axvline(x=2002, color='blue', linestyle=':', linewidth=2, alpha=0.5)
ax.text(2002.2, 200, t['euro'], color='blue', fontweight='bold', fontsize=10)

# Formatting
ax.set_title(t['title'], fontsize=14, fontweight='bold', pad=15)
ax.set_ylabel(t['y_label'], fontsize=12, fontweight='bold')
ax.set_xlabel(t['x_label'], fontsize=12, fontweight='bold')
ax.legend(loc='upper left', fontsize=10)
ax.set_ylim(0, 950)

plt.tight_layout()

# ==========================================
# 5. SAVE THE FILE
# ==========================================
# Ensures it saves with the correct language suffix
filename = f'../img/bubble_{LANGUAGE}.png'

# Optional: ensure it saves directly to your img folder if you run it from the script's directory
# output_dir = '../img'
# os.makedirs(output_dir, exist_ok=True)
# filepath = os.path.join(output_dir, filename)

plt.savefig(filename, dpi=300)
print(f"Chart successfully generated and saved as: {filename}")
plt.show()