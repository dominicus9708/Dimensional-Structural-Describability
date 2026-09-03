from pathlib import Path
import csv
import math

BASE = Path(__file__).resolve().parents[1]
INPUT = BASE / 'data' / 'solar_b23_surface_invariance_inputs_001.csv'
OUTPUT = BASE / 'results' / 'solar_b23_surface_invariance_001.csv'

rows = []
with INPUT.open(newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        GM = float(row['GM_m3_s2'])
        R = float(row['R_m'])
        c = float(row['c_m_s'])
        phi_abs = GM / R
        x_phi = phi_abs / c**2
        h00_scale = 2.0 * x_phi
        g_surface = GM / R**2
        vesc = math.sqrt(2.0 * GM / R)
        clock_factor = math.sqrt(1.0 - 2.0 * x_phi)
        z_grav = 1.0 / clock_factor - 1.0
        rows.append({
            **row,
            'phi_abs_m2_s2': f'{phi_abs:.12e}',
            'X_surface_phi_over_c2': f'{x_phi:.12e}',
            'metric_departure_2GM_over_Rc2': f'{h00_scale:.12e}',
            'g_surface_m_s2': f'{g_surface:.12e}',
            'escape_velocity_m_s': f'{vesc:.12e}',
            'surface_clock_factor_vs_infinity': f'{clock_factor:.12e}',
            'surface_gravitational_redshift': f'{z_grav:.12e}',
        })

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT.open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f'Wrote {len(rows)} rows to {OUTPUT}')
