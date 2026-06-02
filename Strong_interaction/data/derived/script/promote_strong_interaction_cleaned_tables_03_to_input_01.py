#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
promote_strong_interaction_cleaned_tables_03_to_input_01.py

Input promotion script for the Strong_interaction benchmark pipeline in the
Dimensional-Structural Describability project.

Author: Kwon Dominicus

Purpose
-------
This script promotes reviewed cleaned_tables/03 input-candidate files into:

    Strong_interaction/data/derived/input/01/

The promotion is limited to source-registry, reference-support, and missing-data
inputs.  It explicitly does not create numerical benchmark input, standard-baseline
input, or event-level input.

Input:

    Strong_interaction/data/derived/cleaned_tables/03/

Output:

    Strong_interaction/data/derived/input/01/

Safety rule
-----------
If any candidate file marks itself as numerical benchmark input, standard-baseline
input, or event-level input, this script fails unless the file is the manifest and
only records those flags as False.  This prevents accidental promotion of incomplete
metadata into validation data.
"""

from __future__ import annotations

import csv
import datetime as _dt
import pathlib
import shutil
import sys
from typing import Any, Iterable


SCRIPT_VERSION = "001"
SOURCE_BATCH = "03"
INPUT_BATCH = "01"


PROMOTION_MAP = {
    "benchmark_source_registry_input_candidates_003.csv": "strong_interaction_source_registry_input_001.csv",
    "missing_numerical_data_input_candidates_003.csv": "strong_interaction_missing_numerical_data_input_001.csv",
    "reference_support_input_candidates_003.csv": "strong_interaction_reference_support_input_001.csv",
    "input_candidate_manifest_003.csv": "strong_interaction_input_source_candidate_manifest_001.csv",
}


DISALLOWED_TRUE_FLAGS = [
    "is_numerical_benchmark_input",
    "is_standard_baseline_input",
    "is_event_level_input",
]

REQUIRED_FALSE_OR_EMPTY_FLAGS = [
    "promotion_allowed_as_numerical_input",
]


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def locate_paths() -> dict[str, pathlib.Path]:
    script_path = pathlib.Path(__file__).resolve()
    strong_root = script_path.parents[3]
    return {
        "strong_root": strong_root,
        "cleaned_03": strong_root / "data" / "derived" / "cleaned_tables" / SOURCE_BATCH,
        "input_01": strong_root / "data" / "derived" / "input" / INPUT_BATCH,
    }


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: pathlib.Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def boolish(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def validate_candidate_file(path: pathlib.Path) -> tuple[bool, str, int]:
    rows = read_csv(path)
    if not rows:
        return False, "empty_or_unreadable_candidate_file", 0

    errors: list[str] = []
    for idx, row in enumerate(rows, start=1):
        for flag in DISALLOWED_TRUE_FLAGS:
            if flag in row and boolish(row.get(flag)):
                errors.append(f"row_{idx}:{flag}=True")
        for flag in REQUIRED_FALSE_OR_EMPTY_FLAGS:
            if flag in row and boolish(row.get(flag)):
                errors.append(f"row_{idx}:{flag}=True")
        # Source-registry/reference-support/missing-data candidates may be promoted,
        # but only as non-numerical registry/support input.
        if "promotion_allowed_to_data_derived_input" in row and not boolish(row.get("promotion_allowed_to_data_derived_input")):
            errors.append(f"row_{idx}:promotion_allowed_to_data_derived_input_not_true")

    if errors:
        return False, "; ".join(errors[:20]), len(rows)
    return True, "validated_non_numerical_input_candidate", len(rows)


def make_promoted_input_manifest(paths: dict[str, pathlib.Path], promotion_rows: list[dict[str, Any]]) -> pathlib.Path:
    out = paths["input_01"] / "strong_interaction_input_manifest_001.csv"
    rows = []
    for row in promotion_rows:
        if row["promotion_status"] == "promoted":
            rows.append({
                "input_file": row["output_file"],
                "input_path": row["output_path"],
                "source_file": row["source_file"],
                "source_path": row["source_path"],
                "input_batch": INPUT_BATCH,
                "input_stage": "source_registry_reference_support_missing_data_input",
                "is_source_registry_input": "source_registry" in row["output_file"],
                "is_reference_support_input": "reference_support" in row["output_file"],
                "is_missing_data_input": "missing_numerical_data" in row["output_file"],
                "is_numerical_benchmark_input": False,
                "is_standard_baseline_input": False,
                "is_event_level_input": False,
                "requires_numerical_data_before_standard": True,
                "allowed_next_use": "manual_acquisition_planning_and_audit_only",
                "disallowed_next_use": "standard_or_structural_numerical_validation",
                "row_count": row["row_count"],
                "created_utc": utc_now(),
            })
    write_csv(out, rows, [
        "input_file", "input_path", "source_file", "source_path", "input_batch", "input_stage",
        "is_source_registry_input", "is_reference_support_input", "is_missing_data_input",
        "is_numerical_benchmark_input", "is_standard_baseline_input", "is_event_level_input",
        "requires_numerical_data_before_standard", "allowed_next_use", "disallowed_next_use",
        "row_count", "created_utc",
    ])
    return out


def write_summary(paths: dict[str, pathlib.Path], promotion_rows: list[dict[str, Any]], input_manifest: pathlib.Path) -> pathlib.Path:
    out = paths["input_01"] / "strong_interaction_input_summary_001.txt"
    lines = [
        "Strong_interaction data/derived/input/01 promotion summary",
        "========================================================",
        f"Generated UTC: {utc_now()}",
        f"Script version: {SCRIPT_VERSION}",
        "",
        "Input source layer:",
        f"- {paths['cleaned_03']}",
        "",
        "Output input layer:",
        f"- {paths['input_01']}",
        "",
        "Status:",
        "- This input batch is source-registry/reference-support/missing-data input only.",
        "- It is not numerical benchmark input.",
        "- It is not standard-baseline input.",
        "- It is not event-level input.",
        "- Actual OPAL/JADE/L3 CSV/YAML/YODA or DELPHI event-level files remain required before numerical validation.",
        "",
        "Promoted files:",
    ]
    for row in promotion_rows:
        lines.append(f"- {row['output_file']}: status={row['promotion_status']} rows={row['row_count']} validation={row['validation_message']}")
    lines.extend([
        f"- {input_manifest.name}: generated input manifest",
        "",
        "Next allowed use:",
        "- Use this input batch to guide manual acquisition of numerical benchmark data.",
        "- Do not run standard/structural numerical validation from this input batch.",
        "- When actual numerical data are acquired, process them separately into cleaned_tables/03 or later numerical branch before creating a separate numerical input batch.",
    ])
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def main() -> int:
    paths = locate_paths()
    paths["input_01"].mkdir(parents=True, exist_ok=True)
    print(f"[INFO] cleaned_03: {paths['cleaned_03']}")
    print(f"[INFO] input_01: {paths['input_01']}")

    promotion_rows: list[dict[str, Any]] = []
    failed = False

    for source_name, output_name in PROMOTION_MAP.items():
        source_path = paths["cleaned_03"] / source_name
        output_path = paths["input_01"] / output_name
        if not source_path.exists():
            promotion_rows.append({
                "source_file": source_name,
                "source_path": str(source_path),
                "output_file": output_name,
                "output_path": str(output_path),
                "row_count": 0,
                "promotion_status": "missing_source",
                "validation_message": "source_file_not_found",
                "created_utc": utc_now(),
            })
            failed = True
            continue

        valid, message, row_count = validate_candidate_file(source_path)
        if valid:
            shutil.copyfile(source_path, output_path)
            status = "promoted"
        else:
            status = "blocked"
            failed = True

        promotion_rows.append({
            "source_file": source_name,
            "source_path": str(source_path),
            "output_file": output_name,
            "output_path": str(output_path),
            "row_count": row_count,
            "promotion_status": status,
            "validation_message": message,
            "created_utc": utc_now(),
        })

    promotion_manifest = paths["input_01"] / "strong_interaction_input_promotion_manifest_001.csv"
    write_csv(promotion_manifest, promotion_rows, [
        "source_file", "source_path", "output_file", "output_path", "row_count",
        "promotion_status", "validation_message", "created_utc",
    ])

    input_manifest = make_promoted_input_manifest(paths, promotion_rows)
    summary_path = write_summary(paths, promotion_rows, input_manifest)

    print(f"[OK] promotion manifest: {promotion_manifest}")
    print(f"[OK] input manifest: {input_manifest}")
    print(f"[OK] summary: {summary_path}")
    if failed:
        print("[WARN] Some files were not promoted. Review promotion manifest.")
        return 1
    print("[DONE] input/01 promotion completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
