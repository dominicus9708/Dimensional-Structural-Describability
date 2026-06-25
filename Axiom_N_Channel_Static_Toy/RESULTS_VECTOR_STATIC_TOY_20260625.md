# D2 Vector Static Toy Model: Result Note

## Note classification

```text
검증 노트 / 정적식 / structural / vector-static / D2 finite toy model
```

## Selected model

The selected first vector-static toy model is the **D2 Carrier--Boundary--Connectivity Multi-Target Vector Benchmark**.

\[
\mathbf D_{\mathrm{VS}}
=
(D_{\mathrm{act}},D_{\mathrm{cap}},D_{\mathrm{exp}},D_{\mathrm{bnd}},D_{\mathrm{conn}}).
\]

It is static: no \(t\), no relation-update rule, and no propagation term occurs in the descriptor or targets.

## Ten carrier-level hold-out seeds

A single shared scalar uses one convex \(\boldsymbol\theta\) to summarize the five components for all three targets. The vector-static model preserves the five components and permits a target-specific affine readout.

```text
Target                              Shared scalar MAE   Vector MAE    Vector MAE reduction
restriction survival                0.072680393         0.045435626   37.456% ± 1.278%
restriction connectivity            0.139467717         0.060651533   56.509% ± 0.462%
selected-inactive interface reach   0.413460309         0.279293201   32.452% ± 0.308%
```

All ten splits improved MAE, RMSE, and \(R^2\) for the vector-static readout relative to the single shared scalar projection.

```text
Target                              Shared R²           Vector R²
restriction survival                0.810512726         0.933553249
restriction connectivity            0.269658856         0.856382316
selected-inactive interface reach  -0.005785771         0.397657311
```

## Important distinction

A scalar projection chosen separately for each target also recovers much of the lost information.

```text
Target                              Task-specific scalar MAE   Vector MAE
restriction survival                0.047568816                0.045435626
restriction connectivity            0.069422615                0.060651533
selected-inactive interface reach   0.281197728                0.279293201
```

Therefore the precise result is not that scalar descriptors are unusable. Rather:

```text
One common scalar projection is too compressed to represent
survival, connectivity, and interface structure at the same time.

A scalar projection can remain useful when it is selected for
one declared task.

The vector-static layer preserves the shared structural record
before a task-specific scalar projection is chosen.
```

## Scope

This is a finite D2 structural result. It is not evidence for a physical law, quantum prediction, particle-size bound, or vector dynamics. It supports keeping a vector-static middle layer between the scalar static descriptor and later dynamics.
