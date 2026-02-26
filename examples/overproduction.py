import numpy as np
import matplotlib.pyplot as plt

# 1. Setup the scenario
land_consumed = np.linspace(1, 200, 200) # We keep building...
housing_units = land_consumed * 50       # ...at a constant density (50 homes/ha)

# 2. Define the Demographic Reality
demographic_limit = 5000  # The population stops growing at 5000 families

# 3. Calculate "Raw Output" (What the GDP measures)
# GDP just sees construction activity. It looks like a straight line up.
raw_output = housing_units

# 4. Calculate "Social Efficiency" (What your formula measures)
# We use numpy.minimum to "clamp" the benefit at the demographic limit
useful_benefit = np.minimum(housing_units, demographic_limit)
efficiency_score = useful_benefit / land_consumed

# 5. Plotting
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot Efficiency
color = 'tab:red'
ax1.set_xlabel('Land Consumed (Hectares)')
ax1.set_ylabel('Law Efficiency Score', color=color, fontsize=12, fontweight='bold')
ax1.plot(land_consumed, efficiency_score, color=color, linewidth=3)
ax1.tick_params(axis='y', labelcolor=color)

# Add the "Cliff" annotation
ax1.axvline(x=100, color='grey', linestyle='--')
ax1.text(105, 40, '← Overproduction Starts Here\n(The "Valdeluz" Effect)', color='black')

# Plot Raw Housing Stock (Ghost homes included)
ax2 = ax1.twinx()
color = 'tab:blue'
ax2.set_ylabel('Total Housing Stock (Units)', color=color)
ax2.plot(land_consumed, housing_units, color=color, linestyle=':', alpha=0.5)
ax2.tick_params(axis='y', labelcolor=color)

plt.title('The "Speculation Trap": Why Building More Can Lower Efficiency')
plt.grid(True, alpha=0.3)
plt.show()