# Describability–Mass Geometric-Surface Test 001

## Scope

This note tests the candidate describability–mass relation inside the later structural-gravity layer built downstream of the Formation Axiom System, Property Axiom System / realized-axis specialization, Channel-Indexed Static Aggregation, and Structural Reorganization Dynamics.

The predecessor papers do not derive gravity. They permit a later audited physical-response bridge. Therefore the expressions below are source-scale diagnostics, not yet calibrated gravitational laws.

## 1. Candidate describability relation

For N internal particles with mean rest mass m_bar and interaction/internal-state energy E_int,

M_N = N m_bar + E_int / c^2.

At external resolution epsilon, let C_epsilon be the number of externally distinguishable effective bounded components, with

1 <= C_epsilon <= N.

Define the relative external describability

R_D^(epsilon) = D_ext^(epsilon) / D_int ~= C_epsilon / N,

and the describability gap

Delta_D^(epsilon) = 1 - R_D^(epsilon) = 1 - C_epsilon / N.

Equivalently,

N = C_epsilon / R_D^(epsilon),

so

M_N = m_bar C_epsilon / R_D^(epsilon) + E_int / c^2.

## 2. Geometric-surface source diagnostics

Before supplying a calibrated gravity bridge, define only the dimensional source-shape diagnostics

X_frak = M_N / R,

G_frak = M_N / R^2,

K_frak = M_N / R^3.

They are intended respectively as candidate scalings for geometric-distortion depth, surface slope, and local curvature/source concentration.

Substituting the describability relation gives

X_frak^(epsilon)
= (1/R) [m_bar C_epsilon / R_D^(epsilon) + E_int/c^2],

G_frak^(epsilon)
= (1/R^2) [m_bar C_epsilon / R_D^(epsilon) + E_int/c^2],

K_frak^(epsilon)
= (1/R^3) [m_bar C_epsilon / R_D^(epsilon) + E_int/c^2].

Because

C_epsilon / R_D^(epsilon) = N,

the arbitrary observational-resolution dependence cancels exactly when the physical state N, R, and E_int is fixed.

This is the first major pass condition:

changing epsilon may change C_epsilon and R_D^(epsilon), but must not by itself change the physical geometric surface.

## 3. Resolution-invariance test

Take N = 10^6 and E_int = 0.

Three descriptions of the same physical system are:

- fully resolved: C_epsilon = 10^6, R_D = 1;
- intermediate: C_epsilon = 10^3, R_D = 10^-3;
- externally one bounded source: C_epsilon = 1, R_D = 10^-6.

In every case,

C_epsilon / R_D = 10^6,

and therefore the same M_N, X_frak, G_frak, and K_frak are recovered.

Result: PASS.

A direct law such as X proportional to R_D or X proportional to Delta_D would fail this test because the predicted geometry would depend on observer resolution.

## 4. Increasing particle count inside one externally bounded source

For C_epsilon = 1 and negligible E_int,

R_D = 1/N,

M_N ~= m_bar / R_D.

The geometric diagnostics become

X_frak ~= m_bar / (R R_D),

G_frak ~= m_bar / (R^2 R_D),

K_frak ~= m_bar / (R^3 R_D).

Thus decreasing relative external describability accompanies increasing total mass, but the geometric response still depends essentially on R.

## 5. Fixed-density growth test

Let the object grow by adding equal particles at approximately fixed mean density. Then

R proportional to N^(1/3).

For C_epsilon = 1,

R_D = N^-1.

Normalized to N = 1,

X_frak proportional to N^(2/3) = R_D^(-2/3),

G_frak proportional to N^(1/3) = R_D^(-1/3),

K_frak proportional to N^0.

This is structurally important:

- geometric depth grows;
- surface slope grows more slowly;
- local density/curvature-source scale remains constant.

Therefore a larger bounded object can have a much larger total distortion without requiring a larger local source density.

## 6. Compaction at fixed N test

Now keep N, C_epsilon, R_D, and M_N fixed while decreasing the physical radius R.

Then

X_frak proportional to R^-1,

G_frak proportional to R^-2,

K_frak proportional to R^-3.

For R/R0 = 1, 0.5, 0.1, 0.01, the normalized factors are:

| R/R0 | X_frak/X0 | G_frak/G0 | K_frak/K0 |
| ---: | ---: | ---: | ---: |
| 1 | 1 | 1 | 1 |
| 0.5 | 2 | 4 | 8 |
| 0.1 | 10 | 100 | 1000 |
| 0.01 | 100 | 10000 | 1000000 |

Result: the describability ratio alone cannot encode physical compaction. A boundedness/geometry coordinate such as R_eff or a full source distribution must remain independent.

## 7. Bounded-component-merger test

Keep N, M_N, R, and E_int fixed while changing the external description from many distinguishable sub-bounds to one unresolved bound.

Then C_epsilon decreases and R_D decreases in the same proportion, so

C_epsilon / R_D = N

remains fixed.

Therefore X_frak, G_frak, and K_frak remain fixed.

Result: PASS for physical resolution invariance.

Interpretation: descriptive compression is not itself a new gravitational charge.

## 8. Consequence for the geometric-distortion surface

The clean candidate bridge is not

X = F(R_D)

alone.

Instead, the source-scale part is constrained to retain the physical mass-energy and geometry, for example

X = B_X[M_N, rho(x), bounded structure, ...],

while

R_D^(epsilon) = C_epsilon/N

acts as a description-compression coordinate or comparison diagnostic.

When M_N is rewritten through the describability variables,

M_N = m_bar C_epsilon/R_D^(epsilon) + E_int/c^2,

the epsilon dependence cancels if the same physical system is being described.

Hence the current test supports the following separation:

1. N and E_int determine physical source amount;
2. R or rho(x) determines geometric concentration and shape;
3. C_epsilon/N measures internal–external describability compression;
4. bounded interaction can change both geometry and describability, but the two effects must not be identified;
5. any additional structural-gravity correction must be built from resolution-invariant bounded-state data, not from one arbitrary observational epsilon alone.

## 9. Status

The candidate relation passes the basic resolution-invariance and macroscopic-continuum consistency tests when C_epsilon and R_D are used as a paired representation of N.

It fails as a standalone gravity multiplier if either R_D or Delta_D is inserted independently into the geometric response.

The next structural-gravity test should therefore search for a resolution-invariant boundedness functional, or use physical state variables such as R_eff, rho(x), interaction energy, and structural coordinates alongside the describability-compression curve.