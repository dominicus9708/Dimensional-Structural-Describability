#!/usr/bin/env python3
"""Reusable audit for the D2 static-descriptor layer map.

It imports existing D2 code, verifies scalar/vector relationships, reads the
internal registry, and optionally re-runs existing scripts. It creates no new
physical descriptor or empirical claim.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

EPS = 1e-12
VALID_CLASSES = {
    "scalar_static", "vector_static", "scalar_static_projection",
    "scalar_dynamic", "scalar_field_dynamic", "vector_dynamic",
}


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("d2_static_descriptor", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load static descriptor module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_registry(registry: dict[str, Any]) -> dict[str, Any]:
    seen: set[str] = set()
    counts: Counter[str] = Counter()
    errors: list[str] = []
    for item in registry.get("descriptors", []):
        identifier = item.get("id")
        cls = item.get("classification")
        if not identifier or identifier in seen:
            errors.append(f"duplicate or missing descriptor id: {identifier!r}")
        seen.add(identifier)
        if cls not in VALID_CLASSES:
            errors.append(f"invalid class for {identifier}: {cls!r}")
        counts[cls] += 1
        if cls.startswith("scalar") and item.get("codomain") not in {"R", "scalar field"}:
            errors.append(f"scalar class has incompatible codomain for {identifier}")
        if cls == "vector_static" and not str(item.get("codomain", "")).startswith("R^"):
            errors.append(f"vector-static class has incompatible codomain for {identifier}")
    if errors:
        raise AssertionError("Registry validation failed: " + "; ".join(errors))
    return {"descriptor_count": len(seen), "classification_counts": dict(sorted(counts.items()))}


def audit_existing_static_module(module) -> dict[str, Any]:
    configurations = [p for p in module.all_admissible_configurations() if p.domain != 0]
    if len(configurations) != 21_798:
        raise AssertionError(f"Unexpected nonempty D2 enumeration: {len(configurations)}")

    recovery_error = projection_error = 0.0
    dimensions: set[int] = set()
    component_min = [math.inf] * 3
    component_max = [-math.inf] * 3
    scalar_min, scalar_max = math.inf, -math.inf
    range_errors = 0

    for configuration in configurations:
        vector = module.channel_descriptors(configuration)
        scalar = module.nchannel_descriptor(configuration)
        base = module.single_channel_toy_dw(configuration)
        recovered = module.nchannel_descriptor(configuration, theta=(1.0, 0.0, 0.0))
        reconstructed = sum(weight * value for weight, value in zip(module.THETA, vector))
        dimensions.add(len(vector))
        recovery_error = max(recovery_error, abs(base - recovered))
        projection_error = max(projection_error, abs(scalar - reconstructed))
        scalar_min, scalar_max = min(scalar_min, scalar), max(scalar_max, scalar)
        for index, value in enumerate(vector):
            component_min[index] = min(component_min[index], value)
            component_max[index] = max(component_max[index], value)
            if value < -EPS or value > 1.0 + EPS:
                range_errors += 1
        if scalar < -EPS or scalar > 1.0 + EPS:
            range_errors += 1

    if dimensions != {3}:
        raise AssertionError(f"Channel-vector dimension changed unexpectedly: {dimensions}")
    if recovery_error > EPS:
        raise AssertionError(f"N=1 recovery error: {recovery_error}")
    if projection_error > EPS:
        raise AssertionError(f"Scalar projection mismatch: {projection_error}")
    if range_errors:
        raise AssertionError("Normalized D2 descriptors left [0,1].")

    return {
        "status": "pass",
        "nonempty_admissible_configurations": len(configurations),
        "implemented_vector_static": {
            "source": "channel_descriptors(configuration)",
            "dimension": 3,
            "component_ranges": [
                {"min": component_min[i], "max": component_max[i]}
                for i in range(3)
            ],
        },
        "implemented_scalar_static": {
            "source": "single_channel_toy_dw(configuration)",
            "n_equals_one_recovery_max_abs_error": recovery_error,
        },
        "implemented_scalar_static_projection": {
            "source": "nchannel_descriptor(configuration, theta)",
            "theta": list(module.THETA),
            "projection_reconstruction_max_abs_error": projection_error,
            "range": {"min": scalar_min, "max": scalar_max},
        },
        "interpretation": {
            "channel_tuple_is_vector_static": True,
            "weighted_nchannel_output_is_scalar_static_projection": True,
            "no_explicit_time_variable_in_audited_module": True,
        },
    }


def validate_reference_results(project_root: Path, registry: dict[str, Any]) -> list[dict[str, Any]]:
    checked: list[dict[str, Any]] = []
    for ref in registry.get("reference_results", []):
        path = project_root / ref["relative_path"]
        record: dict[str, Any] = {
            "id": ref["id"], "relative_path": ref["relative_path"],
            "exists": path.exists(), "kind": ref["kind"],
        }
        if not path.exists():
            record["status"] = "missing"
            checked.append(record)
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        record["status"] = "pass" if payload.get("status") == ref.get("expected_status", "pass") else "unexpected_status"
        record["payload_status"] = payload.get("status")
        if ref["id"] == "predictive_holdout_20260625":
            holdout = payload["holdout_results"]
            single = holdout["single_channel"]
            learned = holdout.get("learned_theta_three_channel", holdout.get("learned_three_channel"))
            record["scalar_projection_result"] = {
                "single_mae": single["mae"],
                "learned_three_channel_mae": learned["mae"],
                "mae_improved": learned["mae"] < single["mae"],
            }
        elif ref["id"] == "predictive_robustness_20seed":
            record["scalar_projection_result"] = {
                "all_runs_mae_improved": payload["all_runs_mae_improved"],
                "all_runs_rmse_improved": payload["all_runs_rmse_improved"],
                "all_runs_r2_improved": payload["all_runs_r2_improved"],
            }
        elif ref["id"] == "carrier_boundary_ablation_10seed":
            record["carrier_boundary_scalar_projection_result"] = {
                name: data["M4_vs_M1"]["all_runs_mae_improved"]
                for name, data in payload["repeat_summary"].items()
            }
        checked.append(record)
    return checked


def rerun_existing_scripts(project_root: Path, output_root: Path, level: str) -> list[str]:
    script_dir = project_root / "src" / "structural" / "script"
    names = ["run_d2_nchannel_static_toy.py"]
    if level in {"predictive", "full"}:
        names += ["run_d2_nchannel_predictive_toy.py", "run_d2_nchannel_predictive_robustness.py"]
    if level == "full":
        names.append("run_d2_carrier_boundary_ablation.py")
    commands: list[str] = []
    for name in names:
        command = [sys.executable, str(script_dir / name), "--output-root", str(output_root)]
        if name == "run_d2_nchannel_predictive_robustness.py":
            command += ["--first-seed", "20260625", "--repeat-count", "20"]
        if name == "run_d2_carrier_boundary_ablation.py":
            command += ["--first-seed", "20260625", "--repeat-count", "10"]
        subprocess.run(command, check=True)
        commands.append(" ".join(command))
    return commands


def markdown_report(result: dict[str, Any]) -> str:
    static = result["module_audit"]
    lines = [
        "# Static descriptor layer audit", "",
        "## Classification boundary", "", "```text",
        "scalar static            fixed p -> R",
        "vector static            fixed p -> R^m, m >= 2",
        "scalar static projection scalar result after theta^T D_vec",
        "scalar dynamic           time-indexed scalar aggregate",
        "scalar-field dynamic     alpha(x,t): scalar at each local point",
        "vector dynamic           time-indexed vector state; not implemented",
        "```", "", "## Implemented D2 static check", "",
        f"- nonempty admissible configurations: {static['nonempty_admissible_configurations']}",
        f"- implemented channel-vector dimension: {static['implemented_vector_static']['dimension']}",
        f"- N=1 recovery maximum absolute error: {static['implemented_scalar_static']['n_equals_one_recovery_max_abs_error']:.12g}",
        f"- scalar projection reconstruction maximum absolute error: {static['implemented_scalar_static_projection']['projection_reconstruction_max_abs_error']:.12g}",
        "", "## Registry counts", "", "```text",
    ]
    for key, value in result["registry_audit"]["classification_counts"].items():
        lines.append(f"{key}: {value}")
    lines += ["```", "", "## Recorded benchmark summaries", ""]
    for item in result["reference_results"]:
        lines.append(f"- {item['id']}: {item['status']}")
    lines += [
        "", "## Interpretation", "",
        "The existing three-channel tuple is already an implemented vector-static intermediate representation.",
        "The weighted descriptor and M0--M4 remain scalar-static projections because their codomain is one real value.",
        "The final paper-level Static Structural Descriptor Vector remains proposed until its components and admissibility statements are formally fixed.", "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--output-root", type=Path, default=None)
    parser.add_argument("--rerun", choices=("none", "structure", "predictive", "full"), default="none")
    args = parser.parse_args()
    root = args.project_root.resolve()
    output = args.output_root.resolve() if args.output_root else root / "results" / "structural"
    registry = json.loads((root / "descriptor_registry.json").read_text(encoding="utf-8"))

    rerun_commands = rerun_existing_scripts(root, output, args.rerun) if args.rerun != "none" else []
    result = {
        "status": "pass",
        "scope": "internal layer classification and reproducibility audit; not a physical validation",
        "registry_audit": validate_registry(registry),
        "module_audit": audit_existing_static_module(load_module(root / "src" / "structural" / "script" / "run_d2_nchannel_static_toy.py")),
        "reference_results": validate_reference_results(root, registry),
        "rerun_level": args.rerun,
        "rerun_commands": rerun_commands,
    }
    result["reference_results_all_present"] = all(item["exists"] for item in result["reference_results"])
    result["reference_results_all_pass"] = all(item["status"] == "pass" for item in result["reference_results"])

    stamp = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d_%H%M%S")
    out = output / f"{stamp}_static_descriptor_audit"
    out.mkdir(parents=True, exist_ok=False)
    (out / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "audit_report.md").write_text(markdown_report(result), encoding="utf-8")
    print(f"RESULT_DIRECTORY={out.resolve()}")
    print("STATUS=PASS")
    print(f"N1_RECOVERY_MAX_ABS_ERROR={result['module_audit']['implemented_scalar_static']['n_equals_one_recovery_max_abs_error']:.12g}")
    print(f"PROJECTION_RECONSTRUCTION_MAX_ABS_ERROR={result['module_audit']['implemented_scalar_static_projection']['projection_reconstruction_max_abs_error']:.12g}")


if __name__ == "__main__":
    main()
