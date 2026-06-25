#!/usr/bin/env python3
"""Carrier-level hold-out benchmark for the D2 N-channel static descriptor.

This is a finite structural toy test, not an empirical or physical prediction test.
The exact target is the probability that at least one recorded active relation
survives a uniformly chosen nonempty element-complete restriction.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import random
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

EPS = 1e-12
SEED = 20260625
TRAIN_FRACTION = 0.70
FIXED_THETA = (0.5, 0.3, 0.2)


def load_d2_module():
    sibling = Path(__file__).with_name("run_d2_nchannel_static_toy.py")
    spec = importlib.util.spec_from_file_location("d2_axiom_static_toy", sibling)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load D2 model: {sibling}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    # Compatibility with the earlier compact static script in this repository.
    if not hasattr(module, "all_admissible_configurations"):
        @dataclass(frozen=True)
        class Configuration:
            domain: int
            active_relations: int
        module.Configuration = Configuration
        module.VERTEX_COUNT = getattr(module, "VERTEX_COUNT", len(module.V))
        module.all_submasks = module.subs
        module.induced_relations = lambda domain: module.R[domain]
        module.channel_descriptors = lambda config: tuple(module.d3(config.domain, config.active_relations)[1])
        def all_admissible_configurations():
            for domain in range(1 << module.VERTEX_COUNT):
                for active in module.subs(module.R[domain]):
                    yield Configuration(domain, active)
        module.all_admissible_configurations = all_admissible_configurations
    return module


def restriction_survival_probability(module, config):
    """Exact target: mean of 1[A intersect R_Y is nonempty] over nonempty Y subseteq S."""
    s, a = config.domain, config.active_relations
    if s == 0:
        raise ValueError("Target is undefined on an empty carrier.")
    survivors = sum(
        1 for y in module.all_submasks(s)
        if y != 0 and (a & module.induced_relations(y))
    )
    return survivors / ((1 << s.bit_count()) - 1)


def carrier_split(module, seed=SEED, train_fraction=TRAIN_FRACTION):
    grouped = {}
    for domain in range(1, 1 << module.VERTEX_COUNT):
        grouped.setdefault(domain.bit_count(), []).append(domain)
    rng = random.Random(seed)
    train, test, detail = set(), set(), {}
    for size in sorted(grouped):
        group = list(grouped[size])
        rng.shuffle(group)
        n_train = max(1, round(train_fraction * len(group)))
        train.update(group[:n_train])
        test.update(group[n_train:])
        detail[str(size)] = {
            "all_selected_carriers": len(group),
            "train_selected_carriers": n_train,
            "test_selected_carriers": len(group) - n_train,
        }
    if train & test:
        raise AssertionError("Carrier overlap in train/test split.")
    return train, test, detail


def solve(matrix, vector):
    n = len(vector)
    a = [row[:] + [rhs] for row, rhs in zip(matrix, vector)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(a[row][col]))
        if abs(a[pivot][col]) <= EPS:
            raise ValueError("Singular normal-equation matrix.")
        a[col], a[pivot] = a[pivot], a[col]
        scale = a[col][col]
        for j in range(col, n + 1):
            a[col][j] /= scale
        for row in range(n):
            if row == col:
                continue
            factor = a[row][col]
            for j in range(col, n + 1):
                a[row][j] -= factor * a[col][j]
    return [a[row][n] for row in range(n)]


def fit_affine(features, targets):
    width = len(features[0]) + 1
    xx = [[0.0] * width for _ in range(width)]
    xy = [0.0] * width
    for row, target in zip(features, targets):
        design = [1.0, *row]
        for i in range(width):
            xy[i] += design[i] * target
            for j in range(width):
                xx[i][j] += design[i] * design[j]
    return solve(xx, xy)


def predict(coefficients, features):
    return [coefficients[0] + sum(beta * value for beta, value in zip(coefficients[1:], row)) for row in features]


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


def metric(targets, predictions):
    err = [target - pred for target, pred in zip(targets, predictions)]
    mae = sum(abs(x) for x in err) / len(err)
    rmse = math.sqrt(sum(x * x for x in err) / len(err))
    mean_y = sum(targets) / len(targets)
    sse = sum(x * x for x in err)
    sst = sum((y - mean_y) ** 2 for y in targets)
    return {
        "mae": mae,
        "rmse": rmse,
        "r2": 1.0 - sse / sst,
        "prediction_min": min(predictions),
        "prediction_max": max(predictions),
        "predictions_below_zero": sum(x < 0.0 for x in predictions),
        "predictions_above_one": sum(x > 1.0 for x in predictions),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=Path("results") / "structural")
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--train-fraction", type=float, default=TRAIN_FRACTION)
    args = parser.parse_args()
    d2 = load_d2_module()
    configs = [p for p in d2.all_admissible_configurations() if p.domain != 0]
    assert len(configs) == 21798
    train_domains, test_domains, by_size = carrier_split(d2, args.seed, args.train_fraction)
    rows = [{
        "domain": p.domain,
        "active": p.active_relations,
        "size": p.domain.bit_count(),
        "channels": list(d2.channel_descriptors(p)),
        "target": restriction_survival_probability(d2, p),
    } for p in configs]
    train = [r for r in rows if r["domain"] in train_domains]
    test = [r for r in rows if r["domain"] in test_domains]
    y_train = [r["target"] for r in train]
    y_test = [r["target"] for r in test]

    base_coeff = fit_affine([[r["channels"][0]] for r in train], y_train)
    base_pred = predict(base_coeff, [[r["channels"][0]] for r in test])

    fixed_coeff = fit_affine([[dot(FIXED_THETA, r["channels"])] for r in train], y_train)
    fixed_pred = predict(fixed_coeff, [[dot(FIXED_THETA, r["channels"])] for r in test])

    full_coeff = fit_affine([r["channels"] for r in train], y_train)
    betas = full_coeff[1:]
    if any(beta < -EPS for beta in betas):
        raise AssertionError("Target is not representable by nonnegative convex N-channel weights.")
    scale = sum(betas)
    theta = [beta / scale for beta in betas]
    learned_coeff = [full_coeff[0], scale]
    learned_pred = predict(learned_coeff, [[dot(theta, r["channels"])] for r in test])
    full_pred = predict(full_coeff, [r["channels"] for r in test])
    reparameterization_error = max(abs(x - y) for x, y in zip(learned_pred, full_pred))
    assert reparameterization_error <= 1e-10

    result = {
        "status": "pass",
        "scope": "finite D2 carrier-hold-out structure benchmark; not empirical validation",
        "target": {
            "name": "restriction_survival_probability",
            "formula": "mean over nonempty Y subseteq S of indicator[A intersect R_Y is nonempty]",
            "computed_directly_not_from_descriptor": True,
            "range_all_configurations": [min(r["target"] for r in rows), max(r["target"] for r in rows)],
            "unique_target_values": len({r["target"] for r in rows}),
        },
        "data_split": {
            "seed": args.seed,
            "train_fraction": args.train_fraction,
            "split_unit": "selected carrier S, stratified by |S|",
            "nonempty_configurations": len(rows),
            "train_configurations": len(train),
            "test_configurations": len(test),
            "train_selected_carriers": len(train_domains),
            "test_selected_carriers": len(test_domains),
            "by_carrier_cardinality": by_size,
        },
        "model_parameters": {
            "single_channel_affine_coefficients": base_coeff,
            "fixed_theta": list(FIXED_THETA),
            "fixed_theta_affine_coefficients": fixed_coeff,
            "full_three_channel_affine_coefficients": full_coeff,
            "learned_theta": theta,
            "learned_descriptor_affine_coefficients": learned_coeff,
            "full_vector_to_convex_descriptor_max_abs_error": reparameterization_error,
        },
        "holdout_results": {
            "single_channel": metric(y_test, base_pred),
            "fixed_theta_three_channel": metric(y_test, fixed_pred),
            "learned_theta_three_channel": metric(y_test, learned_pred),
        },
    }
    base = result["holdout_results"]["single_channel"]
    learned = result["holdout_results"]["learned_theta_three_channel"]
    result["improvement_vs_single"] = {
        "learned_theta_mae_reduction_percent": 100 * (base["mae"] - learned["mae"]) / base["mae"],
        "learned_theta_rmse_reduction_percent": 100 * (base["rmse"] - learned["rmse"]) / base["rmse"],
    }

    out = args.output_root / datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d_%H%M%S")
    out.mkdir(parents=True, exist_ok=False)
    (out / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (out / "holdout_predictions.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["domain_mask", "active_relation_mask", "carrier_size", "D1", "D2", "D3", "target", "prediction_single", "prediction_fixed", "prediction_learned"])
        for r, p1, pf, pn in zip(test, base_pred, fixed_pred, learned_pred):
            writer.writerow([r["domain"], r["active"], r["size"], *r["channels"], r["target"], p1, pf, pn])
    report = f"""# D2 N-channel predictive toy benchmark

- status: pass
- target: exact restriction survival probability, computed directly by enumeration
- split: selected carrier level, stratified by |S|, seed={args.seed}

```text
                         MAE        RMSE       R2
single-channel        {base['mae']:.9f}  {base['rmse']:.9f}  {base['r2']:.9f}
fixed 3-channel       {result['holdout_results']['fixed_theta_three_channel']['mae']:.9f}  {result['holdout_results']['fixed_theta_three_channel']['rmse']:.9f}  {result['holdout_results']['fixed_theta_three_channel']['r2']:.9f}
learned 3-channel     {learned['mae']:.9f}  {learned['rmse']:.9f}  {learned['r2']:.9f}
```

\[
\theta=({theta[0]:.9f},\,{theta[1]:.9f},\,{theta[2]:.9f}),
\qquad
\text{{MAE reduction}}={result['improvement_vs_single']['learned_theta_mae_reduction_percent']:.3f}\%,
\qquad
\text{{RMSE reduction}}={result['improvement_vs_single']['learned_theta_rmse_reduction_percent']:.3f}\%.
\]

This result is restricted to the finite D2 structural target. It is not a physical accuracy claim.
"""
    (out / "test_report.md").write_text(report, encoding="utf-8")
    print(f"RESULT_DIRECTORY={out.resolve()}")
    print("STATUS=PASS")
    print(f"HOLDOUT_MAE_SINGLE={base['mae']:.12f}")
    print(f"HOLDOUT_MAE_LEARNED_N={learned['mae']:.12f}")

if __name__ == "__main__":
    main()
