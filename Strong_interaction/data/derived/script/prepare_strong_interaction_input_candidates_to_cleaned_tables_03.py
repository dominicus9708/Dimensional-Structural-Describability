#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prepare_strong_interaction_input_candidates_to_cleaned_tables_03.py

Third derived-cleaning layer for the Strong_interaction benchmark pipeline in the
Dimensional-Structural Describability project.

Author: Kwon Dominicus

Purpose
-------
This script prepares cleaned_tables/03 as an input-candidate normalization layer
from cleaned_tables/02.

It does not create data/derived/input directly.  It writes files that can be
reviewed in cleaned_tables/04 and then copied/promoted to data/derived/input as
source-registry input, not as numerical benchmark input.

Output:

    Strong_interaction/data/derived/cleaned_tables/03/

Important status
----------------
The output is suitable only for source-registry / missing-data / reference-support
pipeline input.  It is explicitly not suitable for standard-baseline numerical
execution, event-shape validation, or 10000+ event benchmark execution.
"""

from __future__ import annotations

import csv
import datetime as _dt
import pathlib
import sys
from typing import Any, Iterable


SCRIPT_VERSION = "001"
OUTPUT_BATCH = "03"
SOURCE_BATCH = "02"


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def locate_paths() -> dict[str, pathlib.Path]:
    script_path = pathlib.Path(__file__).resolve()
    strong_root = script_path.parents[3]
    return {
        "strong_root": strong_root,
        "cleaned_02": strong_root / "data" / "derived" / "cleaned_tables" / SOURCE_BATCH,
        "output_dir": strong_root / "data" / "derived" / "cleaned_tables" / OUTPUT_BATCH,
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


def safe_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def make_source_registry_input_candidate(paths: dict[str, pathlib.Path]) -> tuple[pathlib.Path, int]:
    source_rows = read_csv(paths["cleaned_02"] / "benchmark_source_registry_refined_002.csv")
    rows: list[dict[str, Any]] = []

    for row in source_rows:
        source_id = row.get("source_id", "")
        role = row.get("candidate_role", "")
        has_numerical_now = safe_bool(row.get("has_numerical_benchmark_input_now"))
        is_final = False

        if source_id == "DELPHI_OPEN_DATA_THRUST_EEC_NOTE_2025":
            input_use_class = "manual_event_level_acquisition_registry"
            blocker = "requires_exact_DELPHI_open_data_event_or_analysis_repository"
        elif source_id in {
            "OPAL_EVENT_SHAPES_91_209GEV_2005",
            "OPAL_EVENT_SHAPES_NNLO_2011",
            "JADE_EVENT_SHAPES_22_44GEV",
            "L3_FLAVOUR_TAGGED_EVENT_SHAPE_197GEV",
        }:
            input_use_class = "manual_binned_distribution_acquisition_registry"
            blocker = "requires_actual_CSV_YAML_YODA_or_supplementary_numeric_tables"
        elif source_id == "HEPDATA_CSV_FORMAT_REFERENCE":
            input_use_class = "service_format_reference_only"
            blocker = "not_a_dataset"
        else:
            input_use_class = "manual_review_registry"
            blocker = "unknown_or_unclassified"

        rows.append({
            "input_candidate_id": f"SRCREG03_{source_id}",
            "source_id": source_id,
            "input_candidate_type": "source_registry_input_candidate",
            "input_use_class": input_use_class,
            "candidate_role": role,
            "benchmark_priority": row.get("benchmark_priority", ""),
            "title": row.get("title", ""),
            "arxiv_id": row.get("arxiv_id", ""),
            "doi": row.get("doi", ""),
            "arxiv_abs_url": row.get("arxiv_abs_url", ""),
            "arxiv_eprint_url": row.get("arxiv_eprint_url", ""),
            "inspire_manual_url": row.get("inspire_manual_url", ""),
            "doi_url": row.get("doi_url", ""),
            "hepdata_manual_search_url": row.get("hepdata_manual_search_url", ""),
            "rivet_manual_search_url": row.get("rivet_manual_search_url", ""),
            "needed_data_type": row.get("needed_data_type", ""),
            "target_observables": row.get("target_observables", ""),
            "hepdata_search_attempted": row.get("hepdata_search_attempted", ""),
            "hepdata_search_all_success": row.get("hepdata_search_all_success", ""),
            "hepdata_http_statuses": row.get("hepdata_http_statuses", ""),
            "hepdata_errors": row.get("hepdata_errors", ""),
            "has_numerical_benchmark_input_now": has_numerical_now,
            "is_source_registry_input_candidate": True,
            "is_reference_support_input_candidate": False,
            "is_missing_data_input_candidate": False,
            "is_numerical_benchmark_input": False,
            "is_standard_baseline_input": False,
            "is_event_level_input": False,
            "requires_numerical_data_before_standard": True,
            "promotion_allowed_to_data_derived_input": True,
            "promotion_allowed_as_numerical_input": False,
            "blocking_reason_before_standard": blocker,
            "final_input_status": "candidate_for_source_registry_input_only",
            "audit_note": "cleaned_tables_03 normalizes cleaned_tables_02 into source-registry input candidates only.",
            "created_utc": utc_now(),
        })

    out = paths["output_dir"] / "benchmark_source_registry_input_candidates_003.csv"
    write_csv(out, rows, [
        "input_candidate_id", "source_id", "input_candidate_type", "input_use_class", "candidate_role",
        "benchmark_priority", "title", "arxiv_id", "doi", "arxiv_abs_url", "arxiv_eprint_url",
        "inspire_manual_url", "doi_url", "hepdata_manual_search_url", "rivet_manual_search_url",
        "needed_data_type", "target_observables", "hepdata_search_attempted", "hepdata_search_all_success",
        "hepdata_http_statuses", "hepdata_errors", "has_numerical_benchmark_input_now",
        "is_source_registry_input_candidate", "is_reference_support_input_candidate", "is_missing_data_input_candidate",
        "is_numerical_benchmark_input", "is_standard_baseline_input", "is_event_level_input",
        "requires_numerical_data_before_standard", "promotion_allowed_to_data_derived_input",
        "promotion_allowed_as_numerical_input", "blocking_reason_before_standard", "final_input_status",
        "audit_note", "created_utc",
    ])
    return out, len(rows)


def make_missing_data_input_candidate(paths: dict[str, pathlib.Path]) -> tuple[pathlib.Path, int]:
    missing_rows = read_csv(paths["cleaned_02"] / "missing_numerical_data_manifest_002.csv")
    rows: list[dict[str, Any]] = []
    for row in missing_rows:
        rows.append({
            "input_candidate_id": f"MISS03_{row.get('missing_item_id', '')}",
            "missing_item_id": row.get("missing_item_id", ""),
            "input_candidate_type": "missing_data_manifest_input_candidate",
            "severity": row.get("severity", ""),
            "description": row.get("description", ""),
            "why_not_from_01": row.get("why_not_from_01", ""),
            "required_before_input": row.get("required_before_input", ""),
            "next_output_if_resolved": row.get("next_output_if_resolved", ""),
            "is_source_registry_input_candidate": False,
            "is_reference_support_input_candidate": False,
            "is_missing_data_input_candidate": True,
            "is_numerical_benchmark_input": False,
            "is_standard_baseline_input": False,
            "is_event_level_input": False,
            "requires_numerical_data_before_standard": True,
            "promotion_allowed_to_data_derived_input": True,
            "promotion_allowed_as_numerical_input": False,
            "final_input_status": "candidate_for_missing_data_manifest_input_only",
            "audit_note": "Missing numerical data is preserved as a blocking manifest, not as validation data.",
            "created_utc": utc_now(),
        })
    out = paths["output_dir"] / "missing_numerical_data_input_candidates_003.csv"
    write_csv(out, rows, [
        "input_candidate_id", "missing_item_id", "input_candidate_type", "severity", "description",
        "why_not_from_01", "required_before_input", "next_output_if_resolved",
        "is_source_registry_input_candidate", "is_reference_support_input_candidate", "is_missing_data_input_candidate",
        "is_numerical_benchmark_input", "is_standard_baseline_input", "is_event_level_input",
        "requires_numerical_data_before_standard", "promotion_allowed_to_data_derived_input",
        "promotion_allowed_as_numerical_input", "final_input_status", "audit_note", "created_utc",
    ])
    return out, len(rows)


def make_reference_support_input_candidate(paths: dict[str, pathlib.Path]) -> tuple[pathlib.Path, int]:
    support_rows = read_csv(paths["cleaned_02"] / "reference_support_tables_index_002.csv")
    rows: list[dict[str, Any]] = []
    for row in support_rows:
        support_file = row.get("support_file", "")
        rows.append({
            "input_candidate_id": f"REFSUP03_{support_file}",
            "support_file": support_file,
            "input_candidate_type": "reference_support_input_candidate",
            "source_path": row.get("source_path", ""),
            "exists": row.get("exists", ""),
            "row_count": row.get("row_count", ""),
            "role": row.get("role", ""),
            "status": row.get("status", ""),
            "is_source_registry_input_candidate": False,
            "is_reference_support_input_candidate": True,
            "is_missing_data_input_candidate": False,
            "is_numerical_benchmark_input": False,
            "is_standard_baseline_input": False,
            "is_event_level_input": False,
            "requires_numerical_data_before_standard": True,
            "promotion_allowed_to_data_derived_input": True,
            "promotion_allowed_as_numerical_input": False,
            "final_input_status": "candidate_for_reference_support_input_only",
            "audit_note": "Reference support may accompany input registry but is not validation data.",
            "created_utc": utc_now(),
        })
    out = paths["output_dir"] / "reference_support_input_candidates_003.csv"
    write_csv(out, rows, [
        "input_candidate_id", "support_file", "input_candidate_type", "source_path", "exists", "row_count",
        "role", "status", "is_source_registry_input_candidate", "is_reference_support_input_candidate",
        "is_missing_data_input_candidate", "is_numerical_benchmark_input", "is_standard_baseline_input",
        "is_event_level_input", "requires_numerical_data_before_standard", "promotion_allowed_to_data_derived_input",
        "promotion_allowed_as_numerical_input", "final_input_status", "audit_note", "created_utc",
    ])
    return out, len(rows)


def make_input_candidate_manifest(paths: dict[str, pathlib.Path], stats: list[dict[str, Any]]) -> tuple[pathlib.Path, int]:
    rows = []
    for stat in stats:
        rows.append({
            "candidate_file": stat["output_file"],
            "candidate_path": str(paths["output_dir"] / stat["output_file"]),
            "row_count": stat["row_count"],
            "candidate_layer": "cleaned_tables_03",
            "intended_promotion_target": "data/derived/input",
            "promotion_type": "source_registry_or_reference_support_only",
            "is_numerical_benchmark_input": False,
            "is_standard_baseline_input": False,
            "is_event_level_input": False,
            "requires_review_before_input": True,
            "requires_numerical_data_before_standard": True,
            "status": stat["status"],
            "notes": stat["notes"],
            "created_utc": utc_now(),
        })
    out = paths["output_dir"] / "input_candidate_manifest_003.csv"
    write_csv(out, rows, [
        "candidate_file", "candidate_path", "row_count", "candidate_layer", "intended_promotion_target",
        "promotion_type", "is_numerical_benchmark_input", "is_standard_baseline_input", "is_event_level_input",
        "requires_review_before_input", "requires_numerical_data_before_standard", "status", "notes", "created_utc",
    ])
    return out, len(rows)


def write_summary(paths: dict[str, pathlib.Path], stats: list[dict[str, Any]], manifest_path: pathlib.Path) -> pathlib.Path:
    out = paths["output_dir"] / "cleaning_summary_003.txt"
    lines = [
        "Strong_interaction cleaned_tables/03 input-candidate normalization summary",
        "======================================================================",
        f"Generated UTC: {utc_now()}",
        f"Script version: {SCRIPT_VERSION}",
        "",
        "Status:",
        "- cleaned_tables/03 prepares candidates that may be promoted to data/derived/input.",
        "- The candidates are source-registry, reference-support, and missing-data inputs only.",
        "- They are not numerical benchmark input, not standard-baseline input, and not event-level input.",
        "- Actual OPAL/JADE/L3 CSV/YAML/YODA or DELPHI event-level files remain required before numerical validation.",
        "",
        "Input layer:",
        f"- {paths['cleaned_02']}",
        "",
        "Output layer:",
        f"- {paths['output_dir']}",
        "",
        "Produced outputs:",
    ]
    for stat in stats:
        lines.append(f"- {stat['output_file']}: rows={stat['row_count']} status={stat['status']} notes={stat['notes']}")
    lines.extend([
        f"- {manifest_path.name}: input candidate manifest",
        "",
        "Recommended next stage:",
        "1. Review cleaned_tables/03 input candidates.",
        "2. Run cleaned_tables/04 as a final promotion audit layer.",
        "3. Copy/promote only source-registry/reference-support/missing-data files into data/derived/input.",
        "4. Do not run standard or structural numerical validation until actual numerical benchmark tables are acquired.",
    ])
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def main() -> int:
    paths = locate_paths()
    paths["output_dir"].mkdir(parents=True, exist_ok=True)
    print(f"[INFO] cleaned_02: {paths['cleaned_02']}")
    print(f"[INFO] output_dir: {paths['output_dir']}")

    stats: list[dict[str, Any]] = []

    src_path, src_rows = make_source_registry_input_candidate(paths)
    stats.append({
        "output_file": src_path.name,
        "row_count": src_rows,
        "status": "success",
        "notes": "Source-registry input candidates prepared; not numerical input.",
    })

    miss_path, miss_rows = make_missing_data_input_candidate(paths)
    stats.append({
        "output_file": miss_path.name,
        "row_count": miss_rows,
        "status": "success",
        "notes": "Missing-data manifest input candidates prepared; blocking status preserved.",
    })

    ref_path, ref_rows = make_reference_support_input_candidate(paths)
    stats.append({
        "output_file": ref_path.name,
        "row_count": ref_rows,
        "status": "success",
        "notes": "Reference-support input candidates prepared; not validation data.",
    })

    manifest_path, manifest_rows = make_input_candidate_manifest(paths, stats)
    manifest_stats = stats + [{
        "output_file": manifest_path.name,
        "row_count": manifest_rows,
        "status": "success",
        "notes": "Input candidate manifest prepared.",
    }]

    cleaning_manifest = paths["output_dir"] / "cleaning_manifest_003.csv"
    write_csv(cleaning_manifest, manifest_stats, ["output_file", "row_count", "status", "notes"])
    summary_path = write_summary(paths, stats, manifest_path)

    print(f"[OK] input candidate manifest: {manifest_path}")
    print(f"[OK] cleaning manifest: {cleaning_manifest}")
    print(f"[OK] summary: {summary_path}")
    print("[DONE] cleaned_tables/03 input-candidate normalization completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
