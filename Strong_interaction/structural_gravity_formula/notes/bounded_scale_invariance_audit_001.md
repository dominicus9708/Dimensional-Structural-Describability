# Bounded-scale invariance audit 001

## Purpose

This audit tests whether a bounded-unit mass `m_B`, a bounded-source minimum structural scale `ell_B`, the external distinguishability count `C_epsilon`, and the describability ratio `R_D^(epsilon)` can form a hierarchy- and resolution-invariant geometric coupling ingredient.

This is a structural-gravity specialization audit. The Formation and Property Axiom Systems do not themselves assign a gravitational meaning to these variables, and the Structural Reorganization Dynamics paper places physical-response maps after the constitutive dynamic layer.

## 1. Bounded realization count

Use the surviving describability relation

\[
R_D^{(\epsilon)}=\frac{C_\epsilon}{N_B},
\qquad
N_B=\frac{C_\epsilon}{R_D^{(\epsilon)}}.
\]

For a homogeneous selected bounded level,

\[
M=N_Bm_B.
\]

## 2. Additive bounded structural measure

To avoid assuming a spherical three-dimensional volume, let one bounded realization carry a positive additive `d`-measure

\[
v_B:=\ell_B^d.
\]

Here `ell_B` is a measure-equivalent structural scale, not a universal lattice spacing of space.

For a purely descriptive regrouping of `k` lower bounded units into one higher bounded unit, with no physical reorganization,

\[
m_B' = k m_B,
\qquad
v_B'=k v_B,
\qquad
\ell_B'=k^{1/d}\ell_B,
\qquad
N_B'=N_B/k.
\]

If actual binding, contraction, expansion, overlap, or source redistribution occurs, these equalities need not hold; that is a physical transition rather than a pure regrouping.

## 3. Two immediate invariants

The total additive bounded measure is

\[
V_\Sigma=N_Bv_B
=\frac{C_\epsilon}{R_D^{(\epsilon)}}\ell_B^d.
\]

Define the corresponding aggregate structural scale

\[
L_\Sigma:=V_\Sigma^{1/d}
=\ell_B\left(\frac{C_\epsilon}{R_D^{(\epsilon)}}\right)^{1/d}.
\]

The mass reconstruction is

\[
M=\frac{m_BC_\epsilon}{R_D^{(\epsilon)}}.
\]

Both `M` and `L_Sigma` are unchanged by (i) a resolution change `C_epsilon -> a C_epsilon`, `R_D -> a R_D`, and (ii) the pure regrouping transformation above.

A second invariant is the specific bounded measure

\[
\sigma_B:=\frac{v_B}{m_B}=\frac{\ell_B^d}{m_B}.
\]

Under pure regrouping, numerator and denominator both scale by `k`.

## 4. Unique monomial with source-to-distortion dimensions

For a dimensionless distortion field `X`, a Poisson-like source coefficient `kappa_(X,d)` would carry

\[
[\kappa_{X,d}]=L^{d-2}M^{-1}.
\]

Consider a monomial built only from `ell_B`, `m_B`, and `N_B`:

\[
I=\ell_B^\alpha m_B^\beta N_B^\gamma.
\]

Dimensional matching forces

\[
\alpha=d-2,
\qquad
\beta=-1.
\]

Pure-regrouping invariance then forces

\[
\gamma=-\frac{2}{d}.
\]

Hence the unique monomial is

\[
\boxed{
\kappa_{B,d}^{\rm inv}
=
\frac{\ell_B^{d-2}}{m_B}
N_B^{-2/d}
}
\]

or, using describability data,

\[
\boxed{
\kappa_{B,d}^{\rm inv}
=
\frac{\ell_B^{d-2}}{m_B}
\left(
\frac{R_D^{(\epsilon)}}{C_\epsilon}
\right)^{2/d}
}.
\]

## 5. Cancellation result

Substituting

\[
L_\Sigma=\ell_BN_B^{1/d},
\qquad
M=N_Bm_B,
\]

shows that

\[
\boxed{
\kappa_{B,d}^{\rm inv}
=
\frac{L_\Sigma^{d-2}}{M}
}.
\]

Thus, once full invariance under arbitrary pure bounded-level regrouping is required, the explicit microscopic bounded-unit scale cancels. The describability variables act as bookkeeping that reconstructs the same aggregate mass and structural scale.

This is a positive invariance result but a negative result for obtaining a new universal gravitational coupling from an arbitrarily chosen bounded hierarchy.

## 6. What bounded structure can still contribute

A nontrivial dimensionless structural factor can survive if it compares the additive bounded measure with an independently supplied external structural extent.

Let

\[
V_{\rm ext}=L_{\rm ext}^d.
\]

Define

\[
\boxed{
\Pi_B
:=
\frac{V_\Sigma}{V_{\rm ext}}
=
\frac{C_\epsilon}{R_D^{(\epsilon)}}
\frac{\ell_B^d}{L_{\rm ext}^d}
}.
\]

For homogeneous bounded units this is also

\[
\Pi_B
=
\frac{\bar\rho}{\rho_B},
\qquad
\rho_B=\frac{m_B}{\ell_B^d},
\qquad
\bar\rho=\frac{M}{V_{\rm ext}}.
\]

`Pi_B` is invariant under resolution changes and pure hierarchy regrouping, but it need not equal one. It records packing/concentration or the distinction between additive internal bounded measure and external structural extent.

This kind of dimensionless factor is a better candidate for the later DSD structural modifier `F_d` than the raw describability ratio itself.

## 7. Canonical-minimal bounded realization branch

The cancellation theorem applies when the bounded level is freely replaceable by a pure descriptive regrouping.

A different branch opens if DSD itself selects a canonical minimal realized bounded level `B_min` through formation and describability conditions. In that case

\[
(m_{\min},\ell_{\min})
\]

are not arbitrary analyst-selected hierarchy coordinates and must not be transformed by an optional regrouping rule before entering a physical specialization.

This branch is logically distinct from the hierarchy-invariant aggregate branch.

The next question is therefore not whether every bounded level supplies a universal minimum length, but whether the DSD formation/describability rules define a unique or equivalence-class-stable `B_min` for a realized source.

## Verdict

- PASS: `M = m_B C_epsilon/R_D` remains resolution invariant.
- PASS: `L_Sigma = ell_B (C_epsilon/R_D)^(1/d)` is resolution invariant and pure-regrouping invariant under additive measure preservation.
- PASS: the unique hierarchy-invariant monomial with dimensions `L^(d-2)/M` exists.
- IMPORTANT CANCELLATION: that monomial reduces to `L_Sigma^(d-2)/M`; arbitrary microscopic bounded-level information cancels.
- PASS as a structural descriptor: `Pi_B = V_Sigma/V_ext = rho_bar/rho_B` survives as a nontrivial dimensionless packing/concentration factor.
- OPEN: whether DSD defines a canonical minimal bounded realization `B_min` whose `(m_min, ell_min)` are physically selected rather than descriptively chosen.
