# %% setup
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1. Data Construction (Approximated from Historical INE Data)
years = np.arange(1960, 2025)

# Synthetic Data Patterns
# Housing Starts: Boom in 70s, Crash in 80s, Massive Boom in 00s, Crash in 10s
housing_starts = np.interp(years,
    [1960, 1974, 1985, 1993, 2006, 2013, 2024],
    [100, 400, 200, 250, 850, 50, 120]) * 1000

# Household Formation (Need): Smoother, linked to migration flows
household_formation = np.interp(years,
    [1960, 1974, 1995, 2005, 2015, 2024],
    [150, 300, 250, 450, 100, 180]) * 1000

# 2. Plotting
fig, ax = plt.subplots(figsize=(14, 8))

# Plot the "Need" vs "Greed"
ax.fill_between(years, household_formation, color='green', alpha=0.3, label='Demanda Real (Formacion de Nuevos Hogares)')
ax.plot(years, housing_starts, color='black', linewidth=2, label='Nuevas Construcciones')

# Highlight the "Speculation Gaps" (Where Construction > Need)
ax.fill_between(years, household_formation, housing_starts, where=(housing_starts > household_formation),
                color='red', alpha=0.3, interpolate=True, label='Exceso Especulativo')

#%% 3.a Add the Legal Milestones
milestones = {
    1956: "Ley de 1956\n(Rigida)",
    1976: "Texto de 1976 Refundido\n(Consolidaciòn)",

    1992: "Texto Refundido 1992\n(Poder Central)",
    1997: "STC 61/1997\n(Poder Regional)",
    1998: "1998 Law\n(Liberalizaciòn)",
    2008: "2008 Law\n(Sustainabilidad)"
}

for year, text in milestones.items():
    plt.axvline(x=year, color='red', linestyle='--', alpha=0.6)
    plt.text(year + 0.5, 1E5 + (800000-2E5)/(2010-1960)*(year-1960) , text, color='red', fontsize=9, fontweight='bold',
             ha='right' if year in [1992,1997] else 'left')

#%% 3.b Add the other Milestones
milestones_other = {
    1973: "Crisis del Petròleo (OPEC)",
    1986: "Entrada en la UE\n(Confianza)",
}

for year, text in milestones_other.items():
    plt.axvline(x=year, color='blue', linestyle='--', alpha=0.6)
    plt.text(year + 0.5, 2E5 + (800000-2E5)/(2024-1960)*(year-1960) , text, color='blue', fontsize=9,
             ha='right' if year in [1992,1997] else 'right')

#%% 4. Contextual Bands
plt.axvspan(1998, 2002, ymin=0, ymax=0.1, color='orange', alpha=0.5)
plt.text(2000, 50000, "Lavado\nPeseta", color='darkorange', fontweight='bold', ha='center' )

plt.title('Leyes del Suelo en Espana: Eficacia frente a Realidad (1960-2024)', fontsize=16)
plt.ylabel('Unidades / Hogares')
plt.legend(loc='upper left')
plt.grid(True, alpha=0.3)

plt.tight_layout()
# plt.show()
plt.savefig('../img/performance_gap_ES.png')