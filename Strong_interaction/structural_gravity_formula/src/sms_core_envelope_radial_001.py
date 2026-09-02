from __future__ import annotations

import csv
import math
from pathlib import Path

G = 6.67430e-11
C = 299_792_458.0
M_SUN = 1.98847e30
R_SUN = 6.957e8
AU = 1.495978707e11

BASE = Path(__file__).resolve().parents[1]
INPUT = BASE / "data" / "sms_hosokawa_mass_coordinate_proxy_001.csv"
OUTPUT = BASE / "results" / "sms_core_envelope_radial_001.csv"


def read_points(path: Path):
    rows = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    if len(rows) < 2:
        raise ValueError("Need at least origin and one outer mass-coordinate point.")
    rows.sort(key=lambda r: float(r["enclosed_mass_fraction"]))
    return rows


def main() -> None:
    rows = read_points(INPUT)
    total_mass_msun = float(rows[-1]["total_mass_Msun"])
    surface_radius_au = float(rows[-1]["surface_radius_AU"])
    total_mass = total_mass_msun * M_SUN
    surface_radius = surface_radius_au * AU

    fractions = [float(r["enclosed_mass_fraction"]) for r in rows]
    radii = []
    for i, r in enumerate(rows):
        if i == len(rows) - 1:
            radii.append(surface_radius)
        else:
            radii.append(float(r["radius_Rsun"]) * R_SUN)

    if fractions[0] != 0.0 or radii[0] != 0.0:
        raise ValueError("First row must be the origin with fraction=0 and radius=0.")
    if abs(fractions[-1] - 1.0) > 1e-12:
        raise ValueError("Last row must enclose the total mass (fraction=1).")

    shell_rho = []
    for i in range(1, len(rows)):
        dm = (fractions[i] - fractions[i - 1]) * total_mass
        dv = (4.0 * math.pi / 3.0) * (radii[i] ** 3 - radii[i - 1] ** 3)
        shell_rho.append(dm / dv)

    output_rows = []
    for i in range(1, len(rows)):
        f = fractions[i]
        r = radii[i]
        enclosed_mass = f * total_mass
        enclosed_energy = enclosed_mass * C**2
        rho_mean = 3.0 * enclosed_mass / (4.0 * math.pi * r**3)
        rho_shell_i = shell_rho[i - 1]
        g = G * enclosed_mass / r**2

        # Exact potential at a shell boundary for piecewise-uniform spherical shells.
        # Inner enclosed mass contributes -G M(<r)/r.
        # Each complete outer shell contributes -2*pi*G*rho*(b^2-a^2).
        outer_integral = 0.0
        for j in range(i + 1, len(rows)):
            a = radii[j - 1]
            b = radii[j]
            outer_integral += 2.0 * math.pi * shell_rho[j - 1] * (b**2 - a**2)
        phi = -G * (enclosed_mass / r + outer_integral)

        output_rows.append(
            {
                "mass_fraction_enclosed": f,
                "r_Rsun": r / R_SUN,
                "r_AU": r / AU,
                "shell_rho_kg_m3": rho_shell_i,
                "mean_enclosed_rho_kg_m3": rho_mean,
                "g_m_s2": g,
                "abs_phi_m2_s2": abs(phi),
                "abs_phi_over_c2": abs(phi) / C**2,
                "Eenc_over_R_J_m": enclosed_energy / r,
                "Eenc_over_R2_J_m2": enclosed_energy / r**2,
                "Eenc_over_R3_J_m3": enclosed_energy / r**3,
                "poisson_source_4piG_shellrho_s2": 4.0 * math.pi * G * rho_shell_i,
            }
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(output_rows[0].keys()))
        writer.writeheader()
        writer.writerows(output_rows)

    peak = max(output_rows, key=lambda r: r["g_m_s2"])
    print(f"input:  {INPUT}")
    print(f"output: {OUTPUT}")
    print(f"peak boundary g: {peak['g_m_s2']:.6e} m/s^2 at {peak['r_Rsun']:.3f} R_sun")


if __name__ == "__main__":
    main()
