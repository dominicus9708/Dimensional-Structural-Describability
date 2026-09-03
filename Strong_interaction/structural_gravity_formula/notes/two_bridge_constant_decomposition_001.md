# Two-bridge constant decomposition 001

## Purpose

This note separates the structural-gravity response into two candidate constitutive stages without assuming three spatial dimensions, an inverse-square law, or a preassigned gravitational constant.

The two stages are:

1. bounded/source structure -> internal structural distortion;
2. internal structural-distortion gradient -> acceleration-like physical response.

The existing DSD dynamics paper explicitly requires a constitutive bridge before typed property data acquire dynamical coefficients, and it proves that property labels alone do not uniquely determine such coefficients. The present note therefore treats both stages as structural-gravity specialization data to be audited rather than as consequences of the predecessor axioms.

## 1. Internal localization dimension

Let `d` denote the dimension of the localization carrier used by the structural-gravity specialization. This is not identified automatically with realized-axis rank. Let

\[
\rho_d(\mathbf y)
\]

be a mass-density source on that carrier, with

\[
[\rho_d]=M L^{-d}.
\]

Let the isotropic scalar structural-distortion readout be dimensionless:

\[
X(\mathbf y)\in\mathbb R.
\]

The scalar choice is only the first isotropic specialization; tensorial distortion can be treated later.

## 2. First bridge: source to structural distortion

Introduce the internal distortion-gradient field

\[
\mathbf D_X:=-\nabla X.
\]

A minimal local source-closure candidate is

\[
\nabla\cdot\mathbf D_X=\kappa_{X,d}\rho_d,
\]

or equivalently

\[
-\Delta X=\kappa_{X,d}\rho_d.
\]

This is a proposed structural-gravity constitutive specialization, not a theorem of Formation, Property, Static Aggregation, or Structural Reorganization Dynamics.

Because `X` is dimensionless,

\[
[\kappa_{X,d}]=L^{d-2}M^{-1}.
\]

No `d=3` assumption has been used.

For a radially symmetric source, integration gives

\[
S_{d-1}r^{d-1}|\partial_r X|=\kappa_{X,d}M(<r),
\]

where `S_{d-1}` is the area of the unit `(d-1)`-sphere. Outside the source,

\[
|\partial_r X|
=\frac{\kappa_{X,d}}{S_{d-1}}\frac{M}{r^{d-1}}.
\]

Thus the `r^{1-d}` gradient law follows from a dimension-generic divergence closure rather than from preloading the three-dimensional inverse-square law. For `d=3`, the exponent becomes `-2` only after specialization.

## 3. Describability and bounded-hierarchy input

The surviving bookkeeping relation is

\[
\mathcal R_D^{(\epsilon)}=\frac{C_\epsilon}{N_B},
\qquad
M=\frac{m_BC_\epsilon}{\mathcal R_D^{(\epsilon)}}.
\]

Using source density alone gives the characteristic length

\[
L_{\rho,d}=\left(\frac{M}{\rho_d}\right)^{1/d}.
\]

The corresponding source-specific quantity with the same dimensions as the first bridge is

\[
\kappa_{X,d}^{\rm src}
=F_B\frac{L_{\rho,d}^{d-2}}{M}
=F_B M^{-2/d}\rho_d^{-(d-2)/d},
\]

where `F_B` is dimensionless bounded-structure information.

This passes pure resolution and bounded-hierarchy regrouping invariance when expressed through the invariant mass reconstruction, but it remains source dependent. Therefore it is not yet a universal first-bridge constant.

## 4. Second bridge: distortion gradient to acceleration

Let the physical acceleration-like response be

\[
\mathbf a_X=-\chi_X\nabla X.
\]

Since `X` is dimensionless,

\[
[\chi_X]=L^2T^{-2}.
\]

This target dimension is independent of `d`.

The DSD structural-information speed `c_info` has speed dimensions, so

\[
\chi_X=\beta_X c_{\rm info}^2
\]

is a natural candidate specialization. It is not derived by the current dynamics paper: `c_info` is an infimal finite-propagation bound relative to a supplied localization metric, metric time, discrepancy convention, resolution, and model class; equality with a physical propagation speed requires additional conditions and saturation is not automatic.

Thus the conservative form is

\[
\chi_X=\beta_X c_X^2,
\]

where `c_X` is a structural-gravity propagation/response scale to be independently fixed, and comparison with `c_info` or the measured speed of light is a later audit.

## 5. Normalization degeneracy

If the distortion field is rescaled by

\[
X\mapsto \lambda X,
\]

then the same source and acceleration equations are preserved under

\[
\kappa_{X,d}\mapsto\lambda\kappa_{X,d},
\qquad
\chi_X\mapsto\frac{\chi_X}{\lambda}.
\]

Therefore the two coefficients are not separately physical until DSD supplies an absolute normalization of `X`.

The invariant product is

\[
\mathcal K_{X,d}:=\chi_X\kappa_{X,d},
\]

with

\[
[\mathcal K_{X,d}]=L^dM^{-1}T^{-2}.
\]

For a radial source,

\[
|\mathbf a_X(r)|
=\frac{\mathcal K_{X,d}}{S_{d-1}}
\frac{M(<r)}{r^{d-1}}.
\]

For the three-dimensional specialization,

\[
|\mathbf a_X(r)|
=\frac{\chi_X\kappa_{X,3}}{4\pi}
\frac{M(<r)}{r^2}.
\]

Only after this derivation may one compare

\[
\frac{\chi_X\kappa_{X,3}}{4\pi}
\]

with the measured Newtonian gravitational constant.

## 6. Current audit verdict

### First bridge `kappa_X,d`

- dimension-generic source-to-distortion role: coherent;
- second-order divergence closure: proposed constitutive specialization, not yet derived;
- describability/boundedness bookkeeping: compatible;
- universal numerical value from current mass+density+describability inputs: not obtained.

### Second bridge `chi_X`

- gradient-to-acceleration role: coherent if the earlier acceleration-as-distortion-gradient interpretation is retained;
- required dimensions: speed squared, independent of spatial dimension;
- `c_info^2` is a natural candidate scale but is not automatically the physical coefficient;
- universal numerical value: not obtained.

### Joint invariant

- the product `chi_X*kappa_X,d` is invariant under normalization of the distortion field;
- in `d=3`, its `1/(4*pi)` normalized value is the quantity that can eventually be compared with measured `G`;
- separate determination of the two constants requires an independent DSD normalization condition for the distortion field.

## 7. Next required step

The next audit should search for an intrinsic normalization of `X` that does not use measured gravity. Candidate sources of normalization may include a formation/boundedness threshold, a status transition, or another structurally defined reference state. If no such normalization is derivable, the theory should target only the invariant product rather than claiming two independently measurable constants.
