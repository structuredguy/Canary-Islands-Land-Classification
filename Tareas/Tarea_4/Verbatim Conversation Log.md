# Urban Planning Homework & Constrained Optimization — Conversation Log

---

## User
Hi I got the following homework:
Se deberá contestar a las preguntas que se concretan al final (justificando los resultados obtenidos), partiendo de los siguientes datos:

"Superficie bruta del sector o área a ordenar: coincidirá en Hectáreas con el último numero del dni/nie/pasaporte del alumno al que se le incrementará dos unidades. (En el caso que el resultado sea la cifra "0", se aplicara el 9, y en caso de ser el "1" se aplicará el 2).

Coeficiente de edificabilidad: se escogerá uno superior al 0,9 y otro inferior a éste para apreciar sus diferencias.

Cesiones para espacios libres, dotaciones e infraestructuras: 45 metros cuadrados por cada 100 metros de edificabilidad residencial.

Terreno a ocupar por viario: 10% de la superficie bruta en cada caso.

Coeficiente de ocupación de parcela: Usar un coeficiente superior al 84% y otro inferior al 61% (y a su vez, cada uno con cada coeficiente de edificabilidad fijado por el alumno según apartado precedente).

Superficie mínima de parcela resultante: 700 metros cuadrados.

SE SOLICITA: Realizar y justificar los cálculos y resultados, obteniendo:

- El numero de parcelas totales resultantes en cada uno de los cuatro supuestos.

- El número de plantas necesarias para consumir o poder construir toda la edificabilidad teórica del sector, en cada uno de los cuatro supuestos.

- Si el número de plantas fuese 2: ¿Qué haría para poder consumir su edificabilidad teórica? ¿Qué parámetros propone modificar y, cuáles serían sus efectos?

- REALIZAR TODOS LOS CALCULOS EN TRABAJO QUE SE SUBA AL AULA VIRTUAL PARA SU ENTREGA.- Un simple resultado sin justificar su procedencia, carece de valor y no se puntuará. 

(Se recomienda tener cuidado con las unidades y utilizar la formulación conceptual o teórica al plantear cada desarrollo, para evitar confusiones).

---

## Assistant
To calculate the exact figures for your submission, please confirm:

1. **The last digit of your DNI/NIE/Passport** (to determine the gross sector area in hectares using your assignment's rule, or let me know if you prefer an example number).
2. **Your preferred language** for the step-by-step justification—**Spanish** (ready to submit to your Aula Virtual) or **English**?

---

## User
4 and Spanish for final text. Thanks. Lets break it down first in a markdown document in English. Don't worry about the presentation layer

---

## Assistant
I will now generate a structured English breakdown of your urban planning assignment in a Markdown document, covering the parameter selection, conceptual formulas, step-by-step calculations for all four scenarios, and the analysis of the two-floor height restriction.

*(Generated file: `urban_planning_breakdown.md` — "Urban Planning Assignment Breakdown")*

Review the numbers and chosen parameters ($C_{e1} = 1.0$, $C_{e2} = 0.6$, $C_{\text{ocup},1} = 90\%$, $C_{\text{ocup},2} = 50\%$). Whenever you're ready, let me know if you'd like any adjustments or if I should generate the complete, formal **Spanish** version ready for submission to your *Aula Virtual*.

---

## User
That looks very good. I am on the move now. Can you give me some more context? I recently saw a documentary about the basement abusive development in the London houses of the foreign oligarchs. I like constrained optimization problems and searches of optimal solutions when the solution space is discrete (but large).

---

## Assistant
Question 3 of your assignment—forcing a two-floor cap ($N_p = 2$) while preserving total buildable floor area ($E_{\text{total}}$)—is the exact mathematical mechanism behind London’s "iceberg home" phenomenon.

## 1. The "Iceberg Home" Loophole: Exploiting Unconstrained Axes
In a standard urban planning mass-balance equation, total buildable floor area is governed by:
$$E_{\text{total}} = N_{\text{parcels}} \cdot S_{\text{parcel}} \cdot C_{\text{ocup}} \cdot N_p$$

When a regulator fixes $N_p$ to a low ceiling (such as $N_p = 2$) and heritage or facade rules lock $S_{\text{parcel}}$ and above-ground $C_{\text{ocup}}$, the system appears over-constrained—unless a developer finds an unpriced, unconstrained orthogonal axis: **$z < 0$ (the subsoil)**.

* **How London's Loophole Worked:** In boroughs like Kensington & Chelsea (RBKC) and Westminster, strict conservation-area rules, listed-building protections, and "right-to-light" laws made building upward or outward nearly impossible. Until 2015, local planning rules heavily regulated above-ground bulk and height while treating subterranean excavation largely under permissive rules. Ultra-wealthy buyers responded by excavating 3-to-4-storey subterranean mega-basements (housing pools, cinemas, and car lifts) beneath historic townhouses, multiplying floor area without altering the street-facing envelope.
* **Closing the Constraint Set:** Once neighbor complaints, structural party-wall failures, and groundwater/drainage disruption mounted, RBKC (via Policy CL7, now Policy CD11) and Camden re-constrained the $z < 0$ axis—capping new basements at **1 storey**, limiting excavation to **50% of the garden area**, mandating **1 meter of topsoil** above basement slabs for sustainable drainage (SuDS), and enforcing strict ground-movement thresholds (Burland Scale 0–1).
* **How Spanish & Canary Islands Law Handles Subsoil:** Unlike pre-2015 London, Spanish urbanism explicitly incorporates the vertical stack into planning control. Under Canary Islands Law 4/2017 (*Ley del Suelo y de los Espacios Naturales Protegidos de Canarias*), land (*suelo*) as the physical support of development rights (*aprovechamiento urbanístico*) legally comprises the surface, the airspace (*vuelo*), and the subsoil (*subsuelo*), all of which are governed by detailed planning (*ordenación pormenorizada*) and local building ordinances. Municipal plans explicitly define whether below-grade floors (*plantas bajo rasante*) count toward *edificabilidad* (typically exempting mandatory parking/utilities while counting habitable or commercial space) and cap maximum subterranean footprint (*ocupación bajo rasante*). State law (RDL 7/2015) even allows separating ground level (*rasante*), *subsuelo*, and *vuelo* into distinct superimposed property regimes (*complejos inmobiliarios urbanísticos*).

---

## 2. Urban Planning as a Discrete Constrained Optimization Problem
Every Spanish *Plan Parcial* or *Proyecto de Reparcelación* is effectively a **Mixed-Integer Nonlinear Program (MINLP)** disguised as administrative law. What you solved analytically in your homework for uniform parcels becomes a massive discrete combinatorial search in practice:

* **Discrete & Quantized Decision Variables:**
  * Integer parcel count $N \in \mathbb{Z}^+$, discrete floor counts $N_{p,i} \in \{1, 2, \dots, N_{\max}\}$ per parcel $i$, dwelling unit counts $U_i \in \mathbb{Z}^+$, and parking stalls $P_i \in \mathbb{Z}^+$.
  * Discrete parcel geometries $S_i$ bounded below by minimum parcel size ($S_i \ge 700\text{ m}^2$ in your assignment) and geometric road-frontage rules.
* **Statutory Hard Constraints (Canary Islands & State Benchmarks):**
  Your homework parameters sit right inside the statutory bounds of **Ley 4/2017 (Art. 138)** for *suelo urbanizable* and *suelo urbano no consolidado*:
  * **Gross Buildability Ceiling:** $C_e \le 1.20\text{ m}^2/\text{m}^2$ (up to $1.50$ in urban renewal/rehabilitation).
  * **Population Density Ceiling:** $\le 400\text{ inhabitants/ha}$ ($500\text{ hab/ha}$ in renewal).
  * **Public Land Cessions (*Cesiones*):** $\ge 40\text{ m}^2$ of land for public open spaces, facilities, and infrastructure per $100\text{ m}^2$ of building area (with at least $50\%$ dedicated to public open spaces)—just below the $45\text{ m}^2 / 100\text{ m}^2$ specified in your prompt.
  * **Parking & Social Housing Quotas:** $\ge 1$ off-street parking space per dwelling, plus at least $30\%$ of residential buildable area reserved for protected housing (*vivienda protegida*) in new transformations under Ley 4/2017 ($40\%$ baseline in state law RDL 7/2015).

---

## 3. Why the Discrete Solution Space Explodes (and How It Is Searched)
Once you move from identical theoretical parcels to a real irregular sector with multiple landowners, the discrete search space becomes **NP-hard**:

1. **The *Reparcelación* (Land Readjustment) Matching Problem:** Under Spanish law, original landowners contribute irregular plots and must receive urbanized parcels whose homogenized buildable value (*unidades de aprovechamiento*) matches their exact contributed share. Assigning $N$ discrete parcels and discrete building typologies to $M$ owners without fractional leftovers or monetary compensation imbalances is a **multi-dimensional integer bin-packing / partitioning problem**.
2. **Spatial Discretization & MAUP:** How a sector is partitioned into blocks, streets, and parcels directly alters spatial metrics and feasible densities—a geometric instance of the **Modifiable Areal Unit Problem (MAUP)**, where boundary placement and aggregation levels shift outcomes even when underlying land totals stay constant.
3. **Practical Solvers Used in Computational Urbanism:**
   * **MILP / CP-SAT (Constraint Programming):** Used to optimize unit mixes, protected-housing allocations, and *reparcelación* parcel assignments where exact integer satisfaction of legal quotas is mandatory.
   * **Multi-Objective Evolutionary Algorithms (e.g., NSGA-II):** Used to search large discrete street-grid and parcel-subdivision spaces along Pareto frontiers—trading off road paving length ($S_{\text{viario}}$), solar exposure, green-space connectivity, and real-estate yield.

Would you like to formalize your assignment's 4-hectare sector as a small Python MILP/CP-SAT model (e.g., optimizing heterogeneous parcel sizes and floor counts under the exact Ley 4/2017 constraints), or proceed to generating the final Spanish submission text?

---

## User
Hi I created an Urban Planning directory in my Google Drive. Can you save this conversation verbatim and the solution doc into two markdown files there?