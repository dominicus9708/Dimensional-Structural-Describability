#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_strong_interaction_nested_event_links_002.py

Nested-link extraction script for the Strong_interaction event-level raw data
workflow.

Author: Kwon Dominicus

Purpose
-------
The shortlist downloader can retrieve CERN Open Data pages, record JSON, guide
pages, or metadata files rather than the final event-level ROOT/HDF5/Parquet data.
This script inspects those downloaded files and extracts nested file links,
record IDs, bucket links, and data-like URLs for the next download attempt.

Placement:
    Strong_interaction/data/raw/script/

Input:
    Strong_interaction/data/raw/source_tables/02/event_raw_shortlist_downloads/
    Strong_interaction/data/raw/references/02/strong_interaction_event_raw_shortlist_download_manifest_raw_002.csv

Outputs:
    Strong_interaction/data/raw/references/02/
        strong_interaction_event_raw_nested_links_raw_002.csv
        strong_interaction_event_raw_nested_links_shortlist_raw_002.csv
        strong_interaction_event_raw_nested_links_rejected_raw_002.csv
        strong_interaction_event_raw_nested_links_summary_raw_002.txt

This script does not download nested files. It creates a vetted target list for a
subsequent download step.
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

URL_PATTERN = re.compile(r"https?://[^\s\)\]\}\>'\"\\]+", re.IGNORECASE)
RELATIVE_URL_PATTERN = re.compile(r"(?P<url>/(?:record|records|api|files|download|eos|docs|about|static)/[^\s\)\]\}\>'\"\\]+)", re.IGNORECASE)
EVENT_COUNT_PATTERN = re.compile(r"(?P<num>\d{1,3}(?:[, ]\d{3})+|\d{4,})(?:\s*)(?P<label>events?|entries|collisions|hadronic\s+events|selected\s+events)", re.IGNORECASE)

DATA_EXTENSIONS = {
    ".root", ".h5", ".hdf5", ".parquet", ".csv", ".tsv", ".jsonl", ".json",
    ".yaml", ".yml", ".yoda", ".npz", ".npy", ".dat", ".txt", ".zip", ".tar", ".gz", ".tgz", ".tar.gz"
}

HIGH_VALUE_EXTENSIONS = {".root", ".h5", ".hdf5", ".parquet", ".jsonl", ".npz", ".npy", ".zip", ".tar", ".gz", ".tgz", ".tar.gz"}

DATA_HINTS = re.compile(r"(file|files|download|bucket|root|eos|event|events|ntupl|tuple|parquet|hdf5|h5|jsonl|csv|dataset|data|record)", re.IGNORECASE)
DELPHI_HINTS = re.compile(r"(delphi|z0|z-pole|91\.2|hadron|thrust|eec|energy[-_ ]energy|lep)", re.IGNORECASE)
PAGE_HINTS = re.compile(r"(about|guide|docs|documentation|getting-started|docker|cvmfs|simulation|analysis|portal|static|\.js$|\.css$|\.pdf$)", re.IGNORECASE)


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def locate_paths() -> dict[str, pathlib.Path]:
    script_path = pathlib.Path(__file__).resolve()
    strong_root = script_path.parents[3]
    return {
        "strong_root": strong_root,
        "references_02": strong_root / "data" / "raw" / "references" / RAW_BATCH,
        "download_manifest": strong_root / "data" / "raw" / "references" / RAW_BATCH / "strong_interaction_event_raw_shortlist_download_manifest_raw_002.csv",
        "download_dir": strong_root / "data" / "raw" / "source_tables" / RAW_BATCH / "event_raw_shortlist_downloads",
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


def file_extension_from_url(url: str) -> str:
    path = urllib.parse.urlparse(url).path.lower()
    name = pathlib.PurePosixPath(path).name
    if name.endswith(".tar.gz"):
        return ".tar.gz"
    if name.endswith(".yoda.h5"):
        return ".yoda.h5"
    return pathlib.PurePosixPath(name).suffix.lower()


def normalize_url(url: str, base_url: str = "https://opendata.cern.ch") -> str:
    url = url.strip().rstrip(".,;:)"]}")
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if url.startswith("/"):
        return base_url.rstrip("/") + url
    return url


def extract_event_count(text: str) -> str:
    counts = []
    for m in EVENT_COUNT_PATTERN.finditer(text or ""):
        try:
            counts.append(int(re.sub(r"[,\s]", "", m.group("num"))))
        except Exception:
            pass
    return str(max(counts)) if counts else ""


def flatten_json(obj: Any, context: str = "") -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            ctx = f"{context}.{k}" if context else str(k)
            if isinstance(v, str):
                if v.startswith("http") or v.startswith("/"):
                    out.append((v, ctx))
                for url in URL_PATTERN.findall(v):
                    out.append((url, ctx + " " + v[:400]))
                for m in RELATIVE_URL_PATTERN.finditer(v):
                    out.append((m.group("url"), ctx + " " + v[:400]))
            else:
                out.extend(flatten_json(v, ctx))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(flatten_json(v, f"{context}[{i}]"))
    return out


def extract_links_from_file(path: pathlib.Path, source_row: dict[str, str]) -> list[dict[str, Any]]:
    try:
        raw = path.read_bytes()
    except Exception:
        return []
    text = decode_text(raw[:10_000_000])
    source_url = source_row.get("data_url", "")
    event_count = extract_event_count(text)
    pairs: list[tuple[str, str]] = []

    try:
        obj = json.loads(text)
        pairs.extend(flatten_json(obj, "json"))
    except Exception:
        pass

    for url in URL_PATTERN.findall(text):
        idx = text.find(url)
        context = text[max(0, idx - 250): idx + 750].replace("\n", " ")
        pairs.append((url, context))
    for m in RELATIVE_URL_PATTERN.finditer(text):
        url = m.group("url")
        idx = m.start()
        context = text[max(0, idx - 250): idx + 750].replace("\n", " ")
        pairs.append((url, context))

    out = []
    seen = set()
    for n, (url, context) in enumerate(pairs, start=1):
        norm = normalize_url(url)
        if norm in seen:
            continue
        seen.add(norm)
        ext = file_extension_from_url(norm)
        combined = f"{norm} {context} {path.name} {source_url}"
        score = 0
        reasons = []
        if ext in HIGH_VALUE_EXTENSIONS:
            score += 6
            reasons.append("high_value_file_extension")
        elif ext in DATA_EXTENSIONS:
            score += 3
            reasons.append("data_extension")
        elif not ext:
            score += 1
            reasons.append("extensionless_possible_api_or_bucket")
        else:
            score -= 2
            reasons.append("non_data_extension")
        if DATA_HINTS.search(combined):
            score += 2
            reasons.append("data_hint")
        if DELPHI_HINTS.search(combined):
            score += 2
            reasons.append("delphi_context")
        if PAGE_HINTS.search(combined):
            score -= 2
            reasons.append("page_or_document_hint")
        if event_count:
            try:
                if int(event_count) >= 10000:
                    score += 4
                    reasons.append("event_count_ge_10000_in_source_file")
            except Exception:
                pass
        if "opendata.cern.ch" in norm:
            score += 1
            reasons.append("cern_opendata_url")

        if score >= 6:
            decision = "shortlist_nested_download_target"
        elif score >= 3:
            decision = "review_nested_candidate"
        else:
            decision = "reject_nested_low_priority"

        out.append({
            "nested_id": f"NESTED_{path.stem}_{n:04d}",
            "source_download_file": str(path),
            "source_candidate_id": source_row.get("candidate_id", ""),
            "source_data_url": source_url,
            "nested_url": norm,
            "file_extension": ext,
            "score": score,
            "decision": decision,
            "reasons": ";".join(reasons),
            "detected_event_count_in_source": event_count,
            "context_preview": context[:800],
            "created_utc": utc_now(),
        })
    return out


def main() -> int:
    paths = locate_paths()
    manifest_rows = read_csv(paths["download_manifest"])
    if not manifest_rows:
        print(f"[ERROR] download manifest missing or empty: {paths['download_manifest']}")
        return 1

    all_rows: list[dict[str, Any]] = []
    by_output = {row.get("output_file", ""): row for row in manifest_rows if row.get("output_file")}
    for output_file, row in by_output.items():
        path = pathlib.Path(output_file)
        if not path.exists():
            continue
        all_rows.extend(extract_links_from_file(path, row))

    # Deduplicate nested_url while preserving best score.
    best: dict[str, dict[str, Any]] = {}
    for row in all_rows:
        url = row["nested_url"]
        if url not in best or int(row["score"]) > int(best[url]["score"]):
            best[url] = row
    rows = sorted(best.values(), key=lambda r: (-int(r["score"]), r["nested_url"]))
    shortlist = [r for r in rows if r["decision"] == "shortlist_nested_download_target"]
    rejected = [r for r in rows if r["decision"] != "shortlist_nested_download_target"]

    fieldnames = [
        "nested_id", "source_download_file", "source_candidate_id", "source_data_url", "nested_url",
        "file_extension", "score", "decision", "reasons", "detected_event_count_in_source",
        "context_preview", "created_utc"
    ]
    references = paths["references_02"]
    nested_all_path = references / "strong_interaction_event_raw_nested_links_raw_002.csv"
    nested_short_path = references / "strong_interaction_event_raw_nested_links_shortlist_raw_002.csv"
    nested_reject_path = references / "strong_interaction_event_raw_nested_links_rejected_raw_002.csv"
    write_csv(nested_all_path, rows, fieldnames)
    write_csv(nested_short_path, shortlist, fieldnames)
    write_csv(nested_reject_path, rejected, fieldnames)

    ext_counts = Counter(r["file_extension"] or "[no_extension]" for r in rows)
    decision_counts = Counter(r["decision"] for r in rows)
    summary_path = references / "strong_interaction_event_raw_nested_links_summary_raw_002.txt"
    summary_path.write_text(
        "Strong_interaction nested event/raw link extraction summary\n"
        "========================================================\n"
        f"Generated UTC: {utc_now()}\n"
        f"Script version: {SCRIPT_VERSION}\n\n"
        f"Downloaded manifest rows inspected: {len(manifest_rows)}\n"
        f"Downloaded files found locally: {len(by_output)}\n"
        f"Unique nested URLs found: {len(rows)}\n"
        f"Nested shortlist targets: {len(shortlist)}\n"
        f"Nested rejected/review candidates: {len(rejected)}\n\n"
        "Decision counts:\n" + "\n".join(f"- {k}: {v}" for k, v in decision_counts.most_common()) + "\n\n"
        "Top extension counts:\n" + "\n".join(f"- {k}: {v}" for k, v in ext_counts.most_common(20)) + "\n\n"
        "Interpretation:\n"
        "- Shortlist rows are nested candidates for the next download step.\n"
        "- They are still not verified event-level data.\n"
        "- Prioritize high-value file extensions and CERN Open Data URLs.\n"
        f"All nested links: {nested_all_path}\n"
        f"Shortlist: {nested_short_path}\n",
        encoding="utf-8",
    )

    print(f"[OK] nested all: {nested_all_path}")
    print(f"[OK] nested shortlist: {nested_short_path}")
    print(f"[OK] nested rejected: {nested_reject_path}")
    print(f"[OK] summary: {summary_path}")
    print(f"[DONE] nested_urls={len(rows)} shortlist={len(shortlist)} rejected={len(rejected)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
