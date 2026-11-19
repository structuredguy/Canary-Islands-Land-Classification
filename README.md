# Canary Islands Land Classification & Urban Planning

Repository covering Canary Islands urban planning law (*Ley 4/2017*, *Decreto 183/2018*, *RDL 7/2015*) alongside parametric sector modeling and economic optimization workflows (`Tareas/Tarea_3`, `Tareas/Tarea_4`).

## Standardized Zoning Terminology

For cross-agent and cross-module conventions, see [AGENTS.md](file:///c:/dev/Canary-Islands-Land-Classification/AGENTS.md):

- **`BCR` (Building Coverage Ratio / Lot Coverage %)** replaces literal *"occupancy"* for Spanish *ocupacion de parcela* ($S_{\text{footprint}} / S_{\text{neta}}$).
- **`Gross FAR`** replaces *"constructability"* for gross buildability coefficient $C_e = E_{\text{teorica}} / S_{\text{bruta}}$ ($\text{m}^2_t / \text{m}^2_s$).
- **`Net FAR`** denotes net buildability over buildable plots ($E_{\text{teorica}} / S_{\text{neta}} = \text{BCR} \cdot N_p$).
