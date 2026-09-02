# 1 kg bounded-unit invariance test 001

## Purpose

Test the proposed describability ratio against a fixed-mass geometric-distortion source scale without assuming that the deepest physical unit must be an elementary particle.

The selected bounded unit may be an atom, molecule, or higher bounded aggregate, provided its mass is independently known or otherwise explicitly declared.

## Input convention

Total mass and outer radius are fixed:

- M = 1 kg
- R = 0.1 m
- external effective count C_epsilon = 1

For a selected bounded unit of mass m_B,

N_B = M / m_B,

R_D^(epsilon) = C_epsilon / N_B.

Therefore

M = m_B C_epsilon / R_D^(epsilon).

The diagnostic geometric-source scales are

X_hat = M/R,
G_hat = M/R^2,
K_hat = M/R^3.

These are not yet a physical gravitational law and contain no G.

## Species test

Using NIST relative isotopic masses and the 2022 CODATA atomic mass constant, 1 kg contains approximately:

- H-1: 5.97538e26 atoms
- He-4: 1.50456e26 atoms
- C-12: 5.01845e25 atoms
- N-14: 4.30058e25 atoms
- Xe-136: 4.43107e24 atoms

With C_epsilon = 1, R_D ranges from about 1.67e-27 for H-1 to 2.26e-25 for Xe-136, a factor of about 135.

Nevertheless all cases reconstruct the same M = 1 kg and therefore the same source scales:

X_hat = 10 kg/m,
G_hat = 100 kg/m^2,
K_hat = 1000 kg/m^3.

Thus R_D by itself cannot be a geometric/gravitational charge.

## Bounded-level regrouping test

For the same 1 kg N-14 system, regroup the chosen bounded description unit by a factor k:

m_B' = k m_B,
N_B' = N_B/k,
R_D' = k R_D

when C_epsilon remains 1.

Then

m_B'/R_D' = m_B/R_D = M.

The test used k = 2, 10^3, and 10^6. Numerical reconstruction remains 1 kg to floating-point precision and X_hat, G_hat, K_hat remain unchanged.

This establishes a useful bounded-level covariance:

m_B -> k m_B,
R_D -> k R_D,

while

m_B C_epsilon / R_D

is invariant.

## Structural-gravity candidate form

The fixed-mass source reconstruction can therefore be written as

M_B = m_B C_epsilon / R_D^(epsilon),

and the geometric diagnostics as

X_hat = m_B C_epsilon / [R_D^(epsilon) R],

G_hat = m_B C_epsilon / [R_D^(epsilon) R^2],

K_hat = m_B C_epsilon / [R_D^(epsilon) R^3].

The absolute value of R_D is description-level dependent. The reconstructed physical source is invariant under a change of bounded-unit level, provided m_B and R_D are transformed consistently.

## Audit result

PASS as a diagnostic invariance test.

Surviving interpretation:

1. bounded-unit count and describability ratio can vary strongly with the selected structural level;
2. this must not alter the physical geometric source when M and R are unchanged;
3. the invariant combination is m_B C_epsilon / R_D, not R_D alone;
4. physical changes in binding may still alter measured total mass, radius, internal energy distribution, or structural coordinates, and those changes remain legitimate inputs to structural gravity.

## Provenance

- Atomic mass constant: 2022 CODATA, m_u = 1.66053906892(52)e-27 kg.
- Relative isotopic masses: NIST Atomic Weights and Isotopic Compositions.
- The k-regrouping cases are project diagnostics, not claims that the listed groups are realized physical molecules or clusters.
