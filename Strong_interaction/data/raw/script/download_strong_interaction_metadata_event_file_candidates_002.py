#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_strong_interaction_metadata_event_file_candidates_002.py

Downloader for metadata-derived DELPHI/CERN event-file candidates.

Author: Kwon Dominicus

Purpose
-------
This script downloads only the shortlist produced by:

    parse_strong_interaction_metadata_records_for_event_files_002.py

Input:
    Strong_interaction/data/raw/references/02/
        strong_interaction_metadata_record_file_candidates_shortlist_raw_002.csv

Outputs:
    Strong_interaction/data/raw/source_tables/02/metadata_event_file_downloads/
    Strong_interaction/data/raw/references/02/
        strong_interaction_metadata_event_file_download_manifest_raw_002.csv
        strong_interaction_metadata_event_file_download_summary_raw_002.txt

This remains a raw acquisition step.  Downloaded files must be inspected before
being treated as event-level data or promoted into cleaned_tables/input.
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
    "Dimensional-Structural-Describability/Strong_interaction metadata-event downloader "
    "(Kwon Dominicus; DELPHI metadata shortlist)"
)
TIMEOUT_SECONDS = 240
SLEEP_SECONDS = 0.75
MAX_SIZE_MB_DEFAULT = 3000

BLOCKED_CONTENT_HINTS = [
    "text/html",
    "application/xhtml",
    "application/javascript",
    "text/javascript",
    "text/css",
]


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def locate_paths() -> dict[str, pathlib.Path]:
    script_path = pathlib.Path(__file__).resolve()
    strong_root = script_path.parents[3]
    return {
        "strong_root": strong_root,
        "references_02": strong_root / "data" / "raw" / "references" / RAW_BATCH,
        "shortlist": strong_root / "data" / "raw" / "references" / RAW_BATCH / "strong_interaction_metadata_record_file_candidates_shortlist_raw_002.csv",
        "download_dir": strong_root / "data" / "raw" / "source_tables" / RAW_BATCH / "metadata_event_file_downloads",
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


def safe_filename(url: str, candidate_id: str) -> str:
    parsed = urllib.parse.urlparse(url)
    name = pathlib.PurePosixPath(parsed.path).name
    if not name:
        name = candidate_id + ".dat"
    if "." not in pathlib.PurePosixPath(name).name:
        name = name + ".dat"
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("._")
    return name[:180] or f"{candidate_id}.dat"


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
            content_type = res.headers.get("Content-Type", "")
            allowed, validation = content_allowed(content_type, allow_html)
            if not allowed:
                return False, None, validation, status, headers, validation
            content_length = res.headers.get("Content-Length")
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
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
    if any(t in lowered for t in [".root", "x-root", "application/root"]):
        return "possible_event_root_file"
    if any(t in lowered for t in [".h5", ".hdf5", "hdf5"]):
        return "possible_hdf5_file"
    if ".parquet" in lowered:
        return "possible_parquet_file"
    if any(t in lowered for t in [".zip", ".tar", ".gz", "gzip", "zip"]):
        return "possible_archive_file"
    if any(t in lowered for t in [".xdst", ".xsdst", ".dst", ".fadana", ".al"]):
        return "possible_delphi_event_or_analysis_format"
    if "json" in lowered:
        return "json_metadata_or_data"
    if any(t in lowered for t in [".dat", "text/plain", "octet-stream"]):
        if size_bytes > 5_000_000:
            return "large_dat_or_binary_candidate"
        return "small_dat_or_metadata_candidate"
    return "unknown_raw_candidate"


def main() -> int:
    parser = argparse.ArgumentParser(description="Download metadata-derived DELPHI/CERN event-file candidates.")
    parser.add_argument("--max-size-mb", type=int, default=MAX_SIZE_MB_DEFAULT, help="Maximum file size per candidate. Default: 3000 MB.")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of candidates. 0 means all.")
    parser.add_argument("--allow-html", action="store_true", help="Allow HTML downloads. Normally disabled.")
    args = parser.parse_args()

    paths = locate_paths()
    paths["download_dir"].mkdir(parents=True, exist_ok=True)
    rows = read_csv(paths["shortlist"])
    if not rows:
        print(f"[ERROR] shortlist missing or empty: {paths['shortlist']}")
        return 1

    targets = rows[: args.limit] if args.limit and args.limit > 0 else rows
    manifest_rows: list[dict[str, Any]] = []

    for idx, row in enumerate(targets, start=1):
        started = utc_now()
        candidate_id = row.get("candidate_id", f"metadata_candidate_{idx:03d}")
        url = row.get("candidate_url", "")
        filename = f"{candidate_id}__{safe_filename(url, candidate_id)}"
        output_path = paths["download_dir"] / filename
        ok, data, error, status, headers, validation = download(url, args.max_size_mb, args.allow_html)
        if ok and data is not None:
            output_path.write_bytes(data)
            size = len(data)
            digest = sha256_bytes(data)
            output_file = str(output_path)
            download_status = "downloaded"
        else:
            size = 0
            digest = ""
            output_file = ""
            download_status = "failed_or_blocked"
        content_type = headers.get("Content-Type", "")
        manifest_rows.append({
            "candidate_id": candidate_id,
            "candidate_url": url,
            "source_nested_id": row.get("source_nested_id", ""),
            "json_path": row.get("json_path", ""),
            "file_extension": row.get("file_extension", ""),
            "score": row.get("score", ""),
            "reasons": row.get("reasons", ""),
            "download_attempted": True,
            "success": ok,
            "download_status": download_status,
            "http_status": status,
            "content_type": content_type,
            "content_length": headers.get("Content-Length", ""),
            "classification": classify_downloaded(content_type, filename, size) if ok else "not_downloaded",
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
    manifest_path = references / "strong_interaction_metadata_event_file_download_manifest_raw_002.csv"
    write_csv(manifest_path, manifest_rows, [
        "candidate_id", "candidate_url", "source_nested_id", "json_path", "file_extension", "score", "reasons",
        "download_attempted", "success", "download_status", "http_status", "content_type", "content_length",
        "classification", "validation_message", "size_bytes", "sha256", "output_file", "error", "started_utc", "finished_utc"
    ])

    success_count = sum(1 for r in manifest_rows if r.get("success") is True)
    total_bytes = sum(int(r.get("size_bytes") or 0) for r in manifest_rows)
    class_counts: dict[str, int] = {}
    for r in manifest_rows:
        cls = str(r.get("classification", ""))
        class_counts[cls] = class_counts.get(cls, 0) + 1

    summary_path = references / "strong_interaction_metadata_event_file_download_summary_raw_002.txt"
    summary_path.write_text(
        "Strong_interaction metadata-derived event file download summary\n"
        "=============================================================\n"
        f"Generated UTC: {utc_now()}\n"
        f"Script version: {SCRIPT_VERSION}\n\n"
        f"Shortlist rows: {len(rows)}\n"
        f"Attempted downloads: {len(manifest_rows)}\n"
        f"Successful downloads: {success_count}\n"
        f"Total downloaded bytes: {total_bytes}\n\n"
        "Classification counts:\n" + "\n".join(f"- {k}: {v}" for k, v in sorted(class_counts.items())) + "\n\n"
        "Interpretation:\n"
        "- Downloaded files are metadata-derived raw candidates, not final numerical input.\n"
        "- DELPHI-specific .xdst/.xsdst/.dst/.fadana/.al candidates may require DELPHI software or format documentation.\n"
        "- A later inventory step must inspect file signatures and event-count evidence.\n"
        f"Download directory: {paths['download_dir']}\n"
        f"Manifest: {manifest_path}\n",
        encoding="utf-8",
    )

    print(f"[OK] metadata event download manifest: {manifest_path}")
    print(f"[OK] summary: {summary_path}")
    print(f"[DONE] attempted={len(manifest_rows)} success={success_count} bytes={total_bytes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
