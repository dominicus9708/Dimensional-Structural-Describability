#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
search_strong_interaction_cern_delphi_event_records_003.py

CERN Open Data record-search pipeline for the Strong_interaction benchmark raw
acquisition workflow.

Author: Kwon Dominicus

Purpose
-------
The batch-02 path reached DELPHI condition/support databases and metadata, but
metadata-derived api/files candidates did not expose a direct event-level file.
This batch-03 script therefore starts a new, cleaner CERN Open Data record search
focused on record-level discovery rather than api/files fragments.

Placement:
    Strong_interaction/data/raw/script/

Outputs:
    Strong_interaction/data/raw/source_tables/03/cern_record_search_pages/
    Strong_interaction/data/raw/references/03/
        strong_interaction_cern_delphi_record_search_manifest_raw_003.csv
        strong_interaction_cern_delphi_record_candidates_raw_003.csv
        strong_interaction_cern_delphi_record_candidates_shortlist_raw_003.csv
        strong_interaction_cern_delphi_record_candidates_rejected_raw_003.csv
        strong_interaction_cern_delphi_record_search_summary_raw_003.txt

This script does not download event files. It builds a record-level candidate
registry for the next reviewed acquisition step.
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import pathlib
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from typing import Any, Iterable


SCRIPT_VERSION = "003"
RAW_BATCH = "03"
BASE_URL = "https://opendata.cern.ch"
USER_AGENT = (
    "Dimensional-Structural-Describability/Strong_interaction CERN DELPHI record search "
    "(Kwon Dominicus; batch 03)"
)
TIMEOUT_SECONDS = 90
SLEEP_SECONDS = 0.8

SEARCH_QUERIES = [
    "DELPHI event data",
    "DELPHI events",
    "DELPHI DST",
    "DELPHI xDST",
    "DELPHI xsdst",
    "DELPHI FADANA",
    "DELPHI hadronic events",
    "DELPHI Z0 hadronic",
    "DELPHI LEP data",
    "DELPHI reconstructed data",
    "DELPHI track data",
    "DELPHI particle data",
    "DELPHI collision data",
    "DELPHI 1994 data",
    "DELPHI open data event",
    "DELPHI open data DST",
    "DELPHI open data FADANA",
]

HIGH_VALUE_HINTS = re.compile(r"(event|events|dst|xdst|xsdst|fadana|root|ntupl|ntuple|tuple|hadron|hadronic|z0|z-pole|lep|reconstruct|reconstructed|track|particle|collision|data)", re.IGNORECASE)
SUPPORT_HINTS = re.compile(r"(calib|calibration|geometry|condition|database|dbcalb|dbgeom|dblepm|dbrunt|dbscon|dbsysf|alignment|detector|guide|docs|about|docker|cvmfs|software|tutorial)", re.IGNORECASE)
FILE_HINTS = re.compile(r"(files|download|uri|bucket|eos|root|dst|xdst|xsdst|fadana|tar|zip|gz|dat)", re.IGNORECASE)
EVENT_COUNT_PATTERN = re.compile(r"(?P<num>\d{1,3}(?:[, ]\d{3})+|\d{4,})(?:\s*)(?P<label>events?|entries|collisions|hadronic\s+events|selected\s+events)", re.IGNORECASE)
URL_PATTERN = re.compile(r"https?://[^\s\)\]\}\>'\"\\]+", re.IGNORECASE)


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def locate_paths() -> dict[str, pathlib.Path]:
    script_path = pathlib.Path(__file__).resolve()
    strong_root = script_path.parents[3]
    return {
        "strong_root": strong_root,
        "references_03": strong_root / "data" / "raw" / "references" / RAW_BATCH,
        "source_tables_03": strong_root / "data" / "raw" / "source_tables" / RAW_BATCH,
        "search_pages": strong_root / "data" / "raw" / "source_tables" / RAW_BATCH / "cern_record_search_pages",
    }


def write_csv(path: pathlib.Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def safe_filename(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    return value[:160] or "unnamed"


def safe_request(url: str) -> tuple[bool, bytes | None, str, int | str, dict[str, str]]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json,text/html,*/*"})
    headers: dict[str, str] = {}
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as res:
            headers = {k: v for k, v in res.headers.items()}
            data = res.read(50 * 1024 * 1024 + 1)
            if len(data) > 50 * 1024 * 1024:
                return False, None, "blocked_search_response_too_large", getattr(res, "status", ""), headers
            return True, data, "", getattr(res, "status", ""), headers
    except urllib.error.HTTPError as exc:
        return False, None, f"HTTPError {exc.code}: {exc.reason}", exc.code, headers
    except urllib.error.URLError as exc:
        return False, None, f"URLError: {exc.reason}", "", headers
    except Exception as exc:
        return False, None, f"{type(exc).__name__}: {exc}", "", headers


def extract_event_count(text: str) -> str:
    counts = []
    for m in EVENT_COUNT_PATTERN.finditer(text or ""):
        try:
            counts.append(int(re.sub(r"[,\s]", "", m.group("num"))))
        except Exception:
            pass
    return str(max(counts)) if counts else ""


def iter_records_from_json(obj: Any) -> list[dict[str, Any]]:
    if isinstance(obj, dict):
        if isinstance(obj.get("hits"), dict) and isinstance(obj["hits"].get("hits"), list):
            return [h for h in obj["hits"]["hits"] if isinstance(h, dict)]
        if isinstance(obj.get("hits"), list):
            return [h for h in obj["hits"] if isinstance(h, dict)]
        if isinstance(obj.get("metadata"), dict) or obj.get("recid") or obj.get("id"):
            return [obj]
    return []


def get_record_id(record: dict[str, Any]) -> str:
    for key in ("id", "recid", "record_id"):
        if record.get(key) is not None:
            return str(record.get(key))
    meta = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    for key in ("recid", "id"):
        if meta.get(key) is not None:
            return str(meta.get(key))
    links = record.get("links") if isinstance(record.get("links"), dict) else {}
    for v in links.values():
        m = re.search(r"/(?:records|record)/(\d+)", str(v))
        if m:
            return m.group(1)
    return ""


def record_to_text(record: dict[str, Any]) -> str:
    try:
        return json.dumps(record, ensure_ascii=False)
    except Exception:
        return str(record)


def collect_file_candidates(record: dict[str, Any]) -> tuple[int, int, str]:
    text = record_to_text(record)
    file_count = 0
    filelike_count = 0
    examples = []

    def walk(obj: Any, path: str = "") -> None:
        nonlocal file_count, filelike_count, examples
        if isinstance(obj, dict):
            keys = {str(k).lower() for k in obj.keys()}
            if keys & {"files", "file", "uri", "url", "key", "filename", "size", "checksum", "download", "bucket"}:
                file_count += 1
                ctx = json.dumps(obj, ensure_ascii=False)[:500]
                if FILE_HINTS.search(ctx):
                    filelike_count += 1
                    if len(examples) < 5:
                        examples.append(ctx)
            for k, v in obj.items():
                walk(v, f"{path}.{k}" if path else str(k))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, f"{path}[{i}]")

    walk(record)
    # Fallback: count URLs and file hints in raw text.
    url_count = len(URL_PATTERN.findall(text))
    if url_count and FILE_HINTS.search(text):
        filelike_count += url_count
    return file_count, filelike_count, " | ".join(examples)


def score_record(record: dict[str, Any], query: str) -> dict[str, Any]:
    text = record_to_text(record)
    meta = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    title = meta.get("title") or record.get("title") or ""
    description = meta.get("description") or meta.get("abstract") or record.get("description") or ""
    recid = get_record_id(record)
    event_count = extract_event_count(text)
    file_dict_count, filelike_count, file_examples = collect_file_candidates(record)

    score = 0
    reasons = []
    if "delphi" in text.lower():
        score += 3
        reasons.append("delphi_context")
    if HIGH_VALUE_HINTS.search(text):
        score += 5
        reasons.append("event_or_data_hint")
    if SUPPORT_HINTS.search(text):
        score -= 3
        reasons.append("support_or_doc_hint")
    if filelike_count > 0:
        score += min(8, 2 + filelike_count)
        reasons.append("filelike_metadata_present")
    if event_count:
        try:
            if int(event_count) >= 10000:
                score += 5
                reasons.append("event_count_ge_10000")
        except Exception:
            pass
    if any(token in text.lower() for token in ["xdst", "xsdst", "dst", "fadana", "root"]):
        score += 5
        reasons.append("delphi_event_format_hint")
    if any(token in text.lower() for token in ["guide", "documentation", "about delphi", "docker", "cvmfs"]):
        score -= 4
        reasons.append("documentation_hint")

    if score >= 10:
        decision = "shortlist_record_for_file_parsing"
    elif score >= 6:
        decision = "review_record_candidate"
    else:
        decision = "reject_record_low_priority"

    links = record.get("links") if isinstance(record.get("links"), dict) else {}
    api_url = links.get("self") or links.get("latest") or (f"{BASE_URL}/api/records/{recid}" if recid else "")
    web_url = links.get("html") or (f"{BASE_URL}/record/{recid}" if recid else "")

    return {
        "record_candidate_id": f"CERN_DELPHI_RECORD_{recid or abs(hash(text)) % 10**10}",
        "recid": recid,
        "query": query,
        "title": str(title)[:500],
        "api_url": api_url,
        "web_url": web_url,
        "score": score,
        "decision": decision,
        "reasons": ";".join(reasons),
        "detected_event_count": event_count,
        "file_dict_count": file_dict_count,
        "filelike_count": filelike_count,
        "file_examples": file_examples,
        "description_preview": re.sub(r"\s+", " ", str(description))[:1000],
        "created_utc": utc_now(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Search CERN Open Data records for DELPHI event-level candidates.")
    parser.add_argument("--size", type=int, default=100, help="Records per query. Default: 100.")
    args = parser.parse_args()

    paths = locate_paths()
    for key in ("references_03", "search_pages"):
        paths[key].mkdir(parents=True, exist_ok=True)

    search_rows: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []

    for idx, query in enumerate(SEARCH_QUERIES, start=1):
        encoded = urllib.parse.quote(query)
        url = f"{BASE_URL}/api/records/?q={encoded}&size={args.size}"
        started = utc_now()
        ok, data, error, status, headers = safe_request(url)
        out_file = ""
        record_count = 0
        if ok and data is not None:
            out_path = paths["search_pages"] / f"cern_record_search_{idx:03d}_{safe_filename(query)}_raw_{SCRIPT_VERSION}.json"
            out_path.write_bytes(data)
            out_file = str(out_path)
            try:
                obj = json.loads(data.decode("utf-8", errors="replace"))
                records = iter_records_from_json(obj)
                record_count = len(records)
                for rec in records:
                    candidates.append(score_record(rec, query))
            except Exception as exc:
                error = f"json_parse_error:{type(exc).__name__}:{exc}"
        search_rows.append({
            "query_id": idx,
            "query": query,
            "url": url,
            "success": ok,
            "http_status": status,
            "content_type": headers.get("Content-Type", ""),
            "output_file": out_file,
            "record_count": record_count,
            "error": error,
            "started_utc": started,
            "finished_utc": utc_now(),
        })
        time.sleep(SLEEP_SECONDS)

    # Deduplicate by recid/api_url/title, keeping best score.
    best: dict[str, dict[str, Any]] = {}
    for cand in candidates:
        key = cand.get("recid") or cand.get("api_url") or cand.get("title")
        if key not in best or int(cand["score"]) > int(best[key]["score"]):
            best[key] = cand
    deduped = sorted(best.values(), key=lambda r: (-int(r["score"]), str(r.get("recid", ""))))
    shortlist = [r for r in deduped if r["decision"] == "shortlist_record_for_file_parsing"]
    rejected = [r for r in deduped if r["decision"] != "shortlist_record_for_file_parsing"]

    refs = paths["references_03"]
    search_manifest = refs / "strong_interaction_cern_delphi_record_search_manifest_raw_003.csv"
    write_csv(search_manifest, search_rows, [
        "query_id", "query", "url", "success", "http_status", "content_type", "output_file", "record_count", "error", "started_utc", "finished_utc"
    ])

    fieldnames = [
        "record_candidate_id", "recid", "query", "title", "api_url", "web_url", "score", "decision", "reasons",
        "detected_event_count", "file_dict_count", "filelike_count", "file_examples", "description_preview", "created_utc"
    ]
    all_path = refs / "strong_interaction_cern_delphi_record_candidates_raw_003.csv"
    short_path = refs / "strong_interaction_cern_delphi_record_candidates_shortlist_raw_003.csv"
    reject_path = refs / "strong_interaction_cern_delphi_record_candidates_rejected_raw_003.csv"
    write_csv(all_path, deduped, fieldnames)
    write_csv(short_path, shortlist, fieldnames)
    write_csv(reject_path, rejected, fieldnames)

    decision_counts = Counter(r["decision"] for r in deduped)
    reason_counts = Counter()
    for r in deduped:
        for reason in str(r.get("reasons", "")).split(";"):
            if reason:
                reason_counts[reason] += 1

    summary_path = refs / "strong_interaction_cern_delphi_record_search_summary_raw_003.txt"
    summary_path.write_text(
        "Strong_interaction CERN DELPHI record search summary\n"
        "==================================================\n"
        f"Generated UTC: {utc_now()}\n"
        f"Script version: {SCRIPT_VERSION}\n"
        f"Raw batch: {RAW_BATCH}\n\n"
        f"Search queries: {len(SEARCH_QUERIES)}\n"
        f"Search responses saved: {sum(1 for r in search_rows if r['success'])}\n"
        f"Unique record candidates: {len(deduped)}\n"
        f"Shortlist records for file parsing: {len(shortlist)}\n"
        f"Rejected/review records: {len(rejected)}\n\n"
        "Decision counts:\n" + "\n".join(f"- {k}: {v}" for k, v in decision_counts.most_common()) + "\n\n"
        "Top reason counts:\n" + "\n".join(f"- {k}: {v}" for k, v in reason_counts.most_common(20)) + "\n\n"
        "Interpretation:\n"
        "- Batch 03 starts a new record-level route because batch 02 reached support DBs and invalid api/files endpoints.\n"
        "- Shortlist records should be parsed for file lists before downloading any large raw files.\n"
        "- Do not treat record-level candidates as event data until file-level inspection confirms event/DST/xDST/FADANA content.\n"
        f"Search manifest: {search_manifest}\n"
        f"Record shortlist: {short_path}\n",
        encoding="utf-8",
    )

    print(f"[OK] search manifest: {search_manifest}")
    print(f"[OK] all candidates: {all_path}")
    print(f"[OK] shortlist: {short_path}")
    print(f"[OK] rejected: {reject_path}")
    print(f"[OK] summary: {summary_path}")
    print(f"[DONE] records={len(deduped)} shortlist={len(shortlist)} rejected={len(rejected)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
