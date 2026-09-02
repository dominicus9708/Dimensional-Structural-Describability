# N2 temporary negative-ion resonance case 001

## Purpose

Use a molecular temporary-bound resonance with independently available structural length information to test the transient-source bookkeeping without claiming a gravity signal.

## Process

\[
e^-+\mathrm{N_2}\rightarrow \mathrm{N_2^-}{}^*(X\,^2\Pi_g)\rightarrow e^-+\mathrm{N_2}.
\]

The well-known shape resonance is near 2.3 eV. A literature summary table reports an experimental resonance energy of about 2.32 eV and width about 0.41 eV.

## Lifetime

Using

\[
\tau=\frac{\hbar}{\Gamma},
\]

with \(\Gamma=0.41\,\mathrm{eV}\),

\[
\tau\simeq1.61\times10^{-15}\,\mathrm{s}.
\]

This is a derived quantity from the reported experimental width, not a separately measured lifetime.

## Structural length

Reference bond lengths:

\[
r_e(\mathrm{N_2})\approx1.098\,\AA,
\]

\[
r_e(\mathrm{N_2^-},X\,^2\Pi_g)\approx1.193\,\AA.
\]

Hence

\[
\frac{r_-}{r_0}\approx1.08652,
\]

or an approximately 8.65 percent increase in internuclear separation in the resonance-state structural reference.

If one merely cubes this length ratio as a geometric proxy,

\[
\left(\frac{r_-}{r_0}\right)^3\approx1.28267.
\]

This is not a measured molecular volume ratio; it is only a scale diagnostic.

## Temporary excess-energy concentration proxy

If, only for a diagnostic calculation, the resonance structural length is identified with a spherical radius proxy,

\[
R_{\rm proxy}=1.193\,\AA,
\]

then

\[
\mathcal C_{\rm tr,proxy}
=
\frac{E_r}{(4\pi/3)R_{\rm proxy}^3}
\approx5.23\times10^{10}\,\mathrm{J\,m^{-3}}.
\]

Its mass-equivalent value is

\[
\rho_{\rm tr,proxy}
=\frac{\mathcal C_{\rm tr,proxy}}{c^2}
\approx5.81\times10^{-7}\,\mathrm{kg\,m^{-3}}.
\]

Do not interpret either number as the actual N2- source density. The bond length is one-dimensional structural data, not a full 3D energy-density radius.

## Audit result

This case improves on the Xe DR case because an experimental/spectroscopic structural length is available independently of the resonance width. However, it also exposes an important distinction:

\[
L_{\rm struct}\neq R_{\rm eff}
\]

in general.

Therefore future data ingestion must retain the measured structural length as its own observable. A 3D effective radius may be introduced only if a defensible mapping or density distribution is independently supplied.

## Current use

The clean directly supported transient state is therefore

\[
\mathcal S_{\rm tr}^{(L)}=(E_r,\Gamma,\tau,L_{\rm struct}),
\]

while \(\mathcal C_{\rm tr}\) remains conditional on an explicit spatial mapping.
