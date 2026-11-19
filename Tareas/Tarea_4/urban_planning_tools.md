# Urban Planning Software, Web Platforms & Python Stack

Tools that directly model parcel subdivision, Gross Building Coefficient (FAR / $C_e$), Plot Occupancy ($C_{\text{ocup}}$), courtyard massing (O/U/H), and discrete constrained optimization—grouped by workflow.

---

## 1. Web Apps (Instant Massing, FAR & Coverage)

| Tool | Best For | How It Maps to Tarea 4 |
| :--- | :--- | :--- |
| **TestFit** | Automated site feasibility & unit/parking yield | Input FAR ($C_e$), height ($N_p$), setbacks, and parking ratios; solves building footprints + parking garages in real time. |
| **Giraffe** (`giraffe.build`) | Map-first master planning & GIS overlays | Draw O/U/H footprints on parcels, extrude stories, and get live FAR ($C_e$), site coverage ($C_{\text{ocup}}$), and financial pro-forma tables. |
| **Autodesk Forma** | Conceptual massing + environmental analysis | Parametric block/courtyard layouts with live FAR/coverage tracking plus real-time sun, wind, daylight, and noise simulation. |
| **Digital Blue Foam** | Rapid generative site prototyping | Browser-based zoning envelope and courtyard massing exploration. |

---

## 2. Desktop Apps (Including Your Existing Stack)

* **Rhino 8 + Grasshopper** *(already in your workspace)*:
  * Industry standard for parametric parcel subdivision, O/U/H courtyard generation, and evolutionary optimization (**Galapagos** for single-objective, **Wallacei** for multi-objective NSGA-II Pareto fronts).
* **QGIS** *(already in your workspace)*:
  * **02UrbanPlanning** plugin (with *ParcelFlux*): generates street networks, subdivides blocks into parcels, and tests site coverage, setbacks, and FAR caps in 3D.
* **ArcGIS CityEngine** *(Esri)*:
  * Procedural **CGA grammar** rules that subdivide whole sectors into parcels and extrude buildings up to FAR/occupancy/height caps at city scale.

---

## 3. Python Packages (Optimization & Spatial Geometry)

* **Discrete Constrained Optimization (Exact & Evolutionary):**
  * **`ortools` (Google OR-Tools CP-SAT / MILP):** Best for discrete *reparcelación*, exact integer plot counts ($N_{\text{parcelas}}$), discrete floor counts ($N_p$), and statutory quotas (VPO, parking).
  * **`pymoo`:** Multi-objective evolutionary optimization (NSGA-II) for trading off road length ($S_{\text{viario}}$), yield, and compactness.
* **Urban Geometry & Morphology:**
  * **`shapely` & `geopandas`:** Core polygon operations (setbacks via negative buffers, O/U/H footprint intersection, net land subtraction).
  * **`momepy`:** Quantitative urban morphology (blocks, plots, courtyards, building-to-plot coverage ratios).
  * **`osmnx`:** Pulls real street networks and building footprints from OpenStreetMap for benchmarking.

---

## 4. Recommended Combo for Exploring Tarea 4

1. **Python (`ortools` + `shapely`)** to solve discrete parcel & floor combinations mathematically.
2. **Rhino 8 / Grasshopper** (or **QGIS**) to generate the 3D O/U/H massing and verify footprints visually.
