# D2 N-Channel Static Toy Model

This module performs an exhaustive finite consistency test of a three-channel static descriptor on the current \(3\times3\) D2 Structural Admissibility realization.

## Scope

This is a structural consistency toy model. It does not calibrate a physical observable, derive a quantum rule, calculate a particle-size limit, or provide empirical validation.

The descriptor uses three bounded D2 channels:

1. active-relation participation;
2. induced internal-relation capacity;
3. blocked-boundary shielding.

The model tests:

- recovery of the one-channel toy descriptor at \(N=1\);
- convex boundedness of the three-channel aggregation;
- restriction closure over all admissible \((p,Y)\) pairs;
- rejection of a deliberately transmissive boundary status under the canonical D2 blocked rule;
- conservative gluing over all selected-domain pairs;
- \(D_4\) symmetry invariance.

## Location in the local research tree

```text
D:\Paper\Dimensional_Structural_Describability\Axiom_N_Channel_Static_Toy
```

## Input

No external files are needed. The script encodes the D2 lattice directly from the current axiom manuscript.

## Output

Each run creates:

```text
results\structural\YYYYMMDD_HHMMSS\summary.json
results\structural\YYYYMMDD_HHMMSS\test_report.md
```

## PowerShell

```powershell
cd D:\Paper\Dimensional_Structural_Describability\Axiom_N_Channel_Static_Toy
python .\src\structural\script\run_d2_nchannel_static_toy.py `
  --output-root .\results\structural
```
