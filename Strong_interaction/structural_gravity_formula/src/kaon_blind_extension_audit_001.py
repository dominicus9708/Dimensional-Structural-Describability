from pathlib import Path
import csv
import math

HBARC_GEV_FM = 0.1973269804

BASE = Path(__file__).resolve().parents[1]
INPUT = BASE / "data" / "kaon_blind_extension_inputs_001.csv"
OUTPUT = BASE / "results" / "kaon_blind_extension_audit_001.csv"

rows = []
with INPUT.open("r", encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
        mode = row["input_mode"]
        mass = float(row["mass_GeV"])

        if mode == "derive_from_Breit_and_LF":
            rB = float(row["r_B_fm"])
            rperp = float(row["r_perp_fm"])
            rB2 = (rB / HBARC_GEV_FM) ** 2
            rperp2 = (rperp / HBARC_GEV_FM) ** 2
            Aprime = rperp2 / 4.0
            # Paper convention: r_B^2 = 6 A'(0) - 3/(4m^2) [1 + 2 C(0)],
            # with C(0) the spin-zero D-term form factor in that convention.
            D0 = ((4.0 * mass**2 / 3.0) * (6.0 * Aprime - rB2) - 1.0) / 2.0
            rA = math.sqrt(6.0 * Aprime) * HBARC_GEV_FM
            absD = abs(D0)
        elif mode == "direct_A_radius_and_D":
            rA = float(row["r_A_fm"])
            absD = abs(float(row["abs_D0"]))
            Aprime = (rA / HBARC_GEV_FM) ** 2 / 6.0
            D0 = -absD  # sign not used; source reports pressure-form-factor magnitude convention
        else:
            raise ValueError(mode)

        base = rA / mass
        frozen = absD * base

        rows.append({
            "framework": row["framework"],
            "candidate": row["candidate"],
            "mass_GeV": f"{mass:.12e}",
            "A_prime_GeV-2": f"{Aprime:.12e}",
            "r_A_fm": f"{rA:.12e}",
            "abs_D0": f"{absD:.12e}",
            "ell_over_m_fm_per_GeV": f"{base:.12e}",
            "frozen_absD_ell_over_m_fm_per_GeV": f"{frozen:.12e}",
            "source": row["source"],
        })

by_framework = {}
for row in rows:
    by_framework.setdefault(row["framework"], {})[row["candidate"]] = row

for framework, group in by_framework.items():
    if "pion" not in group or "kaon" not in group:
        continue
    pi = group["pion"]
    k = group["kaon"]
    pi_base = float(pi["ell_over_m_fm_per_GeV"])
    k_base = float(k["ell_over_m_fm_per_GeV"])
    pi_F = float(pi["abs_D0"])
    k_F = float(k["abs_D0"])
    pi_inv = float(pi["frozen_absD_ell_over_m_fm_per_GeV"])
    k_inv = float(k["frozen_absD_ell_over_m_fm_per_GeV"])

    required_F_K_over_pi = pi_base / k_base
    observed_D_K_over_pi = k_F / pi_F
    frozen_K_over_pi = k_inv / pi_inv
    missing_factor = required_F_K_over_pi / observed_D_K_over_pi

    for target in (pi, k):
        target["required_F_K_over_pi_for_universality"] = f"{required_F_K_over_pi:.12e}"
        target["observed_absD_K_over_pi"] = f"{observed_D_K_over_pi:.12e}"
        target["frozen_candidate_K_over_pi"] = f"{frozen_K_over_pi:.12e}"
        target["missing_dimensionless_factor_K_over_pi"] = f"{missing_factor:.12e}"

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
fieldnames = list(rows[0].keys())
for extra in [
    "required_F_K_over_pi_for_universality",
    "observed_absD_K_over_pi",
    "frozen_candidate_K_over_pi",
    "missing_dimensionless_factor_K_over_pi",
]:
    if extra not in fieldnames:
        fieldnames.append(extra)

with OUTPUT.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {OUTPUT}")
