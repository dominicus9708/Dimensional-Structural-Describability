# D2 N-Channel Static Toy Model

This package contains two distinct finite tests on the current \(3\times3\) D2 realization of the Structural Admissibility axiom system.

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

## Carrier--boundary ablation

`src/structural/script/run_d2_carrier_boundary_ablation.py` is a controlled comparison between a historical-style selected-domain N-channel surrogate and the current active-carrier plus boundary-clause form.

It requires NumPy only:

```powershell
py -m pip install -r .\requirements-ablation.txt

# Two carrier-level hold-out splits (the default reproducibility run)
python .\src\structural\script\run_d2_carrier_boundary_ablation.py `
  --output-root .\results\structural

# Ten splits, written as one result directory
python .\src\structural\script\run_d2_carrier_boundary_ablation.py `
  --output-root .\results\structural `
  --first-seed 20260625 `
  --repeat-count 10
```

The regime is an explicit comparison extension: \(C\subseteq S\) and `interface` labels are allowed. The canonical D2 regime remains its all-blocked carrier-exact subset. See `CARRIER_BOUNDARY_ABLATION_SPEC.md` for the model definition and `RESULTS_CARRIER_BOUNDARY_ABLATION_20260625.md` for the 10-split result note.

## D. Static-descriptor layer audit

`descriptor_registry.json` is an internal layer map. It does not change formal paper terminology. It records whether each expression is static/dynamic and scalar/vector, and distinguishes a vector channel tuple from a scalar projection of that tuple.

`run_static_descriptor_audit.py` reuses the existing D2 code. It checks:

1. `channel_descriptors` is the implemented three-component vector-static intermediate representation;
2. `nchannel_descriptor` is exactly the scalar projection \(\boldsymbol\theta^{\mathsf T}\mathbf D\);
3. the \(N=1\) projection recovers the one-channel toy \(D_w\) analogue;
4. the recorded predictive and carrier--boundary result summaries remain readable and marked `pass`.

```powershell
# Fast layer and stored-result audit
python .\src\structural\script\run_static_descriptor_audit.py `
  --project-root . `
  --output-root .\results\structural `
  --rerun none

# Re-run the existing axiom-consistency script, then audit
python .\src\structural\script\run_static_descriptor_audit.py `
  --project-root . `
  --output-root .\results\structural `
  --rerun structure

# Re-run the existing predictive scripts; no new formula implementation is created
python .\src\structural\script\run_static_descriptor_audit.py `
  --project-root . `
  --output-root .\results\structural `
  --rerun predictive

# Re-run every existing benchmark, including the 10-split carrier--boundary ablation
python .\src\structural\script\run_static_descriptor_audit.py `
  --project-root . `
  --output-root .\results\structural `
  --rerun full
```

See `STATIC_DESCRIPTOR_LAYER_MAP.md` for the formal internal classification rule.

## E. Selected vector-static toy benchmark

`run_d2_vector_static_multitarget_toy.py` selects the extended D2 carrier--boundary regime as the first vector-static benchmark. It preserves

```text
(D_act, D_cap, D_exp, D_bnd, D_conn)
```

and compares it with one shared scalar projection and with task-specific scalar projections across survival, connectivity, and interface-reach targets. See `VECTOR_STATIC_TOY_MODEL_SPEC.md` and `RESULTS_VECTOR_STATIC_TOY_20260625.md`.

```powershell
# Install the existing NumPy dependency first
py -m pip install -r .\requirements-ablation.txt

# Ten selected-domain hold-out seeds
python .\src\structural\script\run_d2_vector_static_multitarget_toy.py `
  --output-root .\results\structural `
  --first-seed 20260625 `
  --repeat-count 10 `
  --theta-grid-step 0.1
```
