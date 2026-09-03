# Planetary-scale geometric-surface test 001

## Scope

Test whether the previously introduced source-scale diagnostics retain their intended ordering at planetary scale without using an absolute fitted gravitational constant.

Define

- D1 = M/R : distortion-depth scale candidate
- D2 = M/R^2 : surface-slope/acceleration scale candidate
- D3 = M/R^3 : bulk curvature/density scale candidate

Use Earth-normalized ratios. In these ratios an overall universal bridge coefficient cancels.

## Data

Mass, mean radius, bulk density, equatorial gravity, and escape velocity are taken from JPL Solar System Dynamics Planetary Physical Parameters:
https://ssd.jpl.nasa.gov/planets/phys_par.html

Bodies: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune, and Ceres.

## Consistency tests

Compare

D1_i/D1_Earth with (v_esc,i/v_esc,Earth)^2,

D2_i/D2_Earth with g_i/g_Earth,

D3_i/D3_Earth with rho_i/rho_Earth.

The D1 and D3 comparisons are primarily consistency checks because escape velocity and bulk density are themselves closely tied to M and R in standard planetary parameter reductions. They are not independent evidence for a new DSD gravity law.

The D2 comparison is also not fully independent because tabulated planetary gravity is based on gravitational parameters and reference radii, but the residuals are informative: rotation, oblateness, and the use of equatorial gravity versus mean radius produce percent-level departures for giant planets.

## Main Earth-normalized results

| body | D1 | vesc^2 | D2 | g | D3 | rho |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Mercury | 0.14436 | 0.14425 | 0.37702 | 0.37755 | 0.98467 | 0.98467 |
| Venus | 0.85799 | 0.85715 | 0.90324 | 0.90510 | 0.95088 | 0.95096 |
| Earth | 1 | 1 | 1 | 1 | 1 | 1 |
| Mars | 0.20196 | 0.20206 | 0.37961 | 0.37857 | 0.71353 | 0.71353 |
| Jupiter | 28.9638 | 28.9423 | 2.63948 | 2.52959 | 0.24054 | 0.24054 |
| Saturn | 10.4113 | 10.4019 | 1.13907 | 1.06531 | 0.12462 | 0.12462 |
| Uranus | 3.65142 | 3.65052 | 0.91725 | 0.90510 | 0.23042 | 0.23035 |
| Neptune | 4.43702 | 4.43293 | 1.14809 | 1.13776 | 0.29707 | 0.29709 |
| Ceres | 0.002131 | 0.002077 | 0.02891 | 0.02755 | 0.39213 | 0.39214 |

## Interpretation

1. M/R preserves the ordering of a far-field depth proxy and the squared escape-speed scale.
2. M/R^2 preserves the ordering of the surface-slope scale. Terrestrial planets agree at sub-percent level; giant-planet residuals reach several percent because equatorial gravity includes effects not represented by a spherical mean-radius proxy.
3. M/R^3 is exactly the correct scaling class for mean density up to the common spherical factor 3/(4 pi).
4. Planetary scale therefore supports keeping depth, slope, and local/bulk curvature descriptors separate.
5. The result does not show that DSD has derived gravity. It only shows that the candidate source scales survive a cross-scale consistency audit from microscopic bounded systems to planetary bodies.

## Strong null pair

Earth and Venus are especially useful:

- D1_V/D1_E = 0.8580
- D2_V/D2_E = 0.9032
- D3_V/D3_E = 0.9509

JPL values give corresponding

- vesc^2 ratio = 0.8572
- gravity ratio = 0.9051
- density ratio = 0.9510

Their similar mass, size, and bulk density but very different atmosphere/thermal state make them a natural next null test for any proposed extra structural-boundedness term. Any DSD term that predicts a large far-field gravity difference beyond the M,R baseline would be immediately suspect.

## Audit status

PASS as a scale-consistency test.

Do not treat this as an independent empirical confirmation of a new constitutive law. The next stage must test residual structural terms after the ordinary M,R, rotation, oblateness, and internal-density-profile effects are accounted for.
