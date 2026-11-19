# Input Parameters of the Tarea 4 Urban Planning Model

This table classifies every parameter in the sector model according to whether it is **Fixed** (imposed by the legislator, municipal planning ordinance, or assignment rules) or **Free** (selectable by the promoter/designer within legal bounds).

---

## 1. Core Assignment Model Inputs

| Parameter | Symbol | Value / Domain | Unit | Fixed vs. Free | Legal / Assignment Authority |
| :--- | :---: | :--- | :---: | :--- | :--- |
| **DNI / NIE Last Digit** | $d$ | $4$ | — | **Fixed** (Identity seed) | Given personal rule ($d + 2 = 6\text{ ha}$). |
| **Gross Sector Area** | $S_{\text{bruta}}$ | $60,000$ ($6\text{ ha}$) | $\text{m}^2\text{s}$ | **Fixed** (Legislator / Plan) | Delimited by the *Plan General* (assignment: $d + 2\text{ ha}$). |
| **Road Network Ratio** | $r_{\text{viario}}$ | $10\%$ ($S_{\text{viario}} = 6,000$) | $\%$ ($\text{m}^2\text{s}$) | **Fixed** (Agreed / Plan) | Fixed at $10\%$ by the assignment; in practice set by road standards in the *Plan Parcial*. |
| **Public Cession Ratio** | $r_{\text{ces}}$ | $45 / 100 = 0.45$ | $\text{m}^2\text{s}/\text{m}^2\text{c}$ | **Fixed Floor** (Legislator) | Non-negotiable statutory minimum ($\ge 40\text{ m}^2\text{s}/100\text{ m}^2\text{c}$ in Ley 4/2017 Art. 138; $45$ in assignment). |
| **Minimum Plot Size** | $S_{\text{min}}$ | $700$ | $\text{m}^2\text{s}$ | **Fixed Floor** (Legislator / Plan) | Subdivision lower bound ($S_{\text{parcela}} \ge 700\text{ m}^2\text{s}$); prohibits smaller plots. |
| **Gross Building Coeff.** | $C_e$ | Chosen: $1.0$ ($>0.9$) & $0.6$ ($<0.9$)<br>Legal cap: $\le 1.20$ | $\text{m}^2\text{c}/\text{m}^2\text{s}$ | **Free within Bounds** (Promoter / Plan) | **Assignment:** Student/promoter selects one $>0.9$ and one $<0.9$.<br>**Real Law:** Capped at $1.20$ by Ley 4/2017 Art. 138 ($1.50$ in renewal); agreed in sector planning. |
| **Plot Occupancy Coeff.** | $C_{\text{ocup}}$ | Chosen: $90\%$ ($>84\%$) & $50\%$ ($<61\%$)<br>Physical cap: $\le 100\%$ | $\%$ | **Free within Bounds** (Promoter / Architect) | **Assignment:** Student/promoter selects one $>84\%$ and one $<61\%$.<br>**Real Law:** Bounded by physical limit ($100\%$) and municipal setback/garden ordinances. |
| **Max Floor Cap** | $N_{\text{plantas}}$ | Q1–Q2: Unconstrained output<br>Q3: $N_p = 2$ | floors | **Fixed Cap in Q3** (Legislator / Plan) | **Q1–Q2:** Output variable ($3, 5, 2, 2$).<br>**Q3:** Hard zoning/landscape cap imposed by planning authority. |

---

## 2. Derived State & Output Variables (Not Inputs)

| Quantity | Formula | Role |
| :--- | :--- | :--- |
| **Theoretical Buildability** | $E_{\text{teórica}} = S_{\text{bruta}} \cdot C_e$ | Derived ceiling of lucrative floor area ($\text{m}^2\text{c}$). |
| **Mandatory Cessions** | $S_{\text{cesiones}} = 0.45 \cdot E_{\text{teórica}}$ | Driven directly by $C_e$; reduces available net land. |
| **Net Lucrative Land** | $S_{\text{neta}} = S_{\text{bruta}} - S_{\text{viario}} - S_{\text{cesiones}}$ | Residual land available for private plots ($\text{m}^2\text{s}$). |
| **Resulting Plot Count** | $N_{\text{parcelas}} = \lfloor S_{\text{neta}} / S_{\text{min}} \rfloor$ | Discrete integer decision/output; remainder distributed to plots. |
| **Total Building Footprint** | $S_{\text{ocup,total}} = S_{\text{neta}} \cdot C_{\text{ocup}}$ | Max ground footprint across all plots ($\text{m}^2\text{s}$). |
| **Required Floors** | $N_{\text{plantas}} = \lceil E_{\text{teórica}} / S_{\text{ocup,total}} \rceil$ | Discrete integer floors needed when $N_p$ is unconstrained. |

---

## 3. Additional Statutory Parameters (Ley 4/2017 & RDL 7/2015 Context)

When extending the homework model toward a real Canary Islands *Plan Parcial*, the legislator fixes these extra hard constraints:

| Statutory Parameter | Value / Bound | Fixed vs. Free | Legal Source |
| :--- | :--- | :--- | :--- |
| **Max Gross Buildability** | $\le 1.20\text{ m}^2\text{c}/\text{m}^2\text{s}$ ($1.50$ renewal) | **Fixed Ceiling** (Legislator) | Ley 4/2017 Art. 138 |
| **Max Population Density** | $\le 400\text{ hab/ha}$ ($500$ renewal) | **Fixed Ceiling** (Legislator) | Ley 4/2017 Art. 138 |
| **Protected Housing (*VPO*)** | $\ge 30\%$ residential $E_{\text{teórica}}$ ($40\%$ state baseline) | **Fixed Minimum** (Legislator) | Ley 4/2017 / RDL 7/2015 |
| **Off-Street Parking** | $\ge 1\text{ stall / dwelling}$ | **Fixed Minimum** (Legislator) | Ley 4/2017 Art. 138 |
| **Subsoil (*Subsuelo*) Rules** | Computability & max footprint below grade | **Fixed Rules** (Municipal Plan) | Municipal *Ordenanzas* & Ley 4/2017 |
| **Parcel Mix & Typology** | Individual plot sizes $S_i \ge 700\text{ m}^2\text{s}$, unit mix, actual footprint $\le C_{\text{ocup}}$ | **Free within Bounds** (Promoter) | *Proyecto de Reparcelación* |

---

## 4. Key Optimization Takeaway (Who Controls What in Question 3?)

* **What the promoter CANNOT lower:** $S_{\text{bruta}}$, $S_{\text{viario}}$ ($10\%$), $r_{\text{ces}}$ ($0.45$), $S_{\text{min}}$ ($700\text{ m}^2\text{s}$), and (in Q3) $N_p = 2$.
* **What the promoter CAN adjust:**
  1. **$C_{\text{ocup}}$** (up toward $\le 100\%$, though $100\%$ is still insufficient for $C_e = 1.0$ under $N_p = 2$).
  2. **$C_e$** (downward from $1.0$ to $\le \frac{1.8\,C_{\text{ocup}}}{1 + 0.9\,C_{\text{ocup}}}$).
  3. **Parcel layout & subterranean/attic design** (within municipal *bajo rasante* / *TAU* allowances).

---

## 5. Note: Gross Building Coefficient ($C_e$) vs. Plot Occupancy Coefficient ($C_{\text{ocup}}$)

Although both coefficients shape building density, they govern orthogonal geometric dimensions and trigger different legal effects:

* **Gross Building Coefficient ($C_e$, *Edificabilidad Bruta* — $\text{m}^2\text{c}/\text{m}^2\text{s}$):**
  * **What it measures:** Total cumulative floor area allowed across **all stories** ($E_{\text{teórica}}$) divided by the **entire gross sector area** ($S_{\text{bruta}}$, before subtracting roads or public cessions).
  * **Role in the model:** Sets the total economic development volume (*aprovechamiento*) and directly drives mandatory public cessions ($S_{\text{cesiones}} = 0.45 \cdot S_{\text{bruta}} \cdot C_e$). Increasing $C_e$ adds total floor area ($\text{m}^2\text{c}$) while reducing net private land ($S_{\text{neta}}$) and resulting plot count ($N_{\text{parcelas}}$).
  * **Example:** At $C_e = 1.0\text{ m}^2\text{c}/\text{m}^2\text{s}$ on $60,000\text{ m}^2\text{s}$, the sector holds $60,000\text{ m}^2\text{c}$ of total floor area.

* **Plot Occupancy Coefficient ($C_{\text{ocup}}$, *Ocupación de Parcela* — $\%$):**
  * **What it measures:** Maximum **ground-level footprint** (*proyección horizontal*) of a building divided by the **net plot area** ($S_{\text{ocup,total}} / S_{\text{neta}}$).
  * **Role in the model:** Governs the balance between built footprint and unbuilt private space (setbacks, gardens, courtyards, permeable soil). It does **not** affect $E_{\text{teórica}}$, $S_{\text{cesiones}}$, or $N_{\text{parcelas}}$, but inversely controls **building height**: lowering $C_{\text{ocup}}$ concentrates the same floor area onto a smaller footprint, requiring more floors ($N_{\text{plantas}}$).
  * **Example:** At $C_{\text{ocup}} = 50\%$ on a $700\text{ m}^2\text{s}$ plot, the building footprint cannot exceed $350\text{ m}^2\text{s}$ per floor, leaving $350\text{ m}^2\text{s}$ open at ground level.

