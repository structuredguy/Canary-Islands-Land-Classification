# Rhino 8 / Grasshopper + Galapagos Guide for `Tarea_4`

## 1. Files Created
- [tarea4_sector_galapagos.3dm](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/tarea4_sector_galapagos.3dm): Rhino 8 document (units in **Meters**) containing the baked optimal 2-floor solution (`92` objects across 5 color-coded layers).
- [tarea4_galapagos.gh](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/tarea4_galapagos.gh): Grasshopper 1 parametric sector model pre-wired to **Galapagos**, initialized at **Scenario 2** ($C_e = 1.000$, $C_{\text{ocup}} = 50.0\%$) so the initial red over-height deficit ($4.44 \to 5$ floors) is immediately visible.
- [verify_galapagos_math.py](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/verify_galapagos_math.py): Standalone Python benchmark confirming the exact global optimum of the Galapagos penalty fitness function.

---

## 2. How to Run Galapagos in Rhino 8
1. Open [tarea4_galapagos.gh](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/tarea4_galapagos.gh) in Rhino 8's Grasshopper (`_Grasshopper`).
   *(Tip: If you also open [tarea4_sector_galapagos.3dm](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/tarea4_sector_galapagos.3dm), turn off layers `01`–`04` while running Galapagos so Rhino only displays Grasshopper's live preview.)*
2. Double-click the **Galapagos** component on the canvas.
3. Under the **Options** tab, verify **Fitness: Maximize** is selected (Population = `50`, Max Stagnant = `25` are pre-configured).
4. Switch to the **Solvers** tab and click **Start Solver** (Evolutionary Solver).
5. Watch the sliders (`Ce`, `C_ocup`, `n_cols`) and the 3D Rhino viewport converge from the red-deficit $S_2$ state (`Fitness = -303,200`) to the all-blue feasible 2-floor optimum (`Fitness = 53,482.5`).
6. Click **OK** to accept the winning genome.

---

## 3. Model & Fitness Formulation

### Genome (Decision Sliders)
- `Ce`: Gross Building Coefficient $\in [0.400, 1.200]\text{ m}^2\text{c}/\text{m}^2\text{s}$ (3 decimals; capped by Ley 4/2017 Art. 138).
- `C_ocup`: Plot Occupancy Coefficient $\in [0.300, 0.900]$ (3 decimals; capped at $90\%$ to preserve setbacks/courtyards).
- `n_cols`: Superblock columns along $X \in \{2, 3, 4\}$ (street width $w$ is solved analytically so total road area is exact $6,000\text{ m}^2\text{s} = 10\%$).
- *(User toggle outside Genome)* `typology`: `0 = Perimeter Setback Box`, `1 = Courtyard O-Block`.

### Scalar Fitness Function (Maximize)
$$\text{Fitness} = E_{\text{mat}} - 10 \cdot \text{Deficit} - 200{,}000 \cdot \max(0, C_{\text{ocup}} - 0.90) - 500 \cdot \max(0, 700 - S_{\text{parcela,avg}}) - 0.5 \cdot S_{\text{rem}}$$

---

## 4. Benchmark Comparison Table

| Configuration | $C_e$ | $C_{\text{ocup}}$ | $E_{\text{teórica}}$ ($\text{m}^2\text{c}$) | $S_{\text{cesiones}}$ ($\text{m}^2\text{s}$) | $S_{\text{neta}}$ ($\text{m}^2\text{s}$) | Plots | $N_{\text{plantas,exact}}$ | Deficit ($\text{m}^2\text{c}$) | Fitness |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Scenario 1 ($S_1$)** | $1.000$ | $90.0\%$ | $60,000$ | $27,000$ | $27,000$ | $38$ | $2.47$ ($3$ fl) | $11,400$ | $-65,600.0$ |
| **Scenario 2 ($S_2$)** | $1.000$ | $50.0\%$ | $60,000$ | $27,000$ | $27,000$ | $38$ | $4.44$ ($5$ fl) | $33,000$ | $-303,200.0$ |
| **Scenario 3 ($S_3$)** | $0.600$ | $90.0\%$ | $36,000$ | $16,200$ | $37,800$ | $54$ | $1.06$ ($2$ fl) | $0$ | $+36,000.0$ |
| **Scenario 4 ($S_4$)** | $0.600$ | $50.0\%$ | $36,000$ | $16,200$ | $37,800$ | $54$ | $1.90$ ($2$ fl) | $0$ | $+36,000.0$ |
| **Galapagos Optimum** | **$0.895$** | **$90.0\%$** | **$53,700$** | **$24,165$** | **$29,835$** | **$42$** | **$2.00$ ($2$ fl)** | **$0$** | **$+53,482.5$** |
| **Low-Remainder Feasible** | $0.885$ | $88.2\%$ | $53,100$ | $23,895$ | $30,105$ | $43$ | $2.00$ ($2$ fl) | $0$ | $+53,097.5$ |

---

## 5. Multi-Objective Pareto + Hard Constraint in Octopus (`tarea4_octopus_pareto.gh`)

Based on **`Octopus 0.4\Examples\Octopus Original Multi-Objective Optimization\02_twoObjectivesAndHardConstraint.gh`**, [tarea4_octopus_pareto.gh](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/tarea4_octopus_pareto.gh) wires the 6-hectare urban sector directly into **Octopus (`OctopusOriginalComponent`)**:

1. **Genes (`G` port — 4 Sliders):**
   - `Ce` $\in [0.400, 1.200]$, `C_ocup` $\in [0.300, 0.900]$, `n_cols` $\in \{2, 3, 4\}$, `typology` $\in \{0=\text{Box}, 1=\text{O-Patio}, 2=\text{U}, 3=\text{H}, 4=\text{Opposed-C}\}$.
2. **Objectives (`O` port — `Oct_Objs` + `Oct_Names`):**
   - **Obj 1 (`-E_mat [m2c]`):** Negated so Octopus's minimizer **maximizes** 2-floor floor area (up to $53,700\text{ m}^2\text{c}$).
   - **Obj 2 (`C_ocup [%]`):** Minimizes plot footprint coverage (maximizes private gardens/courtyards).
   - **Obj 3 (`Remainder [m2s]`):** Minimizes leftover parcel remainder $\pmod{700\text{ m}^2\text{s}}$.
3. **Boolean Hard Constraint (`O` port — `Np<=2 Valid`):**
   - Outputs `True` iff $N_{\text{plantas,exact}} \le 2.0$ and $S_{\text{parcela,avg}} \ge 700\text{ m}^2\text{s}$. Octopus automatically throws away any genome that outputs `False` (no penalty weights needed).
4. **3D Phenotype (`P` port — `SectorMesh`):**
   - Feeds a vertex-colored 3D mesh of the entire sector into Octopus so checking **Meshes** in the Octopus viewport displays every Pareto-optimal solution as a 3D miniature urban sector. Right-click any solution cube/mesh $\to$ **Reinstate Solution** to push its parameters back into Rhino 8.

> [!NOTE]
> **Rhino 8 `.NET Core` vs. `.NET Framework` Compatibility (`System.Random` Warning):**
> Octopus 0.4 was compiled for `.NET Framework 4.8` (where `System.Random` is marked `[Serializable]`). Rhino 8 runs on `.NET Core` (`System.Private.CoreLib`) by default, where Microsoft removed `[Serializable]` from `System.Random`.
> - Both [tarea4_octopus_pareto.gh](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/tarea4_octopus_pareto.gh) and the example files in `Octopus 0.4\Examples` have had their legacy `gaByteArr` history cleared (`ga_count = 0`) so they open in Rhino 8 with **zero popup warning** (keeping all gene, objective, constraint, and mesh wires intact).
> - If you want Octopus to **save** its internal Pareto history inside the `.gh` file without a `System.Random` serialization warning, run `_SetDotNetRuntime` in the Rhino 8 command line, select **`Runtime=NETFramework`**, and restart Rhino 8.


