import numpy as np
import matplotlib.pyplot as plt

# Time period: The 70s Boom (1965 - 1985)
years = np.arange(1965, 1985)

# 1. Real Demand (Tourists pouring in)
# Grows fast, then stabilizes due to Oil Crisis (1973)
tourist_demand = np.array([10, 15, 22, 30, 35, 40, 42, 43, 40, 38, 40, 42, 45, 50, 55, 60, 62, 65, 68, 70])

# 2. Adaptation Supply (Hotels)
# Follows demand closely because hotels go bankrupt if empty.
hotel_supply = tourist_demand * 1.1  # 10% buffer

# 3. Speculative Supply (Second Homes / Urbanizaciones)
# Grows based on "Hype" and cheap credit, ignores the 1973 crisis.
speculative_supply = np.array([12, 18, 25, 35, 45, 60, 75, 90, 100, 110, 115, 120, 125, 135, 150, 165, 180, 195, 210, 225])

# Plotting
plt.figure(figsize=(12, 6))

# Plot Demand (The "Truth")
plt.plot(years, tourist_demand, 'k--', linewidth=2, label='Real Tourist Demand (Overnight Stays)')

# Plot Healthy Supply
plt.plot(years, hotel_supply, 'g-', linewidth=2, label='Adaptation (Hotel Capacity)')

# Plot Speculative Supply
plt.plot(years, speculative_supply, 'r-', linewidth=2, label='Total Construction (Boom + Speculation)')

# Fill the "Speculation Gap"
plt.fill_between(years, hotel_supply, speculative_supply, where=(speculative_supply > hotel_supply),
                 color='red', alpha=0.2, hatch='//', label='The "Speculation Wedge"')

# Annotate the 1973 Oil Crisis
plt.axvline(x=1973, color='gray', linestyle=':')
plt.text(1973.5, 100, '1973 Oil Crisis\n(Demand drops, Construction continues)', fontsize=10)

plt.title('The 1970s: Distinguishing Adaptation from Speculation')
plt.ylabel('Index (1965=10)')
plt.legend()
plt.grid(True, alpha=0.3)
# plt.show()

plt.savefig('../img/decoupling_point_EN.png')