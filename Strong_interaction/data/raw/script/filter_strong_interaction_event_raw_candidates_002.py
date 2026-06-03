#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
filter_strong_interaction_event_raw_candidates_002.py

Candidate URL filtering/probing script for the Strong_interaction event-level raw
benchmark workflow.

Author: Kwon Dominicus

Purpose
-------
The event raw discovery script may return many URLs with no file extension, PDF
links, JavaScript, JSON metadata, or page links.  This script filters and ranks
those candidates before any unverified download is attempted.

Placement:
    Strong_interaction/data/raw/script/

Input:
    Strong_interaction/data/raw/references/02/strong_interaction_event_raw_candidate_registry_raw_002.csv

Outputs:
    Strong_interaction/data/raw/references/02/
        strong_interaction_event_raw_candidate_domain_summary_raw_002.csv
        strong_interaction_event_raw_candidate_shortlist_raw_002.csv
        strong_interaction_event_raw_candidate_rejected_raw_002.csv
        strong_interaction_event_raw_candidate_filter_summary_raw_002.txt

Optional probing:
    Pass --probe to perform HTTP HEAD / small GET checks and record status,
    Content-Type, Content-Length, and final URL.  The default mode performs only
    offline URL/metadata classification.
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from typing import Any, Iterable, Optional


SCRIPT_VERSION = "002"
RAW_BATCH = "02"
USER_AGENT = (
    "Dimensional-Structural-Describability/Strong_interaction candidate filter "
    "(Kwon Dominicus; raw URL audit)"
)
TIMEOUT_SECONDS = 30
SLEEP_SECONDS = 0.25

FILELIKE_EXTENSIONS = {
    ".root", ".h5", ".hdf5", ".parquet", ".csv", ".tsv", ".jsonl", ".json",
    ".yaml", ".yml", ".yoda", ".npz", ".npy", ".dat", ".txt", ".zip", ".tar", ".gz", ".tgz", ".tar.gz"
}

WEAK_EXTENSIONS = {".pdf", ".js", ".html", ".htm"}

BAD_PAGE_HINTS = re.compile(
    r"(search|literature\?|/abs/|/pdf/|google|javascript|static|assets|favicon|\.js$|\.css$|login|account|oauth)",
    re.IGNORECASE,
)

GOOD_DATA_HINTS = re.compile(
    r"(files|download|record|opendata|root|ntupl|tuple|event|events|parquet|hdf5|h5|jsonl|csv|data|dataset|cern)",
    re.IGNORECASE,
)

DELPHI_HINTS = re.compile(r"(delphi|z0|z-pole|91\.2|hadron|thrust|eec|energy[-_ ]energy)", re.IGNORECASE)

EVENT_COUNT_PATTERN = re.compile(r"(?P<num>\d{1,3}(?:[, ]\d{3})+|\d{4,})(?:\s*)(?P<label>events?|entries|collisions|hadronic\s+events|selected\s+events)", re.IGNORECASE)


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def locate_paths() -> dict[str, pathlib.Path]:
    script_path = pathlib.Path(__file__).resolve()
    strong_root = script_path.parents[3]
    return {
        "strong_root": strong_root,
        "references_02": strong_root / "data" / "raw" / "references" / RAW_BATCH,
        "candidate_registry": strong_root / "data" / "raw" / "references" / RAW_BATCH / "strong_interaction_event_raw_candidate_registry_raw_002.csv",
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


def classify_offline(row: dict[str, str], min_event_count: int) -> dict[str, Any]:
    url = row.get("data_url", "")
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc.lower()
    path = parsed.path
    ext = row.get("file_extension") or file_extension_from_url(url)
    context = " ".join([
        row.get("title_or_context", ""),
        row.get("expected_data_kind", ""),
        row.get("candidate_kind", ""),
        row.get("source_id", ""),
        url,
    ])
    detected_event_count = row.get("detected_event_count", "") or extract_event_count(context)
    event_count_verified = boolish(row.get("event_count_verified"))
    if detected_event_count:
        try:
            event_count_verified = event_count_verified or int(detected_event_count) >= min_event_count
        except Exception:
            pass

    score = 0
    reasons = []

    if ext in FILELIKE_EXTENSIONS:
        score += 4
        reasons.append("filelike_extension")
    elif not ext:
        reasons.append("no_extension")
    elif ext in WEAK_EXTENSIONS:
        score -= 3
        reasons.append("weak_page_or_document_extension")
    else:
        score -= 1
        reasons.append("unknown_extension")

    if GOOD_DATA_HINTS.search(context):
        score += 2
        reasons.append("good_data_hint")
    if DELPHI_HINTS.search(context):
        score += 2
        reasons.append("delphi_or_eventshape_context")
    if BAD_PAGE_HINTS.search(url):
        score -= 3
        reasons.append("bad_page_hint")
    if event_count_verified:
        score += 5
        reasons.append("event_count_verified")
    if domain.endswith("opendata.cern.ch") or domain.endswith("cern.ch"):
        score += 2
        reasons.append("cern_domain")
    if domain.endswith("githubusercontent.com") or domain.endswith("github.com"):
        score += 1
        reasons.append("github_domain")
    if domain.endswith("inspirehep.net") or domain.endswith("zenodo.org"):
        score -= 1
        reasons.append("metadata_domain_possible")

    if score >= 5 and (ext in FILELIKE_EXTENSIONS or event_count_verified):
        decision = "shortlist"
    elif score >= 3 and not ext:
        decision = "needs_probe_extensionless"
    else:
        decision = "reject_or_low_priority"

    return {
        **row,
        "domain": domain,
        "url_path": path,
        "offline_score": score,
        "offline_reasons": ";".join(reasons),
        "offline_decision": decision,
        "detected_event_count_refined": detected_event_count,
        "event_count_verified_refined": event_count_verified,
    }


def safe_probe(url: str) -> dict[str, Any]:
    result = {
        "probe_attempted": True,
        "probe_success": False,
        "probe_method": "HEAD_then_GET_range",
        "probe_http_status": "",
        "probe_content_type": "",
        "probe_content_length": "",
        "probe_final_url": "",
        "probe_error": "",
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
            return result
    except Exception as head_exc:
        # Some servers do not allow HEAD. Try a small range GET.
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*", "Range": "bytes=0-2047"})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as res:
                result.update({
                    "probe_success": True,
                    "probe_http_status": getattr(res, "status", ""),
                    "probe_content_type": res.headers.get("Content-Type", ""),
                    "probe_content_length": res.headers.get("Content-Length", ""),
                    "probe_final_url": res.geturl(),
                    "probe_error": f"HEAD_failed:{type(head_exc).__name__}",
                })
                return result
        except Exception as get_exc:
            result["probe_error"] = f"HEAD:{type(head_exc).__name__}:{head_exc}; GET:{type(get_exc).__name__}:{get_exc}"
            return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Filter/probe Strong_interaction event raw candidate URLs.")
    parser.add_argument("--probe", action="store_true", help="Probe shortlist/extensionless candidates over HTTP for content type and status.")
    parser.add_argument("--probe-limit", type=int, default=80, help="Maximum number of candidates to probe. Default: 80.")
    parser.add_argument("--min-event-count", type=int, default=10000, help="Minimum event count threshold. Default: 10000.")
    args = parser.parse_args()

    paths = locate_paths()
    rows = read_csv(paths["candidate_registry"])
    if not rows:
        print(f"[ERROR] candidate registry not found or empty: {paths['candidate_registry']}")
        return 1

    classified = [classify_offline(row, args.min_event_count) for row in rows]

    # Probe likely useful rows only.
    probe_candidates = [r for r in classified if r["offline_decision"] in {"shortlist", "needs_probe_extensionless"}]
    for idx, row in enumerate(probe_candidates[: args.probe_limit]):
        if args.probe:
            row.update(safe_probe(row.get("data_url", "")))
            # Upgrade/reject by content-type.
            ctype = str(row.get("probe_content_type", "")).lower()
            if any(t in ctype for t in ["text/html", "application/javascript", "text/javascript"]):
                row["offline_decision"] = "reject_page_content_type"
                row["offline_reasons"] += ";probe_page_content_type"
            elif any(t in ctype for t in ["application/octet-stream", "application/x-root", "application/json", "text/csv", "text/plain", "application/x-yaml", "application/zip", "application/x-tar"]):
                if row["offline_decision"] == "needs_probe_extensionless":
                    row["offline_decision"] = "shortlist_probe_filelike_content"
                    row["offline_reasons"] += ";probe_filelike_content_type"
        else:
            row.update({
                "probe_attempted": False,
                "probe_success": False,
                "probe_method": "not_requested",
                "probe_http_status": "",
                "probe_content_type": "",
                "probe_content_length": "",
                "probe_final_url": "",
                "probe_error": "",
            })
        time.sleep(SLEEP_SECONDS if args.probe else 0)

    # Ensure all rows contain probe fields.
    probe_defaults = {
        "probe_attempted": False,
        "probe_success": False,
        "probe_method": "not_requested",
        "probe_http_status": "",
        "probe_content_type": "",
        "probe_content_length": "",
        "probe_final_url": "",
        "probe_error": "",
    }
    for row in classified:
        for k, v in probe_defaults.items():
            row.setdefault(k, v)

    shortlist = [r for r in classified if str(r.get("offline_decision")) in {"shortlist", "shortlist_probe_filelike_content"}]
    needs_probe = [r for r in classified if str(r.get("offline_decision")) == "needs_probe_extensionless"]
    rejected = [r for r in classified if r not in shortlist]

    references = paths["references_02"]
    references.mkdir(parents=True, exist_ok=True)

    fieldnames = list(dict.fromkeys(list(classified[0].keys()) + [
        "domain", "url_path", "offline_score", "offline_reasons", "offline_decision",
        "detected_event_count_refined", "event_count_verified_refined", "probe_attempted", "probe_success",
        "probe_method", "probe_http_status", "probe_content_type", "probe_content_length", "probe_final_url", "probe_error"
    ]))

    shortlist_path = references / "strong_interaction_event_raw_candidate_shortlist_raw_002.csv"
    rejected_path = references / "strong_interaction_event_raw_candidate_rejected_raw_002.csv"
    write_csv(shortlist_path, shortlist, fieldnames)
    write_csv(rejected_path, rejected, fieldnames)

    # Domain/extension summary.
    summary_rows = []
    by_domain_ext = Counter((r.get("domain", ""), r.get("file_extension", ""), r.get("offline_decision", "")) for r in classified)
    for (domain, ext, decision), count in sorted(by_domain_ext.items(), key=lambda x: (-x[1], x[0])):
        summary_rows.append({"domain": domain, "file_extension": ext, "decision": decision, "count": count})
    domain_summary_path = references / "strong_interaction_event_raw_candidate_domain_summary_raw_002.csv"
    write_csv(domain_summary_path, summary_rows, ["domain", "file_extension", "decision", "count"])

    text_summary_path = references / "strong_interaction_event_raw_candidate_filter_summary_raw_002.txt"
    ext_counts = Counter(r.get("file_extension", "") for r in classified)
    decision_counts = Counter(r.get("offline_decision", "") for r in classified)
    domain_counts = Counter(r.get("domain", "") for r in classified)
    text_summary_path.write_text(
        "Strong_interaction event raw candidate filter summary\n"
        "===================================================\n"
        f"Generated UTC: {utc_now()}\n"
        f"Script version: {SCRIPT_VERSION}\n\n"
        f"Input candidates: {len(classified)}\n"
        f"Shortlist candidates: {len(shortlist)}\n"
        f"Needs probe extensionless candidates: {len(needs_probe)}\n"
        f"Rejected/low priority candidates: {len(rejected)}\n"
        f"HTTP probing enabled: {args.probe}\n\n"
        "Top extension counts:\n"
        + "\n".join(f"- {ext or '[no_extension]'}: {count}" for ext, count in ext_counts.most_common(15))
        + "\n\nDecision counts:\n"
        + "\n".join(f"- {decision}: {count}" for decision, count in decision_counts.most_common())
        + "\n\nTop domain counts:\n"
        + "\n".join(f"- {domain or '[no_domain]'}: {count}" for domain, count in domain_counts.most_common(20))
        + "\n\nInterpretation:\n"
        + "- Use shortlist only for reviewed raw-data download attempts.\n"
        + "- Empty-extension candidates should not be downloaded blindly. Probe them first.\n"
        + "- PDF/JS/HTML candidates are normally not event-level raw data.\n",
        encoding="utf-8",
    )

    print(f"[OK] shortlist: {shortlist_path}")
    print(f"[OK] rejected: {rejected_path}")
    print(f"[OK] domain summary: {domain_summary_path}")
    print(f"[OK] summary: {text_summary_path}")
    print(f"[DONE] input={len(classified)} shortlist={len(shortlist)} needs_probe={len(needs_probe)} rejected={len(rejected)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
