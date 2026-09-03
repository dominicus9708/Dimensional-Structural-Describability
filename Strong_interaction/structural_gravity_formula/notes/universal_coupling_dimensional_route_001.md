# Universal coupling dimensional route 001

## Purpose

After the normalization audit, the two coefficients of the provisional chain

\[
\rho_d \to X \to \mathbf a_X
\]

are not treated as independently physical unless a canonical normalization of \(X\) is derived. Define instead a potential-like distortion variable \(\Phi_X\) and one normalization-invariant source coupling \(\mathcal C_{X,d}\):

\[
\mathbf a_X=-\nabla\Phi_X,
\qquad
\Delta_d\Phi_X=\mathcal C_{X,d}\rho_d.
\]

Then

\[
[\mathcal C_{X,d}]=L^dM^{-1}T^{-2}.
\]

For isotropic spherical specialization,

\[
G_{X,d}:=\frac{\mathcal C_{X,d}}{S_{d-1}},
\qquad
|\mathbf a_X(r)|=G_{X,d}\frac{M(<r)}{r^{d-1}}.
\]

No Newtonian \(G\), inverse-square law, or three-dimensional coupling dimension is used as an input.

## Conditional uniqueness of the Laplacian closure

The Laplacian source closure is not a theorem of the present DSD core. However, consider a structural-gravity specialization that explicitly requires all of the following in a regular weak-response regime:

1. locality;
2. linear response in the distortion field and source density;
3. local homogeneity of the localization carrier;
4. local isotropy with no preferred direction;
5. invariance under \(\Phi_X\mapsto\Phi_X+\text{constant}\);
6. minimal second-order spatial differential closure.

For a scalar field on a locally Euclidean \(d\)-dimensional specialization, a constant-coefficient linear second-order scalar operator has principal part \(A^{ij}\partial_i\partial_j\). Isotropy forces \(A^{ij}\propto\delta^{ij}\), and shift invariance excludes a zeroth-order term. Under the stated minimality condition, the operator is therefore proportional to \(\Delta_d\).

This is a conditional structural-gravity result: the assumptions must be declared and audited; they are not inherited automatically from the Formation, Property, Static Aggregation, or Dynamics layers.

## What the current DSD core cannot supply

Formation/property statuses and describability ratios can provide qualitative or dimensionless structural information. Existing resolution- and hierarchy-invariant bookkeeping reconstructs physical source mass, but the predecessor layers do not provide a universal dimensionful mass or length scale.

Therefore a nonzero universal \(\mathcal C_{X,d}\) cannot be obtained from dimensionless describability/boundedness information alone. A universal dimensionful structural scale must be independently derived or admitted.

## Route A: universal structural mass scale

Suppose a later bounded-formation theorem supplies a universal structural mass scale \(m_*\), independently of gravitational measurements. If a universal propagation/response speed \(c_X\) and an action scale \(\hbar\) are also admitted as non-gravitational inputs, dimensional analysis fixes the coupling form up to a dimensionless structural factor \(F_d\):

\[
\boxed{
\mathcal C_{X,d}
=F_d\,\hbar^{d-2}c_X^{4-d}m_*^{-(d-1)}
}
\]

because this is the unique monomial in \(\hbar,c_X,m_*\) with dimensions \(L^dM^{-1}T^{-2}\).

Special cases are

\[
\mathcal C_{X,1}=F_1\frac{c_X^3}{\hbar},
\]

\[
\mathcal C_{X,2}=F_2\frac{c_X^2}{m_*},
\]

\[
\boxed{
\mathcal C_{X,3}=F_3\frac{\hbar c_X}{m_*^2}
}
\]

and

\[
\mathcal C_{X,4}=F_4\frac{\hbar^2}{m_*^3}.
\]

For the later three-dimensional specialization,

\[
\boxed{
G_{X,3}
=\frac{F_3}{4\pi}\frac{\hbar c_X}{m_*^2}
}
\]

is the quantity to compare with measured Newtonian \(G\), only after \(F_3\), \(c_X\), and \(m_*\) have been fixed independently of gravitational measurements.

## Route B: universal structural length scale

If instead DSD produces a universal minimum structural length or resolution \(\ell_*\), and if one additionally has the non-gravitational relation

\[
m_* = \frac{\hbar}{c_X\ell_*},
\]

then Route A can be rewritten as

\[
\boxed{
\mathcal C_{X,d}
=F_d\frac{c_X^3\ell_*^{d-1}}{\hbar}
}
\]

and in \(d=3\),

\[
G_{X,3}
=\frac{F_3}{4\pi}\frac{c_X^3\ell_*^2}{\hbar}.
\]

The relation between \(m_*\) and \(\ell_*\) is not supplied by the current DSD core and must not be assumed merely to obtain the desired dimensions.

## Role of describability and boundedness

The dimensionless factor \(F_d\) is the natural place for DSD-specific structure such as a resolution-invariant boundedness/describability invariant. Raw observer-resolution-dependent quantities such as \(\mathcal R_D^{(\epsilon)}\) cannot serve directly as a universal physical coupling.

A viable \(F_d\) must satisfy at least:

- invariance under observational resolution changes that leave the physical source unchanged;
- invariance under pure regrouping of bounded description levels;
- no change under relabeling of equivalent bounded decompositions;
- independence from gravitational observables used later for validation;
- a declared behavior under genuine formation/status transitions.

## Immediate research target

The problem is now split cleanly:

1. derive or rule out a universal bounded-formation scale \(m_*\) or \(\ell_*\);
2. construct a resolution- and hierarchy-invariant dimensionless DSD factor \(F_d\);
3. determine whether structural-gravity propagation fixes \(c_X\), and whether \(c_X=c_{\rm info}\) or \(c\) is a theorem, a specialization, or only an empirical correspondence;
4. only then compute \(\mathcal C_{X,d}\) and compare the \(d=3\) specialization with measured gravity.

## Audit verdict

- PASS: the normalization redundancy reduces the physical problem to one coupling \(\mathcal C_{X,d}\).
- CONDITIONAL PASS: Laplacian closure is uniquely selected under explicit local, isotropic, homogeneous, linear, shift-invariant, minimal second-order assumptions.
- IMPOSSIBILITY WITH CURRENT CORE ALONE: purely dimensionless describability/boundedness data cannot fix a nonzero dimensionful universal coupling.
- PROMISING OPEN ROUTE: a universal bounded-formation mass or length scale plus a DSD invariant factor can make the coupling calculable without inserting measured gravity.
- FORBIDDEN FOR DERIVATION: using \(G\), \(GM\), gravitational radius, Planck units derived from \(G\), or any downstream gravitational observable to choose \(m_*\), \(\ell_*\), \(F_d\), or \(c_X\).
