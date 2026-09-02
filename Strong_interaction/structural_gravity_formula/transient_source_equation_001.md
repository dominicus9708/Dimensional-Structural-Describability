# Transient Source Equation 001

## Purpose

Develop the minimal equation set needed to test temporary bounded concentration before importing empirical collision data.

## A. Two-body invariant source state

For two incoming constituents with four-momenta \(p_1^\mu\) and \(p_2^\mu\),

\[
P^\mu=p_1^\mu+p_2^\mu.
\]

The temporary composite invariant mass is

\[
M_*^2c^2=P^\mu P_\mu,
\]

or equivalently

\[
M_*^2c^4
=
E_{\rm tot}^2-c^2|\mathbf P_{\rm tot}|^2.
\]

In the center-of-mass frame,

\[
M_*c^2=E_{\rm cm}.
\]

No binding-energy subtraction is required for this temporary-state comparison.

## B. Effective concentration

For a declared effective radius \(R_{\rm eff}\),

\[
V_{\rm eff}=\frac{4\pi}{3}R_{\rm eff}^3,
\]

\[
\mathcal C_{\rm src}
=
\frac{E_{\rm cm}}{V_{\rm eff}},
\]

\[
\rho_{\rm src}
=
\frac{\mathcal C_{\rm src}}{c^2}.
\]

For two configurations at fixed constituent identity,

\[
\frac{\mathcal C_2}{\mathcal C_1}
=
\frac{E_2}{E_1}
\left(\frac{R_1}{R_2}\right)^3.
\]

At approximately fixed \(E_{\rm cm}\),

\[
\frac{\mathcal C_2}{\mathcal C_1}
\simeq
\left(\frac{R_1}{R_2}\right)^3.
\]

This is the direct concentration lever to be tested before introducing a gravity-specific response law.

## C. Temporary-state lifetime

If a resonance width \(\Gamma\) is experimentally available,

\[
\tau\simeq\frac{\hbar}{\Gamma}.
\]

Keep \(\tau\) independent at this stage. Do not assume \(\mathcal C_{\rm src}\tau\), \(\mathcal C_{\rm src}/\tau\), or another lifetime weighting without data support.

## D. Resolution and describability

For description resolution \(\epsilon\), define only as a provisional coarse-graining rule

\[
R_{\rm eff}^{(\epsilon)}
=
\max(R_{\rm physical},\epsilon).
\]

Then

\[
\mathcal C^{(\epsilon)}
=
\frac{E_{\rm cm}}
{\frac{4\pi}{3}[R_{\rm eff}^{(\epsilon)}]^3}.
\]

This permits

\[
\mathcal C_{\rm int}
\neq
\mathcal C_{\rm ext}
\]

without implying a change in total energy.

## E. Geometric-distortion null test

Do not yet posit a constitutive equation for \(X\).

Use

\[
X=X(E_{\rm cm},R_{\rm eff},\tau;\epsilon,\ldots)
\]

as an unknown response map.

The principal null test is

\[
\left.
\frac{\partial X_{\rm far}}
{\partial R_{\rm eff}}
\right|_{E_{\rm cm}}
=0.
\]

A nonzero result would mean that source compactness/bounded concentration contributes information not removed by fixing total center-of-mass energy, subject to ordinary finite-size and standard-interaction explanations being removed first.

## F. First data target

The first preferred empirical class is an electron-ion dielectronic-recombination resonance because one dataset can provide or constrain:

- collision/resonance energy \(E_r\),
- center-of-mass energy,
- resonance width \(\Gamma\),
- lifetime \(\tau\),
- charge state and constituent identity,
- state-specific structure calculations from which a defensible spatial scale may later be obtained.

The spatial scale must be sourced independently; resonance width alone does not define \(R_{\rm eff}\).
