# D2 N-channel predictive toy benchmark: results

## Scope

This is a finite D2 structural benchmark. The target, channels, and restrictions are all defined on the current axiom-compatible D2 realization. It is not a physical prediction, empirical calibration, or quantum result.

## Exact target

For each nonempty admissible configuration \(p=(S,A)\), the target was computed directly by enumerating every nonempty element-complete restriction:

\[
Y_{\mathrm{surv}}(p)
=
\frac{1}{2^{|S|}-1}
\sum_{\varnothing\ne Y\subseteq S}
\mathbf 1\!\left[A\cap R_Y\ne\varnothing\right].
\]

The target was not formed from \(D_1\), \(D_2\), or \(D_3\).

## Primary carrier-level hold-out

- Nonempty admissible configurations: 21,798
- Train configurations: 16,343
- Hold-out configurations: 5,455
- Split unit: selected carrier \(S\), stratified by \(|S|\)
- Seed: 20260625

```text
                         MAE        RMSE       R²
single-channel        0.054940519  0.072061009  0.814023758
fixed 3-channel       0.044879482  0.062630468  0.859515595
learned 3-channel     0.038376020  0.052241574  0.902256181
```

The learned three-channel descriptor was

\[
\boldsymbol{\theta}
=(0.664192924,\,0.266621493,\,0.069185583).
\]

Relative to the single-channel baseline, its hold-out MAE decreased by 30.150% and RMSE by 27.504%.

## Twenty repeated carrier-level splits

Seeds 20260625–20260644 were evaluated under the same cardinality-stratified carrier split rule.

```text
Metric                 Single-channel          Learned 3-channel
MAE mean ± std          0.055199966 ± 0.000851191   0.039154796 ± 0.001706382
RMSE mean ± std         0.071856305 ± 0.001016763   0.052421751 ± 0.001520171
R² mean ± std           0.817065019 ± 0.004623235   0.902522502 ± 0.006458632
```

```text
MAE reduction mean ± std:  29.048% ± 3.344%
RMSE reduction mean ± std: 27.051% ± 1.655%
All 20 splits improved MAE:  True
All 20 splits improved RMSE: True
All 20 splits improved R²:   True
```

The learned weights remained nonnegative in every split. Their means were

\[
\theta_1=0.662985\pm0.002483,
\qquad
\theta_2=0.269930\pm0.016192,
\qquad
\theta_3=0.067085\pm0.017659.
\]

## Interpretation

The result supports a narrow structural statement: for this exact D2 restriction-survival target, the three documented channels approximate hold-out configurations more accurately than the first channel alone. It does not establish a general predictive advantage outside this finite D2 toy setting.