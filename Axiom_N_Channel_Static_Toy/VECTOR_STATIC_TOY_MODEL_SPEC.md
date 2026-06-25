# D2 Carrier--Boundary--Connectivity Vector Static Toy Model

## Note classification

```text
검증 노트 / 정적식 / structural / vector-static / D2 finite toy model
```

## Selection rationale

This is the first selected toy model for the vector-static layer because it reuses the current extended D2 carrier--boundary regime and can separate, without introducing time evolution:

\[
C_p\subseteq S_p,
\qquad
\kappa_p\in\{\mathrm{blocked},\mathrm{interface}\},
\qquad
A_p\subseteq R_{C_p}.
\]

The canonical D2 subset is retained:

\[
C_p=S_p,
\qquad
\kappa_p(r)=\mathrm{blocked}
\quad
\text{for all exposed relations.}
\]

`interface` is a boundary label only. It never inserts an active relation and never causes bridge recovery under conservative gluing.

## Candidate vector-static descriptor

\[
\mathbf D_{\mathrm{VS}}(p)
=
\left(
D_{\mathrm{act}},
D_{\mathrm{cap}},
D_{\mathrm{exp}},
D_{\mathrm{bnd}},
D_{\mathrm{conn}}
\right)
\in[0,1]^5.
\]

```text
D_act:
active-relation participation in C_p

D_cap:
induced internal-relation capacity of C_p

D_exp:
carrier exposure to its boundary

D_bnd:
status-aware boundary shielding under κ_p

D_conn:
active-graph ordered-pair reachability in C_p
```

The first four components are local-average structural quantities. The last component is global and prevents connectivity from being discarded by premature scalar averaging.

## Exact D2 targets

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
\#\{y\in S_p\setminus C_p:\exists r\ni y,\;\kappa_p(r)=\mathrm{interface}\}
}{\max(1,|S_p\setminus C_p|)}.
\]

The targets are calculated directly by finite enumeration and boundary records. They are not constructed from descriptor outputs.

## Comparators

Shared scalar projection:

\[
D_{\theta}^{\mathrm{shared}}
=
\boldsymbol\theta^{\mathsf T}\mathbf D_{\mathrm{VS}},
\qquad
\theta_q\ge0,
\qquad
\sum_q\theta_q=1.
\]

A single \(\boldsymbol\theta\) is learned from the training partition to serve all three targets. Each target gets a separate affine readout, but the scalar summary is shared.

Task-specific scalar projection:

\[
D_{\theta^{(j)}}
=
\boldsymbol\theta^{(j)\mathsf T}\mathbf D_{\mathrm{VS}}.
\]

Each target gets its own scalar projection. This is included to distinguish the failure of one universal scalar summary from the possible usefulness of target-specific scalar projections.

Vector-static readout:

\[
\widehat{\mathbf Y}
=
\mathbf a+oldsymbol\Beta^{\mathsf T}\mathbf D_{\mathrm{VS}}.
\]

## Evaluation protocol

- 495,936 extended D2 configurations.
- 70/30 train/hold-out split by selected domain \(S_p\), stratified by \(|S_p|\).
- Ten seeds: 20260625--20260634.
- MAE, RMSE, and \(R^2\) reported per exact target.

## Interpretation boundary

A vector advantage means that a single common scalar projection loses task-relevant static structure in this finite D2 regime. It does not establish a final universal vector formula, a physical predictive advantage, or a need for time dynamics.
