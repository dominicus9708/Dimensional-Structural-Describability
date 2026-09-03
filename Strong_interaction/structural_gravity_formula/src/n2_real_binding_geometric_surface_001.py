from pathlib import Path
import csv
import math

C = 299_792_458.0
EV = 1.602_176_634e-19

HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]
INPUT = ROOT / 'data' / 'n2_real_binding_inputs_001.csv'
OUTPUT = ROOT / 'results' / 'n2_real_binding_geometric_surface_001.csv'

vals = {}
with INPUT.open(newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        vals[row['quantity']] = float(row['value'])

m_u = vals['atomic_mass_constant']
m_N = vals['atomic_mass_14N'] * m_u
D0_J = vals['N2_dissociation_energy_D0'] * EV
Delta_m_pair = D0_J / C**2
m_N2 = 2.0 * m_N - Delta_m_pair
M0 = vals['initial_total_mass']
R0 = vals['reference_external_radius']

N_atom = M0 / m_N
N_mol = N_atom / 2.0
R_D_atom = 1.0 / N_atom
R_D_mol = 1.0 / N_mol
M_matter_final = N_mol * m_N2
M_escape = M0 - M_matter_final
fractional_mass_change = M_escape / M0

# Same external radius: open matter subsystem after binding energy escapes.
X0 = M0 / R0
G0 = M0 / R0**2
K0 = M0 / R0**3
X_open = M_matter_final / R0
G_open = M_matter_final / R0**2
K_open = M_matter_final / R0**3

# Closed system: emitted energy remains inside the declared source boundary.
M_closed = M0
X_closed = M_closed / R0
G_closed = M_closed / R0**2
K_closed = M_closed / R0**3

# Ideal-gas geometry sensitivity only: at equal T and P, 2N -> N2 halves
# the number of gas entities, so V_final/V_initial ~ 1/2 and R scales as V^(1/3).
volume_ratio_same_TP = 0.5
radius_ratio_same_TP = volume_ratio_same_TP ** (1.0 / 3.0)
R_same_TP = R0 * radius_ratio_same_TP
X_same_TP = M_matter_final / R_same_TP
G_same_TP = M_matter_final / R_same_TP**2
K_same_TP = M_matter_final / R_same_TP**3

rows = [
    {
        'scenario': 'initial_atomic_reference',
        'mass_kg': M0,
        'radius_m': R0,
        'bounded_unit_mass_kg': m_N,
        'bounded_unit_count': N_atom,
        'C_epsilon': 1.0,
        'R_D': R_D_atom,
        'mB_C_over_RD_kg': m_N / R_D_atom,
        'Xhat_M_over_R': X0,
        'Ghat_M_over_R2': G0,
        'Khat_M_over_R3': K0,
    },
    {
        'scenario': 'molecular_open_same_R',
        'mass_kg': M_matter_final,
        'radius_m': R0,
        'bounded_unit_mass_kg': m_N2,
        'bounded_unit_count': N_mol,
        'C_epsilon': 1.0,
        'R_D': R_D_mol,
        'mB_C_over_RD_kg': m_N2 / R_D_mol,
        'Xhat_M_over_R': X_open,
        'Ghat_M_over_R2': G_open,
        'Khat_M_over_R3': K_open,
    },
    {
        'scenario': 'closed_total_same_R',
        'mass_kg': M_closed,
        'radius_m': R0,
        'bounded_unit_mass_kg': m_N2,
        'bounded_unit_count': N_mol,
        'C_epsilon': 1.0,
        'R_D': R_D_mol,
        'mB_C_over_RD_kg': M_closed,
        'Xhat_M_over_R': X_closed,
        'Ghat_M_over_R2': G_closed,
        'Khat_M_over_R3': K_closed,
    },
    {
        'scenario': 'molecular_open_same_TP_ideal_geometry',
        'mass_kg': M_matter_final,
        'radius_m': R_same_TP,
        'bounded_unit_mass_kg': m_N2,
        'bounded_unit_count': N_mol,
        'C_epsilon': 1.0,
        'R_D': R_D_mol,
        'mB_C_over_RD_kg': m_N2 / R_D_mol,
        'Xhat_M_over_R': X_same_TP,
        'Ghat_M_over_R2': G_same_TP,
        'Khat_M_over_R3': K_same_TP,
    },
]

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT.open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f'm_N = {m_N:.15e} kg')
print(f'm_N2 = {m_N2:.15e} kg')
print(f'N atoms in 1 kg = {N_atom:.15e}')
print(f'N2 molecules = {N_mol:.15e}')
print(f'escaped binding-energy mass equivalent = {M_escape:.15e} kg')
print(f'fractional matter-mass change = {fractional_mass_change:.15e}')
print(f'R_D atom = {R_D_atom:.15e}')
print(f'R_D molecule = {R_D_mol:.15e}')
print(f'open same-R X/G/K ratios = {X_open/X0:.15e}, {G_open/G0:.15e}, {K_open/K0:.15e}')
print(f'same-T,P radius ratio = {radius_ratio_same_TP:.15e}')
print(f'same-T,P X/G/K ratios = {X_same_TP/X0:.15e}, {G_same_TP/G0:.15e}, {K_same_TP/K0:.15e}')
print(f'output: {OUTPUT}')
