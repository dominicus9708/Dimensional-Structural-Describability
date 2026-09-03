# N2 real-binding geometric-surface test 001

## Purpose

Test the difference between a pure change of bounded-unit description level and a real physical binding event using

2 N -> N2.

The test keeps the previously defined describability ratio

R_D^(epsilon) = C_epsilon / N_B

but now allows the bounded-unit mass m_B itself to change because binding energy is released.

## Source data

- 14N relative atomic mass: 14.00307400443 u (NIST isotopic composition table).
- atomic mass constant: 1.66053906892e-27 kg (2022 CODATA value used in this project calculation).
- N2 ground-state dissociation energy: D0 = 9.759 eV from the NIST spectroscopic compilation.
- N2 equilibrium bond-length reference: about 1.098 angstrom from NIST CCCBDB.

The bond length is recorded as an internal structural coordinate and is NOT identified with the external source radius R used in the 1 kg geometric-surface test.

## Initial 1 kg atomic reference

For pure 14N atoms,

m_N = 2.3252651469334047e-26 kg,

N_atom = 1 kg / m_N = 4.300584822848334e25.

With C_epsilon = 1,

R_D,atom = 1/N_atom = 2.3252651469334047e-26.

For R = 0.1 m the source-scale diagnostics are

Xhat = M/R = 10,
Ghat = M/R^2 = 100,
Khat = M/R^3 = 1000.

These are geometric-source diagnostics only, not a completed gravitational constitutive law.

## Real N2 binding

For each formed molecule,

m_N2 = 2 m_N - D0/c^2.

Numerically,

D0/c^2 = 1.7396997693166655e-35 kg per molecule,

m_N2 = 4.65053029212711e-26 kg.

The number of molecules after complete pairing is

N_mol = N_atom/2 = 2.150292411424167e25,

so

R_D,mol = 1/N_mol = 4.6505302938668093e-26.

The describability ratio therefore nearly doubles, as expected when two prior bounded units become one higher-level bounded unit.

However, unlike a pure relabeling,

m_N2 != 2 m_N.

Therefore the reconstructed matter mass

m_B C_epsilon / R_D

also changes physically.

## Open matter subsystem

If the binding energy escapes the declared matter-source boundary, the final molecular matter mass is

M_matter = 0.9999999996259138 kg,

and the escaped mass-equivalent is

Delta M_escape = 3.7408620645607016e-10 kg.

The fractional matter-mass change is

Delta M/M = 3.7408620645607016e-10.

At the same external radius, Xhat, Ghat and Khat all decrease by exactly this same fractional amount.

This is the first case in this branch where the earlier bounded-level invariance is intentionally broken by a real physical energy transfer rather than by description alone.

## Closed total system

If the released binding energy remains inside the declared source boundary as radiation/internal energy, then the total source mass-energy remains 1 kg.

Hence for fixed external R,

Xhat, Ghat, Khat

remain unchanged globally even though the internal bounded structure changes from atomic to molecular.

This distinction is essential:

- boundedness transition alone does not create or destroy total source;
- energy crossing the source boundary changes the source total;
- internal redistribution can change local geometry/curvature without changing the far-field total-source diagnostic.

## Geometry sensitivity at equal T and P

A separate ideal-gas diagnostic was included only to estimate the scale of geometry change. If an ideal atomic gas were converted completely into a diatomic gas at the same T and P, the number of gas entities would halve, giving

V_final/V_initial ~ 1/2,
R_final/R_initial ~ 2^(-1/3) = 0.7937005.

For the open molecular matter subsystem this gives approximately

Xhat_final/Xhat_initial = 1.259921,
Ghat_final/Ghat_initial = 1.587401,
Khat_final/Khat_initial = 2.000000.

Thus the geometric concentration effect can dominate the tiny binding-mass loss by many orders of magnitude in these source-scale diagnostics.

This equal-T,P calculation is a model sensitivity test, not a claim that a macroscopic atomic-nitrogen sample can be held as a stable equilibrium reference under ordinary conditions.

## Structural-gravity reading

The surviving identity is not strict invariance of m_B/R_D under every physical process. It is instead

M_declared = m_B C_epsilon / R_D

for the matter sector represented by the chosen bounded unit.

Under pure change of description level, this quantity is invariant.

Under real binding with energy escape,

Delta(m_B C_epsilon / R_D) = -E_escape/c^2.

For a closed source including the emitted energy channel,

Delta M_total = 0.

Therefore a useful structural-gravity separation is

1. R_D records description compression / bounded-unit count at the selected level;
2. m_B records the physical mass-energy of that realized bounded unit;
3. their ratio reconstructs the declared source total;
4. R and the spatial distribution determine geometric depth/slope/curvature diagnostics;
5. a boundedness transition can alter local geometry strongly while leaving the closed-system far-source total unchanged.

## Audit status

PASS as a consistency test.

The test does not establish a new gravitational law. It demonstrates that the describability-mass bookkeeping distinguishes pure hierarchical regrouping from real binding-energy transfer and remains compatible with closed-system source conservation.
