#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
refine_strong_interaction_sources_to_cleaned_tables_02.py

Second derived-cleaning/refinement layer for the Strong_interaction benchmark
pipeline in the Dimensional-Structural Describability project.

Author: Kwon Dominicus

Purpose
-------
This script creates:

    Strong_interaction/data/derived/cleaned_tables/02/

from the existing cleaned_tables/01 outputs plus HEPData discovery and alternative
source-route manifests in raw/references.

Important status
----------------
This is NOT a numerical benchmark input stage.  It is an audit/refinement layer
that records:

- What was successfully cleaned in cleaned_tables/01.
- Why HEPData automatic discovery did not produce final numerical input.
- Which alternative source routes should be followed next.
- Which candidate is appropriate for DELPHI event-level data, OPAL/JADE binned
  event-shape tables, L3 flavour-tagged extension, and Rivet/YODA follow-up.

The output is deliberately marked as not final input to avoid favorable or
selective post-processing of incomplete data.
"""

from __future__ import annotations

import csv
import datetime as _dt
import pathlib
import sys
from typing import Any, Iterable


SCRIPT_VERSION = "001"
OUTPUT_BATCH = "02"


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def locate_paths() -> dict[str, pathlib.Path]:
    script_path = pathlib.Path(__file__).resolve()
    strong_root = script_path.parents[3]
    return {
        "strong_root": strong_root,
        "raw_references": strong_root / "data" / "raw" / "references",
        "cleaned_01": strong_root / "data" / "derived" / "cleaned_tables" / "01",
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


def boolish(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y", "success"}


def build_refined_candidate_registry(paths: dict[str, pathlib.Path]) -> tuple[pathlib.Path, int]:
    source_meta = read_csv(paths["cleaned_01"] / "source_reference_metadata_cleaned_001.csv")
    download_candidates = read_csv(paths["cleaned_01"] / "benchmark_download_candidates_cleaned_001.csv")
    hep_search = read_csv(paths["raw_references"] / "strong_interaction_hepdata_search_manifest_raw_001.csv")
    hep_records = read_csv(paths["raw_references"] / "strong_interaction_hepdata_record_candidates_raw_001.csv")
    alt_sources = read_csv(paths["raw_references"] / "strong_interaction_alternative_source_registry_raw_001.csv")

    hep_success_by_source: dict[str, list[dict[str, str]]] = {}
    for row in hep_search:
        hep_success_by_source.setdefault(row.get("source_id", ""), []).append(row)

    record_count_by_source: dict[str, int] = {}
    for row in hep_records:
        record_count_by_source[row.get("source_id", "")] = record_count_by_source.get(row.get("source_id", ""), 0) + 1

    alt_by_source = {row.get("source_id", ""): row for row in alt_sources}
    download_by_source = {row.get("source_id", ""): row for row in download_candidates}

    rows: list[dict[str, Any]] = []
    for meta in source_meta:
        source_id = meta.get("source_id", "")
        alt = alt_by_source.get(source_id, {})
        dc = download_by_source.get(source_id, {})
        hep_rows = hep_success_by_source.get(source_id, [])
        hep_attempted = bool(hep_rows)
        hep_all_success = bool(hep_rows) and all(boolish(r.get("success")) for r in hep_rows)
        hep_http_statuses = "; ".join(str(r.get("http_status", "")) for r in hep_rows if r.get("http_status", ""))
        hep_errors = "; ".join(str(r.get("error", "")) for r in hep_rows if r.get("error", ""))
        has_numerical_input = False
        final_input_status = "not_final_input"

        if source_id == "DELPHI_OPEN_DATA_THRUST_EEC_NOTE_2025":
            next_route = "CERN_Open_Data_or_analysis_repository_manual_confirmation"
            recommended_stage = "raw_event_level_acquisition_before_cleaned_tables_03"
        elif source_id in {"OPAL_EVENT_SHAPES_91_209GEV_2005", "OPAL_EVENT_SHAPES_NNLO_2011", "JADE_EVENT_SHAPES_22_44GEV", "L3_FLAVOUR_TAGGED_EVENT_SHAPE_197GEV"}:
            next_route = "INSPIRE_or_DOI_or_arXiv_source_or_Rivet_YODA_manual_confirmation"
            recommended_stage = "binned_table_or_yoda_acquisition_before_cleaned_tables_03"
        elif source_id == "HEPDATA_CSV_FORMAT_REFERENCE":
            next_route = "service_reference_only"
            recommended_stage = "do_not_promote_to_input"
        else:
            next_route = "review_manually"
            recommended_stage = "hold"

        rows.append({
            "source_id": source_id,
            "benchmark_priority": meta.get("benchmark_priority", ""),
            "candidate_role": meta.get("candidate_role", ""),
            "title": meta.get("title", ""),
            "arxiv_id": meta.get("arxiv_id", alt.get("arxiv_id", "")),
            "doi": meta.get("doi", alt.get("doi", "")),
            "html_cleaned_kind": meta.get("cleaned_kind", ""),
            "has_event_shape_metadata": meta.get("has_event_shape", ""),
            "has_thrust_metadata": meta.get("has_thrust", ""),
            "has_track_eec_metadata": meta.get("has_track_eec", ""),
            "has_alpha_s_metadata": meta.get("has_alpha_s", ""),
            "cleaned_01_is_final_numerical_input": meta.get("is_final_numerical_input", "False"),
            "hepdata_search_attempted": hep_attempted,
            "hepdata_search_all_success": hep_all_success,
            "hepdata_http_statuses": hep_http_statuses,
            "hepdata_errors": hep_errors,
            "hepdata_record_candidate_count": record_count_by_source.get(source_id, 0),
            "has_numerical_benchmark_input_now": has_numerical_input,
            "final_input_status": final_input_status,
            "next_route": next_route,
            "recommended_stage": recommended_stage,
            "arxiv_abs_url": alt.get("arxiv_abs_url", ""),
            "arxiv_eprint_url": alt.get("arxiv_eprint_url", ""),
            "inspire_manual_url": alt.get("inspire_manual_url", ""),
            "doi_url": alt.get("doi_url", ""),
            "hepdata_manual_search_url": alt.get("hepdata_manual_search_url", ""),
            "rivet_manual_search_url": alt.get("rivet_manual_search_url", ""),
            "needed_data_type": dc.get("needed_data_type", ""),
            "target_observables": dc.get("target_observables", ""),
            "audit_note": "cleaned_tables_02_refines_source_registry_only; no numerical benchmark table promoted.",
            "created_utc": utc_now(),
        })

    out = paths["output_dir"] / "benchmark_source_registry_refined_002.csv"
    write_csv(out, rows, [
        "source_id", "benchmark_priority", "candidate_role", "title", "arxiv_id", "doi",
        "html_cleaned_kind", "has_event_shape_metadata", "has_thrust_metadata", "has_track_eec_metadata",
        "has_alpha_s_metadata", "cleaned_01_is_final_numerical_input", "hepdata_search_attempted",
        "hepdata_search_all_success", "hepdata_http_statuses", "hepdata_errors", "hepdata_record_candidate_count",
        "has_numerical_benchmark_input_now", "final_input_status", "next_route", "recommended_stage",
        "arxiv_abs_url", "arxiv_eprint_url", "inspire_manual_url", "doi_url", "hepdata_manual_search_url",
        "rivet_manual_search_url", "needed_data_type", "target_observables", "audit_note", "created_utc",
    ])
    return out, len(rows)


def build_missing_manifest(paths: dict[str, pathlib.Path]) -> tuple[pathlib.Path, int]:
    rows = [
        {
            "missing_item_id": "NUMERICAL_EVENT_SHAPE_TABLES",
            "severity": "blocking_for_standard_baseline",
            "description": "No OPAL/JADE/L3 numerical event-shape CSV/YAML/YODA table has been promoted to final input.",
            "why_not_from_01": "cleaned_tables/01 contains HTML provenance metadata and reference support tables only.",
            "required_before_input": "Acquire binned event-shape tables from HEPData, journal supplement, arXiv source, or Rivet/YODA.",
            "next_output_if_resolved": "cleaned_tables/03",
        },
        {
            "missing_item_id": "DELPHI_EVENT_LEVEL_SAMPLE",
            "severity": "blocking_for_10000_event_benchmark",
            "description": "No DELPHI event-level file or 10000+ event sample has been acquired.",
            "why_not_from_01": "DELPHI file in 01 is an arXiv analysis-note HTML metadata source, not event data.",
            "required_before_input": "Locate exact CERN Open Data record or analysis repository and confirm size/format.",
            "next_output_if_resolved": "cleaned_tables/03_or_later",
        },
        {
            "missing_item_id": "HEPDATA_AUTOMATIC_RECORDS",
            "severity": "nonblocking_if_manual_route_used",
            "description": "HEPData automatic search produced no candidate records because HTTP access failed or was blocked.",
            "why_not_from_01": "01 was not intended to perform online record discovery.",
            "required_before_input": "Use alternative source registry, manual HEPData search, INSPIRE, DOI, arXiv source, or Rivet/YODA.",
            "next_output_if_resolved": "raw/source_tables_then_cleaned_tables/03",
        },
    ]
    out = paths["output_dir"] / "missing_numerical_data_manifest_002.csv"
    write_csv(out, rows, [
        "missing_item_id", "severity", "description", "why_not_from_01", "required_before_input", "next_output_if_resolved",
    ])
    return out, len(rows)


def build_support_index(paths: dict[str, pathlib.Path]) -> tuple[pathlib.Path, int]:
    rows = []
    for filename, role, status in [
        ("nist_constants_cleaned_selected_001.csv", "constants_support", "usable_reference_support"),
        ("pdg_particle_masses_selected_001.csv", "particle_mass_width_support", "usable_reference_support"),
        ("source_reference_metadata_cleaned_001.csv", "provenance_metadata", "usable_for_source_registry_not_input"),
        ("benchmark_download_candidates_cleaned_001.csv", "next_acquisition_candidates", "usable_for_planning_not_input"),
    ]:
        path = paths["cleaned_01"] / filename
        row_count = 0
        if path.exists():
            row_count = len(read_csv(path))
        rows.append({
            "support_file": filename,
            "source_path": str(path),
            "exists": path.exists(),
            "row_count": row_count,
            "role": role,
            "status": status,
            "promote_to_final_input": False,
            "reason": "Reference/provenance/planning support only; not numerical event-shape benchmark input.",
            "created_utc": utc_now(),
        })
    out = paths["output_dir"] / "reference_support_tables_index_002.csv"
    write_csv(out, rows, [
        "support_file", "source_path", "exists", "row_count", "role", "status", "promote_to_final_input", "reason", "created_utc",
    ])
    return out, len(rows)


def write_summary(paths: dict[str, pathlib.Path], stats: list[dict[str, Any]]) -> pathlib.Path:
    out = paths["output_dir"] / "cleaning_summary_002.txt"
    lines = [
        "Strong_interaction cleaned_tables/02 source-registry refinement summary",
        "=====================================================================",
        f"Generated UTC: {utc_now()}",
        f"Script version: {SCRIPT_VERSION}",
        "",
        "Status:",
        "- cleaned_tables/02 is not a numerical benchmark input layer.",
        "- It refines cleaned_tables/01 and records HEPData automatic-discovery failure plus alternative source routes.",
        "- No HTML metadata, PDG reference table, or NIST reference table is promoted to final input.",
        "",
        "Input layers:",
        f"- {paths['cleaned_01']}",
        f"- {paths['raw_references']}",
        "",
        "Output layer:",
        f"- {paths['output_dir']}",
        "",
        "Produced outputs:",
    ]
    for stat in stats:
        lines.append(f"- {stat['output_file']}: rows={stat['row_count']} status={stat['status']} notes={stat['notes']}")
    lines.extend([
        "",
        "Next stage:",
        "1. Use benchmark_source_registry_refined_002.csv to manually inspect INSPIRE/DOI/arXiv source/HEPData/Rivet routes.",
        "2. Acquire actual binned CSV/YAML/YODA or DELPHI event-level files into data/raw/source_tables.",
        "3. Run a numerical cleaner into cleaned_tables/03.",
        "4. Promote only reviewed numerical tables into data/derived/input.",
    ])
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def main() -> int:
    paths = locate_paths()
    paths["output_dir"].mkdir(parents=True, exist_ok=True)
    print(f"[INFO] cleaned_01: {paths['cleaned_01']}")
    print(f"[INFO] raw_references: {paths['raw_references']}")
    print(f"[INFO] output_dir: {paths['output_dir']}")

    stats: list[dict[str, Any]] = []
    registry_path, registry_rows = build_refined_candidate_registry(paths)
    stats.append({"output_file": registry_path.name, "row_count": registry_rows, "status": "success", "notes": "Refined source registry only; no final input."})

    missing_path, missing_rows = build_missing_manifest(paths)
    stats.append({"output_file": missing_path.name, "row_count": missing_rows, "status": "success", "notes": "Blocking missing numerical data recorded."})

    support_path, support_rows = build_support_index(paths)
    stats.append({"output_file": support_path.name, "row_count": support_rows, "status": "success", "notes": "Reference support files indexed."})

    manifest_path = paths["output_dir"] / "cleaning_manifest_002.csv"
    write_csv(manifest_path, stats, ["output_file", "row_count", "status", "notes"])
    summary_path = write_summary(paths, stats)

    print(f"[OK] manifest: {manifest_path}")
    print(f"[OK] summary: {summary_path}")
    print("[DONE] cleaned_tables/02 source-registry refinement completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
