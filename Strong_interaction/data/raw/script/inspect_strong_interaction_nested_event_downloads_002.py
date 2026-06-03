#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inspect_strong_interaction_nested_event_downloads_002.py

Inventory/inspection script for downloaded nested DELPHI/CERN raw candidates.

Author: Kwon Dominicus

Purpose
-------
This script inspects files downloaded into:

    Strong_interaction/data/raw/source_tables/02/nested_event_downloads/

using the manifest:

    Strong_interaction/data/raw/references/02/strong_interaction_nested_event_download_manifest_raw_002.csv

It avoids loading multi-GB files fully.  It reads only head/tail samples and
records basic file signatures, text/binary indicators, keyword hits, and a
conservative next-action decision.

Outputs:
    Strong_interaction/data/raw/references/02/
        strong_interaction_nested_event_file_inventory_raw_002.csv
        strong_interaction_nested_event_priority_candidates_raw_002.csv
        strong_interaction_nested_event_file_inventory_summary_raw_002.txt

This script does not create cleaned_tables or derived/input.  It only classifies
raw candidates.
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import math
import pathlib
import re
from collections import Counter
from typing import Any, Iterable


SCRIPT_VERSION = "002"
RAW_BATCH = "02"
SAMPLE_BYTES_DEFAULT = 262_144

EVENT_HINTS = re.compile(rb"(event|events|hadron|track|particle|thrust|eec|energy|momentum|run|entry|entries|z0|lep)", re.IGNORECASE)
CONDITION_HINTS = re.compile(rb"(calib|calibration|geometry|geom|runt|run|misc|scon|sysf|lepm|database|condition|alignment|detector)", re.IGNORECASE)
METADATA_HINTS = re.compile(rb"(record|metadata|license|description|doi|json|schema|docs|guide|about|portal)", re.IGNORECASE)

MAGIC_SIGNATURES = [
    (b"root", "possible_root_magic_lowercase"),
    (b"ROOT", "possible_root_magic"),
    (b"\x89HDF\r\n\x1a\n", "hdf5_magic"),
    (b"PAR1", "parquet_magic"),
    (b"PK\x03\x04", "zip_magic"),
    (b"\x1f\x8b", "gzip_magic"),
    (b"{", "json_object_start"),
    (b"[", "json_array_start"),
]


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def locate_paths() -> dict[str, pathlib.Path]:
    script_path = pathlib.Path(__file__).resolve()
    strong_root = script_path.parents[3]
    return {
        "strong_root": strong_root,
        "references_02": strong_root / "data" / "raw" / "references" / RAW_BATCH,
        "manifest": strong_root / "data" / "raw" / "references" / RAW_BATCH / "strong_interaction_nested_event_download_manifest_raw_002.csv",
        "download_dir": strong_root / "data" / "raw" / "source_tables" / RAW_BATCH / "nested_event_downloads",
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


def read_sample(path: pathlib.Path, n: int) -> tuple[bytes, bytes]:
    size = path.stat().st_size
    with path.open("rb") as f:
        head = f.read(min(n, size))
        if size > n:
            f.seek(max(0, size - n))
            tail = f.read(min(n, size))
        else:
            tail = b""
    return head, tail


def printable_ratio(data: bytes) -> float:
    if not data:
        return 0.0
    printable = sum(1 for b in data if b in (9, 10, 13) or 32 <= b <= 126)
    return printable / len(data)


def shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    length = len(data)
    return -sum((c / length) * math.log2(c / length) for c in counts.values())


def detect_magic(head: bytes) -> str:
    for sig, label in MAGIC_SIGNATURES:
        if head.startswith(sig):
            return label
    return "unknown_or_custom_binary"


def try_json_keys(head: bytes) -> str:
    text = head.decode("utf-8", errors="ignore").strip()
    if not text or text[0] not in "[{":
        return ""
    try:
        obj = json.loads(text)
    except Exception:
        return "json_like_but_not_full_sample"
    if isinstance(obj, dict):
        return ";".join(list(obj.keys())[:20])
    if isinstance(obj, list):
        return f"list_len_sample_{len(obj)}"
    return type(obj).__name__


def classify(row: dict[str, str], path: pathlib.Path, head: bytes, tail: bytes) -> dict[str, Any]:
    name = path.name
    size = path.stat().st_size
    lower_name = name.lower()
    combined_sample = head + tail
    magic = detect_magic(head)
    pratio = printable_ratio(combined_sample)
    entropy = shannon_entropy(head[:65536])
    event_hits = len(EVENT_HINTS.findall(combined_sample))
    condition_hits = len(CONDITION_HINTS.findall(combined_sample))
    metadata_hits = len(METADATA_HINTS.findall(combined_sample))
    json_keys = try_json_keys(head)

    if any(token in lower_name for token in ["dbcalb", "dbgeom", "dblepm", "dbmisc", "dbrunt", "dbscon", "dbsysf"]):
        role_guess = "delphi_condition_or_detector_database"
    elif magic in {"possible_root_magic", "possible_root_magic_lowercase"}:
        role_guess = "possible_root_event_or_tree_file"
    elif magic == "hdf5_magic":
        role_guess = "possible_hdf5_event_file"
    elif magic == "parquet_magic":
        role_guess = "possible_parquet_event_file"
    elif "json" in lower_name or magic in {"json_object_start", "json_array_start"}:
        role_guess = "metadata_json_or_record"
    elif size > 100_000_000:
        role_guess = "large_custom_binary_or_database"
    elif size > 5_000_000:
        role_guess = "medium_custom_binary_or_database"
    else:
        role_guess = "small_metadata_or_support_file"

    if role_guess in {"possible_root_event_or_tree_file", "possible_hdf5_event_file", "possible_parquet_event_file"}:
        priority = "high"
        next_action = "inspect_with_format_specific_reader_and_count_entries"
    elif role_guess == "large_custom_binary_or_database" and event_hits > condition_hits:
        priority = "medium"
        next_action = "inspect_binary_schema_or_external_documentation_before_event_use"
    elif role_guess in {"delphi_condition_or_detector_database", "large_custom_binary_or_database", "medium_custom_binary_or_database"}:
        priority = "support"
        next_action = "treat_as_condition_or_detector_support_until event schema is proven"
    elif role_guess == "metadata_json_or_record":
        priority = "metadata"
        next_action = "parse_json_for_additional_file_links_or_record_context"
    else:
        priority = "low"
        next_action = "keep_for_audit_do_not_promote"

    return {
        "nested_id": row.get("nested_id", ""),
        "success": row.get("success", ""),
        "classification_from_manifest": row.get("classification", ""),
        "content_type": row.get("content_type", ""),
        "size_bytes": size,
        "file_name": name,
        "output_file": str(path),
        "nested_url": row.get("nested_url", ""),
        "magic_signature": magic,
        "printable_ratio_sample": f"{pratio:.4f}",
        "entropy_head_64k": f"{entropy:.4f}",
        "event_keyword_hits_sample": event_hits,
        "condition_keyword_hits_sample": condition_hits,
        "metadata_keyword_hits_sample": metadata_hits,
        "json_keys_sample": json_keys,
        "role_guess": role_guess,
        "priority": priority,
        "next_action": next_action,
        "created_utc": utc_now(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect downloaded nested event/raw candidates without reading full multi-GB files.")
    parser.add_argument("--sample-bytes", type=int, default=SAMPLE_BYTES_DEFAULT, help="Head/tail sample bytes per file. Default: 262144.")
    args = parser.parse_args()

    paths = locate_paths()
    manifest = read_csv(paths["manifest"])
    if not manifest:
        print(f"[ERROR] manifest missing or empty: {paths['manifest']}")
        return 1

    rows: list[dict[str, Any]] = []
    for row in manifest:
        if str(row.get("success", "")).lower() != "true":
            continue
        output_file = row.get("output_file", "")
        if not output_file:
            continue
        path = pathlib.Path(output_file)
        if not path.exists():
            continue
        head, tail = read_sample(path, args.sample_bytes)
        rows.append(classify(row, path, head, tail))

    references = paths["references_02"]
    inventory_path = references / "strong_interaction_nested_event_file_inventory_raw_002.csv"
    priority_path = references / "strong_interaction_nested_event_priority_candidates_raw_002.csv"
    fieldnames = [
        "nested_id", "success", "classification_from_manifest", "content_type", "size_bytes",
        "file_name", "output_file", "nested_url", "magic_signature", "printable_ratio_sample",
        "entropy_head_64k", "event_keyword_hits_sample", "condition_keyword_hits_sample",
        "metadata_keyword_hits_sample", "json_keys_sample", "role_guess", "priority", "next_action", "created_utc"
    ]
    write_csv(inventory_path, rows, fieldnames)
    priority_rows = [r for r in rows if r["priority"] in {"high", "medium", "support", "metadata"}]
    priority_rows = sorted(priority_rows, key=lambda r: (str(r["priority"]), -int(r["size_bytes"])))
    write_csv(priority_path, priority_rows, fieldnames)

    role_counts = Counter(r["role_guess"] for r in rows)
    priority_counts = Counter(r["priority"] for r in rows)
    total_bytes = sum(int(r["size_bytes"]) for r in rows)
    summary_path = references / "strong_interaction_nested_event_file_inventory_summary_raw_002.txt"
    summary_path.write_text(
        "Strong_interaction nested event file inventory summary\n"
        "====================================================\n"
        f"Generated UTC: {utc_now()}\n"
        f"Script version: {SCRIPT_VERSION}\n\n"
        f"Successful downloaded files inspected: {len(rows)}\n"
        f"Total inspected bytes: {total_bytes}\n\n"
        "Priority counts:\n" + "\n".join(f"- {k}: {v}" for k, v in priority_counts.most_common()) + "\n\n"
        "Role counts:\n" + "\n".join(f"- {k}: {v}" for k, v in role_counts.most_common()) + "\n\n"
        "Interpretation:\n"
        "- DBcalb/DBgeom/DBlepm/DBrunt/DBscon/DBsysf are likely DELPHI condition/detector database support files unless event schema is proven.\n"
        "- ROOT/HDF5/Parquet magic signatures would be stronger event-level candidates.\n"
        "- Metadata JSON should be parsed for further record/file links.\n"
        f"Inventory: {inventory_path}\n"
        f"Priority candidates: {priority_path}\n",
        encoding="utf-8",
    )

    print(f"[OK] inventory: {inventory_path}")
    print(f"[OK] priority candidates: {priority_path}")
    print(f"[OK] summary: {summary_path}")
    print(f"[DONE] inspected={len(rows)} total_bytes={total_bytes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
