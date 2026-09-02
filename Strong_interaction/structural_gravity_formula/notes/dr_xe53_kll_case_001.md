# DR_XE53_KLL_001 — first transient-source application

## Scope

This note applies the current transient-source equations to one measured dielectronic-recombination resonance. It is a calibration/thought-experiment case, not a structural-gravity validation result.

## Source-backed inputs

Process:

\[
{}^{136}\mathrm{Xe}^{53+}+e^-\rightarrow{}^{136}\mathrm{Xe}^{52+**}\rightarrow\cdots
\]

Selected isolated KLL resonance:

\[
[2p_{3/2}2p_{3/2}]_2.
\]

The experiment reports an electron–ion center-of-mass collision resonance at approximately

\[
E_r\approx 21.5\ \mathrm{keV},
\]

with experimental FWHM about

\[
\mathrm{FWHM}_{\rm exp}=27\ \mathrm{eV}.
\]

The paper infers an experimental energy spread of about 26 eV while using a calculated natural width

\[
\Gamma\approx 8\ \mathrm{eV}.
\]

Source: Wang et al., Eur. Phys. J. D 78, 122 (2024), DOI: https://doi.org/10.1140/epjd/s10053-024-00914-7

## Derived quantities

The resonance collision energy corresponds to an excess invariant-mass scale

\[
\Delta M_r=\frac{E_r}{c^2}\approx 3.8327\times10^{-32}\ \mathrm{kg}.
\]

This is an excess above the separated threshold description; it is not newly created energy.

Using the calculated natural width only as a lifetime proxy,

\[
\tau_{\Gamma}=\frac{\hbar}{\Gamma}\approx 8.23\times10^{-17}\ \mathrm{s}.
\]

Because \(\Gamma\) is theoretical in this case, \(\tau_{\Gamma}\) is also model-derived. The measured 27 eV FWHM must not be substituted directly into \(\hbar/\Gamma\), because it includes experimental broadening.

## Spatial scale: model-only

No experimental radius for this individual transient state is supplied by the selected measurement. For order-of-magnitude exploration only, use the nonrelativistic hydrogenic expectation scale for a 2p orbital,

\[
\langle r\rangle_{2p}=\frac{5a_0}{Z_{\rm eff}}.
\]

Taking \(Z_{\rm eff}=54\) to 53 gives

\[
R_{\rm eff}^{\rm model}\approx 4.90\text{--}4.99\ \mathrm{pm}.
\]

This is not a measured Xe DR radius and should be replaced by a relativistic atomic-structure radius if one is available.

## Transient excess-energy concentration

To avoid swamping the transient effect with the static Xe rest mass, define the first diagnostic concentration from the resonance excess energy rather than total ion rest energy:

\[
\mathcal C_{\rm tr}
=\frac{E_r}{\frac43\pi R_{\rm eff}^3}.
\]

With the model radius bracket,

\[
\mathcal C_{\rm tr}\approx(6.61\text{--}6.99)\times10^{18}\ \mathrm{J\,m^{-3}}.
\]

The mass-equivalent concentration is

\[
\rho_{\rm tr}=\frac{\mathcal C_{\rm tr}}{c^2}
\approx 73.5\text{--}77.8\ \mathrm{kg\,m^{-3}}.
\]

These values are model-dependent because \(R_{\rm eff}\) is model-dependent.

## Audit distinction

Keep three layers separate:

1. **Measured:** \(E_r\approx21.5\) keV; experimental line FWHM \(\approx27\) eV.
2. **Theory supplied by the experiment paper:** natural width \(\Gamma\approx8\) eV.
3. **Current thought-experiment model:** \(R_{\rm eff}\approx4.90\text{--}4.99\) pm and all concentration quantities derived from it.

## Immediate lesson

For transient binding the useful source variable is not only total rest mass. The state can carry a positive excess invariant-energy scale while becoming spatially localized for a finite lifetime. The minimal diagnostic state is therefore

\[
\mathcal S_{\rm tr}=(E_r,R_{\rm eff},\tau).
\]

No rule mapping \(\mathcal S_{\rm tr}\) to gravitational acceleration or geometric distortion is assumed here.
