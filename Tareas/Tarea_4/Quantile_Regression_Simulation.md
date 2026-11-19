# Non-Linear Quantile Regression Simulation (`Tarea_4`)

Replaces the ad-hoc `sigma_p` uncertainty heuristic in [scipy_sector_optimizer.py](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/scipy_sector_optimizer.py) with an Excel-driven **non-crossing non-linear quantile regression** workflow implemented in [quantile_profit_optimizer.py](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/quantile_profit_optimizer.py).

> **Terminology Note (per [AGENTS.md](file:///c:/dev/Canary-Islands-Land-Classification/AGENTS.md)):** This document uses **`BCR` (Building Coverage Ratio / Lot Coverage %)** for Spanish *ocupación* (`C_ocup`) and **`Gross FAR` / `Net FAR`** for gross/net *edificabilidad* (`Ce`, `e_neta`).

## 1. Spreadsheet Input Schema

Generated workbook: [market_price_quantiles_sim.xlsx](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/market_price_quantiles_sim.xlsx)

- **`Quartile_Summary`** (main input read by the optimizer): `C_ocup` (`BCR`), `Ce_2floor` (`Gross FAR` on 2-floor frontier via bijection $\text{Gross FAR} = \frac{1.8\,\text{BCR}}{1 + 0.9\,\text{BCR}}$), `n_comps`, `Q25_EUR_m2t`, `Q50_EUR_m2t`, `Q75_EUR_m2t`, `IQR_EUR_m2t`, `Bowley_Skew`, `Typology_Note`.
- **`Simulated_Raw_Comps`** (169 synthetic comparables): used strictly to cross-check grouped quartile fitting against sample-level pinball/check-loss minimization.

Edit `Quartile_Summary` directly with real market comps and re-run `python Tareas/Tarea_4/quantile_profit_optimizer.py` (the script does not overwrite an existing workbook).

## 2. Mathematical Pipeline

1. **Joint Non-Crossing 4-Parameter Logistic Curves (`SLSQP`)**:
   Each quartile $\tau \in \{0.25, 0.50, 0.75\}$ is modeled as:
   $$\hat{Q}_\tau(P \mid C_e) = L_\tau + \frac{U_\tau - L_\tau}{1 + \exp\big(k_\tau (C_e - c_{0,\tau})\big)}$$
   Fitted jointly across the 7 buckets weighted by `n_comps` via pseudo-Huber L1 minimum distance (Chamberlain grouped-quantile estimator) with strict grid non-crossing constraints ($\hat{Q}_{25} + 40 \le \hat{Q}_{50}$ and $\hat{Q}_{50} + 40 \le \hat{Q}_{75}$).
   - Sheet MAE: `Q25 = 12.6`, `Q50 = 10.6`, `Q75 = 13.7 EUR/m2t`.
   - Mean delta vs. raw 169-sample pinball-loss fit: `8.0`, `2.4`, `13.7 EUR/m2t`.

2. **Quantile Equivariance (No Monte Carlo Sampling Noise)**:
   Because Net Margin $\Pi(C_e; P) = (P - 1400)(0.90 \, S_{\text{bruta}} C_e) - 50 S_{\text{bruta}}$ is strictly affine increasing in price $P$:
   $$Q_\tau\big(\Pi \mid C_e\big) = \big(\hat{Q}_\tau(P \mid C_e) - 1400\big)(0.90 \, S_{\text{bruta}} C_e) - 50 S_{\text{bruta}}$$

3. **Closed-Form Asymmetric Split-Normal Expectation & $\text{CVaR}_{25}$**:
   From $\Delta_- = \hat{Q}_{50} - \hat{Q}_{25}$ and $\Delta_+ = \hat{Q}_{75} - \hat{Q}_{50}$, define $\sigma_- = \Delta_- / \Phi^{-1}(0.75)$ and $\sigma_+ = \Delta_+ / \Phi^{-1}(0.75)$. A 50/50 two-piece half-normal matching $(\hat{Q}_{25}, \hat{Q}_{50}, \hat{Q}_{75})$ exactly yields closed-form expected price and worst-25% conditional tail expectation:
   $$E[P \mid C_e] = \hat{Q}_{50} + \frac{\sigma_+ - \sigma_-}{\sqrt{2\pi}}, \qquad \text{CVaR}_{25}(P \mid C_e) = \hat{Q}_{50} - \sigma_- \frac{\phi(\Phi^{-1}(0.75))}{0.25}$$

## 3. Simulation Outcomes (Smooth Frontier vs. Discrete 700 m2s DE)

| Criterion | Smooth `Gross FAR*` | Smooth `BCR*` | Smooth Peak | Discrete DE `Gross FAR*` (Plots) | Discrete Margin |
| :--- | :---: | :---: | :---: | :---: | :---: |
| $\text{CVaR}_{25}$ (Downside) | `0.6180` | `49.7%` | `38.87M EUR` | `0.6251` (`53`) | `38.84M EUR` |
| $Q_{25}$ (Bear) | `0.6055` | `48.2%` | `46.87M EUR` | `0.6000` (`54`) | `46.85M EUR` |
| $Q_{50}$ (Median) | `0.5947` | `47.0%` | `56.02M EUR` | `0.6000` (`54`) | `56.01M EUR` |
| $E[\Pi]$ (Skew-Adjusted) | `0.5756` | `44.9%` | `59.64M EUR` | `0.5741` (`55`) | `59.64M EUR` |
| $Q_{75}$ (Luxury Tail) | `0.5606` | `43.3%` | `71.70M EUR` | `0.5656` (`55`) | `71.64M EUR` |

- **Right-skew optionality:** Strong positive Bowley skew at low density lifts $E[\Pi]$ (`59.64M`) above $Q_{50}$ (`56.02M`) and shifts the optimal `Gross FAR` down to `0.576` (`BCR = 44.9%`).
- **Downside compression:** Under $\text{CVaR}_{25}$ risk aversion, the optimum shifts right toward `Gross FAR = 0.618` (`BCR = 49.7%`, `50.5%` discrete), trading luxury upside for volume stability.

Visual output: [fig5_quantile_profit_opt.svg](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/fig5_quantile_profit_opt.svg)

## 4. Variable Hard Build Cost Sensitivity $C_{\text{build}}(\text{Gross FAR})$

Implemented in [cost_sensitivity_check.py](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/cost_sensitivity_check.py) ([fig6_cost_curve_sensitivity.svg](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/fig6_cost_curve_sensitivity.svg)).

1. **Why build cost decreases initially ($\text{Gross FAR} = 0.48 \to 0.78$):**
   - **Shared party walls (`medianeras`):** Shifting from detached 4-facade villas to semi-detached (`pareados`) and row townhouses (`adosados`) cuts exterior facade/insulation/scaffolding per $\text{m}^2_t$ by ~20–30%.
   - **Procurement & site mobilization:** Larger sector volume amortizes cranes, earthworks mobilization, and repetitive formwork across ~45–54k $\text{m}^2_t$ instead of ~29k $\text{m}^2_t$.
   - **Specification correlation:** Units achieving `3,400–4,150 EUR/m2t` carry bespoke finishes, pools, and curtain glazing (`~1,650–1,750 EUR/m2t`), whereas `2,060 EUR/m2t` units use standard finishes (`~1,250 EUR/m2t`).
2. **Why it kinks upward again near `90%` lot coverage ($\text{BCR} > 72\%$, $\text{Gross FAR} > 0.785$):**
   - **Surface parking exhaustion:** Statutory `>= 1` stall/dwelling no longer fits on the shrinking `10–20%` unbuilt yard, forcing excavated basement garages (`sótanos`), retaining walls, and mechanical ventilation.

| Cost Regime | `Gross FAR*` ($E[\Pi]$) | `BCR*` | Hard Cost at Opt | Peak $E[\Pi]$ | Margin at `0.895` |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Constant (`1,400 EUR/m2t`) | `0.576` | `44.9%` | `1,400 EUR/m2t` | `59.64M` | `28.95M` |
| Decreasing (`Facade + Scale`) | `0.610` | `48.7%` | `1,502 EUR/m2t` | `55.77M` | `34.81M` |
| U-Shape (`+Basement >72%`) | `0.608` | `48.5%` | `1,505 EUR/m2t` | `55.72M` | `22.48M` |

## 5. Mixed Subsidized Housing (`40% VPO`) + Market Decoupling (`Tarea_3` + `Tarea_4`)

Implemented in [vpo_mixed_optimizer.py](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/vpo_mixed_optimizer.py) ([fig7_vpo_mixed_opt.svg](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_4/fig7_vpo_mixed_opt.svg)).

1. **What `40%` Applies To:** In [Tarea_3.md](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_3/Tarea_3.md#L146-L150) & [line 231](file:///c:/dev/Canary-Islands-Land-Classification/Tareas/Tarea_3/Tarea_3.md#L231), the statutory VPO reserve (`40%` RDL 7/2015 Art. 20.1.b; `>= 30%` Canary floor Ley 4/2017 Art. 138) applies to **total residential buildability $E_{\text{teorica}}$ ($\text{m}^2_t$)**, NOT net land area (`S_neta`). At `40%` total VPO = `10%` Municipal PMS + `30%` Promoter VPO, leaving `60%` free market.
2. **Search Space Expansion (`2D -> 3D/4D`):** Splitting lot coverage into $\text{BCR}_M$ (Market) and $\text{BCR}_V$ (VPO) yields a 3D search `(Gross FAR, BCR_M, BCR_V)` (or 4D with VPO floor cap $N_{p,V}$). On the height-binding frontier:
   $$\text{Gross FAR}_{\max}(\text{BCR}_M, \text{BCR}_V) = \frac{0.90}{0.45 + \frac{0.60}{2\,\text{BCR}_M} + \frac{0.40}{N_{p,V}\,\text{BCR}_V}}$$
3. **Single Unified Construction Cost (`unified_build_cost`):** All regimes share ONE physical cost equation combining envelope S/V + scale via $\text{Net FAR}_{\text{zone}} = N_p \cdot \text{BCR}$, vertical elevator/seismic core cost ($N_p \ge 3$), **common underground garage (`+250 EUR/m2t` when `BCR > 70%` or `Np >= 3`)**, and finish tier (luxury market vs. basic statutory VPO).

| Regime (`Unified Cost`) | `Gross FAR*` | `BCR_M*` | `BCR_V*` (`NpV`) | $C_{\text{mkt}}$ | $C_{\text{vpo}}$ | $S_{\text{mkt}}$ | $S_{\text{vpo}}$ | Peak $E[\Pi]$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `0%` VPO Baseline | `0.6106` | `48.8%` | — | `1,533` | — | `33,763 m2s` | `0 m2s` | `54.72M` |
| `40%` VPO Strict $N_p \le 2$ | `0.6696` | `44.6%` | `90.0%` (`2F`) | `1,574` | `1,417` | `26,994 m2s` | `8,928 m2s` | `44.75M` |
| `40%` VPO `Tarea_3` 5F Towers | `0.7152` | `45.3%` | `55.0%` (`5F`) | `1,568` | `1,462` | `28,448 m2s` | `6,242 m2s` | `47.06M` |


