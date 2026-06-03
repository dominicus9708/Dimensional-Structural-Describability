#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_strong_interaction_nested_event_targets_002.py

Nested target downloader for the Strong_interaction event-level raw data workflow.

Author: Kwon Dominicus

Purpose
-------
This script downloads only the nested shortlist targets created by:

    extract_strong_interaction_nested_event_links_002.py

Input:
    Strong_interaction/data/raw/references/02/
        strong_interaction_event_raw_nested_links_shortlist_raw_002.csv

Outputs:
    Strong_interaction/data/raw/source_tables/02/nested_event_downloads/
    Strong_interaction/data/raw/references/02/
        strong_interaction_nested_event_download_manifest_raw_002.csv
        strong_interaction_nested_event_download_summary_raw_002.txt

This remains raw acquisition. Downloaded files must be inspected before any
cleaned_tables or derived/input promotion.
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import pathlib
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Iterable


SCRIPT_VERSION = "002"
RAW_BATCH = "02"
USER_AGENT = (
    "Dimensional-Structural-Describability/Strong_interaction nested downloader "
    "(Kwon Dominicus; CERN nested targets)"
)
TIMEOUT_SECONDS = 180
SLEEP_SECONDS = 0.75
MAX_SIZE_MB_DEFAULT = 3000

BLOCKED_CONTENT_HINTS = ["text/html", "application/xhtml", "text/javascript", "application/javascript", "text/css"]


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def locate_paths() -> dict[str, pathlib.Path]:
    script_path = pathlib.Path(__file__).resolve()
    strong_root = script_path.parents[3]
    return {
        "strong_root": strong_root,
        "references_02": strong_root / "data" / "raw" / "references" / RAW_BATCH,
        "nested_shortlist": strong_root / "data" / "raw" / "references" / RAW_BATCH / "strong_interaction_event_raw_nested_links_shortlist_raw_002.csv",
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


def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def safe_filename(url: str, nested_id: str) -> str:
    parsed = urllib.parse.urlparse(url)
    name = pathlib.PurePosixPath(parsed.path).name
    if not name:
        name = nested_id + ".dat"
    if "." not in pathlib.PurePosixPath(name).name:
        name = name + ".dat"
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("._")
    return name[:180] or f"{nested_id}.dat"


def content_allowed(content_type: str, allow_html: bool) -> tuple[bool, str]:
    lowered = (content_type or "").lower()
    if allow_html:
        return True, "allowed_by_allow_html"
    if any(h in lowered for h in BLOCKED_CONTENT_HINTS):
        return False, f"blocked_page_content_type:{content_type}"
    return True, f"content_type_allowed_or_unknown:{content_type}"


def download(url: str, max_size_mb: int, allow_html: bool) -> tuple[bool, bytes | None, str, int | str, dict[str, str], str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/octet-stream,application/json,text/plain,*/*"})
    headers: dict[str, str] = {}
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as res:
            status = getattr(res, "status", "")
            headers = {k: v for k, v in res.headers.items()}
            ctype = res.headers.get("Content-Type", "")
            allowed, validation = content_allowed(ctype, allow_html)
            if not allowed:
                return False, None, validation, status, headers, validation
            clen = res.headers.get("Content-Length")
            if clen:
                size_mb = int(clen) / (1024 * 1024)
                if size_mb > max_size_mb:
                    msg = f"blocked_by_size_limit:{size_mb:.2f}MB>{max_size_mb}MB"
                    return False, None, msg, status, headers, validation
            data = res.read(max_size_mb * 1024 * 1024 + 1)
            if len(data) > max_size_mb * 1024 * 1024:
                msg = f"blocked_by_size_limit_after_read:>{max_size_mb}MB"
                return False, None, msg, status, headers, validation
            return True, data, "", status, headers, validation
    except urllib.error.HTTPError as exc:
        return False, None, f"HTTPError {exc.code}: {exc.reason}", exc.code, headers, ""
    except urllib.error.URLError as exc:
        return False, None, f"URLError: {exc.reason}", "", headers, ""
    except Exception as exc:
        return False, None, f"{type(exc).__name__}: {exc}", "", headers, ""


def classify_downloaded(content_type: str, filename: str, size_bytes: int) -> str:
    lowered = f"{content_type} {filename}".lower()
    if any(token in lowered for token in [".root", "x-root", "application/root"]):
        return "possible_event_root_file"
    if any(token in lowered for token in [".h5", ".hdf5", "hdf5"]):
        return "possible_hdf5_file"
    if ".parquet" in lowered:
        return "possible_parquet_file"
    if any(token in lowered for token in [".zip", ".tar", ".gz", "gzip", "zip"]):
        return "possible_archive_file"
    if "json" in lowered:
        return "json_metadata_or_data"
    if any(token in lowered for token in [".dat", "text/plain", "octet-stream"]):
        if size_bytes > 5_000_000:
            return "large_dat_or_binary_candidate"
        return "small_dat_or_metadata_candidate"
    return "unknown_raw_candidate"


def main() -> int:
    parser = argparse.ArgumentParser(description="Download nested CERN/OpenData targets from shortlist.")
    parser.add_argument("--max-size-mb", type=int, default=MAX_SIZE_MB_DEFAULT, help="Maximum file size per target. Default: 3000 MB.")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of nested targets. 0 means all.")
    parser.add_argument("--allow-html", action="store_true", help="Allow HTML/page downloads. Normally disabled.")
    args = parser.parse_args()

    paths = locate_paths()
    paths["download_dir"].mkdir(parents=True, exist_ok=True)
    rows = read_csv(paths["nested_shortlist"])
    if not rows:
        print(f"[ERROR] nested shortlist missing or empty: {paths['nested_shortlist']}")
        return 1
    targets = rows[: args.limit] if args.limit and args.limit > 0 else rows

    manifest_rows: list[dict[str, Any]] = []
    for idx, row in enumerate(targets, start=1):
        started = utc_now()
        nested_id = row.get("nested_id", f"nested_{idx:03d}")
        url = row.get("nested_url", "")
        fname = f"{nested_id}__{safe_filename(url, nested_id)}"
        out_path = paths["download_dir"] / fname
        ok, data, error, status, headers, validation = download(url, args.max_size_mb, args.allow_html)
        if ok and data is not None:
            out_path.write_bytes(data)
            size = len(data)
            digest = sha256_bytes(data)
            output_file = str(out_path)
            status_text = "downloaded"
        else:
            size = 0
            digest = ""
            output_file = ""
            status_text = "failed_or_blocked"
        content_type = headers.get("Content-Type", "")
        manifest_rows.append({
            "nested_id": nested_id,
            "nested_url": url,
            "source_candidate_id": row.get("source_candidate_id", ""),
            "file_extension": row.get("file_extension", ""),
            "score": row.get("score", ""),
            "reasons": row.get("reasons", ""),
            "download_attempted": True,
            "success": ok,
            "download_status": status_text,
            "http_status": status,
            "content_type": content_type,
            "content_length": headers.get("Content-Length", ""),
            "classification": classify_downloaded(content_type, fname, size) if ok else "not_downloaded",
            "validation_message": validation,
            "size_bytes": size,
            "sha256": digest,
            "output_file": output_file,
            "error": error,
            "started_utc": started,
            "finished_utc": utc_now(),
        })
        time.sleep(SLEEP_SECONDS)

    references = paths["references_02"]
    manifest_path = references / "strong_interaction_nested_event_download_manifest_raw_002.csv"
    write_csv(manifest_path, manifest_rows, [
        "nested_id", "nested_url", "source_candidate_id", "file_extension", "score", "reasons",
        "download_attempted", "success", "download_status", "http_status", "content_type", "content_length",
        "classification", "validation_message", "size_bytes", "sha256", "output_file", "error", "started_utc", "finished_utc"
    ])

    success_count = sum(1 for r in manifest_rows if r.get("success") is True)
    total_bytes = sum(int(r.get("size_bytes") or 0) for r in manifest_rows)
    class_counts: dict[str, int] = {}
    for row in manifest_rows:
        class_counts[str(row.get("classification", ""))] = class_counts.get(str(row.get("classification", "")), 0) + 1

    summary_path = references / "strong_interaction_nested_event_download_summary_raw_002.txt"
    summary_path.write_text(
        "Strong_interaction nested event target download summary\n"
        "====================================================\n"
        f"Generated UTC: {utc_now()}\n"
        f"Script version: {SCRIPT_VERSION}\n\n"
        f"Nested shortlist rows: {len(rows)}\n"
        f"Attempted downloads: {len(manifest_rows)}\n"
        f"Successful downloads: {success_count}\n"
        f"Total downloaded bytes: {total_bytes}\n\n"
        "Classification counts:\n" + "\n".join(f"- {k}: {v}" for k, v in sorted(class_counts.items())) + "\n\n"
        "Interpretation:\n"
        "- These are nested raw candidates, not final numerical input.\n"
        "- Large ROOT/HDF5/Parquet/archive files are the most relevant for 10000+ event checks.\n"
        "- JSON/small DAT files are usually metadata or condition-data candidates.\n"
        f"Download directory: {paths['download_dir']}\n"
        f"Manifest: {manifest_path}\n",
        encoding="utf-8",
    )

    print(f"[OK] nested download manifest: {manifest_path}")
    print(f"[OK] summary: {summary_path}")
    print(f"[DONE] attempted={len(manifest_rows)} success={success_count} bytes={total_bytes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
