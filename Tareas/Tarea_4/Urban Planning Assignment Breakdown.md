# Urban Planning Sector Calculation Breakdown

## 1. Base Data & Chosen Parameters

### Fixed Data (Derived from Assignment Rules)

* **Last digit of DNI/NIE/Passport:** $4$

* **Gross Sector Area (**$S_{\text{bruta}}$**):**
  

  $$
  \text{Rule: } \text{Last digit} + 2 = 4 + 2 = 6\text{ ha}
  $$

  
  *(Note: Since* $6 \neq 0$ *and* $6 \neq 1$*, no exception rule applies).*
  Converting hectares to square meters of land ($\text{m}^2\text{s}$):
  

  $$
  S_{\text{bruta}} = 6\text{ ha} \times 10,000\frac{\text{m}^2\text{s}}{\text{ha}} = 60,000\text{ m}^2\text{s}
  $$

* **Road Network Area (**$S_{\text{viario}}$**):** $10\%$ of gross sector area:
  

  $$
  S_{\text{viario}} = 0.10 \times S_{\text{bruta}} = 0.10 \times 60,000\text{ m}^2\text{s} = 6,000\text{ m}^2\text{s}
  $$

* **Mandatory Public Cessions (**$S_{\text{cesiones}}$**):** $45\text{ m}^2\text{s}$ for open spaces, facilities, and infrastructure per $100\text{ m}^2\text{c}$ (square meters of built floor area / *metros cuadrados construidos*) of residential buildability:
  

  $$
  S_{\text{cesiones}} = 0.45 \times E_{\text{teórica}}
  $$

* **Minimum Resulting Plot Size (**$S_{\text{min}}$**):** $700\text{ m}^2\text{s}$

### Student-Selected Parameters

To compare high-intensity vs. low-intensity development clearly while keeping arithmetic clean and legally realistic (e.g., staying below typical regional gross buildability caps of $1.20\text{ m}^2\text{c}/\text{m}^2\text{s}$), we select:

1. **Gross Building Coefficients (**$C_e$**):**

   * **High (**$> 0.9$**):** $C_{e1} = 1.0\text{ m}^2\text{c}/\text{m}^2\text{s}$

   * **Low (**$< 0.9$**):** $C_{e2} = 0.6\text{ m}^2\text{c}/\text{m}^2\text{s}$

2. **Plot Occupancy Coefficients (**$C_{\text{ocup}}$**):**

   * **High (**$> 84\%$**):** $C_{\text{ocup},1} = 90\%$ ($0.90$)

   * **Low (**$< 61\%$**):** $C_{\text{ocup},2} = 50\%$ ($0.50$)

### Matrix of the Four Scenarios (*Supuestos*)

* **Scenario 1 (*Supuesto 1*):** $C_{e1} = 1.0\text{ m}^2\text{c}/\text{m}^2\text{s}$ and $C_{\text{ocup},1} = 90\%$

* **Scenario 2 (*Supuesto 2*):** $C_{e1} = 1.0\text{ m}^2\text{c}/\text{m}^2\text{s}$ and $C_{\text{ocup},2} = 50\%$

* **Scenario 3 (*Supuesto 3*):** $C_{e2} = 0.6\text{ m}^2\text{c}/\text{m}^2\text{s}$ and $C_{\text{ocup},1} = 90\%$

* **Scenario 4 (*Supuesto 4*):** $C_{e2} = 0.6\text{ m}^2\text{c}/\text{m}^2\text{s}$ and $C_{\text{ocup},2} = 50\%$

## 2. Conceptual & Theoretical Formulation

Your professor explicitly requires setting out the conceptual formulas before plugging in numbers, paying close attention to units ($\text{m}^2\text{s}$ for land vs. $\text{m}^2\text{c}$ for built floor area / *metros cuadrados construidos*):

1. **Theoretical Buildable Floor Area (**$E_{\text{teórica}}$**):**
   

   $$
   E_{\text{teórica}} = S_{\text{bruta}} \times C_e \quad [\text{m}^2\text{c}]
   $$

2. **Mandatory Public Cessions (**$S_{\text{cesiones}}$**):**
   

   $$
   S_{\text{cesiones}} = E_{\text{teórica}} \times \frac{45\text{ m}^2\text{s}}{100\text{ m}^2\text{c}} = 0.45 \times E_{\text{teórica}} \quad [\text{m}^2\text{s}]
   $$

3. **Net Lucrative Land Area (**$S_{\text{neta}}$**):**
   

   $$
   S_{\text{neta}} = S_{\text{bruta}} - S_{\text{viario}} - S_{\text{cesiones}} \quad [\text{m}^2\text{s}]
   $$

4. **Maximum Number of Resulting Plots (**$N_{\text{parcelas}}$**):**
   

   $$
   N_{\text{parcelas}} = \left\lfloor \frac{S_{\text{neta}}}{S_{\text{min}}} \right\rfloor \quad [\text{plots}]
   $$

   
   *(Conceptual note: We must take the integer floor* $\lfloor \cdot \rfloor$ *because urban planning law prohibits creating any plot smaller than the minimum plot size of* $700\text{ m}^2\text{s}$*. Any remainder land is distributed among the resulting plots, making the average plot size slightly larger than* $700\text{ m}^2\text{s}$*).*

5. **Maximum Total Ground Footprint / Occupied Area (**$S_{\text{ocup,total}}$**):**
   

   $$
   S_{\text{ocup,total}} = S_{\text{neta}} \times C_{\text{ocup}} \quad [\text{m}^2\text{s}]
   $$

6. **Number of Floors Required (**$N_{\text{plantas}}$**):**
   

   $$
   N_{\text{plantas,exact}} = \frac{E_{\text{teórica}}}{S_{\text{ocup,total}}} \implies N_{\text{plantas}} = \left\lceil \frac{E_{\text{teórica}}}{S_{\text{ocup,total}}} \right\rceil \quad [\text{floors}]
   $$

   
   *(Conceptual note: Because a building cannot have a fraction of a floor without exceeding the maximum allowed footprint on lower levels, any decimal result must be rounded up* $\lceil \cdot \rceil$ *to the next whole number of stories).*

## 3. Step-by-Step Calculations by Scenario

### Group A: High Building Coefficient ($C_{e1} = 1.0\text{ m}^2\text{c}/\text{m}^2\text{s}$)

*Applies to Scenarios 1 and 2:*

* **Theoretical Buildability:**
  

  $$
  E_{\text{teórica},1} = 60,000\text{ m}^2\text{s} \times 1.0\frac{\text{m}^2\text{c}}{\text{m}^2\text{s}} = 60,000\text{ m}^2\text{c}
  $$

* **Mandatory Cessions:**
  

  $$
  S_{\text{cesiones},1} = 0.45 \times 60,000 = 27,000\text{ m}^2\text{s}
  $$

* **Road Network:**
  

  $$
  S_{\text{viario}} = 6,000\text{ m}^2\text{s}
  $$

* **Net Lucrative Land:**
  

  $$
  S_{\text{neta},1} = 60,000 - 6,000 - 27,000 = 27,000\text{ m}^2\text{s}
  $$

* **Total Resulting Plots (**$N_{\text{parcelas}}$**):**
  

  $$
  \frac{27,000\text{ m}^2\text{s}}{700\text{ m}^2\text{s}/\text{plot}} = 38.57\text{ plots} \implies \mathbf{38\text{ plots}}
  $$

  
  *(Average plot area:* $\frac{27,000}{38} \approx 710.53\text{ m}^2\text{s}$*, or* $37$ *plots of* $700\text{ m}^2\text{s}$ *plus* $1$ *plot of* $1,100\text{ m}^2\text{s}$*).*

#### Scenario 1 ($C_{e1} = 1.0$, $C_{\text{ocup},1} = 90\%$)

* **Resulting Plots:** $\mathbf{38\text{ plots}}$ *(occupancy does not affect land subdivision).*

* **Maximum Total Footprint:**
  

  $$
  S_{\text{ocup,total},1} = 27,000\text{ m}^2\text{s} \times 0.90 = 24,300\text{ m}^2\text{s}
  $$

* **Required Number of Floors:**
  

  $$
  N_{\text{plantas},1} = \frac{60,000\text{ m}^2\text{c}}{24,300\text{ m}^2\text{s}} \approx 2.47\text{ floors} \implies \mathbf{3\text{ floors}}
  $$

  
  *(2 full floors at* $90\%$ *occupancy plus a 3rd setback/partial floor, or 3 uniform floors at* $\approx 74.07\%$ *occupancy).*

#### Scenario 2 ($C_{e1} = 1.0$, $C_{\text{ocup},2} = 50\%$)

* **Resulting Plots:** $\mathbf{38\text{ plots}}$

* **Maximum Total Footprint:**
  

  $$
  S_{\text{ocup,total},2} = 27,000\text{ m}^2\text{s} \times 0.50 = 13,500\text{ m}^2\text{s}
  $$

* **Required Number of Floors:**
  

  $$
  N_{\text{plantas},2} = \frac{60,000\text{ m}^2\text{c}}{13,500\text{ m}^2\text{s}} \approx 4.44\text{ floors} \implies \mathbf{5\text{ floors}}
  $$

  
  *(4 full floors at* $50\%$ *occupancy plus a 5th partial floor, or 5 uniform floors at* $\approx 44.44\%$ *occupancy).*

### Group B: Low Building Coefficient ($C_{e2} = 0.6\text{ m}^2\text{c}/\text{m}^2\text{s}$)

*Applies to Scenarios 3 and 4:*

* **Theoretical Buildability:**
  

  $$
  E_{\text{teórica},2} = 60,000\text{ m}^2\text{s} \times 0.6\frac{\text{m}^2\text{c}}{\text{m}^2\text{s}} = 36,000\text{ m}^2\text{c}
  $$

* **Mandatory Cessions:**
  

  $$
  S_{\text{cesiones},2} = 0.45 \times 36,000 = 16,200\text{ m}^2\text{s}
  $$

* **Road Network:**
  

  $$
  S_{\text{viario}} = 6,000\text{ m}^2\text{s}
  $$

* **Net Lucrative Land:**
  

  $$
  S_{\text{neta},2} = 60,000 - 6,000 - 16,200 = 37,800\text{ m}^2\text{s}
  $$

* **Total Resulting Plots (**$N_{\text{parcelas}}$**):**
  

  $$
  \frac{37,800\text{ m}^2\text{s}}{700\text{ m}^2\text{s}/\text{plot}} = 54.00\text{ plots} \implies \mathbf{54\text{ plots}}
  $$

  
  *(Exact subdivision into* $54$ *plots of* $700\text{ m}^2\text{s}$ *each).*

#### Scenario 3 ($C_{e2} = 0.6$, $C_{\text{ocup},1} = 90\%$)

* **Resulting Plots:** $\mathbf{54\text{ plots}}$

* **Maximum Total Footprint:**
  

  $$
  S_{\text{ocup,total},3} = 37,800\text{ m}^2\text{s} \times 0.90 = 34,020\text{ m}^2\text{s}
  $$

* **Required Number of Floors:**
  

  $$
  N_{\text{plantas},3} = \frac{36,000\text{ m}^2\text{c}}{34,020\text{ m}^2\text{s}} \approx 1.06\text{ floors} \implies \mathbf{2\text{ floors}}
  $$

  
  *(1 full floor at* $90\%$ *occupancy plus a minimal 2nd floor, or 2 uniform floors at* $\approx 47.62\%$ *occupancy).*

#### Scenario 4 ($C_{e2} = 0.6$, $C_{\text{ocup},2} = 50\%$)

* **Resulting Plots:** $\mathbf{54\text{ plots}}$

* **Maximum Total Footprint:**
  

  $$
  S_{\text{ocup,total},4} = 37,800\text{ m}^2\text{s} \times 0.50 = 18,900\text{ m}^2\text{s}
  $$

* **Required Number of Floors:**
  

  $$
  N_{\text{plantas},4} = \frac{36,000\text{ m}^2\text{c}}{18,900\text{ m}^2\text{s}} \approx 1.90\text{ floors} \implies \mathbf{2\text{ floors}}
  $$

  
  *(1 full floor at* $50\%$ *occupancy plus a 2nd floor at* $\approx 45.24\%$ *occupancy, or 2 uniform floors at* $\approx 47.62\%$ *occupancy).*

### Summary Comparison Table

| Parameter | Scenario 1 | Scenario 2 | Scenario 3 | Scenario 4 | 
| ----- | ----- | ----- | ----- | ----- | 
| **Building Coeff. (**$C_e$**)** | $1.0\text{ m}^2\text{c}/\text{m}^2\text{s}$ | $1.0\text{ m}^2\text{c}/\text{m}^2\text{s}$ | $0.6\text{ m}^2\text{c}/\text{m}^2\text{s}$ | $0.6\text{ m}^2\text{c}/\text{m}^2\text{s}$ | 
| **Occupancy Coeff. (**$C_{\text{ocup}}$**)** | $90\%$ | $50\%$ | $90\%$ | $50\%$ | 
| **Theoretical Buildability (**$E_{\text{teórica}}$**)** | $60,000\text{ m}^2\text{c}$ | $60,000\text{ m}^2\text{c}$ | $36,000\text{ m}^2\text{c}$ | $36,000\text{ m}^2\text{c}$ | 
| **Public Cessions (**$S_{\text{cesiones}}$**)** | $27,000\text{ m}^2\text{s}$ | $27,000\text{ m}^2\text{s}$ | $16,200\text{ m}^2\text{s}$ | $16,200\text{ m}^2\text{s}$ | 
| **Road Area (**$S_{\text{viario}}$**)** | $6,000\text{ m}^2\text{s}$ | $6,000\text{ m}^2\text{s}$ | $6,000\text{ m}^2\text{s}$ | $6,000\text{ m}^2\text{s}$ | 
| **Net Lucrative Land (**$S_{\text{neta}}$**)** | $27,000\text{ m}^2\text{s}$ | $27,000\text{ m}^2\text{s}$ | $37,800\text{ m}^2\text{s}$ | $37,800\text{ m}^2\text{s}$ | 
| **Resulting Plots (**$N_{\text{parcelas}}$**)** | $38$ | $38$ | $54$ | $54$ | 
| **Exact Floors (**$N_{\text{plantas,exact}}$**)** | $2.47$ | $4.44$ | $1.06$ | $1.90$ | 
| **Required Floors (**$N_{\text{plantas}}$**)** | $3\text{ floors}$ | $5\text{ floors}$ | $2\text{ floors}$ | $2\text{ floors}$ | 

## 4. Analysis of the 2-Floor Restriction ($N_{\text{plantas}} = 2$)

### Diagnosis by Scenario

The maximum buildable floor area that can physically fit on the plots with $N_{\text{plantas}} = 2$ is:

$$
E_{\text{materializable}} = 2 \times S_{\text{neta}} \times C_{\text{ocup}}
$$

* **Scenarios 3 and 4 (**$C_{e2} = 0.6$**):** No changes are needed. Both scenarios already require $\le 2$ floors ($1.06$ and $1.90$ floors, respectively), meaning $100\%$ of the $36,000\text{ m}^2\text{c}$ theoretical buildability can be consumed within 2 stories.

* **Scenarios 1 and 2 (**$C_{e1} = 1.0$**):** A **2-floor limit prevents consuming the full theoretical buildability** ($60,000\text{ m}^2\text{c}$):

  * **Scenario 1 (**$C_{\text{ocup}} = 90\%$**):** Only $2 \times 24,300 = 48,600\text{ m}^2\text{c}$ can be built, leaving an unbuilt deficit of $11,400\text{ m}^2\text{c}$ ($19\%$ lost).

  * **Scenario 2 (**$C_{\text{ocup}} = 50\%$**):** Only $2 \times 13,500 = 27,000\text{ m}^2\text{c}$ can be built, leaving an unbuilt deficit of $33,000\text{ m}^2\text{c}$ ($55\%$ lost).

### Proposed Parameter Modifications & Their Effects

To reconcile the 2-floor height limit with theoretical buildability in Scenarios 1 and 2, we examine the governing equation:

$$
E_{\text{teórica}} = 2 \times \left(S_{\text{bruta}} - S_{\text{viario}} - 0.45 \cdot E_{\text{teórica}}\right) \times C_{\text{ocup}}
$$

1. **Modifying Plot Occupancy (**$C_{\text{ocup}}$**) Alone — *Insufficient by Itself*:**

   * Solving for the required occupancy in Scenarios 1 and 2:
     

     $$
     C_{\text{ocup,req}} = \frac{60,000}{2 \times 27,000} = 1.1111 \quad (111.11\%)
     $$

   * **Effect:** Physically and legally impossible, as plot occupancy cannot exceed $100\%$. Even increasing $C_{\text{ocup}}$ to $100\%$ only yields $2 \times 27,000 = 54,000\text{ m}^2\text{c}$ (still short by $6,000\text{ m}^2\text{c}$) while eliminating setbacks, private gardens, natural cross-ventilation, and soil permeability.

2. **Reducing the Building Coefficient (**$C_e$**) — *Primary Morphological Adjustment*:**

   * If the 2-floor height cap is non-negotiable (e.g., due to coastal/landscape protection or single-family/low-rise typology rules), $C_e$ must be lowered to match the 2-story capacity:

     * Keeping $C_{\text{ocup}} = 90\%$: $C_e$ must decrease from $1.0$ to $\approx 0.895\text{ m}^2\text{c}/\text{m}^2\text{s}$ ($E_{\text{teórica}} \approx 53,704\text{ m}^2\text{c}$).

     * Keeping $C_{\text{ocup}} = 50\%$: $C_e$ must decrease from $1.0$ to $\approx 0.621\text{ m}^2\text{c}/\text{m}^2\text{s}$ ($E_{\text{teórica}} \approx 37,241\text{ m}^2\text{c}$).

   * **Effects:** Lowers total buildable floor area, which proportionally reduces mandatory public cessions ($S_{\text{cesiones}}$), increases net lucrative land ($S_{\text{neta}}$), and increases the number of resulting plots ($N_{\text{parcelas}}$). However, reducing $C_e$ decreases landowners' *aprovechamiento urbanístico* (development rights), potentially affecting project profitability or requiring compensation.

3. **Combined Adjustment (Recommended Urban Planning Solution):**

   * **Increase** $C_{\text{ocup}}$ (e.g., in Scenario 2, raising occupancy from $50\%$ to $85\%\text{–}90\%$, avoiding $100\%$ so building setbacks and ventilation patios are preserved) **AND slightly reduce** $C_e$ (to $\approx 0.85\text{–}0.895\text{ m}^2\text{c}/\text{m}^2\text{s}$).

   * **Effects:** Maximizes the utilization of authorized development rights under a 2-story typology (e.g., row houses or courtyard blocks) without violating statutory cession standards ($45\text{ m}^2\text{s}/100\text{ m}^2\text{c}$), which are legal minimums that cannot be reduced.

4. **Complementary Legal/Planning Mechanisms (if** $C_e = 1.0$ **must be preserved):**

   * **Transfer of Development Rights (*Transferencia de Aprovechamiento Urbanístico - TAU*):** Materialize the $48,600\text{ m}^2\text{c}$ (or $27,000\text{ m}^2\text{c}$) within this sector in 2 floors and transfer the remaining unbuilt floor area ($11,400\text{ m}^2\text{c}$ or $33,000\text{ m}^2\text{c}$) to another receiving sector with higher permitted building heights.

   * **Non-computable Basements / Semi-basements (*Sótanos / Semisótanos*) or Loft Spaces (*Bajo cubierta*):** Allow subterranean or sloped-roof spaces for ancillary uses (parking, storage) that do not count toward the 2-story height limit or computable *edificabilidad*, improving commercial viability without altering the exterior 2-story profile.