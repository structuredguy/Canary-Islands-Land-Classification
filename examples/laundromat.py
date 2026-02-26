import numpy as np
import matplotlib.pyplot as plt

# Timeline: 1995 to 2002 (The countdown to the Euro)
years = np.arange(1995, 2003)

# 1. The "Deadline Pressure" (Inverse of time remaining)
# As 2002 approaches, the panic to convert Pesetas increases exponentially.
deadline_pressure = 1 / (2003 - years)

# 2. Black Money "Surfacing" (Estimated flow into Real Estate)
# Modeled as a function of deadline pressure.
black_money_flow = deadline_pressure * 20  # Arbitrary billions scale

# 3. Official Interest Rates (Convergence to Euro)
# Rates dropped from ~9% to ~3% to match Germany.
interest_rates = np.array([9.0, 8.5, 6.0, 4.5, 3.0, 3.5, 3.25, 3.0])

# 4. Housing Prices (The Result)
# Prices decouple from interest rates because cash buyers don't care about mortgages.
housing_prices_index = np.array([100, 104, 110, 125, 145, 170, 195, 220])

# Plotting
fig, ax1 = plt.subplots(figsize=(12, 6))

# Plot Housing Prices
color = 'tab:blue'
ax1.set_xlabel('Year')
ax1.set_ylabel('Housing Price Index (1995=100)', color=color, fontweight='bold')
ax1.plot(years, housing_prices_index, color=color, linewidth=3, marker='o', label='Housing Prices')
ax1.tick_params(axis='y', labelcolor=color)

# Plot The "Laundromat Effect" (Black Money Pressure)
ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Black Money "Urgency" (Model)', color=color, fontweight='bold')
ax2.fill_between(years, 0, black_money_flow, color=color, alpha=0.3, label='Peseta "Aflore" (Laundering)')
ax2.tick_params(axis='y', labelcolor=color)

# Annotation: The 1998 Land Law
plt.axvline(x=1998, color='green', linestyle='--', linewidth=2)
plt.text(1996.5, 3.5, '1998 Land Law\n(Opened the door for investment)', color='green', fontweight='bold', bbox=dict(facecolor='white', alpha=0.8))

plt.title('The "Euro Flush": How Black Pesetas Fueled the 1998 Boom')
plt.grid(True, alpha=0.3)
# plt.show()
plt.savefig('../img/laundromat_EN.png')