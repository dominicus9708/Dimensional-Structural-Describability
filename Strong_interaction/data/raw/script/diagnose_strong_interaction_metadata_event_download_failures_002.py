#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diagnose_strong_interaction_metadata_event_download_failures_002.py

Failure-diagnosis script for metadata-derived DELPHI/CERN event-file candidate
download attempts.

Author: Kwon Dominicus

Purpose
-------
The metadata-derived shortlist downloader can fail because a candidate is a page,
a duplicate API-file endpoint, a missing CERN object, a blocked content type, a
404/403 response, a redirect, or a size limit.  This script reads the download
manifest, isolates failed rows, performs optional lightweight HEAD/Range probing,
and writes a diagnosis table for the next acquisition decision.

Input:
    Strong_interaction/data/raw/references/02/
        strong_interaction_metadata_event_file_download_manifest_raw_002.csv

Outputs:
    Strong_interaction/data/raw/references/02/
        strong_interaction_metadata_event_download_failure_diagnosis_raw_002.csv
        strong_interaction_metadata_event_download_failure_diagnosis_summary_raw_002.txt

This script does not download full files.
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import pathlib
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from typing import Any, Iterable


SCRIPT_VERSION = "002"
RAW_BATCH = "02"
USER_AGENT = (
    "Dimensional-Structural-Describability/Strong_interaction metadata failure diagnoser "
    "(Kwon Dominicus; no full download)"
)
TIMEOUT_SECONDS = 45
SLEEP_SECONDS = 0.3

HTML_HINTS = ["text/html", "application/xhtml"]
DATA_CONTENT_HINTS = [
    "application/octet-stream", "application/json", "text/plain", "text/csv",
    "application/zip", "application/gzip", "application/x-tar", "application/x-root",
    "application/x-hdf5", "application/x-parquet"
]


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def locate_paths() -> dict[str, pathlib.Path]:
    script_path = pathlib.Path(__file__).resolve()
    strong_root = script_path.parents[3]
    return {
        "references_02": strong_root / "data" / "raw" / "references" / RAW_BATCH,
        "manifest": strong_root / "data" / "raw" / "references" / RAW_BATCH / "strong_interaction_metadata_event_file_download_manifest_raw_002.csv",
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


def extract_file_uuid(url: str) -> str:
    path = urllib.parse.urlparse(url).path
    m = re.search(r"/api/files/([^/?#]+)", path)
    return m.group(1) if m else ""


def infer_initial_reason(row: dict[str, str]) -> str:
    error = row.get("error", "")
    validation = row.get("validation_message", "")
    http_status = row.get("http_status", "")
    url = row.get("candidate_url", "")
    if "blocked_by_size_limit" in error:
        return "size_limit_blocked_possible_large_file"
    if "blocked_page_content_type" in error or "blocked_page_content_type" in validation:
        return "html_or_page_content_blocked"
    if "HTTPError 404" in error or http_status == "404":
        return "http_404_missing_or_not_direct_file"
    if "HTTPError 403" in error or http_status == "403":
        return "http_403_forbidden_or_access_policy"
    if "HTTPError" in error:
        return "other_http_error"
    if "URLError" in error:
        return "url_or_network_error"
    if not url:
        return "empty_url"
    return "unknown_failure"


def probe_url(url: str) -> dict[str, Any]:
    result = {
        "probe_attempted": True,
        "probe_success": False,
        "probe_method": "HEAD_then_range_GET",
        "probe_http_status": "",
        "probe_content_type": "",
        "probe_content_length": "",
        "probe_final_url": "",
        "probe_error": "",
        "probe_interpretation": "",
    }
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as res:
            result.update({
                "probe_success": True,
                "probe_http_status": getattr(res, "status", ""),
                "probe_content_type": res.headers.get("Content-Type", ""),
                "probe_content_length": res.headers.get("Content-Length", ""),
                "probe_final_url": res.geturl(),
            })
            result["probe_interpretation"] = interpret_probe(result)
            return result
    except Exception as head_exc:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*", "Range": "bytes=0-2047"})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as res:
                result.update({
                    "probe_success": True,
                    "probe_http_status": getattr(res, "status", ""),
                    "probe_content_type": res.headers.get("Content-Type", ""),
                    "probe_content_length": res.headers.get("Content-Length", ""),
                    "probe_final_url": res.geturl(),
                    "probe_error": f"HEAD_failed:{type(head_exc).__name__}:{head_exc}",
                })
                result["probe_interpretation"] = interpret_probe(result)
                return result
        except Exception as get_exc:
            result["probe_error"] = f"HEAD:{type(head_exc).__name__}:{head_exc}; RANGE_GET:{type(get_exc).__name__}:{get_exc}"
            result["probe_interpretation"] = "probe_failed"
            return result


def interpret_probe(probe: dict[str, Any]) -> str:
    ctype = str(probe.get("probe_content_type", "")).lower()
    clen = str(probe.get("probe_content_length", ""))
    status = str(probe.get("probe_http_status", ""))
    if status in {"403"}:
        return "forbidden"
    if status in {"404"}:
        return "missing"
    if any(h in ctype for h in HTML_HINTS):
        return "page_not_raw_file"
    if any(h in ctype for h in DATA_CONTENT_HINTS):
        if clen:
            try:
                n = int(clen)
                if n > 5_000_000:
                    return "large_data_like_endpoint"
                if n <= 2:
                    return "empty_or_placeholder_endpoint"
                return "small_data_or_metadata_endpoint"
            except Exception:
                return "data_like_endpoint_unknown_size"
        return "data_like_endpoint_unknown_size"
    if not ctype:
        return "unknown_content_type"
    return "unrecognized_content_type"


def next_action(initial_reason: str, probe_interpretation: str) -> str:
    if initial_reason == "size_limit_blocked_possible_large_file" or probe_interpretation == "large_data_like_endpoint":
        return "review_for_large_file_download_with_explicit_limit_and_ignore"
    if probe_interpretation in {"page_not_raw_file", "missing", "forbidden"}:
        return "do_not_download_until_alternate_endpoint_found"
    if probe_interpretation in {"small_data_or_metadata_endpoint", "empty_or_placeholder_endpoint"}:
        return "low_priority_metadata_or_placeholder"
    if probe_interpretation == "data_like_endpoint_unknown_size":
        return "review_headers_then_optional_limited_download"
    return "manual_review"


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose failed metadata-derived DELPHI/CERN download rows.")
    parser.add_argument("--probe", action="store_true", help="Perform HEAD/range GET probing for failed URLs.")
    parser.add_argument("--probe-limit", type=int, default=100, help="Maximum failed rows to probe. Default: 100.")
    args = parser.parse_args()

    paths = locate_paths()
    rows = read_csv(paths["manifest"])
    if not rows:
        print(f"[ERROR] manifest missing or empty: {paths['manifest']}")
        return 1

    failed = [r for r in rows if str(r.get("success", "")).lower() != "true"]
    diagnosed: list[dict[str, Any]] = []
    for idx, row in enumerate(failed, start=1):
        initial = infer_initial_reason(row)
        probe = {
            "probe_attempted": False,
            "probe_success": False,
            "probe_method": "not_requested",
            "probe_http_status": "",
            "probe_content_type": "",
            "probe_content_length": "",
            "probe_final_url": "",
            "probe_error": "",
            "probe_interpretation": "not_probed",
        }
        if args.probe and idx <= args.probe_limit:
            probe = probe_url(row.get("candidate_url", ""))
            time.sleep(SLEEP_SECONDS)
        diagnosed.append({
            "candidate_id": row.get("candidate_id", ""),
            "candidate_url": row.get("candidate_url", ""),
            "file_uuid": extract_file_uuid(row.get("candidate_url", "")),
            "file_extension": row.get("file_extension", ""),
            "score": row.get("score", ""),
            "reasons": row.get("reasons", ""),
            "http_status_original": row.get("http_status", ""),
            "error_original": row.get("error", ""),
            "validation_message_original": row.get("validation_message", ""),
            "initial_failure_reason": initial,
            **probe,
            "recommended_next_action": next_action(initial, str(probe.get("probe_interpretation", ""))),
            "created_utc": utc_now(),
        })

    references = paths["references_02"]
    out_path = references / "strong_interaction_metadata_event_download_failure_diagnosis_raw_002.csv"
    fieldnames = [
        "candidate_id", "candidate_url", "file_uuid", "file_extension", "score", "reasons",
        "http_status_original", "error_original", "validation_message_original", "initial_failure_reason",
        "probe_attempted", "probe_success", "probe_method", "probe_http_status", "probe_content_type",
        "probe_content_length", "probe_final_url", "probe_error", "probe_interpretation",
        "recommended_next_action", "created_utc"
    ]
    write_csv(out_path, diagnosed, fieldnames)

    initial_counts = Counter(d["initial_failure_reason"] for d in diagnosed)
    probe_counts = Counter(d["probe_interpretation"] for d in diagnosed)
    action_counts = Counter(d["recommended_next_action"] for d in diagnosed)
    summary_path = references / "strong_interaction_metadata_event_download_failure_diagnosis_summary_raw_002.txt"
    summary_path.write_text(
        "Strong_interaction metadata event download failure diagnosis summary\n"
        "================================================================\n"
        f"Generated UTC: {utc_now()}\n"
        f"Script version: {SCRIPT_VERSION}\n\n"
        f"Manifest rows read: {len(rows)}\n"
        f"Failed rows diagnosed: {len(diagnosed)}\n"
        f"HTTP probing enabled: {args.probe}\n\n"
        "Initial failure reason counts:\n" + "\n".join(f"- {k}: {v}" for k, v in initial_counts.most_common()) + "\n\n"
        "Probe interpretation counts:\n" + "\n".join(f"- {k}: {v}" for k, v in probe_counts.most_common()) + "\n\n"
        "Recommended next action counts:\n" + "\n".join(f"- {k}: {v}" for k, v in action_counts.most_common()) + "\n\n"
        "Interpretation:\n"
        "- Large/data-like failed endpoints may justify a revised downloader.\n"
        "- HTML, forbidden, missing, and placeholder endpoints should not be treated as event data.\n"
        "- Use the diagnosis CSV before changing download rules.\n"
        f"Diagnosis CSV: {out_path}\n",
        encoding="utf-8",
    )

    print(f"[OK] failure diagnosis: {out_path}")
    print(f"[OK] summary: {summary_path}")
    print(f"[DONE] failed_rows={len(diagnosed)} probe={args.probe}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
