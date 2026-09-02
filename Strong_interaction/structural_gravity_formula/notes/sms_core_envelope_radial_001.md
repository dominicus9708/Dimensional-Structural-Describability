# 10^4 Msun SMS core-envelope radial proxy 001

## Scope

This calculation replaces the earlier n=3-polytrope-as-realistic-density reading with a more appropriate core-envelope proxy for a rapidly accreting supermassive protostar.

Hosokawa et al. (2013) report that rapidly accreting stars remain strongly inhomogeneous above 10^4 Msun: most of the interior contracts while a low-mass surface layer inflates. Their Fig. 2 gives radial positions for the 20%, 40%, 60%, and 80% enclosed-mass coordinates. The input radii used here are approximate visual read-offs, not an original numerical table from the paper.

Project continuity values:

- total mass: 10^4 Msun
- surface radius: 100 AU
- approximate enclosed-mass radii at 10^4 Msun: 20% -> 20 R_sun, 40% -> 50 R_sun, 60% -> 130 R_sun, 80% -> 400 R_sun

The model treats each 20%-mass interval as a spherical shell of uniform density only for a first radial diagnostic. It is not claimed to reproduce the full stellar-evolution calculation.

## Equations

For a boundary enclosing mass fraction f at radius r,

M(<r)=f M_*,

g(r)=G M(<r)/r^2.

For a shell between r_{i-1} and r_i,

rho_i = Delta M_i / [(4 pi / 3)(r_i^3-r_{i-1}^3)].

The local Poisson-source diagnostic is

K_rho,i = 4 pi G rho_i.

At a shell boundary the Newtonian potential of the piecewise-uniform spherical model is

Phi(r_i) = -G [M(<r_i)/r_i + sum_{j>i} 2 pi rho_j (r_j^2-r_{j-1}^2)].

This is a standard weak-field reference only; it is not yet the DSD constitutive law for geometric distortion X.

## Main results

| enclosed mass | radius | shell-average rho | g | |Phi|/c^2 |
| ---: | ---: | ---: | ---: | ---: |
| 20% | 20 R_sun | 3.52e2 kg/m^3 | 1.37e3 m/s^2 | 3.86e-4 |
| 40% | 50 R_sun | 2.41e1 kg/m^3 | 4.39e2 m/s^2 | 2.29e-4 |
| 60% | 130 R_sun | 1.36 kg/m^3 | 9.74e1 m/s^2 | 1.13e-4 |
| 80% | 400 R_sun | 4.56e-2 kg/m^3 | 1.37e1 m/s^2 | 4.27e-5 |
| 100% | 100 AU | 2.84e-7 kg/m^3 (outer shell average) | 5.93e-3 m/s^2 | 9.87e-7 |

Within the constant-density inner shell, g rises linearly from zero at the center and reaches about 1.37e3 m/s^2 near the 20%-mass boundary. The boundary acceleration is therefore about 2.31e5 times the surface acceleration.

The center potential of the same piecewise-shell proxy is approximately

|Phi(0)| = 4.42e13 m^2/s^2,

|Phi(0)|/c^2 = 4.92e-4.

## Correction to the earlier Xe comparison

The previous n=3 polytrope baseline gave a central density only about 54 times the whole-star mean and therefore made the Xe53+ KLL transient excess-density proxy appear roughly one million times denser than the SMS center.

That comparison is not appropriate for the rapidly accreting core-envelope star used in this project.

With the figure-constrained proxy, the innermost 20%-mass shell has

rho_shell ~ 352 kg/m^3,

whereas the Xe53+ KLL transient excess-density proxy was about 73.5-77.8 kg/m^3.

Thus the SMS inner-shell average is about 4.5-4.8 times the Xe transient excess-density proxy, not one million times smaller.

This does not equate the stellar rest-mass density with the atomic transient excess-energy density as identical physical source terms. It only corrects their order-of-magnitude comparison.

## Structural-gravity reading

The radial separation now becomes clearer:

1. local density / E-per-volume controls a curvature-source diagnostic;
2. enclosed total source controls the slope g through M(<r)/r^2 in the standard weak-field baseline;
3. the bloated outer envelope can have extremely low local density while retaining a nonzero surface slope because almost all mass is already enclosed;
4. the geometric-distortion depth can remain large in the core even though g -> 0 at the exact center by symmetry.

Therefore

rho(r) high does not imply g(r) high at the same point,

and

g(0)=0 does not imply X(0)=0 or vanishing curvature.

This is directly compatible with the earlier DSD thought-experiment distinction between distortion depth, slope, and curvature.

## Provenance / audit

- Source: Hosokawa et al., Formation of Primordial Supermassive Stars by Rapid Mass Accretion, arXiv:1308.4457.
- The ~100 AU scale is source-supported.
- The core-envelope interpretation is source-supported.
- The 20/40/60/80%-mass radii in the input CSV are approximate visual digitizations from Fig. 2 and must be replaced if machine-readable stellar-profile data become available.
- Piecewise-uniform shells are a project calculation device, not a claim about the exact stellar density profile.
