from __future__ import annotations

import csv
from pathlib import Path

M_U_KG = 1.66053906892e-27  # 2022 CODATA atomic mass constant

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
INPUT = ROOT / "data" / "one_kg_bounded_unit_inputs_001.csv"
OUTPUT = ROOT / "results" / "one_kg_bounded_unit_invariance_001.csv"


def main() -> None:
    rows = []
    with INPUT.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            ar = float(row["relative_atomic_mass_u"])
            k = float(row["group_size_k"])
            M = float(row["total_mass_kg"])
            R = float(row["radius_m"])
            C = float(row["C_epsilon"])

            m_base = ar * M_U_KG
            m_B = k * m_base
            N_B = M / m_B
            R_D = C / N_B

            M_reconstructed = m_B * C / R_D

            X_scale = M / R
            G_scale = M / (R**2)
            K_scale = M / (R**3)

            X_from_descriptor = M_reconstructed / R
            G_from_descriptor = M_reconstructed / (R**2)
            K_from_descriptor = M_reconstructed / (R**3)

            rows.append({
                **row,
                "m_base_kg": f"{m_base:.16e}",
                "m_B_kg": f"{m_B:.16e}",
                "N_B": f"{N_B:.16e}",
                "R_D": f"{R_D:.16e}",
                "M_reconstructed_kg": f"{M_reconstructed:.16e}",
                "X_scale_M_over_R": f"{X_scale:.16e}",
                "G_scale_M_over_R2": f"{G_scale:.16e}",
                "K_scale_M_over_R3": f"{K_scale:.16e}",
                "X_from_descriptor": f"{X_from_descriptor:.16e}",
                "G_from_descriptor": f"{G_from_descriptor:.16e}",
                "K_from_descriptor": f"{K_from_descriptor:.16e}",
                "mass_reconstruction_rel_error": f"{abs(M_reconstructed-M)/M:.3e}",
            })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    with OUTPUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
