# D2 N-Channel Static Toy Model

This package contains two finite tests on the current \(3\times3\) D2 realization of the Structural Admissibility axiom system.

## Scope

These are structural toy-model tests. They do not calibrate a physical observable, derive a quantum rule, calculate a particle-size limit, or provide empirical validation.

## A. Axiom-consistency test

`run_d2_nchannel_static_toy.py` checks the three-channel static descriptor against the D2 axiom rules:

1. recovery of the one-channel toy descriptor at \(N=1\);
2. convex boundedness of the three-channel aggregation;
3. restriction closure;
4. rejection of a deliberately transmissive boundary status under the canonical D2 blocked rule;
5. conservative gluing;
6. \(D_4\) symmetry invariance.

## B. Predictive hold-out toy benchmark

`run_d2_nchannel_predictive_toy.py` compares a single-channel and a three-channel static descriptor against an exact combinatorial target, calculated independently by direct restriction enumeration:

\[
Y_{\mathrm{surv}}(p)
=
\frac{1}{2^{|S_p|}-1}
\sum_{\varnothing\ne Y\subseteq S_p}
\mathbf 1\!\left[A_p\cap R_Y\ne\varnothing\right].
\]

The train/test split is by selected carrier \(S\), stratified by \(|S|\), so records originating from the same carrier do not appear in both partitions.

`run_d2_nchannel_predictive_robustness.py` repeats this carrier-level hold-out comparison over multiple seeds.

## Local project location

```text
D:\Paper\Dimensional_Structural_Describability\Axiom_N_Channel_Static_Toy
```

## Input

No external files are required. Each script encodes the D2 lattice directly from the current axiom manuscript.

## Output

Each run creates a timestamped output folder below:

```text
results\structural\YYYYMMDD_HHMMSS\
```

The predictive run writes `summary.json`, `test_report.md`, `carrier_split.json`, and `holdout_predictions.csv`. The robustness run writes `robustness_summary.json` and `robustness_report.md`.

## PowerShell

```powershell
cd D:\Paper\Dimensional_Structural_Describability\Axiom_N_Channel_Static_Toy

# Axiom-consistency test
python .\src\structural\script\run_d2_nchannel_static_toy.py `
  --output-root .\results\structural

# Carrier-level hold-out benchmark
python .\src\structural\script\run_d2_nchannel_predictive_toy.py `
  --output-root .\results\structural

# Repeated carrier-level robustness test
python .\src\structural\script\run_d2_nchannel_predictive_robustness.py `
  --output-root .\results\structural `
  --first-seed 20260625 `
  --repeat-count 20
```