#!/usr/bin/env python3
"""D2 multi-target vector-static descriptor toy benchmark.

This script reuses the extended carrier--boundary D2 comparison regime. It
compares a five-component static descriptor vector with (i) one shared scalar
projection and (ii) target-specific scalar projections. It is a finite
structural benchmark, not an empirical or physical prediction model.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

try:
    import numpy as np
except ImportError as exc:
    raise SystemExit("Install NumPy first: py -m pip install numpy") from exc

EPS = 1e-12
DEFAULT_SEED = 20260625
DEFAULT_REPEATS = 10
DEFAULT_TRAIN_FRACTION = 0.70
DEFAULT_GRID_STEP = 0.05


def load_ablation_module():
    path = Path(__file__).with_name("run_d2_carrier_boundary_ablation.py")
    spec = importlib.util.spec_from_file_location("d2_carrier_boundary", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load D2 carrier-boundary module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def active_reachability_ratio(ab: Any, carrier: int, active: int) -> float:
    """Fraction of ordered carrier pairs mutually reachable in the active graph."""
    count = carrier.bit_count()
    if count == 0:
        raise ValueError("The active carrier must be nonempty.")
    unseen = carrier
    total = 0
    while unseen:
        start_bit = unseen & -unseen
        start = start_bit.bit_length() - 1
        seen = start_bit
        stack = [start]
        while stack:
            x = stack.pop()
            for edge in ab.bits(active & ab.VM[x]):
                u, v = ab.E[edge]
                nxt = v if u == x else u
                bit = 1 << nxt
                if carrier & bit and not seen & bit:
                    seen |= bit
                    stack.append(nxt)
        component_size = seen.bit_count()
        total += component_size * component_size
        unseen &= ~seen
    return total / (count * count)


def carrier_exposure_ratio(ab: Any, carrier: int) -> float:
    """Mean local exposed-boundary degree normalised by ambient lattice degree."""
    boundary = ab.B[carrier]
    values = [ab.inc(x, boundary) / ab.DEG[x] for x in ab.bits(carrier)]
    return sum(values) / len(values)


def build_vector_dataset(ab: Any):
    """Build extended D2 cases and exact targets using existing axiom primitives."""
    selected_domains: list[int] = []
    features: list[tuple[float, float, float, float, float]] = []
    y_surv: list[float] = []
    y_conn: list[float] = []
    y_interface: list[float] = []
    cache: dict[tuple[int, int], tuple[float, float, float, float]] = {}

    for carrier in range(1, 1 << ab.N):
        for extra in ab.subs(ab.ALL ^ carrier):
            selected = carrier | extra
            for active in ab.subs(ab.R[carrier]):
                key = (carrier, active)
                if key not in cache:
                    cache[key] = (
                        ab.ysurv(carrier, active),
                        ab.yconn(carrier, active),
                        carrier_exposure_ratio(ab, carrier),
                        active_reachability_ratio(ab, carrier, active),
                    )
                survival, connectivity, exposure, reachability = cache[key]
                for interface_mask in ab.pats(carrier):
                    d_act, d_cap, d_bnd = ab.channels(
                        carrier, active, interface_mask, carrier, True
                    )
                    selected_domains.append(selected)
                    features.append((d_act, d_cap, exposure, d_bnd, reachability))
                    y_surv.append(survival)
                    y_conn.append(connectivity)
                    y_interface.append(ab.yinterface(selected, carrier, interface_mask))

    domains = np.asarray(selected_domains, dtype=np.int16)
    descriptor = np.asarray(features, dtype=float)
    targets = np.column_stack((
        np.asarray(y_surv, dtype=float),
        np.asarray(y_conn, dtype=float),
        np.asarray(y_interface, dtype=float),
    ))
    if len(domains) != 495_936:
        raise AssertionError(f"Unexpected extended D2 case count: {len(domains)}")
    if np.any(descriptor < -EPS) or np.any(descriptor > 1.0 + EPS):
        raise AssertionError("A normalised vector-static component left [0,1].")
    if np.any(targets < -EPS) or np.any(targets > 1.0 + EPS):
        raise AssertionError("An exact D2 target left [0,1].")
    return domains, descriptor, targets


def simplex_grid(dim: int, step: float) -> np.ndarray:
    denominator = round(1.0 / step)
    if not math.isclose(denominator * step, 1.0, abs_tol=1e-12):
        raise ValueError("theta-grid-step must divide one exactly")
    rows: list[tuple[float, ...]] = []

    def generate(position: int, remaining: int, prefix: list[int]) -> None:
        if position == dim - 1:
            rows.append(tuple([*(x / denominator for x in prefix), remaining / denominator]))
            return
        for value in range(remaining + 1):
            generate(position + 1, remaining - value, [*prefix, value])

    generate(0, denominator, [])
    return np.asarray(rows, dtype=float)


def affine_fit_scalar(z: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    mean_z = float(z.mean())
    mean_y = float(y.mean())
    centered_z = z - mean_z
    variance = float(centered_z @ centered_z)
    if variance <= EPS:
        return mean_y, 0.0
    slope = float(centered_z @ (y - mean_y) / variance)
    return mean_y - slope * mean_z, slope


def affine_fit_vector(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    design = np.column_stack((np.ones(len(x)), x))
    coefficients, *_ = np.linalg.lstsq(design, y, rcond=None)
    return coefficients


def metric(y: np.ndarray, prediction: np.ndarray) -> dict[str, float | int]:
    error = y - prediction
    sse = float(error @ error)
    centered = y - y.mean()
    sst = float(centered @ centered)
    return {
        "mae": float(np.mean(np.abs(error))),
        "rmse": float(np.sqrt(np.mean(error * error))),
        "r2": float(1.0 - sse / sst) if sst > EPS else 1.0,
        "prediction_min": float(prediction.min()),
        "prediction_max": float(prediction.max()),
        "predictions_below_zero": int(np.sum(prediction < 0.0)),
        "predictions_above_one": int(np.sum(prediction > 1.0)),
    }


def best_scalar_theta(x: np.ndarray, y: np.ndarray, candidates: np.ndarray) -> np.ndarray:
    """Find simplex theta maximising training R2 for one scalar target."""
    x_centered = x - x.mean(axis=0)
    y_centered = y - y.mean()
    covariance = x_centered.T @ x_centered / len(x)
    cross = x_centered.T @ y_centered / len(x)
    variance_y = float(y_centered @ y_centered / len(x))
    variances = np.einsum("qi,ij,qj->q", candidates, covariance, candidates)
    covariances = candidates @ cross
    score = np.full(len(candidates), -np.inf)
    valid = variances > EPS
    score[valid] = (covariances[valid] ** 2) / (variances[valid] * variance_y)
    return candidates[int(np.argmax(score))]


def best_shared_theta(x: np.ndarray, y_matrix: np.ndarray, candidates: np.ndarray) -> np.ndarray:
    """Find one simplex projection jointly maximising the sum of training R2 values."""
    x_centered = x - x.mean(axis=0)
    y_centered = y_matrix - y_matrix.mean(axis=0)
    covariance = x_centered.T @ x_centered / len(x)
    cross = x_centered.T @ y_centered / len(x)
    variance_y = np.mean(y_centered * y_centered, axis=0)
    variances = np.einsum("qi,ij,qj->q", candidates, covariance, candidates)
    covariances = candidates @ cross
    score = np.full(len(candidates), -np.inf)
    valid = variances > EPS
    score[valid] = np.sum(
        (covariances[valid] ** 2) / (variances[valid, None] * variance_y[None, :]),
        axis=1,
    )
    return candidates[int(np.argmax(score))]


def one_run(ab: Any, domains: np.ndarray, x: np.ndarray, y: np.ndarray, candidates: np.ndarray,
            seed: int, train_fraction: float) -> dict[str, Any]:
    train, test, split_detail = ab.split(domains, seed, train_fraction)
    if np.any(train & test) or not np.any(train) or not np.any(test):
        raise AssertionError("Invalid selected-domain train/test split")
    x_train, x_test = x[train], x[test]
    y_train, y_test = y[train], y[test]
    names = ("restriction_survival", "restriction_connectivity", "selected_inactive_interface_reach")

    shared_theta = best_shared_theta(x_train, y_train, candidates)
    shared_train = x_train @ shared_theta
    shared_test = x_test @ shared_theta
    vector_coefficients = affine_fit_vector(x_train, y_train)
    vector_predictions = np.column_stack((np.ones(len(x_test)), x_test)) @ vector_coefficients

    shared_results: dict[str, Any] = {}
    task_results: dict[str, Any] = {}
    vector_results: dict[str, Any] = {}
    for index, name in enumerate(names):
        intercept, slope = affine_fit_scalar(shared_train, y_train[:, index])
        shared_results[name] = {
            "theta": shared_theta.tolist(),
            "intercept": intercept,
            "slope": slope,
            "holdout": metric(y_test[:, index], intercept + slope * shared_test),
        }

        task_theta = best_scalar_theta(x_train, y_train[:, index], candidates)
        task_train = x_train @ task_theta
        task_test = x_test @ task_theta
        intercept, slope = affine_fit_scalar(task_train, y_train[:, index])
        task_results[name] = {
            "theta": task_theta.tolist(),
            "intercept": intercept,
            "slope": slope,
            "holdout": metric(y_test[:, index], intercept + slope * task_test),
        }

        vector_results[name] = {
            "coefficients_with_intercept": vector_coefficients[:, index].tolist(),
            "holdout": metric(y_test[:, index], vector_predictions[:, index]),
        }

    return {
        "seed": seed,
        "data_split": {
            "split_unit": "selected domain S, stratified by |S|",
            "train_cases": int(np.sum(train)),
            "test_cases": int(np.sum(test)),
            "by_cardinality": split_detail,
        },
        "shared_scalar_projection": {"theta": shared_theta.tolist(), "targets": shared_results},
        "task_specific_scalar_projection": {"targets": task_results},
        "vector_static_descriptor": {"targets": vector_results},
    }


def aggregate(values: list[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    return {"mean": float(array.mean()), "population_std": float(array.std()), "min": float(array.min()), "max": float(array.max())}


def reduction(old: float, new: float) -> float:
    return 100.0 * (old - new) / old


def aggregate_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    names = ("restriction_survival", "restriction_connectivity", "selected_inactive_interface_reach")
    result: dict[str, Any] = {}
    for name in names:
        item: dict[str, Any] = {}
        for source, label in (
            ("shared_scalar_projection", "shared_scalar"),
            ("task_specific_scalar_projection", "task_specific_scalar"),
            ("vector_static_descriptor", "vector_static"),
        ):
            metrics = [run[source]["targets"][name]["holdout"] for run in runs]
            item[label] = {
                "mae": aggregate([m["mae"] for m in metrics]),
                "rmse": aggregate([m["rmse"] for m in metrics]),
                "r2": aggregate([m["r2"] for m in metrics]),
            }
        shared_mae = [run["shared_scalar_projection"]["targets"][name]["holdout"]["mae"] for run in runs]
        vector_mae = [run["vector_static_descriptor"]["targets"][name]["holdout"]["mae"] for run in runs]
        shared_rmse = [run["shared_scalar_projection"]["targets"][name]["holdout"]["rmse"] for run in runs]
        vector_rmse = [run["vector_static_descriptor"]["targets"][name]["holdout"]["rmse"] for run in runs]
        shared_r2 = [run["shared_scalar_projection"]["targets"][name]["holdout"]["r2"] for run in runs]
        vector_r2 = [run["vector_static_descriptor"]["targets"][name]["holdout"]["r2"] for run in runs]
        item["vector_vs_shared_scalar"] = {
            "mae_reduction_percent": aggregate([reduction(a, b) for a, b in zip(shared_mae, vector_mae)]),
            "rmse_reduction_percent": aggregate([reduction(a, b) for a, b in zip(shared_rmse, vector_rmse)]),
            "all_runs_mae_improved": all(b < a for a, b in zip(shared_mae, vector_mae)),
            "all_runs_rmse_improved": all(b < a for a, b in zip(shared_rmse, vector_rmse)),
            "all_runs_r2_improved": all(b > a for a, b in zip(shared_r2, vector_r2)),
        }
        result[name] = item

    shared_thetas = np.asarray([run["shared_scalar_projection"]["theta"] for run in runs], dtype=float)
    result["shared_theta"] = {
        "component_order": ["D_act", "D_cap", "D_exp", "D_bnd", "D_conn"],
        "mean": shared_thetas.mean(axis=0).tolist(),
        "population_std": shared_thetas.std(axis=0).tolist(),
    }
    return result


def report(payload: dict[str, Any]) -> str:
    lines = [
        "# D2 multi-target vector-static descriptor toy benchmark", "",
        "## Scope", "",
        "This is a finite structural benchmark on an extended D2 comparison regime.",
        "It compares a preserved vector descriptor with scalar projections of the same vector.",
        "It is not an empirical, physical, or quantum prediction result.", "",
        "## Vector descriptor", "", "```text",
        "D_vec = (D_act, D_cap, D_exp, D_bnd, D_conn)",
        "D_act  active-relation participation",
        "D_cap  induced internal-relation capacity",
        "D_exp  carrier exposure to the boundary",
        "D_bnd  status-aware boundary shielding",
        "D_conn active-graph pair reachability in the carrier",
        "```", "", "## Repeated selected-domain hold-out results", "",
        "```text",
        "Target                              shared scalar MAE   vector MAE   vector vs shared",
    ]
    for name, values in payload["repeat_summary"].items():
        if name == "shared_theta":
            continue
        shared = values["shared_scalar"]["mae"]["mean"]
        vector = values["vector_static"]["mae"]["mean"]
        effect = values["vector_vs_shared_scalar"]["mae_reduction_percent"]
        lines.append(f"{name:34s} {shared:.9f}   {vector:.9f}   {effect['mean']:+.3f}% ± {effect['population_std']:.3f}%")
    lines += ["```", "", "## Interpretation", "",
        "A shared scalar projection must use one theta for all targets. The vector model retains all five coordinates and permits a separate target projection.",
        "Thus an advantage for the vector model means that one scalar summary loses task-relevant static structure in this D2 regime. It does not establish a universal final vector formula.", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=Path("results") / "structural")
    parser.add_argument("--first-seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--repeat-count", type=int, default=DEFAULT_REPEATS)
    parser.add_argument("--train-fraction", type=float, default=DEFAULT_TRAIN_FRACTION)
    parser.add_argument("--theta-grid-step", type=float, default=DEFAULT_GRID_STEP)
    args = parser.parse_args()
    if args.repeat_count < 2:
        raise ValueError("repeat-count must be at least 2")
    if not 0.0 < args.train_fraction < 1.0:
        raise ValueError("train-fraction must lie in (0,1)")

    ab = load_ablation_module()
    domains, descriptor, targets = build_vector_dataset(ab)
    candidates = simplex_grid(descriptor.shape[1], args.theta_grid_step)
    runs = [one_run(ab, domains, descriptor, targets, candidates, args.first_seed + offset, args.train_fraction) for offset in range(args.repeat_count)]
    payload: dict[str, Any] = {
        "status": "pass",
        "scope": "finite D2 vector-static descriptor benchmark; not empirical or physical validation",
        "toy_model_selection": {
            "name": "D2 carrier-boundary-connectivity multi-target vector benchmark",
            "reason": "The existing extended D2 regime is the smallest current model in which active carrier, boundary status, restriction, and connectivity can be separated without adding time evolution.",
            "cases": int(len(domains)),
            "canonical_D2_subset": "C=S and every exposed relation is blocked",
            "comparison_regime": "C subseteq S with blocked/interface labels; interface never auto-activates a relation",
        },
        "descriptor": {
            "classification": "vector static",
            "component_order": ["D_act", "D_cap", "D_exp", "D_bnd", "D_conn"],
            "component_ranges": [{"min": float(descriptor[:, i].min()), "max": float(descriptor[:, i].max())} for i in range(descriptor.shape[1])],
        },
        "targets": {
            "restriction_survival": "exact probability that a nonempty element-complete restriction retains at least one active relation",
            "restriction_connectivity": "exact probability that a nonempty restriction has a connected active graph",
            "selected_inactive_interface_reach": "fraction of selected inactive vertices touched by an interface-labeled boundary relation",
        },
        "comparison": {
            "shared_scalar_projection": "one learned convex theta shared across all targets; each target receives its own affine readout",
            "task_specific_scalar_projection": "one learned convex theta per target; included to show task-specific scalar compression",
            "vector_static_descriptor": "five preserved static coordinates with a separate affine readout per target",
        },
        "first_seed": args.first_seed,
        "repeat_count": args.repeat_count,
        "train_fraction": args.train_fraction,
        "theta_grid_step": args.theta_grid_step,
        "simplex_candidate_count": int(len(candidates)),
        "runs": runs,
        "repeat_summary": aggregate_runs(runs),
    }
    output = args.output_root / (datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d_%H%M%S") + "_vector_static_multitarget")
    output.mkdir(parents=True, exist_ok=False)
    (output / "summary.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "vector_static_report.md").write_text(report(payload), encoding="utf-8")
    print(f"RESULT_DIRECTORY={output.resolve()}")
    print("STATUS=PASS")
    for name, values in payload["repeat_summary"].items():
        if name != "shared_theta":
            print(f"{name.upper()}_VECTOR_VS_SHARED_MAE_REDUCTION_PERCENT={values['vector_vs_shared_scalar']['mae_reduction_percent']['mean']:.6f}")


if __name__ == "__main__":
    main()
