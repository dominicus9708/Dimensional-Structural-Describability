from pathlib import Path
import csv

BASE = Path(__file__).resolve().parents[1]
INPUT = BASE / 'data' / 'planetary_scale_inputs_001.csv'
OUTPUT = BASE / 'results' / 'planetary_scale_geometric_surface_001.csv'

rows = []
with INPUT.open(newline='', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        M = float(r['mass_kg'])
        R = float(r['mean_radius_m'])
        rho = float(r['bulk_density_kg_m3'])
        g = float(r['equatorial_gravity_m_s2'])
        v = float(r['escape_velocity_m_s'])
        rows.append({**r, 'D1_M_over_R': M/R, 'D2_M_over_R2': M/R**2, 'D3_M_over_R3': M/R**3, 'vesc2': v*v, 'rho': rho, 'g': g})

earth = next(r for r in rows if r['body'] == 'Earth')
for r in rows:
    r['D1_rel_Earth'] = r['D1_M_over_R'] / earth['D1_M_over_R']
    r['D2_rel_Earth'] = r['D2_M_over_R2'] / earth['D2_M_over_R2']
    r['D3_rel_Earth'] = r['D3_M_over_R3'] / earth['D3_M_over_R3']
    r['vesc2_rel_Earth'] = r['vesc2'] / earth['vesc2']
    r['gravity_rel_Earth'] = r['g'] / earth['g']
    r['density_rel_Earth'] = r['rho'] / earth['rho']
    r['D1_vs_vesc2_pct'] = 100.0 * (r['D1_rel_Earth'] / r['vesc2_rel_Earth'] - 1.0)
    r['D2_vs_g_pct'] = 100.0 * (r['D2_rel_Earth'] / r['gravity_rel_Earth'] - 1.0)
    r['D3_vs_rho_pct'] = 100.0 * (r['D3_rel_Earth'] / r['density_rel_Earth'] - 1.0)

fields = ['body','D1_M_over_R','D1_rel_Earth','vesc2_rel_Earth','D1_vs_vesc2_pct','D2_M_over_R2','D2_rel_Earth','gravity_rel_Earth','D2_vs_g_pct','D3_M_over_R3','D3_rel_Earth','density_rel_Earth','D3_vs_rho_pct']
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT.open('w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in rows:
        w.writerow({k:r[k] for k in fields})

print(OUTPUT)
