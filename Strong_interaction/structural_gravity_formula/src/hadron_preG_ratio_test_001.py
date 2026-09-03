from pathlib import Path
import csv
import math

HBARC_GEV_FM = 0.1973269804
MPI_GEV = 0.169
QMAX_GEV = 2.0

BASE = Path(__file__).resolve().parents[1]
INPUT = BASE / "data" / "hadron_minimal_bounded_candidates_001.csv"
OUTPUT = BASE / "results" / "hadron_preG_ratio_test_001.csv"


def z_and_derivative_at_zero(mpi_GeV=MPI_GEV, qmax_GeV=QMAX_GEV):
    tcut = 4.0 * mpi_GeV**2
    t0 = tcut * (1.0 - math.sqrt(1.0 + qmax_GeV**2 / tcut))
    a = math.sqrt(tcut)
    b = math.sqrt(tcut - t0)
    z0 = (a - b) / (a + b)
    dzdt0 = -b / (a * (a + b) ** 2)
    return z0, dzdt0


def a0_and_derivative(row):
    model = row["fit_model"]
    if model in {"monopole", "dipole"}:
        n = 1 if model == "monopole" else 2
        ag = float(row["A_g_p0"])
        lg = float(row["A_g_p1"])
        aq = float(row["A_q_p0"])
        lq = float(row["A_q_p1"])
        A0 = ag + aq
        dA = n * ag / lg**2 + n * aq / lq**2
        return A0, dA

    if model == "zexp":
        z0, dzdt0 = z_and_derivative_at_zero()
        A0 = 0.0
        dA = 0.0
        for prefix in ("A_g", "A_q"):
            a0 = float(row[f"{prefix}_p0"])
            a1 = float(row[f"{prefix}_p1"])
            a2 = float(row[f"{prefix}_p2"])
            A0 += a0 + a1 * z0 + a2 * z0**2
            dA += (a1 + 2.0 * a2 * z0) * dzdt0
        return A0, dA

    raise ValueError(model)


def comparison_family(model):
    # The published preferred fits differ: pion uses monopole, proton uses dipole.
    # They are paired as the authors' preferred pole-family fits. z-expansion is
    # kept as the common model-dependence cross-check.
    return "preferred_pole" if model in {"monopole", "dipole"} else "zexp"


rows = []
with INPUT.open("r", encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
        A0, dA = a0_and_derivative(row)
        ell_A_fm = math.sqrt(6.0 * dA / A0) * HBARC_GEV_FM
        mass_GeV = float(row["mass_GeV"])
        Dabs = abs(float(row["D_total"]))
        base = ell_A_fm / mass_GeV
        weighted = Dabs * base
        rows.append({
            "candidate": row["candidate"],
            "fit_model": row["fit_model"],
            "comparison_family": comparison_family(row["fit_model"]),
            "mass_GeV": f"{mass_GeV:.10e}",
            "A0": f"{A0:.10e}",
            "dA_dt_GeV-2": f"{dA:.10e}",
            "ell_A_fm": f"{ell_A_fm:.10e}",
            "ell_over_m_fm_per_GeV": f"{base:.10e}",
            "abs_D0": f"{Dabs:.10e}",
            "D_weighted_ell_over_m_fm_per_GeV": f"{weighted:.10e}",
        })

by_family = {}
for row in rows:
    by_family.setdefault(row["comparison_family"], {})[row["candidate"]] = row

for family, group in by_family.items():
    if "pion" in group and "proton" in group:
        pi = group["pion"]
        p = group["proton"]
        base_ratio = float(pi["ell_over_m_fm_per_GeV"]) / float(p["ell_over_m_fm_per_GeV"])
        weighted_ratio = float(pi["D_weighted_ell_over_m_fm_per_GeV"]) / float(p["D_weighted_ell_over_m_fm_per_GeV"])
        required_F_ratio = 1.0 / base_ratio
        observed_D_ratio = float(pi["abs_D0"]) / float(p["abs_D0"])
        for target in (pi, p):
            target["pair_base_ratio_pi_over_p"] = f"{base_ratio:.10e}"
            target["required_F_pi_over_p_for_universality"] = f"{required_F_ratio:.10e}"
            target["observed_absD_pi_over_p"] = f"{observed_D_ratio:.10e}"
            target["pair_Dweighted_ratio_pi_over_p"] = f"{weighted_ratio:.10e}"

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
fieldnames = list(rows[0].keys())
for extra in [
    "pair_base_ratio_pi_over_p",
    "required_F_pi_over_p_for_universality",
    "observed_absD_pi_over_p",
    "pair_Dweighted_ratio_pi_over_p",
]:
    if extra not in fieldnames:
        fieldnames.append(extra)

with OUTPUT.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {OUTPUT}")
