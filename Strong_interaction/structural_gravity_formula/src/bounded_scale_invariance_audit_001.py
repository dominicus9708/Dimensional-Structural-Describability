from pathlib import Path
import csv
import math

BASE = Path(__file__).resolve().parents[1]
OUTPUT = BASE / "results" / "bounded_scale_invariance_audit_001.csv"

# Arbitrary positive reference values chosen only to test algebraic invariance.
m_B = 2.0
ell_B = 3.0
N_B = 120.0
C_eps = 12.0
R_D = C_eps / N_B

# Pure descriptive regrouping and resolution changes.
k_group = 3.0
a_resolution = 5.0

rows = []
for d in range(1, 7):
    # Additive d-measure attached to one bounded realization.
    v_B = ell_B ** d
    M = N_B * m_B
    V_sum = N_B * v_B
    L_sum = V_sum ** (1.0 / d)

    # Two hierarchy-invariant quantities.
    specific_measure = v_B / m_B
    kappa_inv = (ell_B ** (d - 2.0) / m_B) * (R_D / C_eps) ** (2.0 / d)
    kappa_macro = (L_sum ** (d - 2.0)) / M

    # A nontrivial dimensionless packing factor relative to a supplied external extent.
    L_ext = 1.5 * L_sum
    packing = V_sum / (L_ext ** d)

    # Pure regrouping: k lower bounded units become one higher-level descriptive unit.
    m_g = k_group * m_B
    v_g = k_group * v_B
    ell_g = v_g ** (1.0 / d)
    N_g = N_B / k_group
    C_g = C_eps
    R_g = C_g / N_g
    M_g = N_g * m_g
    V_g = N_g * v_g
    L_g = V_g ** (1.0 / d)
    kappa_g = (ell_g ** (d - 2.0) / m_g) * (R_g / C_g) ** (2.0 / d)
    packing_g = V_g / (L_ext ** d)

    # Resolution change: physical source and bounded level fixed.
    C_r = a_resolution * C_eps
    R_r = a_resolution * R_D
    kappa_r = (ell_B ** (d - 2.0) / m_B) * (R_r / C_r) ** (2.0 / d)

    rows.append({
        "d": d,
        "M": f"{M:.16e}",
        "L_sum": f"{L_sum:.16e}",
        "specific_measure_v_per_m": f"{specific_measure:.16e}",
        "kappa_inv": f"{kappa_inv:.16e}",
        "kappa_macro_equivalent": f"{kappa_macro:.16e}",
        "kappa_macro_ratio": f"{kappa_inv / kappa_macro:.16e}",
        "regroup_kappa_ratio": f"{kappa_g / kappa_inv:.16e}",
        "resolution_kappa_ratio": f"{kappa_r / kappa_inv:.16e}",
        "regroup_mass_ratio": f"{M_g / M:.16e}",
        "regroup_measure_ratio": f"{V_g / V_sum:.16e}",
        "packing_factor": f"{packing:.16e}",
        "regroup_packing_ratio": f"{packing_g / packing:.16e}",
    })

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {OUTPUT}")
