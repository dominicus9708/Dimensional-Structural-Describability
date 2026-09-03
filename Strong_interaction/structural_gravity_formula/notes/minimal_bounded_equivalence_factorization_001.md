# Minimal bounded realization equivalence and factorization audit 001

## Scope

This note continues the structural-gravity audit after introducing a canonical minimal bounded realization `B_min`. The goal is to determine whether different minimal bounded sources can belong to one gravitational-equivalence class without fitting to measured gravity.

The current DSD formal papers do not automatically convert property names, aggregation records, or dynamic labels into physical forces or universal coefficients. Therefore the boundedness predicate, refinement relation, and geometric-response bridge used here remain part of the structural-gravity specialization.

## 1. Minimal bounded realization

Let `B` be an admissible bounded source realization in the structural-gravity specialization. Write

\[
B' \prec_B B
\]

when `B'` is a proper refinement of `B` that is still formation-admissible, describable at the declared internal regime, and bounded under the same specialization.

A canonical minimal bounded realization satisfies

\[
B_{\min}\in\mathcal B,
\qquad
\nexists B'\in\mathcal B\text{ such that }B'\prec_B B_{\min}.
\]

Minimality is therefore order-theoretic and structural. It does not assert a globally minimum spacetime length or globally minimum mass.

## 2. Dimensional pair and scale-free structural signature

For one minimal bounded realization, let

\[
m_B>0,
\qquad
\ell_B>0
\]

be its source mass and characteristic bounded structural scale in a `d`-dimensional localization specialization.

Let

\[
\mathbf z_B
\]

denote a dimensionless structural signature built only from independently defined DSD information, for example resolution-invariant describability information, normalized internal profiles, bounded-refinement data, or other explicitly supplied dimensionless property records. No gravitational observable, measured `G`, `GM`, gravitational radius, or quantity derived from them may enter `\mathbf z_B`.

## 3. Most general source-to-distortion coupling from `(m_B, ell_B)`

For a dimensionless distortion field `X`, a second-order local source coupling has dimensions

\[
[\kappa_{X,d}]=L^{d-2}M^{-1}.
\]

If the only dimensional inputs at the minimal-source level are `m_B` and `ell_B`, then every candidate has the form

\[
\boxed{
\Lambda_d(B)
=
\frac{\ell_B^{d-2}}{m_B}
F_d(\mathbf z_B)
}
\]

where `F_d` is dimensionless.

This equation is a dimensional factorization, not yet a physical law.

## 4. Gravitational-equivalence condition

Different minimal bounded realizations belong to one candidate gravitational-equivalence class only if

\[
\boxed{
\Lambda_d(B_i)=\Lambda_d(B_j)
}
\]

for all members of the class.

Equivalently,

\[
\boxed{
\frac{F_d(\mathbf z_i)}{F_d(\mathbf z_j)}
=
\frac{m_i}{m_j}
\left(\frac{\ell_j}{\ell_i}\right)^{d-2}
}
\]

must hold.

This ratio test does not require the absolute value of the eventual gravitational constant. It is therefore suitable for a non-circular pre-`G` audit.

## 5. Factorization criterion

Suppose two minimal bounded realizations have the same admissible dimensionless signature,

\[
\mathbf z_i=\mathbf z_j.
\]

Then `F_d(\mathbf z_i)=F_d(\mathbf z_j)`. Universality therefore requires

\[
\boxed{
\frac{\ell_i^{d-2}}{m_i}
=
\frac{\ell_j^{d-2}}{m_j}
}
\]

or

\[
\boxed{
m\propto\ell^{d-2}}
\]

within that scale-similar equivalence class.

For `d=3`, the necessary relation reduces to

\[
\boxed{m\propto\ell}.
\]

This is a necessary condition only. It is not asserted as a DSD law.

## 6. No-go result for purely scale-free correction factors

If a family of minimal bounded realizations preserves the same scale-free structural signature `z` while its mass-size scaling is

\[
m\propto\ell^{\mu},
\]

then

\[
\Lambda_d\propto\ell^{d-2-\mu}.
\]

Therefore any correction factor built only from scale-invariant describability or boundedness quantities cannot make the coupling universal unless

\[
\boxed{\mu=d-2}.
\]

If this condition fails, at least one of the following must be true:

1. the realizations do not belong to one gravitational-equivalence class;
2. the structural signature is incomplete;
3. the response factor contains an independently justified dimensionless quantity that changes under physical rescaling;
4. the proposed universal coupling does not follow from these ingredients.

## 7. Scale-sensitive dimensionless route

A non-gravitational scale-sensitive dimensionless quantity may be constructed if an independently justified propagation scale `c_X` and Planck's constant are admitted:

\[
\boxed{
\chi_B
=
\frac{m_Bc_X\ell_B}{\hbar}
}.
\]

This does not use measured gravity. It is not automatically a DSD invariant, but it is a legitimate candidate variable for a later bounded-formation constitutive law.

If a candidate family scales as

\[
m\propto\ell^{\mu}
\]

and a structural response behaves locally as

\[
F_d\propto\chi_B^{\alpha},
\]

then universality requires

\[
\boxed{
\alpha
=
\frac{\mu-(d-2)}{\mu+1}
}
\qquad(\mu\neq-1).
\]

This equation must not be used to fit `alpha` after looking at gravity. A valid DSD derivation would need to obtain the functional dependence of `F_d` independently from bounded formation/describability.

## 8. Current audit verdict

- PASS: minimality can be formulated without postulating a minimum spacetime length.
- PASS: the candidate coupling separates into a dimensional factor `ell_B^(d-2)/m_B` and a dimensionless structural factor.
- PASS: universality can be tested by ratios before any absolute `G` comparison.
- CONDITIONAL: if two candidates have the same scale-free structural signature, universality requires `m proportional to ell^(d-2)`; in `d=3`, `m proportional to ell`.
- NO-GO: purely scale-free describability/boundedness corrections cannot repair a different mass-size exponent.
- OPEN: whether DSD bounded formation supplies a scale-sensitive, non-gravitational dimensionless invariant such as a function of `m_B c_X ell_B / hbar`, or instead partitions minimal bounded realizations into distinct response classes.

## 9. Next test

The next empirical/theoretical step should not select atoms, molecules, or elementary particles as `B_min` by convention. First define the structural-gravity boundedness predicate and proper bounded-refinement relation. Then construct candidate `B_min` classes and record, for each candidate,

- `m_B`,
- `ell_B`,
- dimensionless structural signature `z_B`,
- whether a proper bounded refinement exists,
- the ratio-only quantity `ell_B^(d-2)/m_B`,
- any independently justified scale-sensitive dimensionless invariant.

Only after this classification should candidate response-factor ratios be compared across classes.
