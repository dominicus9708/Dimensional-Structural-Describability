# Directional structural-entropy factor candidate 001

## Motivation

The frozen pre-G hadron candidate

\[
\Lambda_{D,3}=|D(0)|\frac{\ell_A}{m}
\]

showed a suggestive proton-pion near match but failed under the first blind extension to kaon. The next audit asks whether DSD directional structural entropy supplies an independently defined dimensionless factor rather than introducing a fitted correction.

## Source definitions from structural reorganization dynamics

For an admissible direction space at resolution \(\epsilon\),

\[
S_{\rm dir,max}=k_{\rm str}\log M_{\rm dir},
\]

where \(M_{\rm dir}\) is the covering number. For a supplied directional-use distribution \(\{\pi_j\}\),

\[
S_{\rm dir}=-k_{\rm str}\sum_j\pi_j\log\pi_j.
\]

Rank alone does not determine either the direction metric or the use distribution.

## Relative directional-use factor

Define

\[
\eta_{\rm dir}
=
\exp\!\left(\frac{S_{\rm dir}-S_{\rm dir,max}}{k_{\rm str}}\right)
=
\frac{\exp(H_{\rm dir})}{M_{\rm dir}},
\]

with \(H_{\rm dir}=-\sum_j\pi_j\log\pi_j\). Equivalently,

\[
-\log\eta_{\rm dir}
=
D_{\rm KL}(\pi\|u),
\]

where \(u_j=1/M_{\rm dir}\) on the same direction cells.

Hence \(0<\eta_{\rm dir}\le1\). Uniform use gives \(\eta_{\rm dir}=1\), while directional concentration gives \(\eta_{\rm dir}<1\).

This is not yet resolution invariant in complete generality; its convergence or stability must be checked under refinement of the supplied direction partition.

## Mechanical-direction specialization for spherical hadrons

For a spherically symmetric rest-frame spatial stress tensor, write the radial and tangential principal stresses as

\[
\sigma_r(r)=p(r)+\frac{2}{3}s(r),
\qquad
\sigma_t(r)=p(r)-\frac{1}{3}s(r),
\]

with the tangential eigenvalue twofold degenerate.

A nonnegative principal-direction use distribution can be supplied by

\[
q_r(r)=\frac{\sigma_r(r)^2}{\sigma_r(r)^2+2\sigma_t(r)^2},
\qquad
q_{t1}(r)=q_{t2}(r)
=\frac{\sigma_t(r)^2}{\sigma_r(r)^2+2\sigma_t(r)^2}.
\]

Then

\[
H_\sigma(r)
=-q_r\log q_r-2q_t\log q_t,
\qquad
\eta_\sigma(r)=\frac{e^{H_\sigma(r)}}{3}.
\]

The use of squared principal stresses is a constitutive specialization, not a consequence of the DSD entropy definition. It is chosen because the probabilities must be nonnegative while the stress eigenvalues may be signed.

A global hadron descriptor would require a separately declared radial weighting rule, preferably one fixed before comparison across hadrons.

## Candidate coupling placement

If a fixed total structural response is distributed among an effective number \(N_{\rm eff}=3\eta_\sigma\) of principal directions, a zero-parameter directional-concentration amplification candidate is

\[
A_{\rm dir}=\eta_\sigma^{-1}.
\]

This gives the revised pre-G candidate

\[
\boxed{
\Lambda_{D,S,3}
=|D(0)|A_{\rm dir}\frac{\ell_A}{m}
}
\]

only as a candidate. The inverse rather than direct factor is motivated by per-active-direction concentration: fewer effectively used directions imply larger response per used direction. This physical interpretation must be audited rather than assumed.

An alternative direct factor \(|D|\eta_\sigma\ell_A/m\) remains logically possible if the intended observable is total directional participation rather than concentration. The two must not be selected by fitting to kaon.

## Falsification conditions

1. If pion and kaon have the same independently calculated \(\eta_\sigma\), directional structural entropy cannot repair their failed ratio.
2. If the required correction lies outside the range permitted by the chosen finite direction model, the model fails.
3. If changing the radial weighting rule materially changes the conclusion, the candidate is not yet well defined.
4. If the entropy factor is extracted from quantities algebraically equivalent to the same D-term already used, double counting must be checked.
5. The candidate must be frozen before the next hadron blind test.

## Current verdict

Directional structural entropy is a legitimate missing structural layer because the DSD dynamics framework already separates directional opportunity from directional use. It cannot be used as a free fitting factor. The next step is to compute a mechanical-direction entropy from the same-definition pion/kaon EMT pressure and shear distributions and test whether the resulting factor predicts, rather than retrofits, the required correction.
