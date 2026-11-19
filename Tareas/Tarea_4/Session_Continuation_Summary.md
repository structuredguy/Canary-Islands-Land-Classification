# Tarea 4 — Session Continuation Summary (For Antigravity IDE)

This document captures all files built, verified calculations, and legal/mathematical nuances explored in our session so you can resume seamlessly in Antigravity IDE.

---

## 1. Files Created in `Tareas/Tarea_4/`

| File | Purpose & Status |
| :--- | :--- |
| [verify_galapagos_math.py](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/verify_galapagos_math.py) | Exhaustive 3-decimal grid sweep (`801 x 601`) verifying the Galapagos scalar penalty fitness function (`[PASS]`). |
| [tarea4_galapagos.gh](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/tarea4_galapagos.gh) | Grasshopper 1 definition (`Python 3 Script`, 4 sliders initialized at $S_2$, 5 `Custom Preview` layers, pre-wired `Galapagos` component). |
| [tarea4_sector_galapagos.3dm](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/tarea4_sector_galapagos.3dm) | Rhino 8 document (Meters, `92` baked objects across 5 layers) at the 2-floor yield optimum ($C_e = 0.895$, $C_{\text{ocup}} = 90\%$). |
| [galapagos_guide.md](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/galapagos_guide.md) | Step-by-step Galapagos solver instructions and scenario benchmark table. |
| [scipy_sector_optimizer.py](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/scipy_sector_optimizer.py) | SciPy (`1.16.3`) replacement for Galapagos: `SLSQP` + `NonlinearConstraint`, `PchipInterpolator` + `differential_evolution`, and 1,000-draw Monte Carlo + `CVaR`. |
| [fig4_scipy_promoter_opt.svg](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/fig4_scipy_promoter_opt.svg) | Mobile-first SVG chart of sparse market comps and interior profit optimum vs. boundary yield max (verified via RapidOCR, no PNG). |

*(Existing context files read: [Urban Planning Assignment Breakdown.md](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/Urban%20Planning%20Assignment%20Breakdown.md), [input_parameters.md](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/input_parameters.md), [Visual Exploration Notes.md](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/Visual%20Exploration%20Notes.md), [Verbatim Conversation Log.md](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/Verbatim%20Conversation%20Log.md), and [Tarea_3.md](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_3/Tarea_3.md).)*

---

## 2. Mathematical & Optimization Nuances Covered

### A. The 2-Floor Frontier Curve ($N_p = 2$)
Rearranging $E_{\text{teórica}} = 2 \cdot (S_{\text{bruta}} - S_{\text{viario}} - 0.45\,E_{\text{teórica}}) \cdot C_{\text{ocup}}$ with $S_{\text{bruta}} - S_{\text{viario}} = 54{,}000\text{ m}^2\text{s}$ gives the exact Pareto boundary:

$$E_{\text{teórica}}(C_{\text{ocup}}) = \frac{108{,}000\,C_{\text{ocup}}}{1 + 0.90\,C_{\text{ocup}}}, \qquad C_{e,\max}(C_{\text{ocup}}) = \frac{1.8\,C_{\text{ocup}}}{1 + 0.9\,C_{\text{ocup}}}$$

* Points **on** the curve hit $N_{\text{plantas,exact}} = 2.00$ ($0$ deficit); points **below** fit in $\le 2$ floors.
* **Not all curve values are equally valid:**
  1. **Assignment bands ($C_e > 0.9$ vs. $< 0.9$; $C_{\text{ocup}} > 84\%$ vs. $< 61\%$):** The curve crosses $C_e = 0.90$ at **$C_{\text{ocup}} = 90.91\%$**. Keeping $C_e > 0.9$ restricts you to $(90.91\%, 100\%]$ ($C_e \le 0.9474$); $C_e = 1.0$ is unreachable ($111.11\%$).
  2. **Urbanistic / habitability limits:** Pushing $C_{\text{ocup}} \to 100\%$ ($56{,}842\text{ m}^2\text{t}$, $40$ plots) eliminates setbacks, gardens, and natural light/ventilation patios; realistic caps sit around $85\text{–}90\%$.
  3. **Pareto trade-off & plot quantization:** Moving up the curve trades **plots & private yards** ($53 \to 40$ plots) for **floor area & cessions** ($37{,}241 \to 56{,}842\text{ m}^2\text{t}$).

### B. Promoter Objective: Yield Max vs. Profit Max (SciPy Results)
* **Max Buildable Yield (`SLSQP` with $C_{\text{ocup}} \le 90\%$):**
  $C_e^* = 0.895028$, $C_{\text{ocup}}^* = 90.00\% \implies 53{,}701.66\text{ m}^2\text{t}$, $42$ plots, $N_p = 2.000$.
* **Sparse Comps + Unknown Price Function (`PchipInterpolator` + `differential_evolution`):**
  When selling price per $\text{m}^2\text{t}$ drops with crowding (e.g., €3,400 $\to$ €2,100/$\text{m}^2\text{t}$), the chain rule fails due to sparse empirical comps and discontinuous `floor()` plot counts. SciPy's derivative-free `differential_evolution` finds an **interior profit peak** ($C_e^* = 0.6254$, $C_{\text{ocup}}^* = 50.55\%$, $53$ plots, €57.32M net margin after 10% municipal cession & €50/$\text{m}^2\text{s}$ urbanization cost).
* **Distribution Intuition (Monte Carlo 1,000 draws):**
  * Expected margin peak: $C_{\text{ocup}} = 49.3\%$, $C_e = 0.6142$, $\mathbb{E}[\Pi] = \text{€}57.42\text{M}$.
  * Worst-20% `CVaR` peak: $C_{\text{ocup}} = 49.5\%$, $C_e = 0.6164$, $\text{CVaR}_{20} = \text{€}49.96\text{M}$.

---

## 3. Legal & Architectural Nuances (Spanish / Canary Islands Law)

1. **TAU (*Transferencia de Aprovechamiento Urbanístico*):**
   * True legal outlet to materialize remaining $E_{\text{teórica}}$ ($11{,}400\text{ m}^2\text{t}$ in $S_1$, $33{,}000\text{ m}^2\text{t}$ in $S_2$) by transferring rights (via *coeficientes de ponderación*) to a higher-height receiving sector designated in the *Plan General*.
2. **Non-Computable Basements (*Sótanos*) vs. Extra Parking / *Semisótanos*:**
   * **Correction noted in chat:** If garages are strictly **non-computable**, *any* promoter (even with $0$ spare *edificabilidad*) can build them—so they are **not** a mathematical outlet for trapped $E_{\text{teórica}}$, only a commercial efficiency boost freeing 100% of the 2 above-ground floors for living space.
   * **When basements DO consume spare $E_{\text{teórica}}$:** Under "mandatory-only" municipal *ordenanzas* (where only Ley 4/2017's $\ge 1$ stall/dwelling minimum is exempt), a **2nd car bay**, *bodega*, or sloped-lot **walk-out *semisótano*** computes toward $E_{\text{teórica}}$ and acts as a real outlet.
3. ***Bajo Cubierta* (Pitched Roof Attics):**
   * Usually does **not** count as a 3rd facade floor if kept within cornice height and roof-pitch caps ($\sim 30^\circ\text{–}35^\circ$), **but DOES compute toward $E_{\text{teórica}}$** wherever clear headroom exceeds $\sim 1.50\text{–}1.80\text{ m}$. Because $S_1$ leaves $0.47$ floors unbuilt ($11{,}400\text{ m}^2\text{t}$), a computable *bajo cubierta* cleanly absorbs it in PGOs that allow pitched roofs.
4. **10% / 15% Municipal Lucrative Cession (Art. 44.c Ley 4/2017 = 10%; Art. 18.1.b RDL 7/2015 = 5–15%):**
   * **What is ceded:** Urbanized, serviced plots **free of urbanization charges** (*libre de cargas de urbanización*), **not** finished buildings.
   * **Impact on `Tarea_4`:** Does **not** alter total sector $S_{\text{neta}}$, $N_{\text{plantas}}$, or the 2-floor frontier (since Council plots sit inside $S_{\text{neta}}$), because `Tarea_4` asks for *total* sector plots (unlike `Tarea_3`, which isolated *promotores* plots). It **does** reduce promoter net yield to $90\%$ (or $85\%$) while the promoter funds $100\%$ of urbanization costs.
5. **Intensive vs. Extensive Scale ($S_{\text{bruta}}$ & $S_{\text{parcela}}$):**
   * Current equations are scale-invariant. Real-world size breaks invariance via: (a) small-site $700\text{ m}^2\text{s}$ quantization cliffs, (b) mega-sector market absorption/saturation & multi-year holding cost, (c) fixed tie-in costs vs. mega-sector *Sistemas Generales* / VPO thresholds, and (d) actual footprint dimensions ($S_{\text{parcela}}$).
6. **Heterogeneous Plots & `Tarea_3` Mixed-Typology Lesson:**
   * $700\text{ m}^2\text{s}$ is a **lower bound**, not an equal-size mandate.
   * Unlike `Tarea_3` (where 5-story VPO towers balanced 2-story private-pool villas), a sector-wide $N_p = 2$ cap prevents towers from adding height capacity—**but** a **mixed-occupancy layout** ($50\text{–}60\%$ private-pool villas + $85\text{–}90\%$ 2-story VPO/courtyard macro-plots with a communal pool) raises average occupancy and eliminates dead side setbacks.

---

## 4. Suggested Next Steps for Tomorrow (Antigravity IDE)
1. **Extend [scipy_sector_optimizer.py](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/scipy_sector_optimizer.py)** with:
   * Extensive scale sensitivity ($S_{\text{bruta}}$ from $0.5\text{ ha}$ to $50\text{ ha}$ with absorption decay & fixed costs), and/or
   * Mixed-typology optimization splitting $S_{\text{neta}}$ into **private-pool market villas** + **2-story VPO courtyard macro-plot** (with $30\%$ VPO & $10\%$ municipal PMS rules).
2. **Draft the final Spanish submission** (e.g., `Tareas/Tarea_4/Tarea_4.tex` $\to$ PDF, matching `Tarea_3` style) incorporating the analytical derivations, `fig1`–`fig4` SVGs, and Question 3 urbanistic/legal analysis.
