#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_strong_interaction_numerical_sources_001.py

Numerical source downloader for the Strong_interaction benchmark pipeline in the
Dimensional-Structural Describability project.

Author: Kwon Dominicus

Purpose
-------
This script downloads explicitly listed numerical benchmark source files into:

    Strong_interaction/data/raw/source_tables/01/

and writes provenance/download manifests into:

    Strong_interaction/data/raw/references/01/

It is designed for actual numerical materials such as:

- HEPData record/table CSV
- HEPData YAML
- YODA/YODA2/YODA.H5 reference data
- journal supplementary CSV/TXT/DAT tables
- small verified event-level samples

It does not guess record IDs and does not promote manual search pages, arXiv
abstract HTML, PDG/NIST reference tables, or general web pages into numerical
benchmark data.

Input target registry
---------------------
The script expects a target registry at:

    Strong_interaction/data/raw/references/01/strong_interaction_numerical_download_targets_raw_001.csv

If the registry does not exist, a template is created and the script exits
without downloading numerical data.  Fill the template with explicit URLs and
run the script again.

Required target registry columns:

    target_id
    source_id
    data_url
    data_format
    expected_data_kind
    output_filename
    required_for
    license_or_access_note
    selected
    notes

Safety rule
-----------
Only rows with selected=True are downloaded.  A row is downloaded only if the
format/kind looks numerical or if --allow-nonstandard is passed.  This prevents
accidentally storing HTML/provenance pages as numerical benchmark data.
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Iterable, Optional


SCRIPT_VERSION = "001"
RAW_BATCH = "01"
USER_AGENT = (
    "Dimensional-Structural-Describability/Strong_interaction numerical downloader "
    "(Kwon Dominicus; explicit target registry)"
)
TIMEOUT_SECONDS = 120
SLEEP_SECONDS = 1.0
MAX_SIZE_MB_DEFAULT = 500

TARGET_FIELDS = [
    "target_id",
    "source_id",
    "data_url",
    "data_format",
    "expected_data_kind",
    "output_filename",
    "required_for",
    "license_or_access_note",
    "selected",
    "notes",
]

NUMERICAL_FORMATS = {
    "csv", "tsv", "txt", "dat", "yaml", "yml", "json", "root", "yoda", "yoda1", "yoda2", "yoda.h5", "h5", "hdf5", "parquet", "npz", "npy"
}

NUMERICAL_KINDS = {
    "binned_event_shape_table",
    "binned_distribution_table",
    "hepdata_record_csv",
    "hepdata_table_csv",
    "hepdata_record_yaml",
    "hepdata_table_yaml",
    "yoda_reference_data",
    "rivet_reference_data",
    "journal_supplementary_numeric_table",
    "small_event_level_sample",
    "event_level_sample",
    "analysis_output_numeric_table",
}

TEMPLATE_ROWS = [
    {
        "target_id": "OPAL_2005_HEPDATA_TABLE_CSV_TODO",
        "source_id": "OPAL_EVENT_SHAPES_91_209GEV_2005",
        "data_url": "",
        "data_format": "csv",
        "expected_data_kind": "hepdata_table_csv",
        "output_filename": "opal_2005_event_shape_table_TODO_raw_001.csv",
        "required_for": "standard_baseline_binned_event_shape",
        "license_or_access_note": "fill after confirming HEPData/journal/source access",
        "selected": "False",
        "notes": "Fill exact HEPData table CSV URL, then set selected=True.",
    },
    {
        "target_id": "JADE_1997_HEPDATA_TABLE_CSV_TODO",
        "source_id": "JADE_EVENT_SHAPES_22_44GEV",
        "data_url": "",
        "data_format": "csv",
        "expected_data_kind": "hepdata_table_csv",
        "output_filename": "jade_1997_event_shape_table_TODO_raw_001.csv",
        "required_for": "lower_energy_scale_extension",
        "license_or_access_note": "fill after confirming HEPData/journal/source access",
        "selected": "False",
        "notes": "Fill exact HEPData table CSV URL, then set selected=True.",
    },
    {
        "target_id": "L3_2009_FLAVOUR_HEPDATA_TABLE_CSV_TODO",
        "source_id": "L3_FLAVOUR_TAGGED_EVENT_SHAPE_197GEV",
        "data_url": "",
        "data_format": "csv",
        "expected_data_kind": "hepdata_table_csv",
        "output_filename": "l3_2009_flavour_event_shape_table_TODO_raw_001.csv",
        "required_for": "flavour_structure_extension",
        "license_or_access_note": "fill after confirming HEPData/journal/source access",
        "selected": "False",
        "notes": "Fill exact HEPData or supplementary CSV URL, then set selected=True.",
    },
    {
        "target_id": "DELPHI_2025_EVENT_SAMPLE_TODO",
        "source_id": "DELPHI_OPEN_DATA_THRUST_EEC_NOTE_2025",
        "data_url": "",
        "data_format": "root",
        "expected_data_kind": "small_event_level_sample",
        "output_filename": "delphi_2025_open_data_event_sample_TODO_raw_001.root",
        "required_for": "10000_plus_event_benchmark_candidate",
        "license_or_access_note": "confirm CERN Open Data license/record before download",
        "selected": "False",
        "notes": "Only set selected=True after confirming file size and sample scope.",
    },
]


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def locate_paths() -> dict[str, pathlib.Path]:
    script_path = pathlib.Path(__file__).resolve()
    strong_root = script_path.parents[3]
    return {
        "strong_root": strong_root,
        "raw_references": strong_root / "data" / "raw" / "references",
        "raw_references_01": strong_root / "data" / "raw" / "references" / RAW_BATCH,
        "raw_source_tables_01": strong_root / "data" / "raw" / "source_tables" / RAW_BATCH,
        "source_registry_input": strong_root / "data" / "derived" / "input" / "01" / "strong_interaction_source_registry_input_001.csv",
        "missing_input": strong_root / "data" / "derived" / "input" / "01" / "strong_interaction_missing_numerical_data_input_001.csv",
    }


def write_csv(path: pathlib.Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def boolish(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y", "selected"}


def sanitize_filename(value: str) -> str:
    value = pathlib.PurePath(value).name
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    return value[:180] or "downloaded_numeric_source_raw_001.dat"


def infer_format(url: str, output_filename: str, given: str) -> str:
    given = (given or "").strip().lower()
    if given:
        return given
    candidate = output_filename or urllib.parse.urlparse(url).path
    suffixes = pathlib.PurePath(candidate).suffixes
    if suffixes:
        if len(suffixes) >= 2 and suffixes[-2].lower() == ".yoda" and suffixes[-1].lower() == ".h5":
            return "yoda.h5"
        return suffixes[-1].lstrip(".").lower()
    return "unknown"


def is_numerical_target(row: dict[str, str], allow_nonstandard: bool) -> tuple[bool, str]:
    fmt = infer_format(row.get("data_url", ""), row.get("output_filename", ""), row.get("data_format", ""))
    kind = str(row.get("expected_data_kind", "")).strip().lower()
    url = str(row.get("data_url", "")).strip()
    if not url:
        return False, "empty_data_url"
    if not (url.startswith("https://") or url.startswith("http://")):
        return False, "data_url_must_be_http_or_https"
    if allow_nonstandard:
        return True, "allowed_by_allow_nonstandard"
    if fmt in NUMERICAL_FORMATS:
        return True, f"accepted_numerical_format:{fmt}"
    if kind in NUMERICAL_KINDS:
        return True, f"accepted_numerical_kind:{kind}"
    return False, f"rejected_non_numerical_format_or_kind:format={fmt};kind={kind}"


def create_template(paths: dict[str, pathlib.Path], target_path: pathlib.Path) -> pathlib.Path:
    write_csv(target_path, TEMPLATE_ROWS, TARGET_FIELDS)
    readme = paths["raw_references_01"] / f"strong_interaction_numerical_download_targets_template_readme_raw_{SCRIPT_VERSION}.txt"
    readme.write_text(
        "Strong_interaction numerical download target registry template\n"
        "============================================================\n"
        f"Generated UTC: {utc_now()}\n"
        f"Script version: {SCRIPT_VERSION}\n\n"
        "The numerical downloader created this template because no explicit target registry existed.\n"
        "Fill data_url with actual CSV/YAML/YODA/ROOT/HDF5/Parquet/etc. numerical source URLs.\n"
        "Set selected=True only for reviewed numerical targets.\n\n"
        "Do not use arXiv abstract HTML or general manual search pages as numerical targets.\n"
        "If using HEPData, prefer exact record/table export URLs such as ?format=csv, ?format=yaml, or YODA outputs.\n"
        "Large event-level files should be confirmed for size and license before download.\n",
        encoding="utf-8",
    )
    return readme


def safe_request(url: str, accept: Optional[str], max_size_mb: int) -> tuple[bool, bytes | None, str, int | str, dict[str, str]]:
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    response_headers: dict[str, str] = {}
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as res:
            status = getattr(res, "status", "")
            response_headers = {k: v for k, v in res.headers.items()}
            content_length = res.headers.get("Content-Length")
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                if size_mb > max_size_mb:
                    return False, None, f"blocked_by_size_limit:{size_mb:.2f}MB>{max_size_mb}MB", status, response_headers
            data = res.read(max_size_mb * 1024 * 1024 + 1)
            if len(data) > max_size_mb * 1024 * 1024:
                return False, None, f"blocked_by_size_limit_after_read:>{max_size_mb}MB", status, response_headers
            return True, data, "", status, response_headers
    except urllib.error.HTTPError as exc:
        return False, None, f"HTTPError {exc.code}: {exc.reason}", exc.code, response_headers
    except urllib.error.URLError as exc:
        return False, None, f"URLError: {exc.reason}", "", response_headers
    except Exception as exc:
        return False, None, f"{type(exc).__name__}: {exc}", "", response_headers


def accept_header_for_format(fmt: str) -> str:
    fmt = fmt.lower()
    if fmt in {"csv", "tsv"}:
        return "text/csv, text/plain, application/octet-stream, */*"
    if fmt in {"yaml", "yml"}:
        return "application/x-yaml, text/yaml, text/plain, */*"
    if fmt == "json":
        return "application/json, text/plain, */*"
    if fmt in {"yoda", "yoda1", "yoda2"}:
        return "text/plain, application/octet-stream, */*"
    return "application/octet-stream, */*"


def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def load_targets(target_path: pathlib.Path) -> list[dict[str, str]]:
    rows = read_csv(target_path)
    normalized: list[dict[str, str]] = []
    for row in rows:
        normalized.append({field: row.get(field, "") for field in TARGET_FIELDS})
    return normalized


def write_source_context(paths: dict[str, pathlib.Path]) -> pathlib.Path:
    rows = []
    for path, role in [
        (paths["source_registry_input"], "source_registry_input_01"),
        (paths["missing_input"], "missing_numerical_data_input_01"),
    ]:
        rows.append({
            "context_role": role,
            "context_path": str(path),
            "exists": path.exists(),
            "row_count": len(read_csv(path)) if path.exists() else 0,
            "note": "Used as planning context only; numerical target URLs still come from explicit target registry.",
            "created_utc": utc_now(),
        })
    out = paths["raw_references_01"] / f"strong_interaction_numerical_download_context_raw_{SCRIPT_VERSION}.csv"
    write_csv(out, rows, ["context_role", "context_path", "exists", "row_count", "note", "created_utc"])
    return out


def run(args: argparse.Namespace) -> int:
    paths = locate_paths()
    paths["raw_references_01"].mkdir(parents=True, exist_ok=True)
    paths["raw_source_tables_01"].mkdir(parents=True, exist_ok=True)
    target_path = paths["raw_references_01"] / f"strong_interaction_numerical_download_targets_raw_{SCRIPT_VERSION}.csv"

    print(f"[INFO] source_tables_01: {paths['raw_source_tables_01']}")
    print(f"[INFO] references_01: {paths['raw_references_01']}")
    print(f"[INFO] target registry: {target_path}")

    context_path = write_source_context(paths)
    print(f"[OK] context: {context_path}")

    if not target_path.exists():
        readme = create_template(paths, target_path)
        print(f"[WARN] target registry was missing; template created: {target_path}")
        print(f"[OK] template readme: {readme}")
        return 0

    targets = load_targets(target_path)
    selected = [row for row in targets if boolish(row.get("selected"))]
    manifest_rows: list[dict[str, Any]] = []

    if not selected:
        manifest_path = paths["raw_references_01"] / f"strong_interaction_numerical_download_manifest_raw_{SCRIPT_VERSION}.csv"
        write_csv(manifest_path, [], [
            "target_id", "source_id", "data_url", "output_file", "success", "download_status",
            "validation_status", "http_status", "size_bytes", "sha256", "data_format", "expected_data_kind",
            "required_for", "error", "started_utc", "finished_utc",
        ])
        summary = paths["raw_references_01"] / f"strong_interaction_numerical_download_summary_raw_{SCRIPT_VERSION}.txt"
        summary.write_text(
            "Strong_interaction numerical download summary\n"
            "=============================================\n"
            f"Generated UTC: {utc_now()}\n"
            "No selected=True numerical targets were found.\n"
            "Fill strong_interaction_numerical_download_targets_raw_001.csv and run again.\n",
            encoding="utf-8",
        )
        print("[WARN] No selected=True targets. Nothing downloaded.")
        return 0

    for row in selected:
        started = utc_now()
        target_id = row.get("target_id", "")
        source_id = row.get("source_id", "")
        url = row.get("data_url", "").strip()
        fmt = infer_format(url, row.get("output_filename", ""), row.get("data_format", ""))
        valid, validation_message = is_numerical_target(row, args.allow_nonstandard)
        output_filename = sanitize_filename(row.get("output_filename") or f"{target_id}_raw_{SCRIPT_VERSION}.{fmt if fmt != 'unknown' else 'dat'}")
        output_path = paths["raw_source_tables_01"] / output_filename
        success = False
        status: int | str = ""
        size_bytes = 0
        digest = ""
        error = ""
        download_status = "blocked"

        if not valid:
            error = validation_message
        else:
            ok, data, err, status, response_headers = safe_request(url, accept_header_for_format(fmt), args.max_size_mb)
            if ok and data is not None:
                output_path.write_bytes(data)
                success = True
                size_bytes = len(data)
                digest = sha256_bytes(data)
                download_status = "downloaded"
            else:
                error = err
                download_status = "failed"

        manifest_rows.append({
            "target_id": target_id,
            "source_id": source_id,
            "data_url": url,
            "output_file": str(output_path) if success else "",
            "success": success,
            "download_status": download_status,
            "validation_status": validation_message,
            "http_status": status,
            "size_bytes": size_bytes,
            "sha256": digest,
            "data_format": fmt,
            "expected_data_kind": row.get("expected_data_kind", ""),
            "required_for": row.get("required_for", ""),
            "license_or_access_note": row.get("license_or_access_note", ""),
            "notes": row.get("notes", ""),
            "error": error,
            "started_utc": started,
            "finished_utc": utc_now(),
        })
        time.sleep(SLEEP_SECONDS)

    manifest_path = paths["raw_references_01"] / f"strong_interaction_numerical_download_manifest_raw_{SCRIPT_VERSION}.csv"
    write_csv(manifest_path, manifest_rows, [
        "target_id", "source_id", "data_url", "output_file", "success", "download_status",
        "validation_status", "http_status", "size_bytes", "sha256", "data_format", "expected_data_kind",
        "required_for", "license_or_access_note", "notes", "error", "started_utc", "finished_utc",
    ])

    summary_path = paths["raw_references_01"] / f"strong_interaction_numerical_download_summary_raw_{SCRIPT_VERSION}.txt"
    success_count = sum(1 for row in manifest_rows if row.get("success"))
    failed_count = len(manifest_rows) - success_count
    total_bytes = sum(int(row.get("size_bytes") or 0) for row in manifest_rows)
    summary_path.write_text(
        "Strong_interaction numerical download summary\n"
        "=============================================\n"
        f"Generated UTC: {utc_now()}\n"
        f"Script version: {SCRIPT_VERSION}\n\n"
        f"Target registry: {target_path}\n"
        f"Output source tables: {paths['raw_source_tables_01']}\n"
        f"Output references: {paths['raw_references_01']}\n\n"
        f"Selected targets: {len(selected)}\n"
        f"Downloaded successfully: {success_count}\n"
        f"Failed or blocked: {failed_count}\n"
        f"Total downloaded bytes: {total_bytes}\n\n"
        "Interpretation:\n"
        "- Downloaded files are raw numerical source candidates only.\n"
        "- They must be cleaned into data/derived/cleaned_tables before input promotion.\n"
        "- This script does not create derived/input.\n",
        encoding="utf-8",
    )

    print(f"[OK] manifest: {manifest_path}")
    print(f"[OK] summary: {summary_path}")
    print(f"[DONE] selected={len(selected)} success={success_count} failed_or_blocked={failed_count}")
    return 0 if failed_count == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Download explicit numerical source targets for Strong_interaction benchmark.")
    parser.add_argument("--allow-nonstandard", action="store_true", help="Allow downloads whose format/kind is not in the numerical whitelist.")
    parser.add_argument("--max-size-mb", type=int, default=MAX_SIZE_MB_DEFAULT, help="Maximum file size in MB per target. Default: 500.")
    args = parser.parse_args()
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
