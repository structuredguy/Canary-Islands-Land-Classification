# Workspace Agent Instructions (`Canary-Islands-Land-Classification`)

## 1. Mandatory Urban-Planning Terminology (English <-> Spanish)

When writing English code comments, charts, reports, or optimization outputs for Canary Islands (*Ley 4/2017*, *Decreto 183/2018*, *RDL 7/2015*) exercises, **always use exact international zoning terminology** instead of literal translations:

| Spanish Statutory Term | Required English Term | Symbol / Formula | Do Not Use |
| :--- | :--- | :--- | :--- |
| *Ocupacion de parcela* | **`BCR` (Building Coverage Ratio)** / Lot Coverage (`%`) | $\text{BCR} = S_{\text{footprint}} / S_{\text{neta}}$ | *"Occupancy"* (in US CRE/MBS, occupancy means leased share or Owner/Second/Investor status) |
| *Edificabilidad bruta* | **`Gross FAR`** (Gross Floor Area Ratio) | $\text{Gross FAR} = C_e = E_{\text{teorica}} / S_{\text{bruta}}$ ($\text{m}^2_t / \text{m}^2_s$) | *"Constructability"* (use *buildable area* for $\text{m}^2_t$, **`Gross FAR`** for the dimensionless ratio) |
| *Edificabilidad neta* | **`Net FAR`** (Net Floor Area Ratio) | $\text{Net FAR} = E_{\text{teorica}} / S_{\text{neta}} = \text{BCR} \cdot N_p$ | — |
| *Suelo bruto / neto* | Gross sector area / Net buildable land | $S_{\text{bruta}}$, $S_{\text{neta}}$ ($\text{m}^2_s$) | — |
| *Techo edificable / construido* | Gross floor area (GFA) / Buildable area | $E_{\text{teorica}}$ ($\text{m}^2_t$ or $\text{m}^2_c$) | — |

- When referencing `Ley 4/2017` or `Tarea_3`/`Tarea_4` Spanish problem statements, Spanish terms (*ocupacion*, *edificabilidad bruta/neta*) may be cited in italics alongside **`BCR`** and **`Gross FAR` / `Net FAR`**.
- Note on US agency housing terminology: `1-4 units` is the *Property Unit Count* defining "Single-Family" vs. `5+` Multifamily; *Occupancy* denotes Owner-Occupied vs. Second Home vs. Investment.

## 2. Statutory Baseline Reminders (`Tarea_4` & `Tarea_3`)

- **Protected Housing (`VPO`) Reserve:** Statutory percentages (`40%` RDL 7/2015 Art. 20.1.b; `>= 30%` Canary floor Ley 4/2017 Art. 138) apply to **total buildable floor area (`E_teorica` in $\text{m}^2_t$)**, NOT net land area (`S_neta`).
- **Municipal Cession (`10%` PMS):** Under Ley 4/2017 Art. 44.c, `10%` of lucrative development rights are ceded as **serviced net plots free of urbanization charges** (promoter still funds `100%` of sector urbanization).
- **Decoupled Mixed Sectors:** Splitting Market vs. VPO zones replaces uniform `BCR` with **`(BCR_M, BCR_V)`**, linked along the height-binding frontier to `Gross FAR` via:
  $$\text{Gross FAR}_{\max} = \frac{0.90}{0.45 + \frac{1 - \alpha_{\text{VPO}}}{N_{p,M}\,\text{BCR}_M} + \frac{\alpha_{\text{VPO}}}{N_{p,V}\,\text{BCR}_V}}$$

## 3. Charting & Code Conventions

- Always generate **mobile-optimized `.svg` files** (`viewBox`, responsive width, sans-serif fonts); never write `.png` copies alongside `.svg`.
- Verify every generated chart with in-memory `RapidOCR` to guarantee zero text overlap and readable labels.
- Use `# %%` cell separators and ASCII-only identifiers/comments in Python scripts.
