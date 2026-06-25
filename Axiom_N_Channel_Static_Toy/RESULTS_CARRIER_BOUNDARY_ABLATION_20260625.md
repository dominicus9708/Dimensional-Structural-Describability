# D2 Carrier--Boundary Ablation: 2026-06-25 Result Note

## Note classification

```text
검증 노트 / 정적식 일반화 / structural / D2 carrier--boundary ablation
```

## Status

- finite structural ablation: passed
- carrier-level hold-out seeds: 20260625--20260634
- scope: extended D2 comparison regime only
- excluded claims: empirical validation, physical prediction, quantum interpretation, universal formula superiority

## Core result: M4 versus M1

\(M_1\) is the historical-style selected-domain N-channel surrogate. \(M_4\) is the active-carrier plus boundary-clause form.

```text
Target                              M1 MAE mean     M4 MAE mean     M4 vs M1
restriction survival                0.059615151     0.047593673     +20.163% ± 0.832%
restriction connectivity            0.115414720     0.119634863     -3.646% ± 1.281%
selected-inactive interface reach   0.392009587     0.306323984     +21.860% ± 0.331%
```

The same directions appeared in all ten selected-domain hold-out splits:

```text
restriction survival:              M4 improved in 10/10 splits
selected-inactive interface reach: M4 improved in 10/10 splits
restriction connectivity:          M4 did not improve in 10/10 splits
```

## What this supports

The active-carrier and boundary-clause form contributes useful structural signal for at least two independent finite D2 targets:

\[
Y_{\mathrm{surv}}
\quad\text{and}\quad
Y_{\mathrm{int}}.
\]

It does not support a stronger statement that one scalar carrier-boundary descriptor is uniformly superior for all structural tasks. In particular, the connectivity target exposes a limitation of compressing relation survival, carrier structure, and boundary treatment into one scalar.

## Exact compatibility checks

```text
Canonical subset recovery, C=S:
M1=M2 maximum absolute descriptor-channel error: 0
M3=M4 maximum absolute descriptor-channel error: 0

Conservative gluing witness:
An interface-labeled relation between two one-vertex carriers becomes internal
when the carriers are glued, but it remains absent from the active-relation
record. Automatic bridge activation: false.
```

## Research consequence

The third, current formula is positive as a structured extension, not as a completed universal replacement. The next mathematical task is not to add further channels immediately. It is to determine whether connectivity requires:

1. a separate structural descriptor rather than one scalar aggregate;
2. a vector-valued static descriptor \(\mathbf D^{[N]}\);
3. a target-specific projection from the common channel vector.

The result does not yet select among those three possibilities.
