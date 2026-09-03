# Kaon channel-signature audit 001

## Purpose

After the frozen scalar candidate

\[
\Lambda_{D,3}=|D(0)|\frac{\ell_A}{m}
\]

failed for kaons in two independent pion-kaon frameworks, this audit tests whether the missing factor can plausibly be explained by simple channel-count or channel-uniformity descriptors.

No new exponent or fit parameter is introduced.

## Inputs

For the 2024 continuum Schwinger-function calculation, the kaon channel decomposition at the hadron scale is approximately

\[
A_u(0)=0.39,\qquad A_{\bar s}(0)=0.61,
\]

\[
|D_u(0)|\leftrightarrow\theta_{1,u}(0)=0.331,
\qquad
|D_{\bar s}(0)|\leftrightarrow\theta_{1,\bar s}(0)=0.436.
\]

The pion is treated as an isospin-symmetric two-channel baseline, so equal 1/2 shares are used for the normalized comparison. This is a symmetry baseline, not an independently extracted pion flavor decomposition from the table.

## Tested scale-free descriptors

For normalized channel weights \(p_i\), we compute:

\[
H=-\sum_i p_i\ln p_i,
\qquad
H_{\rm norm}=\frac{H}{\ln n},
\]

\[
N_{\rm eff}^{(H)}=e^H,
\qquad
N_{\rm eff}^{(\rm IPR)}=\frac{1}{\sum_i p_i^2},
\]

and the L1 asymmetry from equal weighting.

## Results

For the kaon momentum shares:

\[
H_{A,\rm norm}\simeq0.965,
\qquad
N_{A,\rm eff}^{(H)}\simeq1.952,
\qquad
N_{A,\rm eff}^{(\rm IPR)}\simeq1.908.
\]

For the normalized kaon D-channel shares:

\[
H_{D,\rm norm}\simeq0.986,
\qquad
N_{D,\rm eff}^{(H)}\simeq1.981,
\qquad
N_{D,\rm eff}^{(\rm IPR)}\simeq1.963.
\]

Relative to the symmetric two-channel pion baseline, these common scale-free descriptors differ by only a few percent.

By contrast, the kaon blind audit requires an additional multiplicative correction of approximately

\[
5.0\text{--}5.4
\]

beyond the D-term factor to restore the previously hypothesized universal value.

## Verdict

Simple channel number, normalized channel entropy, or inverse-participation-type uniformity metrics do not directly supply the missing factor.

This does **not** prove that no function of channel structure can do so. A deliberately singular or fitted nonlinear function could always amplify a small asymmetry, but introducing such a function after observing the kaon failure would be post-hoc fitting and is therefore excluded at this stage.

The next viable structural factor must carry more than simple scale-free channel uniformity. It likely needs at least one of:

1. channel-resolved length/scale information;
2. channel-resolved mass-generation information;
3. coupling/closure information between channels;
4. a formation-history or bounded-refinement invariant that is not preserved by total EMT aggregation.

## DSD interpretation

This outcome is consistent with the static-aggregation information-loss principle: preserving only a total D-term or only normalized channel weights is insufficient to reconstruct the full formation structure.

The next audit should therefore retain a vector-valued structural signature before aggregation, rather than trying another single scalar correction.
