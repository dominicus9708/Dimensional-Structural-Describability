# Transient Source Equation 001

## Purpose

Develop the minimal equation set needed to test temporary bounded concentration before importing a gravity-specific constitutive law.

## A. Two-body invariant source state

For two incoming constituents with four-momenta \(p_1^\mu\) and \(p_2^\mu\),

\[
P^\mu=p_1^\mu+p_2^\mu.
\]

Define the total center-of-mass invariant energy by

\[
E_{\Sigma,\mathrm{cm}}^2
=
E_{\rm tot}^2-c^2|\mathbf P_{\rm tot}|^2,
\]

so that

\[
M_*c^2=E_{\Sigma,\mathrm{cm}}.
\]

Do not identify \(E_{\Sigma,\mathrm{cm}}\) with the relative collision energy conventionally denoted \(E_{\rm cm}\) in electron-ion collision papers. In this project use

\[
E_{\rm coll}
\]

for the measured relative collision energy whenever possible.

For a chosen separated-state threshold \(E_{\rm sep}\), define the transient excess energy

\[
\Delta E_{\rm tr}
=
E_{\Sigma,\mathrm{cm}}-E_{\rm sep}.
\]

For a resonance quoted at energy \(E_r\) above that threshold,

\[
\Delta E_{\rm tr}=E_r
\]

within that threshold convention.

This excess energy is a redistribution of the initial system energy, not newly created energy.

## B. Total coarse-grained concentration and transient excess concentration

For a declared effective radius \(R_{\rm eff}\),

\[
V_{\rm eff}=\frac{4\pi}{3}R_{\rm eff}^3.
\]

Two different concentration descriptors must be kept separate.

### B1. Total coarse-grained source concentration

\[
\mathcal C_{\Sigma}
=
\frac{E_{\Sigma,\rm cm}}{V_{\rm eff}},
\]

\[
\rho_{\Sigma}
=
\frac{\mathcal C_{\Sigma}}{c^2}.
\]

This includes the constituent rest-energy baseline and is useful only when that coarse-graining choice is physically appropriate.

### B2. Transient excess-energy concentration

To isolate the temporary interaction/bounded-state change from a large static rest-mass baseline, define

\[
\boxed{
\mathcal C_{\rm tr}
=
\frac{\Delta E_{\rm tr}}{V_{\rm eff}}
}
\]

and

\[
\boxed{
\rho_{\rm tr}
=
\frac{\mathcal C_{\rm tr}}{c^2}.
}
\]

For two transient configurations,

\[
\frac{\mathcal C_{{\rm tr},2}}{\mathcal C_{{\rm tr},1}}
=
\frac{\Delta E_{{\rm tr},2}}{\Delta E_{{\rm tr},1}}
\left(\frac{R_1}{R_2}\right)^3.
\]

At approximately fixed transient excess energy,

\[
\frac{\mathcal C_{{\rm tr},2}}{\mathcal C_{{\rm tr},1}}
\simeq
\left(\frac{R_1}{R_2}\right)^3.
\]

Neither \(\mathcal C_{\Sigma}\) nor \(\mathcal C_{\rm tr}\) is yet a gravitational source law. They are source descriptors.

## C. Temporary-state lifetime

If a natural resonance width \(\Gamma\) is available,

\[
\tau_{\Gamma}\simeq\frac{\hbar}{\Gamma}.
\]

The provenance of \(\tau_{\Gamma}\) inherits the provenance of \(\Gamma\). A theoretical natural width gives a model-derived lifetime; an experimentally broadened FWHM must not automatically be used as \(\Gamma\).

Keep \(\tau\) independent at this stage. Do not assume \(\mathcal C\tau\), \(\mathcal C/\tau\), or another lifetime weighting without data support.

## D. Resolution and describability

For description resolution \(\epsilon\), define only as a provisional coarse-graining rule

\[
R_{\rm eff}^{(\epsilon)}
=
\max(R_{\rm physical},\epsilon).
\]

Then, for example,

\[
\mathcal C_{\rm tr}^{(\epsilon)}
=
\frac{\Delta E_{\rm tr}}
{\frac{4\pi}{3}[R_{\rm eff}^{(\epsilon)}]^3}.
\]

This permits

\[
\mathcal C_{\rm int}
\neq
\mathcal C_{\rm ext}
\]

without implying a change in total invariant energy.

## E. Geometric-distortion null test

Do not yet posit a constitutive equation for \(X\).

Use

\[
X=X(E_{\Sigma,\rm cm},\Delta E_{\rm tr},R_{\rm eff},\tau;\epsilon,\ldots)
\]

as an unknown response map.

The principal compactness null test is

\[
\left.
\frac{\partial X_{\rm far}}
{\partial R_{\rm eff}}
\right|_{E_{\Sigma,\rm cm}}
=0.
\]

A nonzero residual would mean that source compactness/bounded concentration contributes information not removed by fixing total invariant center-of-mass energy, after ordinary finite-size and standard-interaction explanations are removed.

## F. Data provenance classes

Every empirical case must separate:

1. measured quantities,
2. theory values supplied by the experimental paper,
3. project-derived quantities,
4. project model assumptions.

In particular, a model orbital radius must not be recorded as an experimentally measured \(R_{\rm eff}\).

## G. First empirical class

The first empirical class is electron-ion dielectronic recombination because one case can provide or constrain:

- relative collision/resonance energy \(E_r\),
- resonance line shape,
- natural width \(\Gamma\) when available,
- lifetime proxy \(\tau_{\Gamma}\),
- charge state and constituent identity,
- state-specific atomic-structure information from which a spatial scale can be sourced or modeled.

The spatial scale must be sourced independently; resonance width alone does not define \(R_{\rm eff}\).

## H. Structural length is not automatically a source radius

Some molecular datasets provide a directly measured or spectroscopically inferred one-dimensional structural length \(L_{\rm struct}\), such as an internuclear separation, without providing a three-dimensional energy-density radius.

Keep

\[
\boxed{L_{\rm struct}\neq R_{\rm eff}}
\]

unless an explicit mapping is independently justified.

For such cases the directly supported transient-state record should be written first as

\[
\boxed{
\mathcal S_{\rm tr}^{(L)}
=
(\Delta E_{\rm tr},\Gamma,\tau,L_{\rm struct})
}
\]

rather than forcing a volume descriptor.

A provisional mapping

\[
R_{\rm eff}=f(L_{\rm struct})
\]

must be tagged as a project model assumption. For example, setting \(R_{\rm eff}=L_{\rm struct}\) and using a spherical volume is allowed only as a diagnostic proxy, not as a measured source density.

Length-ratio comparisons may be retained without a volume model. If two states have independently known structural lengths,

\[
\Lambda_L=\frac{L_2}{L_1}
\]

is directly meaningful, while

\[
\Lambda_V=\Lambda_L^3
\]

is only a geometric proxy unless three-dimensional similarity is independently supported.
