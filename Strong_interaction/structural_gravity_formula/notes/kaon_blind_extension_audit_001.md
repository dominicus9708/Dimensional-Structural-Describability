# Kaon blind extension audit 001

## Frozen hypothesis

Before inspecting kaon data, the first hadron pre-G candidate was frozen as

\[
\Lambda_{D,3}(B)=|D_B(0)|\frac{\ell_{A,B}}{m_B},
\]

where \(\ell_A\) is defined from the slope of the total EMT momentum/energy form factor \(A(t)\):

\[
\ell_A^2=6A'(0)(\hbar c)^2
\]

when \(A(0)=1\).

The candidate was motivated by the near equality obtained for the lattice-QCD pion and proton central values. No gravitational constant or gravitational observable is used in the definition.

## Blind extension 1: pion-kaon NJL calculation (2026)

Source: Z. Liu and H. Abuki, *Kaon gravitational form factors and mechanical structure in a three-flavor NJL model*, arXiv:2608.29848 (2026).

The paper gives, in one common calculation:

- \(m_\pi=0.138\) GeV, \(m_K=0.469\) GeV;
- transverse light-front mass radii \(r_{\perp,\pi}=0.266\) fm and \(r_{\perp,K}=0.252\) fm;
- Breit-frame mass radii \(r_{B,\pi}=1.24\) fm and \(r_{B,K}=0.381\) fm;
- for spin-zero mesons,
  \[
  r_B^2=6A'(0)-\frac{3}{4m^2}[1+2C(0)],
  \]
  with \(C(0)\) the paper's D-term form factor convention;
- and
  \[
  r_\perp^2=4A'(0).
  \]

Using these relations gives approximately

\[
\ell_{A,\pi}=0.3258\ \mathrm{fm},\qquad |D_\pi|=0.9667,
\]

\[
\ell_{A,K}=0.3086\ \mathrm{fm},\qquad |D_K|=0.6879.
\]

Hence

\[
\Lambda_{D,3}(\pi)\simeq2.2822\ \mathrm{fm/GeV},
\]

\[
\Lambda_{D,3}(K)\simeq0.4527\ \mathrm{fm/GeV},
\]

and therefore

\[
\boxed{\frac{\Lambda_{D,3}(K)}{\Lambda_{D,3}(\pi)}\simeq0.1984.}
\]

The frozen candidate fails by about a factor of five.

The dimensionless factor that would still be required, after the D-term factor is included, is

\[
\frac{F^{\rm missing}_K}{F^{\rm missing}_\pi}\simeq5.04.
\]

## Blind extension 2: continuum Schwinger-function calculation (2024)

Source: Y.-Z. Xu et al., *Pion and kaon electromagnetic and gravitational form factors*, Eur. Phys. J. C 84, 191 (2024), DOI 10.1140/epjc/s10052-024-12518-x.

Within the same symmetry-preserving RL calculation, the paper gives approximately

\[
m_\pi=0.135\ \mathrm{GeV},\qquad m_K=0.495\ \mathrm{GeV},
\]

\[
r^{\theta_2}_\pi=0.47\ \mathrm{fm},\qquad r^{\theta_2}_K=0.40\ \mathrm{fm},
\]

and pressure/D-term-magnitude proxies

\[
|D_\pi|\leftrightarrow\theta_1^\pi(0)=0.97,
\qquad
|D_K|\leftrightarrow\theta_1^K(0)=0.77.
\]

The sign convention differs from the previous source, so only magnitudes are used in this audit.

Then

\[
\Lambda_{D,3}(\pi)\simeq3.3770\ \mathrm{fm/GeV},
\]

\[
\Lambda_{D,3}(K)\simeq0.6222\ \mathrm{fm/GeV},
\]

and

\[
\boxed{\frac{\Lambda_{D,3}(K)}{\Lambda_{D,3}(\pi)}\simeq0.1843.}
\]

The residual dimensionless correction required for universality is

\[
\frac{F^{\rm missing}_K}{F^{\rm missing}_\pi}\simeq5.43.
\]

## Audit verdict

The simple frozen candidate

\[
\boxed{F_3=|D(0)|}
\]

is rejected as a universal minimal-bounded-source factor.

This rejection is stronger than a single-model failure because two distinct common-framework pion-kaon calculations give very similar failure ratios:

\[
\frac{\Lambda_K}{\Lambda_\pi}\approx0.20\quad\text{and}\quad0.18.
\]

The earlier proton-pion near equality must therefore be treated as either:

1. an accidental numerical coincidence;
2. a relation restricted to a narrower structural-equivalence class;
3. or evidence that \(D(0)\) is only one coordinate of a higher-dimensional structural signature \(\mathbf z_B\).

## DSD interpretation

The failure is consistent with the DSD static-aggregation warning: a scalar aggregate can erase channel identity and internal formation structure. The pion and kaon differ strongly in flavor composition and explicit symmetry breaking even though both are spin-zero pseudoscalar hadrons. A single total D-term cannot be assumed to encode the full bounded-source formation signature.

Accordingly, the next candidate should not be another fitted scalar multiplier. The next audit should preserve channel-resolved information before aggregation, schematically

\[
\mathbf z_B=
\{A_i(0),D_i(0),\ell_i/\ell_B,\text{closure/coupling data},\ldots\},
\]

and test whether a structurally defined, gravity-independent map

\[
F_3=\mathcal F(\mathbf z_B)
\]

exists.

No exponent or parameter should be fitted to restore the kaon after observing this failure; any next functional form must be fixed from DSD structural principles before another holdout comparison.
