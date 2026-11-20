# Tarea 4 — Juridical Presentation Map (`master.tex` Tree + Side Jumps)

Visual workspace: [tarea4_presentation_mindmap.canvas](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/tarea4_presentation_mindmap.canvas) (Obsidian JSON Canvas).

> **Audience Rule (Juridical / Urban-Law Readers):** Exclude software/tooling jargon (`CAD`, `Rhino`, `Grasshopper`, `Galapagos`, `SciPy`, `SLSQP`, `differential_evolution`). Those notes sit inside the `# INTERNAL ONLY — DO NOT CONVERT TO LATEX` group on the canvas.

---

## 1. Exported LaTeX Tree (`master.tex -> sec1..sec4 -> sub*`)

1. **Group 1 — `Input` (`sec1_statutory_model.tex`)**
   - `sub1_1_sector_specs.tex`: 6 ha (`60,000 m2s`), `10%` roads, `0.45` cessions, `700 m2s` min lot, `BCR` & `Gross/Net FAR` legal glossary (`fig1`)
   - `sub1_2_scenarios_s1_s4.tex`: `S1–S4` table (`38` vs `54` plots, `-19%` / `-55%` floor deficits)
   - `sub1_3_two_floor_frontier.tex`: Two-floor **Pareto Efficiency Frontier** (Arrow & Debreu, `1954` — *Nobel Prizes 1972/1983*) $\text{Gross FAR}_{\max}(\text{BCR}) = \frac{1.8\,\text{BCR}}{1 + 0.9\,\text{BCR}}$, impossibility of `FAR = 1.0` (`BCR > 90.91%`, `fig2`, `fig3`)
2. **Group 2 — `Legal` (`sec2_legal_realities.tex`)**
   - `sub2_1_tau_outlets.tex`: `TAU` transfers vs. subsoil & attics (why exempt mandatory garages are not an outlet vs. extra bays / sloped *semisótanos* / habitable *bajo cubierta* `> 1.50–1.80 m`)
   - `sub2_2_muni_cession.tex`: `10%–15%` PMS cession as serviced net plots free of urbanization charges (`100%` urbanization funded by promoter)
   - `sub2_3_scale_limits.tex`: Scale effects & land quantization (`700 m2s` plot cliffs vs. mega-sector market absorption)
3. **Group 3 — `Market` (`sec3_market_economics.tex`)**
   - `sub3_1_price_quartiles.tex`: Market price quartiles (`Q25–Q75`), IQR spread, right-skewed expected margin vs. downside stability — **Risk–Efficiency Frontier** (Markowitz, `1952` — *Nobel Prize 1990*, `fig5`)
   - `sub3_2_unified_cost.tex`: Physical construction cost economies & **underground garage inflection (`BCR > 70%` or `>= 3` floors)** (`fig6`)
   - `sub3_3_market_priors.tex`: Expert market sensitivity expectations (combining empirical comparables with marginal price-sensitivity judgment)
4. **Group 4 — `Affordability` (`sec4_mixed_vpo_synthesis.tex`)**
   - `sub4_1_decoupled_frontier.tex`: `40%` VPO statutory reserve on total `m2t` buildability (`10%` PMS + `30%` Promoter) -> decoupled zone coverages `BCR_M` and `BCR_V`
   - `sub4_2_vpo_2f_vs_5f.tex`: Strict 2-floor VPO (`44.7M EUR`) vs. 5-floor VPO towers (`47.1M EUR`, both accounting for shared underground garages) (`fig7`)

---

## 2. Internal Tooling Nodes (`# DO NOT CONVERT TO LATEX`)

- **Obsidian Group (`x=860`):** `[INTERNAL] Rhino 8 + Grasshopper + Galapagos` and `[INTERNAL] SciPy Solver Backend` verify numeric bounds and figures behind the scenes and are omitted when exporting `master.tex`.

---

## 3. Critical Juridical Side Jumps (`\ref{}` / `\hyperref`)

1. `sub1_2_scenarios_s1_s4` $\dashrightarrow$ `sub2_1_tau_outlets`: *Why statutory floor deficits require TAU / bajo cubierta rather than exempt garages.*
2. `sub1_3_two_floor_frontier` $\dashrightarrow$ `sub3_1_price_quartiles`: *Why maximum statutory yield (`Gross FAR = 0.895`) lies away from the market's efficient economic peak (`~0.58–0.61`).*
3. `sub2_2_muni_cession` $\dashrightarrow$ `sub4_1_decoupled_frontier`: *Folding the `10%` PMS cession into the `40%` VPO buildability budget.*
4. `sub3_2_unified_cost` $\dashrightarrow$ `sub4_2_vpo_2f_vs_5f`: *Triggering shared underground garage costs when VPO compacts to `90% BCR` or `5-floor` towers.*

---

## 4. Economics Zotero References Added (`MAJDJRX8`)

- **Arrow & Debreu (`1954`)** (`ZKUGY52H`, `arrowExistenceEquilibriumCompetitive1954`): *"Existence of an Equilibrium for a Competitive Economy"*, *Econometrica* `22(3)`, `265–290`, DOI `10.2307/1907353`.
- **Markowitz (`1952`)** (`G7A3WPIB`, `markowitzPortfolioSelection1952`): *"Portfolio Selection"*, *The Journal of Finance* `7(1)`, `77–91`, DOI `10.1111/j.1540-6261.1952.tb01525.x`.
