# Geometric-distortion constant audit 001

## Scope

This note tests whether the currently surviving DSD quantities can produce a universal structural geometric-distortion constant without using measured gravity as an input.

The starting relations are

\[
\mathcal R_D^{(\epsilon)}=\frac{C_\epsilon}{N_B},
\qquad
M=m_BN_B=\frac{m_BC_\epsilon}{\mathcal R_D^{(\epsilon)}}.
\]

For the present three-dimensional physical specialization, let the source density be \(\rho\), and define

\[
L_\rho=\left(\frac{M}{\rho}\right)^{1/3}.
\]

## Dimensional result

A potential-like geometric-distortion coupling \(K_X\) has target dimensions

\[
[K_X]=L^3M^{-1}T^{-2}.
\]

Using only \(c\), \(M\), \(\rho\), and dimensionless DSD descriptors, a monomial with these dimensions is unique up to a dimensionless factor:

\[
K_X^{\rm eff}=c^2F_B\,M^{-2/3}\rho^{-1/3}.
\]

Equivalently,

\[
K_X^{\rm eff}=c^2F_B\frac{L_\rho}{M}.
\]

Substituting the describability relation gives

\[
\boxed{
K_X^{\rm eff}
=c^2F_B
\left(
\frac{\left(\mathcal R_D^{(\epsilon)}\right)^2}
{m_B^2C_\epsilon^2\rho}
\right)^{1/3}
}
\]

where \(F_B\) is only a placeholder for dimensionless bounded-structure information. If boundedness is binary admissibility rather than a graded quantity, then a realized bounded source has \(F_B=1\) at this stage.

## Invariance audit

### Resolution change

For a fixed physical source and fixed bounded-unit choice,

\[
C_\epsilon\to aC_\epsilon,
\qquad
\mathcal R_D^{(\epsilon)}\to a\mathcal R_D^{(\epsilon)}.
\]

Therefore

\[
\frac{\left(\mathcal R_D^{(\epsilon)}\right)^2}{C_\epsilon^2}
\]

is unchanged.

### Bounded-hierarchy regrouping

For a pure regrouping of \(k\) lower-level units into one higher-level bounded unit,

\[
m_B\to km_B,
\qquad
\mathcal R_D^{(\epsilon)}\to k\mathcal R_D^{(\epsilon)}
\]

at fixed \(C_\epsilon\). Hence

\[
\frac{\left(\mathcal R_D^{(\epsilon)}\right)^2}{m_B^2}
\]

is unchanged.

Thus the candidate passes both resolution and bounded-hierarchy invariance tests.

## Universality audit

With \(F_B=1\), however,

\[
K_0=c^2M^{-2/3}\rho^{-1/3}
\]

is strongly source dependent. The numerical audit uses a 1 kg density reference, Earth mean values, Sun mean values, and the previous \(10^4M_\odot\) supermassive-star average proxy. Their resulting \(K_0\) values differ by many orders of magnitude.

Therefore

\[
\boxed{K_0\neq\text{universal constant}}
\]

and it must not be identified with the measured gravitational constant.

## What would be required to make the constant universal?

A purely dimensionless boundedness/describability factor cannot by itself remove the source dependence unless an additional universal scale or a structural law supplies a source-independent \(L/M\) conversion.

The missing object can be represented abstractly as

\[
\Lambda_*\quad [\Lambda_*]=L/M,
\]

so that a true universal candidate would have the form

\[
\boxed{K_X=c^2F_{\rm DSD}\Lambda_*}.
\]

Possible future derivation routes must obtain \(\Lambda_*\) from DSD formation/boundedness structure without inserting measured gravity, \(G\), \(GM\), gravitational radius, Planck units derived from \(G\), or any downstream gravitational observable.

## Audit verdict

- PASS: resolution invariance.
- PASS: bounded-hierarchy regrouping invariance.
- PASS: correct target dimensions for a three-dimensional potential-like coupling.
- FAIL as a universal constant: \(c^2M^{-2/3}\rho^{-1/3}\) remains source dependent.
- OPEN: whether DSD boundedness/formation structure produces an independent universal \(L/M\) scale \(\Lambda_*\).

This is an insufficiency result, not a failure of the structural-gravity program. It narrows the missing ingredient required for a non-circular derivation of a universal geometric-distortion constant.
