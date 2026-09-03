from pathlib import Path
import csv
import math

C = 299_792_458.0
G_REF = 6.67430e-11  # comparison only; never used to construct K0

BASE = Path(__file__).resolve().parents[1]
INPUT = BASE / "data" / "geometric_distortion_constant_inputs_001.csv"
OUTPUT = BASE / "results" / "geometric_distortion_constant_audit_001.csv"

rows = []
with INPUT.open("r", encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
        M = float(row["M_kg"])
        rho = float(row["rho_kg_m3"])

        # Density-derived characteristic length.
        L_rho = (M / rho) ** (1.0 / 3.0)

        # Resolution- and hierarchy-invariant L/M combination obtained from
        # R_D=C_epsilon/N_B and M=m_B*C_epsilon/R_D.
        Lambda_X = L_rho / M

        # Candidate source-specific geometric response scale with F_B = 1.
        K0 = C**2 * Lambda_X

        rows.append({
            **row,
            "L_rho_m": f"{L_rho:.16e}",
            "Lambda_X_m_per_kg": f"{Lambda_X:.16e}",
            "K0_m3_kg-1_s-2": f"{K0:.16e}",
            "K0_over_Gref": f"{K0 / G_REF:.16e}",
            "F_required_if_forced_to_Gref": f"{G_REF / K0:.16e}",
        })

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {OUTPUT}")
