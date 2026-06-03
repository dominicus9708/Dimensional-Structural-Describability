#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_strong_interaction_event_raw_shortlist_002.py

Shortlist-only raw download script for the Strong_interaction event-level
benchmark workflow.

Author: Kwon Dominicus

Purpose
-------
This script downloads only the candidates that survived
filter_strong_interaction_event_raw_candidates_002.py.

It is intentionally stricter than --download-unverified in the discovery script.
It reads:

    Strong_interaction/data/raw/references/02/
        strong_interaction_event_raw_candidate_shortlist_raw_002.csv

and writes downloaded raw candidates to:

    Strong_interaction/data/raw/source_tables/02/event_raw_shortlist_downloads/

and manifests to:

    Strong_interaction/data/raw/references/02/

This is still raw acquisition.  Downloaded files must be inspected and cleaned
before any numerical cleaned_tables or data/derived/input promotion.
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


SCRIPT_VERSION = "002"
RAW_BATCH = "02"
USER_AGENT = (
    "Dimensional-Structural-Describability/Strong_interaction shortlist downloader "
    "(Kwon Dominicus; reviewed raw candidates only)"
)
TIMEOUT_SECONDS = 120
SLEEP_SECONDS = 0.75
MAX_SIZE_MB_DEFAULT = 2000

SAFE_CONTENT_HINTS = [
    "application/octet-stream",
    "application/x-root",
    "application/root",
    "application/json",
    "application/x-ndjson",
    "text/csv",
    "text/plain",
    "application/x-yaml",
    "text/yaml",
    "application/zip",
    "application/x-tar",
    "application/gzip",
    "application/x-hdf5",
    "application/x-parquet",
]

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
        "shortlist": strong_root / "data" / "raw" / "references" / RAW_BATCH / "strong_interaction_event_raw_candidate_shortlist_raw_002.csv",
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


def boolish(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def safe_filename(value: str, default: str) -> str:
    parsed = urllib.parse.urlparse(value)
    name = pathlib.PurePosixPath(parsed.path).name or default
    if not pathlib.PurePosixPath(name).suffix:
        # Keep extensionless endpoints auditable but not misleading.
        name = name + ".dat"
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("._")
    return name[:180] or default


def content_is_allowed(content_type: str, allow_html: bool) -> tuple[bool, str]:
    lowered = (content_type or "").lower()
    if allow_html:
        return True, "allowed_by_allow_html"
    if any(h in lowered for h in BLOCKED_CONTENT_HINTS):
        return False, f"blocked_content_type:{content_type}"
    if not lowered:
        return True, "empty_content_type_allowed_with_caution"
    if any(h in lowered for h in SAFE_CONTENT_HINTS):
        return True, f"allowed_content_type:{content_type}"
    # Some file servers use generic binary or omit exact type; allow but record caution.
    return True, f"unrecognized_content_type_allowed_with_caution:{content_type}"


def safe_download(url: str, max_size_mb: int, allow_html: bool) -> tuple[bool, bytes | None, str, int | str, dict[str, str], str]:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/octet-stream,text/csv,application/json,text/plain,*/*"}
    req = urllib.request.Request(url, headers=headers)
    response_headers: dict[str, str] = {}
    validation_message = ""
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as res:
            status = getattr(res, "status", "")
            response_headers = {k: v for k, v in res.headers.items()}
            content_type = res.headers.get("Content-Type", "")
            allowed, validation_message = content_is_allowed(content_type, allow_html)
            if not allowed:
                return False, None, validation_message, status, response_headers, validation_message
            content_length = res.headers.get("Content-Length")
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                if size_mb > max_size_mb:
                    msg = f"blocked_by_size_limit:{size_mb:.2f}MB>{max_size_mb}MB"
                    return False, None, msg, status, response_headers, validation_message
            data = res.read(max_size_mb * 1024 * 1024 + 1)
            if len(data) > max_size_mb * 1024 * 1024:
                msg = f"blocked_by_size_limit_after_read:>{max_size_mb}MB"
                return False, None, msg, status, response_headers, validation_message
            return True, data, "", status, response_headers, validation_message
    except urllib.error.HTTPError as exc:
        return False, None, f"HTTPError {exc.code}: {exc.reason}", exc.code, response_headers, validation_message
    except urllib.error.URLError as exc:
        return False, None, f"URLError: {exc.reason}", "", response_headers, validation_message
    except Exception as exc:
        return False, None, f"{type(exc).__name__}: {exc}", "", response_headers, validation_message


def main() -> int:
    parser = argparse.ArgumentParser(description="Download only filtered Strong_interaction raw event candidates.")
    parser.add_argument("--max-size-mb", type=int, default=MAX_SIZE_MB_DEFAULT, help="Maximum file size per candidate. Default: 2000 MB.")
    parser.add_argument("--allow-html", action="store_true", help="Allow HTML downloads. Normally disabled because pages are not raw event data.")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of candidates to attempt. 0 means no limit.")
    parser.add_argument("--require-probe-success", action="store_true", help="Attempt only rows with probe_success=True.")
    args = parser.parse_args()

    paths = locate_paths()
    paths["download_dir"].mkdir(parents=True, exist_ok=True)
    rows = read_csv(paths["shortlist"])
    if not rows:
        print(f"[ERROR] Shortlist missing or empty: {paths['shortlist']}")
        return 1

    attempts = []
    for row in rows:
        if args.require_probe_success and not boolish(row.get("probe_success")):
            continue
        attempts.append(row)
    if args.limit and args.limit > 0:
        attempts = attempts[: args.limit]

    manifest_rows: list[dict[str, Any]] = []
    for idx, row in enumerate(attempts, start=1):
        started = utc_now()
        url = row.get("data_url", "")
        candidate_id = row.get("candidate_id", f"candidate_{idx:03d}")
        filename = f"{candidate_id}__{safe_filename(url, f'candidate_{idx:03d}.dat')}"
        output_path = paths["download_dir"] / filename
        ok, data, error, status, headers, validation_message = safe_download(url, args.max_size_mb, args.allow_html)
        if ok and data is not None:
            output_path.write_bytes(data)
            digest = sha256_bytes(data)
            size = len(data)
            output_file = str(output_path)
            download_status = "downloaded"
        else:
            digest = ""
            size = 0
            output_file = ""
            download_status = "failed_or_blocked"
        manifest_rows.append({
            "candidate_id": candidate_id,
            "source_id": row.get("source_id", ""),
            "data_url": url,
            "offline_decision": row.get("offline_decision", ""),
            "offline_score": row.get("offline_score", ""),
            "offline_reasons": row.get("offline_reasons", ""),
            "probe_success": row.get("probe_success", ""),
            "probe_content_type": row.get("probe_content_type", ""),
            "download_attempted": True,
            "success": ok,
            "download_status": download_status,
            "http_status": status,
            "content_type": headers.get("Content-Type", ""),
            "content_length": headers.get("Content-Length", ""),
            "validation_message": validation_message,
            "size_bytes": size,
            "sha256": digest,
            "output_file": output_file,
            "error": error,
            "started_utc": started,
            "finished_utc": utc_now(),
        })
        time.sleep(SLEEP_SECONDS)

    manifest_path = paths["references_02"] / "strong_interaction_event_raw_shortlist_download_manifest_raw_002.csv"
    write_csv(manifest_path, manifest_rows, [
        "candidate_id", "source_id", "data_url", "offline_decision", "offline_score", "offline_reasons",
        "probe_success", "probe_content_type", "download_attempted", "success", "download_status",
        "http_status", "content_type", "content_length", "validation_message", "size_bytes", "sha256",
        "output_file", "error", "started_utc", "finished_utc"
    ])

    success_count = sum(1 for r in manifest_rows if r.get("success") is True)
    total_bytes = sum(int(r.get("size_bytes") or 0) for r in manifest_rows)
    summary_path = paths["references_02"] / "strong_interaction_event_raw_shortlist_download_summary_raw_002.txt"
    summary_path.write_text(
        "Strong_interaction event raw shortlist download summary\n"
        "=====================================================\n"
        f"Generated UTC: {utc_now()}\n"
        f"Script version: {SCRIPT_VERSION}\n\n"
        f"Shortlist rows: {len(rows)}\n"
        f"Attempted downloads: {len(manifest_rows)}\n"
        f"Successful downloads: {success_count}\n"
        f"Total downloaded bytes: {total_bytes}\n\n"
        "Interpretation:\n"
        "- Downloaded files are raw candidates only, not final numerical input.\n"
        "- HTML is blocked by default.\n"
        "- A later cleaner must inspect file type, structure, and event count.\n"
        f"Download directory: {paths['download_dir']}\n"
        f"Manifest: {manifest_path}\n",
        encoding="utf-8",
    )

    print(f"[OK] download manifest: {manifest_path}")
    print(f"[OK] summary: {summary_path}")
    print(f"[DONE] attempted={len(manifest_rows)} success={success_count} bytes={total_bytes}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
