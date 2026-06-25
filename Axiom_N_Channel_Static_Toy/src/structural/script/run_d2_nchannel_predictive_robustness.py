#!/usr/bin/env python3
"""Repeated carrier-level hold-out robustness test for the D2 N-channel descriptor."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path
from statistics import mean, pstdev
from zoneinfo import ZoneInfo


def load_predictive_module():
    path = Path(__file__).with_name("run_d2_nchannel_predictive_toy.py")
    spec = importlib.util.spec_from_file_location("d2_predictive_toy", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load predictive model: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def aggregate(values):
    return {"mean": mean(values), "population_std": pstdev(values), "min": min(values), "max": max(values)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=Path("results") / "structural")
    parser.add_argument("--first-seed", type=int, default=20260625)
    parser.add_argument("--repeat-count", type=int, default=20)
    parser.add_argument("--train-fraction", type=float, default=0.70)
    args = parser.parse_args()
    if args.repeat_count < 2:
        raise ValueError("repeat-count must be at least two.")

    p = load_predictive_module()
    d2 = p.load_d2_module()
    records = [{
        "domain": config.domain,
        "channels": list(d2.channel_descriptors(config)),
        "target": p.restriction_survival_probability(d2, config),
    } for config in d2.all_admissible_configurations() if config.domain != 0]

    runs = []
    for index in range(args.repeat_count):
        seed = args.first_seed + index
        train_domains, test_domains, _ = p.carrier_split(d2, seed, args.train_fraction)
        train = [r for r in records if r["domain"] in train_domains]
        test = [r for r in records if r["domain"] in test_domains]
        y_train = [r["target"] for r in train]
        y_test = [r["target"] for r in test]
        base_coeff = p.fit_affine([[r["channels"][0]] for r in train], y_train)
        full_coeff = p.fit_affine([r["channels"] for r in train], y_train)
        beta = full_coeff[1:]
        if any(x < -p.EPS for x in beta):
            raise AssertionError(f"Negative channel coefficient for seed {seed}: {beta}")
        scale = sum(beta)
        theta = [x / scale for x in beta]
        learned_coeff = [full_coeff[0], scale]
        base_pred = p.predict(base_coeff, [[r["channels"][0]] for r in test])
        learned_pred = p.predict(learned_coeff, [[p.dot(theta, r["channels"])] for r in test])
        base = p.metric(y_test, base_pred)
        learned = p.metric(y_test, learned_pred)
        runs.append({
            "seed": seed,
            "train_configurations": len(train),
            "test_configurations": len(test),
            "theta": theta,
            "single_channel": base,
            "learned_three_channel": learned,
            "mae_reduction_percent": 100 * (base["mae"] - learned["mae"]) / base["mae"],
            "rmse_reduction_percent": 100 * (base["rmse"] - learned["rmse"]) / base["rmse"],
        })

    base_mae = [x["single_channel"]["mae"] for x in runs]
    learned_mae = [x["learned_three_channel"]["mae"] for x in runs]
    base_rmse = [x["single_channel"]["rmse"] for x in runs]
    learned_rmse = [x["learned_three_channel"]["rmse"] for x in runs]
    base_r2 = [x["single_channel"]["r2"] for x in runs]
    learned_r2 = [x["learned_three_channel"]["r2"] for x in runs]
    theta = [[x["theta"][q] for x in runs] for q in range(3)]
    result = {
        "status": "pass",
        "scope": "repeated finite D2 carrier-hold-out robustness test; not empirical validation",
        "repeat_count": args.repeat_count,
        "first_seed": args.first_seed,
        "train_fraction": args.train_fraction,
        "all_runs_nonnegative_theta": True,
        "all_runs_mae_improved": all(new < old for old, new in zip(base_mae, learned_mae)),
        "all_runs_rmse_improved": all(new < old for old, new in zip(base_rmse, learned_rmse)),
        "all_runs_r2_improved": all(new > old for old, new in zip(base_r2, learned_r2)),
        "aggregate": {
            "single_channel_mae": aggregate(base_mae),
            "learned_three_channel_mae": aggregate(learned_mae),
            "single_channel_rmse": aggregate(base_rmse),
            "learned_three_channel_rmse": aggregate(learned_rmse),
            "single_channel_r2": aggregate(base_r2),
            "learned_three_channel_r2": aggregate(learned_r2),
            "mae_reduction_percent": aggregate([x["mae_reduction_percent"] for x in runs]),
            "rmse_reduction_percent": aggregate([x["rmse_reduction_percent"] for x in runs]),
            "theta_1": aggregate(theta[0]),
            "theta_2": aggregate(theta[1]),
            "theta_3": aggregate(theta[2]),
        },
        "runs": runs,
    }

    out = args.output_root / (datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d_%H%M%S") + "_robustness")
    out.mkdir(parents=True, exist_ok=False)
    (out / "robustness_summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    a = result["aggregate"]
    report = f"""# D2 N-channel predictive toy benchmark: robustness

- repeats: {args.repeat_count}
- seeds: {args.first_seed}–{args.first_seed + args.repeat_count - 1}
- split: selected carrier level, stratified by |S|

```text
Metric                 Single-channel          Learned 3-channel
MAE mean ± std          {a['single_channel_mae']['mean']:.9f} ± {a['single_channel_mae']['population_std']:.9f}   {a['learned_three_channel_mae']['mean']:.9f} ± {a['learned_three_channel_mae']['population_std']:.9f}
RMSE mean ± std         {a['single_channel_rmse']['mean']:.9f} ± {a['single_channel_rmse']['population_std']:.9f}   {a['learned_three_channel_rmse']['mean']:.9f} ± {a['learned_three_channel_rmse']['population_std']:.9f}
R2 mean ± std           {a['single_channel_r2']['mean']:.9f} ± {a['single_channel_r2']['population_std']:.9f}   {a['learned_three_channel_r2']['mean']:.9f} ± {a['learned_three_channel_r2']['population_std']:.9f}
```

```text
MAE reduction mean ± std:  {a['mae_reduction_percent']['mean']:.3f}% ± {a['mae_reduction_percent']['population_std']:.3f}%
RMSE reduction mean ± std: {a['rmse_reduction_percent']['mean']:.3f}% ± {a['rmse_reduction_percent']['population_std']:.3f}%
All splits improved MAE:   {result['all_runs_mae_improved']}
All splits improved RMSE:  {result['all_runs_rmse_improved']}
All splits improved R2:    {result['all_runs_r2_improved']}
```

This strengthens only the finite D2 structural claim. It is not a physical accuracy claim.
"""
    (out / "robustness_report.md").write_text(report, encoding="utf-8")
    print(f"RESULT_DIRECTORY={out.resolve()}")
    print("STATUS=PASS")
    print(f"ALL_RUNS_MAE_IMPROVED={result['all_runs_mae_improved']}")
    print(f"ALL_RUNS_RMSE_IMPROVED={result['all_runs_rmse_improved']}")

if __name__ == "__main__":
    main()
