#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parse_strong_interaction_metadata_records_for_event_files_002.py

Metadata-record parser for the Strong_interaction / DELPHI raw event-data search.

Author: Kwon Dominicus

Purpose
-------
Previous inventory classified downloaded files into metadata JSON/record files
and DELPHI condition/detector support database files.  This script parses only
the metadata JSON/record files and extracts deeper candidate URLs, record IDs,
file names, file sizes, and context hints that may point to actual event/DST/xDST/
FADANA/ROOT/HDF5/Parquet data.

Placement:
    Strong_interaction/data/raw/script/

Inputs:
    Strong_interaction/data/raw/references/02/
        strong_interaction_nested_event_file_inventory_raw_002.csv

    Strong_interaction/data/raw/source_tables/02/nested_event_downloads/
        metadata_json_or_record files referenced by the inventory

Outputs:
    Strong_interaction/data/raw/references/02/
        strong_interaction_metadata_record_file_candidates_raw_002.csv
        strong_interaction_metadata_record_file_candidates_shortlist_raw_002.csv
        strong_interaction_metadata_record_file_candidates_rejected_raw_002.csv
        strong_interaction_metadata_record_file_candidates_summary_raw_002.txt

This script does not download files and does not create cleaned_tables/input.  It
creates the next target registry for reviewed raw acquisition.
"""

from __future__ import annotations

import csv
import datetime as _dt
import json
import pathlib
import re
import urllib.parse
from collections import Counter
from typing import Any, Iterable


SCRIPT_VERSION = "002"
RAW_BATCH = "02"
BASE_URL = "https://opendata.cern.ch"

URL_PATTERN = re.compile(r"https?://[^\s\)\]\}\>'\"\\]+", re.IGNORECASE)
RELATIVE_URL_PATTERN = re.compile(r"(?P<url>/(?:record|records|api|files|download|eos|docs|about|static)/[^\s\)\]\}\>'\"\\]+)", re.IGNORECASE)
RECORD_ID_PATTERN = re.compile(r"(?:recid|record|records?|id)[^0-9]{0,20}(?P<id>\d{4,8})", re.IGNORECASE)
EVENT_COUNT_PATTERN = re.compile(r"(?P<num>\d{1,3}(?:[, ]\d{3})+|\d{4,})(?:\s*)(?P<label>events?|entries|collisions|hadronic\s+events|selected\s+events)", re.IGNORECASE)

HIGH_VALUE_HINTS = re.compile(r"(event|events|dst|xdst|fadana|root|ntupl|ntuple|tuple|hadron|hadronic|z0|z-pole|lep|reconstruction|reconstructed|track|particle|parquet|hdf5|h5|jsonl)", re.IGNORECASE)
SUPPORT_HINTS = re.compile(r"(calib|calibration|geometry|geom|condition|database|dbcalb|dbgeom|dblepm|dbrunt|dbscon|dbsysf|alignment|detector|guide|docs|about|docker|cvmfs|simulation guide)", re.IGNORECASE)
DATA_EXTENSIONS = {".root", ".h5", ".hdf5", ".parquet", ".csv", ".tsv", ".jsonl", ".json", ".yaml", ".yml", ".yoda", ".npz", ".npy", ".dat", ".txt", ".zip", ".tar", ".gz", ".tgz", ".tar.gz"}
HIGH_VALUE_EXTENSIONS = {".root", ".h5", ".hdf5", ".parquet", ".jsonl", ".npz", ".npy", ".zip", ".tar", ".gz", ".tgz", ".tar.gz"}


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def locate_paths() -> dict[str, pathlib.Path]:
    script_path = pathlib.Path(__file__).resolve()
    strong_root = script_path.parents[3]
    return {
        "strong_root": strong_root,
        "references_02": strong_root / "data" / "raw" / "references" / RAW_BATCH,
        "inventory": strong_root / "data" / "raw" / "references" / RAW_BATCH / "strong_interaction_nested_event_file_inventory_raw_002.csv",
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


def decode_text(data: bytes) -> str:
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def normalize_url(url: str) -> str:
    url = str(url).strip().rstrip(".,;:)]}\"'")
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if url.startswith("/"):
        return BASE_URL.rstrip("/") + url
    return url


def file_extension_from_url(url: str) -> str:
    path = urllib.parse.urlparse(url).path.lower()
    name = pathlib.PurePosixPath(path).name
    if name.endswith(".tar.gz"):
        return ".tar.gz"
    if name.endswith(".yoda.h5"):
        return ".yoda.h5"
    return pathlib.PurePosixPath(name).suffix.lower()


def extract_event_count(text: str) -> str:
    counts = []
    for m in EVENT_COUNT_PATTERN.finditer(text or ""):
        try:
            counts.append(int(re.sub(r"[,\s]", "", m.group("num"))))
        except Exception:
            pass
    return str(max(counts)) if counts else ""


def scalar_to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    return ""


def flatten_json(obj: Any, path: str = "") -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if isinstance(obj, dict):
        # Capture file-like dicts as a unit.
        keys = {str(k).lower() for k in obj.keys()}
        filelike_keys = {"uri", "url", "key", "filename", "size", "checksum", "links", "download", "self"}
        if keys & filelike_keys:
            out.append({
                "json_path": path or "json",
                "kind": "dict_candidate",
                "value": obj,
                "context": json.dumps(obj, ensure_ascii=False)[:1500],
            })
        for k, v in obj.items():
            child_path = f"{path}.{k}" if path else str(k)
            if isinstance(v, (dict, list)):
                out.extend(flatten_json(v, child_path))
            else:
                text = scalar_to_text(v)
                if text:
                    out.append({"json_path": child_path, "kind": "scalar", "value": text, "context": f"{child_path}={text}"})
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(flatten_json(v, f"{path}[{i}]"))
    return out


def candidate_from_url(source_file: str, source_nested_id: str, json_path: str, url: str, context: str, source_event_count: str) -> dict[str, Any]:
    norm = normalize_url(url)
    ext = file_extension_from_url(norm)
    combined = f"{norm} {context} {source_file}"
    score = 0
    reasons = []

    if ext in HIGH_VALUE_EXTENSIONS:
        score += 7
        reasons.append("high_value_extension")
    elif ext in DATA_EXTENSIONS:
        score += 3
        reasons.append("data_extension")
    elif not ext:
        score += 1
        reasons.append("extensionless_api_or_record")
    else:
        score -= 2
        reasons.append("non_data_extension")

    if HIGH_VALUE_HINTS.search(combined):
        score += 5
        reasons.append("event_or_dst_hint")
    if SUPPORT_HINTS.search(combined):
        score -= 3
        reasons.append("support_or_doc_hint")
    if "opendata.cern.ch/api/files" in norm:
        score += 4
        reasons.append("cern_api_files_endpoint")
    if "opendata.cern.ch/api/records" in norm:
        score += 2
        reasons.append("cern_api_records_endpoint")
    if source_event_count:
        try:
            if int(source_event_count) >= 10000:
                score += 4
                reasons.append("event_count_ge_10000_in_metadata")
        except Exception:
            pass

    if score >= 9:
        decision = "shortlist_event_file_candidate"
    elif score >= 5:
        decision = "review_metadata_candidate"
    else:
        decision = "reject_low_priority_metadata_candidate"

    return {
        "candidate_id": f"META_{abs(hash((source_file, json_path, norm))) % 10**12:012d}",
        "source_file": source_file,
        "source_nested_id": source_nested_id,
        "json_path": json_path,
        "candidate_url": norm,
        "file_extension": ext,
        "score": score,
        "decision": decision,
        "reasons": ";".join(reasons),
        "detected_event_count_in_source": source_event_count,
        "context_preview": context[:1200],
        "created_utc": utc_now(),
    }


def extract_candidates_from_metadata_file(row: dict[str, str]) -> list[dict[str, Any]]:
    path = pathlib.Path(row.get("output_file", ""))
    if not path.exists():
        return []
    raw = path.read_bytes()
    text = decode_text(raw[:25_000_000])
    source_event_count = extract_event_count(text)
    source_nested_id = row.get("nested_id", "")
    source_file = str(path)
    candidates: list[dict[str, Any]] = []

    parsed = None
    try:
        parsed = json.loads(text)
    except Exception:
        parsed = None

    if parsed is not None:
        for item in flatten_json(parsed, "json"):
            context = item.get("context", "")
            value = item.get("value")
            json_path = item.get("json_path", "")
            # dict candidates: inspect common URL/file fields and stringified context.
            if isinstance(value, dict):
                for k, v in value.items():
                    if isinstance(v, str):
                        if v.startswith("http") or v.startswith("/") or HIGH_VALUE_HINTS.search(v) or k.lower() in {"uri", "url", "key", "filename"}:
                            candidates.append(candidate_from_url(source_file, source_nested_id, f"{json_path}.{k}", v, context, source_event_count))
                    elif isinstance(v, dict):
                        nested_ctx = json.dumps(v, ensure_ascii=False)[:1500]
                        for url in URL_PATTERN.findall(nested_ctx):
                            candidates.append(candidate_from_url(source_file, source_nested_id, f"{json_path}.{k}", url, nested_ctx, source_event_count))
                        for m in RELATIVE_URL_PATTERN.finditer(nested_ctx):
                            candidates.append(candidate_from_url(source_file, source_nested_id, f"{json_path}.{k}", m.group("url"), nested_ctx, source_event_count))
            else:
                value_text = str(value)
                if value_text.startswith("http") or value_text.startswith("/"):
                    candidates.append(candidate_from_url(source_file, source_nested_id, json_path, value_text, context, source_event_count))
                for url in URL_PATTERN.findall(value_text):
                    candidates.append(candidate_from_url(source_file, source_nested_id, json_path, url, context, source_event_count))
                for m in RELATIVE_URL_PATTERN.finditer(value_text):
                    candidates.append(candidate_from_url(source_file, source_nested_id, json_path, m.group("url"), context, source_event_count))

    # Fallback full-text URL scan.
    for url in URL_PATTERN.findall(text):
        idx = text.find(url)
        context = text[max(0, idx - 500): idx + 1000].replace("\n", " ")
        candidates.append(candidate_from_url(source_file, source_nested_id, "text_scan", url, context, source_event_count))
    for m in RELATIVE_URL_PATTERN.finditer(text):
        url = m.group("url")
        idx = m.start()
        context = text[max(0, idx - 500): idx + 1000].replace("\n", " ")
        candidates.append(candidate_from_url(source_file, source_nested_id, "text_scan", url, context, source_event_count))

    return candidates


def main() -> int:
    paths = locate_paths()
    inventory = read_csv(paths["inventory"])
    if not inventory:
        print(f"[ERROR] inventory missing or empty: {paths['inventory']}")
        return 1

    metadata_rows = [r for r in inventory if r.get("role_guess") == "metadata_json_or_record" or r.get("priority") == "metadata"]
    all_candidates: list[dict[str, Any]] = []
    for row in metadata_rows:
        all_candidates.extend(extract_candidates_from_metadata_file(row))

    # Deduplicate by candidate_url while keeping highest score.
    best: dict[str, dict[str, Any]] = {}
    for cand in all_candidates:
        url = cand["candidate_url"]
        if url not in best or int(cand["score"]) > int(best[url]["score"]):
            best[url] = cand
    candidates = sorted(best.values(), key=lambda r: (-int(r["score"]), r["candidate_url"]))
    shortlist = [c for c in candidates if c["decision"] == "shortlist_event_file_candidate"]
    rejected = [c for c in candidates if c["decision"] != "shortlist_event_file_candidate"]

    references = paths["references_02"]
    all_path = references / "strong_interaction_metadata_record_file_candidates_raw_002.csv"
    short_path = references / "strong_interaction_metadata_record_file_candidates_shortlist_raw_002.csv"
    reject_path = references / "strong_interaction_metadata_record_file_candidates_rejected_raw_002.csv"
    fieldnames = [
        "candidate_id", "source_file", "source_nested_id", "json_path", "candidate_url", "file_extension",
        "score", "decision", "reasons", "detected_event_count_in_source", "context_preview", "created_utc"
    ]
    write_csv(all_path, candidates, fieldnames)
    write_csv(short_path, shortlist, fieldnames)
    write_csv(reject_path, rejected, fieldnames)

    decision_counts = Counter(c["decision"] for c in candidates)
    ext_counts = Counter(c["file_extension"] or "[no_extension]" for c in candidates)
    reason_counts = Counter()
    for c in candidates:
        for reason in str(c.get("reasons", "")).split(";"):
            if reason:
                reason_counts[reason] += 1

    summary_path = references / "strong_interaction_metadata_record_file_candidates_summary_raw_002.txt"
    summary_path.write_text(
        "Strong_interaction metadata record file candidate summary\n"
        "========================================================\n"
        f"Generated UTC: {utc_now()}\n"
        f"Script version: {SCRIPT_VERSION}\n\n"
        f"Inventory rows read: {len(inventory)}\n"
        f"Metadata rows parsed: {len(metadata_rows)}\n"
        f"Unique candidate URLs found: {len(candidates)}\n"
        f"Shortlist event/file candidates: {len(shortlist)}\n"
        f"Rejected/review candidates: {len(rejected)}\n\n"
        "Decision counts:\n" + "\n".join(f"- {k}: {v}" for k, v in decision_counts.most_common()) + "\n\n"
        "Top extension counts:\n" + "\n".join(f"- {k}: {v}" for k, v in ext_counts.most_common(20)) + "\n\n"
        "Top reason counts:\n" + "\n".join(f"- {k}: {v}" for k, v in reason_counts.most_common(20)) + "\n\n"
        "Interpretation:\n"
        "- Shortlist rows are next-stage raw acquisition candidates, not verified event data.\n"
        "- Prefer candidates with event/DST/xDST/FADANA/ROOT hints over condition DB or guide/doc links.\n"
        "- Download only reviewed shortlist rows in the next step.\n"
        f"All candidates: {all_path}\n"
        f"Shortlist: {short_path}\n",
        encoding="utf-8",
    )

    print(f"[OK] all candidates: {all_path}")
    print(f"[OK] shortlist: {short_path}")
    print(f"[OK] rejected: {reject_path}")
    print(f"[OK] summary: {summary_path}")
    print(f"[DONE] metadata_rows={len(metadata_rows)} candidates={len(candidates)} shortlist={len(shortlist)} rejected={len(rejected)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
