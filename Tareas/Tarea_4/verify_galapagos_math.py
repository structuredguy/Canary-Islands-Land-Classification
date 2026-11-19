# -*- coding: utf-8 -*-
"""
Mathematical Verification & Benchmark for Tarea 4 Rhino/Galapagos Optimization.
Cross-checks the exact single-objective penalty fitness function proposed for
Grasshopper + Galapagos against the analytical 2-floor feasibility boundary.
"""

import math
import numpy as np

# %% Fixed Assignment Parameters (DNI last digit = 4 -> 6 ha)
S_BRUTA = 60000.0       # m2s
R_VIARIO = 0.10         # 10%
S_VIARIO = S_BRUTA * R_VIARIO  # 6,000 m2s
R_CES = 0.45            # 45 m2s per 100 m2c
S_MIN_PLOT = 700.0      # m2s
NP_CAP = 2              # Max floors in Question 3
CE_LEGAL_MAX = 1.20     # Ley 4/2017 Art. 138 ceiling


def evaluate_sector(ce: float, c_ocup: float, c_ocup_cap: float = 0.90) -> dict:
    """Evaluate all urban planning KPIs and Galapagos scalar fitness."""
    e_teorica = S_BRUTA * ce
    s_cesiones = R_CES * e_teorica
    s_neta = S_BRUTA - S_VIARIO - s_cesiones

    n_parcelas = int(math.floor(s_neta / S_MIN_PLOT)) if s_neta >= S_MIN_PLOT else 0
    s_parcela_avg = (s_neta / n_parcelas) if n_parcelas > 0 else 0.0
    s_remainder = s_neta - n_parcelas * S_MIN_PLOT if n_parcelas > 0 else s_neta

    s_ocup_total = s_neta * c_ocup
    n_plantas_exact = (e_teorica / s_ocup_total) if s_ocup_total > 0 else float("inf")
    n_plantas_ceil = int(math.ceil(n_plantas_exact)) if math.isfinite(n_plantas_exact) else 999

    e_cap_2floors = NP_CAP * s_ocup_total
    e_materializada = min(e_teorica, e_cap_2floors)
    deficit = max(0.0, e_teorica - e_cap_2floors)

    # Single-objective Galapagos fitness (to MAXIMIZE):
    # Maximize materialized 2-floor floor area while strictly penalizing:
    # 1) Unbuilt deficit above 2 floors (N_plantas > 2)
    # 2) Occupancy exceeding realistic cap (e.g., 90% to preserve patios/setbacks)
    # 3) Plot size below 700 m2s
    # 4) Small tie-breaker favoring cleaner plot subdivision (low remainder)
    p_height = 10.0 * deficit
    p_ocup_cap = 200000.0 * max(0.0, c_ocup - c_ocup_cap)
    p_plot = 500.0 * max(0.0, S_MIN_PLOT - s_parcela_avg) if n_parcelas > 0 else 1e7
    p_rem = 0.5 * s_remainder

    fitness = e_materializada - p_height - p_ocup_cap - p_plot - p_rem

    return {
        "Ce": ce,
        "C_ocup": c_ocup,
        "E_teorica": e_teorica,
        "S_cesiones": s_cesiones,
        "S_neta": s_neta,
        "N_parcelas": n_parcelas,
        "S_parcela_avg": s_parcela_avg,
        "S_remainder": s_remainder,
        "S_ocup_total": s_ocup_total,
        "N_plantas_exact": n_plantas_exact,
        "N_plantas_ceil": n_plantas_ceil,
        "E_cap_2floors": e_cap_2floors,
        "E_materializada": e_materializada,
        "Deficit": deficit,
        "Feasible_2floors": (deficit <= 1e-6) and (c_ocup <= c_ocup_cap + 1e-9) and (n_parcelas >= 1),
        "Fitness": fitness,
    }


def ce_max_for_2floors(c_ocup: float) -> float:
    """Analytical hyperbolic boundary where N_plantas_exact == 2.0."""
    return (1.8 * c_ocup) / (1.0 + 0.9 * c_ocup)


# %% Run Verification Sweep & Evolutionary Cross-Check
def main():
    print("=== 1. Assignment Scenarios S1..S4 ===")
    scenarios = [
        ("S1 (Ce=1.0, Ocup=90%)", 1.0, 0.90),
        ("S2 (Ce=1.0, Ocup=50%)", 1.0, 0.50),
        ("S3 (Ce=0.6, Ocup=90%)", 0.6, 0.90),
        ("S4 (Ce=0.6, Ocup=50%)", 0.6, 0.50),
    ]
    for name, ce, oc in scenarios:
        r = evaluate_sector(ce, oc, c_ocup_cap=0.90)
        print(
            f"{name:24s} | S_neta={r['S_neta']:8.1f} | Plots={r['N_parcelas']:2d} "
            f"| Np_exact={r['N_plantas_exact']:4.2f} ({r['N_plantas_ceil']} fl) "
            f"| Deficit={r['Deficit']:7.1f} | Fitness={r['Fitness']:10.1f}"
        )

    print("\n=== 2. Grid Search Over Galapagos Domain (Ce in [0.40, 1.20], C_ocup in [0.30, 0.90]) ===")
    best = None
    best_zero_rem = None
    ce_vals = np.linspace(0.40, 1.20, 801)      # step 0.001 (matches 3-decimal GH slider)
    oc_vals = np.linspace(0.30, 0.90, 601)      # step 0.001

    for oc in oc_vals:
        for ce in ce_vals:
            res = evaluate_sector(float(ce), float(oc), c_ocup_cap=0.90)
            if best is None or res["Fitness"] > best["Fitness"]:
                best = res
            if res["Feasible_2floors"] and res["S_remainder"] < 50.0:
                if best_zero_rem is None or res["E_materializada"] > best_zero_rem["E_materializada"]:
                    best_zero_rem = res

    print("Global Optimum (C_ocup <= 90%, 3-dec slider resolution):")
    for k in ["Ce", "C_ocup", "E_teorica", "S_cesiones", "S_neta", "N_parcelas",
              "S_parcela_avg", "S_remainder", "N_plantas_exact", "Deficit", "Fitness"]:
        print(f"  {k:16s}: {best[k]:.4f}" if isinstance(best[k], float) else f"  {k:16s}: {best[k]}")

    ce_exact_90 = ce_max_for_2floors(0.90)
    print(f"\nAnalytical Hyperbolic Bound at C_ocup=0.90: Ce_max = {ce_exact_90:.6f} "
          f"(E_teorica = {S_BRUTA * ce_exact_90:.2f} m2c)")

    if best_zero_rem:
        print("\nCleanest Low-Remainder Feasible Point (remainder < 50 m2s):")
        print(f"  Ce={best_zero_rem['Ce']:.3f}, C_ocup={best_zero_rem['C_ocup']:.3f}, "
              f"Plots={best_zero_rem['N_parcelas']}, Rem={best_zero_rem['S_remainder']:.1f} m2s, "
              f"E_mat={best_zero_rem['E_materializada']:.1f} m2c, Np_exact={best_zero_rem['N_plantas_exact']:.3f}")

    # Verify also what happens if C_ocup_cap is 85% or 100%
    print("\n=== 3. Sensitivity to C_ocup Upper Bound ===")
    for cap in [0.85, 0.90, 1.00]:
        ce_b = ce_max_for_2floors(cap)
        r_b = evaluate_sector(round(ce_b, 3) - 0.001, cap, c_ocup_cap=cap)
        print(f"  Cap={cap*100:5.1f}% -> Ce*={r_b['Ce']:.3f}, E_mat={r_b['E_materializada']:8.1f} m2c, "
              f"S_neta={r_b['S_neta']:8.1f} m2s, Plots={r_b['N_parcelas']:2d}, Np={r_b['N_plantas_exact']:.3f}")

    # Hard assertions
    assert best["Feasible_2floors"], "Optimum must satisfy 2-floor cap!"
    assert best["Deficit"] == 0.0, "Optimum must have zero unbuilt deficit!"
    assert best["S_parcela_avg"] >= S_MIN_PLOT, "Average plot size must be >= 700 m2s!"
    assert best["Ce"] <= CE_LEGAL_MAX, "Ce must respect Ley 4/2017 Art. 138 cap!"
    print("\n[PASS] All mathematical checks and feasibility assertions passed.")


if __name__ == "__main__":
    main()
