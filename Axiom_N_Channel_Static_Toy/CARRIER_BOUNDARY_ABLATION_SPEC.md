# D2 Carrier--Boundary Ablation: Specification

## Note classification

```text
검증 노트 / 정적식 / structural / D2 유한 비교 regime
```

## Purpose

This benchmark separates the following question from the earlier single-versus-multichannel test:

> When a historical-style N-channel static aggregation is expressed under the current Structural Admissibility axioms, does explicit active-carrier support and boundary-clause information add useful structural signal?

It is a finite structural test only. It does not supply physical calibration, a quantum prediction, or an empirical claim.

## Regimes

The canonical D2 realization remains unchanged:

\[
C_p=S_p,
\qquad
\kappa_p(r)=\mathrm{blocked}
\quad
\text{for every exposed relation.}
\]

The comparison regime permits

\[
\varnothing\ne C_p\subseteq S_p\subseteq X_{\mathrm{D2}},
\qquad
A_p\subseteq R_{C_p},
\]

and labels each exposed relation by either `blocked` or `interface`.

`interface` is a boundary label only. It is not an active relation and it does not trigger relation recovery after gluing.

## Static channel fields

For a vertex \(x\) in a chosen aggregation support:

\[
\alpha_{1}(x)
=
\frac{\deg_{A_p}(x)}{\deg_X(x)},
\]

\[
\alpha_{2}(x)
=
\frac{\deg_{R_{C_p}}(x)}{\deg_X(x)},
\]

\[
\alpha^0_{3}(x)
=
\frac{1}{1+\deg_{\partial_R C_p}(x)},
\]

\[
\alpha^{\kappa}_{3}(x)
=
\frac{1+\deg_{\mathrm{blocked}}(x)}
{1+\deg_{\partial_R C_p}(x)}.
\]

The third status-aware channel equals one at a locally fully blocked boundary and decreases only where `interface` labels occur.

All descriptors use the normalized counting weight on their support:

\[
D(p)=
\frac{1}{|U|}
\sum_{x\in U}
\sum_{q=1}^{3}
\theta_q\alpha_q(x),
\qquad
\theta_q\ge0,
\qquad
\sum_q\theta_q=1.
\]

## Controlled models

\[
M_0(p)
=
\frac{1}{|S_p|}
\sum_{x\in S_p}\alpha_1(x).
\]

\[
M_1(p)
=
\frac{1}{|S_p|}
\sum_{x\in S_p}
\sum_q\theta_q\alpha^0_q(x).
\]

\[
M_2(p)
=
\frac{1}{|C_p|}
\sum_{x\in C_p}
\sum_q\theta_q\alpha^0_q(x).
\]

\[
M_3(p)
=
\frac{1}{|S_p|}
\sum_{x\in S_p}
\left[
\theta_1\alpha_1(x)+
\theta_2\alpha_2(x)+
\theta_3\alpha_3^{\kappa}(x)
\right].
\]

\[
M_4(p)
=
\frac{1}{|C_p|}
\sum_{x\in C_p}
\left[
\theta_1\alpha_1(x)+
\theta_2\alpha_2(x)+
\theta_3\alpha_3^{\kappa}(x)
\right].
\]

\(M_1\) is a controlled D2 surrogate of the historical N-channel aggregation; it is not a claim that every historical term had this exact finite form. The purpose is to isolate aggregation support and boundary-clause effects under identical finite records.

## Exact targets

\[
Y_{\mathrm{surv}}(p)
=
\frac{1}{2^{|C_p|}-1}
\sum_{\varnothing\ne Y\subseteq C_p}
\mathbf 1\!\left[A_p\cap R_Y\ne\varnothing\right].
\]

\[
Y_{\mathrm{conn}}(p)
=
\frac{1}{2^{|C_p|}-1}
\sum_{\varnothing\ne Y\subseteq C_p}
\mathbf 1\!\left[(Y,A_p\cap R_Y)\text{ is connected}\right].
\]

\[
Y_{\mathrm{int}}(p)
=
\frac{
\#\left\{y\in S_p\setminus C_p:
\exists r\ni y,\ \kappa_p(r)=\mathrm{interface}
\right\}
}{\max(1,|S_p\setminus C_p|)}.
\]

The targets are calculated directly from finite restrictions and boundary records; they are not generated from descriptor outputs.

## Interpretation rule

A lower \(M_4\) hold-out error than \(M_1\) means only that carrier-plus-boundary aggregation approximates that exact D2 target more closely under the stated comparison regime. It does not show a general physical advantage or universal scalar-descriptor dominance.
