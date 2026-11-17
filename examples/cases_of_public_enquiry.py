# %% [markdown]
# ### Visualización de Reclamaciones de Información Pública en Canarias (2015-2024)
# Este script genera un gráfico de barras bilingüe comparando el uso del derecho
# de información bajo el marco del D.L. 1/2000 y la actual Ley 4/2017.

# %%
import matplotlib.pyplot as plt
import numpy as np

# Toggle Language: 'ES' or 'EN'
LANG = 'ES'

# Data from the Comisionado de Transparencia de Canarias Reports (Approx/Verified)
years = np.array([2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024])
claims = np.array([18, 91, 154, 357, 244, 386, 525, 577, 644, 773])

# Labels and Text
if LANG == 'ES':
    title = 'Evolución de Reclamaciones al Comisionado de Transparencia'
    xlabel = 'Año'
    ylabel = 'Número de Reclamaciones'
    law_old = 'Vigencia D.L. 1/2000'
    law_new = 'Vigencia Ley 4/2017'
    source = 'Fuente: Informes Anuales del Comisionado de Transparencia de Canarias (2015-2024)'
    transition_label = 'Entrada en vigor Ley 4/2017'
else:
    title = 'Evolution of Claims to the Transparency Commissioner'
    xlabel = 'Year'
    ylabel = 'Number of Claims'
    law_old = 'D.L. 1/2000 Effective'
    law_new = 'Law 4/2017 Effective'
    source = 'Source: Annual Reports of the Canary Islands Transparency Commissioner (2015-2024)'
    transition_label = 'Enactment of Law 4/2017'

# Plotting
plt.figure(figsize=(12, 7))
bars = plt.bar(years, claims, color='skyblue', edgecolor='navy', alpha=0.8, label=ylabel)

# Highlighting the two law domains
plt.axvspan(2014.5, 2017.5, color='gray', alpha=0.15, label=law_old)
plt.axvspan(2017.5, 2024.5, color='green', alpha=0.1, label=law_new)

# Marker for Law 4/2017 Transition (July 2017)
plt.axvline(x=2017.5, color='red', linestyle='--', linewidth=2)
plt.text(2017.6, max(claims)*0.9, transition_label, color='red', fontweight='bold', rotation=0)

# Aesthetics
plt.title(title, fontsize=14, fontweight='bold')
plt.xlabel(xlabel, fontsize=12)
plt.ylabel(ylabel, fontsize=12)
plt.xticks(years)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Adding values on top of bars
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 10, int(yval), ha='center', va='bottom', fontsize=10)

# Source Text Box
plt.text(2014.5, -max(claims)*0.15, source, fontsize=9, style='italic',
         bbox={'facecolor': 'white', 'alpha': 0.5, 'pad': 5})

plt.legend(loc='upper left')
plt.tight_layout()

# Save as Image
plt.savefig(f'../img/cases_of_public_enquiry_{LANG}.png', dpi=300)
plt.show()