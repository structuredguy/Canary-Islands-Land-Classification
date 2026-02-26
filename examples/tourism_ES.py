import matplotlib.pyplot as plt
import numpy as np

# 1. Historical Data (Approximate UNWTO International Tourist Arrivals in Millions)
decades = [1960, 1970, 1980, 1990, 2000, 2010]

# Italy: Steady, mature growth. Already massive in the 60s.
italy_tourists = [18, 30, 38, 43, 41, 43]

# Spain: The "Apertura" catch-up, then massive acceleration in the 80s/90s
spain_tourists = [6, 24, 38, 52, 47, 52]

# 2. Visualization Setup
plt.figure(figsize=(10, 6))
plt.style.use('seaborn-v0_8-whitegrid')

# Plot the lines
plt.plot(decades, spain_tourists, color='red', marker='o', linewidth=3, markersize=8, label='España (La "Apertura" puesta al día)')
plt.plot(decades, italy_tourists, color='blue', marker='s', linestyle='--', linewidth=3, markersize=8, label='Italia (mercado maduro)')

# Annotations for Historical Context
plt.axvline(x=1962, color='grey', linestyle=':', alpha=0.7)
plt.text(1963, 9, '1963: "España es Diferente" -- Fraga (se permiten Bikinis)', fontsize=9)

plt.axvline(x=1998, color='green', linestyle='-', alpha=0.5, linewidth=4)
plt.text(1999, 20, '1998 Ley del Suelo\n(Comienza la Burbuja\nUrbanística)', color='darkgreen', fontweight='bold')

plt.title('Llegadas de Turistas Internacionales: España frente a Italia (1960 - 2010)', fontsize=14, fontweight='bold')
plt.ylabel('Millions of Tourist Arrivals', fontsize=12, fontweight='bold')
plt.xlabel('Año', fontsize=12)
plt.legend(loc='upper left', fontsize=11)
plt.grid(True, alpha=0.3)

# plt.show()

# %%
plt.savefig('../img/tourism.png')