#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parse_strong_interaction_cern_delphi_record_files_003.py

Record-file parser for the batch-03 CERN DELPHI record-search route.

Author: Kwon Dominicus

Purpose
-------
Batch 03 found many DELPHI record-level candidates, including collision-data
records such as lolept*/short*.  This script parses the saved CERN Open Data
record-search JSON pages and extracts file-level candidates for shortlisted
records, while prioritizing collision data over simulation and documentation.

Placement:
    Strong_interaction/data/raw/script/

Inputs:
    Strong_interaction/data/raw/source_tables/03/cern_record_search_pages/
    Strong_interaction/data/raw/references/03/
        strong_interaction_cern_delphi_record_candidates_shortlist_raw_003.csv

Outputs:
    Strong_interaction/data/raw/references/03/
        strong_interaction_cern_delphi_record_file_candidates_raw_003.csv
        strong_interaction_cern_delphi_record_file_candidates_collision_shortlist_raw_003.csv
        strong_interaction_cern_delphi_record_file_candidates_rejected_raw_003.csv
        strong_interaction_cern_delphi_record_file_candidates_summary_raw_003.txt

This script does not download large event files.  It creates a reviewed file-level
target registry for the next controlled download step.
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


SCRIPT_VERSION = "003"
RAW_BATCH = "03"
BASE_URL = "https://opendata.cern.ch"

COLLISION_TITLE_HINTS = re.compile(r"\b(DELPHI\s+collision\s+data|lolept|short)\b", re.IGNORECASE)
SIMULATION_TITLE_HINTS = re.compile(r"\b(simulation|sh_|pythia|hzha|wphact|twogen|kk2f|babayaga)\b", re.IGNORECASE)
DOC_HINTS = re.compile(r"(guide|docs|documentation|about|docker|cvmfs|software|tutorial|how-to)", re.IGNORECASE)
EVENT_FILE_HINTS = re.compile(r"(dst|xdst|xsdst|fadana|event|events|hadron|hadronic|z0|lep|short|lolept|reco|reconstruction|data)", re.IGNORECASE)
SUPPORT_FILE_HINTS = re.compile(r"(dbcalb|dbgeom|dblepm|dbmisc|dbrunt|dbscon|dbsysf|calib|calibration|geometry|condition|database|detector|alignment)", re.IGNORECASE)
HIGH_VALUE_EXTENSIONS = {".root", ".h5", ".hdf5", ".parquet", ".dst", ".xdst", ".xsdst", ".fadana", ".al"}
DATA_EXTENSIONS = HIGH_VALUE_EXTENSIONS | {".dat", ".zip", ".tar", ".gz", ".tgz", ".tar.gz", ".json", ".txt"}


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def locate_paths() -> dict[str, pathlib.Path]:
    script_path = pathlib.Path(__file__).resolve()
    strong_root = script_path.parents[3]
    return {
        "references_03": strong_root / "data" / "raw" / "references" / RAW_BATCH,
        "search_pages": strong_root / "data" / "raw" / "source_tables" / RAW_BATCH / "cern_record_search_pages",
        "shortlist": strong_root / "data" / "raw" / "references" / RAW_BATCH / "strong_interaction_cern_delphi_record_candidates_shortlist_raw_003.csv",
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


def file_extension(name_or_url: str) -> str:
    path = urllib.parse.urlparse(str(name_or_url)).path.lower()
    name = pathlib.PurePosixPath(path).name
    if name.endswith(".tar.gz"):
        return ".tar.gz"
    return pathlib.PurePosixPath(name).suffix.lower()


def normalize_url(value: str) -> str:
    value = str(value).strip().rstrip(".,;:)]}\"'")
    if value.startswith("http://") or value.startswith("https://"):
        return value
    if value.startswith("/"):
        return BASE_URL + value
    return value


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


def title_of(record: dict[str, Any]) -> str:
    meta = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    return str(meta.get("title") or record.get("title") or "")


def record_category(title: str) -> str:
    if COLLISION_TITLE_HINTS.search(title):
        return "collision_data"
    if SIMULATION_TITLE_HINTS.search(title):
        return "simulation_data"
    if DOC_HINTS.search(title):
        return "documentation_or_software"
    return "other_record"


def find_file_dicts(obj: Any, path: str = "json") -> list[tuple[str, dict[str, Any]]]:
    out: list[tuple[str, dict[str, Any]]] = []
    if isinstance(obj, dict):
        keys = {str(k).lower() for k in obj.keys()}
        if keys & {"uri", "url", "key", "filename", "size", "checksum", "links", "download", "bucket"}:
            # require at least one file-looking field to avoid every metadata dict.
            if keys & {"uri", "url", "key", "filename", "download"}:
                out.append((path, obj))
        for k, v in obj.items():
            out.extend(find_file_dicts(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(find_file_dicts(v, f"{path}[{i}]"))
    return out


def extract_candidate_url(fd: dict[str, Any]) -> str:
    # Prefer direct download links, then uri/url, then CERN API file UUID if present.
    links = fd.get("links") if isinstance(fd.get("links"), dict) else {}
    for key in ("download", "self", "uri"):
        if links.get(key):
            return normalize_url(str(links[key]))
    for key in ("download", "uri", "url", "self"):
        if fd.get(key):
            return normalize_url(str(fd[key]))
    # CERN file API often exposes id/uuid/key without an explicit URL.
    for key in ("id", "uuid", "key"):
        value = str(fd.get(key) or "")
        if re.fullmatch(r"[0-9a-fA-F-]{32,40}", value):
            return f"{BASE_URL}/api/files/{value}"
    return ""


def extract_filename(fd: dict[str, Any], candidate_url: str) -> str:
    for key in ("filename", "key", "name"):
        if fd.get(key):
            return pathlib.PurePosixPath(str(fd[key])).name
    return pathlib.PurePosixPath(urllib.parse.urlparse(candidate_url).path).name


def extract_size(fd: dict[str, Any]) -> str:
    for key in ("size", "filesize", "content_length"):
        if fd.get(key) is not None:
            return str(fd[key])
    return ""


def score_file(record: dict[str, Any], file_path: str, fd: dict[str, Any]) -> dict[str, Any]:
    recid = get_record_id(record)
    title = title_of(record)
    category = record_category(title)
    candidate_url = extract_candidate_url(fd)
    filename = extract_filename(fd, candidate_url)
    ext = file_extension(filename or candidate_url)
    size = extract_size(fd)
    context = json.dumps(fd, ensure_ascii=False)[:1200]
    combined = f"{title} {filename} {candidate_url} {context}"

    score = 0
    reasons = []
    if category == "collision_data":
        score += 8
        reasons.append("collision_record")
    elif category == "simulation_data":
        score += 2
        reasons.append("simulation_record")
    elif category == "documentation_or_software":
        score -= 6
        reasons.append("documentation_record")

    if ext in HIGH_VALUE_EXTENSIONS:
        score += 7
        reasons.append("high_value_event_extension")
    elif ext in DATA_EXTENSIONS:
        score += 3
        reasons.append("data_extension")
    elif not ext:
        score += 1
        reasons.append("extensionless_endpoint")
    else:
        score -= 2
        reasons.append("non_data_extension")

    if EVENT_FILE_HINTS.search(combined):
        score += 4
        reasons.append("event_file_hint")
    if SUPPORT_FILE_HINTS.search(combined):
        score -= 4
        reasons.append("support_file_hint")
    if candidate_url:
        score += 2
        reasons.append("download_or_file_url_present")
    if size:
        try:
            s = int(float(size))
            if s > 5_000_000:
                score += 3
                reasons.append("large_file_size_metadata")
            elif s <= 2:
                score -= 3
                reasons.append("placeholder_size_metadata")
        except Exception:
            pass

    if score >= 14 and category == "collision_data":
        decision = "shortlist_collision_file_download"
    elif score >= 10:
        decision = "review_file_candidate"
    else:
        decision = "reject_file_candidate"

    return {
        "file_candidate_id": f"CERN_DELPHI_FILE_{recid}_{abs(hash((file_path, candidate_url, filename))) % 10**10}",
        "recid": recid,
        "record_title": title,
        "record_category": category,
        "file_json_path": file_path,
        "filename": filename,
        "candidate_url": candidate_url,
        "file_extension": ext,
        "size_metadata": size,
        "score": score,
        "decision": decision,
        "reasons": ";".join(reasons),
        "file_context_preview": context,
        "created_utc": utc_now(),
    }


def main() -> int:
    paths = locate_paths()
    shortlist_rows = read_csv(paths["shortlist"])
    if not shortlist_rows:
        print(f"[ERROR] record shortlist missing or empty: {paths['shortlist']}")
        return 1
    allowed_recids = {str(r.get("recid", "")) for r in shortlist_rows if str(r.get("recid", ""))}

    all_records: dict[str, dict[str, Any]] = {}
    for page in sorted(paths["search_pages"].glob("*.json")):
        try:
            obj = json.loads(page.read_text(encoding="utf-8"))
        except Exception:
            continue
        for record in iter_records_from_json(obj):
            recid = get_record_id(record)
            if recid in allowed_recids and recid not in all_records:
                all_records[recid] = record

    candidates: list[dict[str, Any]] = []
    for recid, record in all_records.items():
        for path, fd in find_file_dicts(record):
            candidates.append(score_file(record, path, fd))

    # Deduplicate by recid + candidate_url + filename.
    best: dict[tuple[str, str, str], dict[str, Any]] = {}
    for cand in candidates:
        key = (cand["recid"], cand["candidate_url"], cand["filename"])
        if key not in best or int(cand["score"]) > int(best[key]["score"]):
            best[key] = cand
    deduped = sorted(best.values(), key=lambda r: (-int(r["score"]), r["recid"], r["filename"]))
    collision_shortlist = [r for r in deduped if r["decision"] == "shortlist_collision_file_download"]
    rejected = [r for r in deduped if r["decision"] != "shortlist_collision_file_download"]

    refs = paths["references_03"]
    all_path = refs / "strong_interaction_cern_delphi_record_file_candidates_raw_003.csv"
    short_path = refs / "strong_interaction_cern_delphi_record_file_candidates_collision_shortlist_raw_003.csv"
    reject_path = refs / "strong_interaction_cern_delphi_record_file_candidates_rejected_raw_003.csv"
    fieldnames = [
        "file_candidate_id", "recid", "record_title", "record_category", "file_json_path", "filename", "candidate_url",
        "file_extension", "size_metadata", "score", "decision", "reasons", "file_context_preview", "created_utc"
    ]
    write_csv(all_path, deduped, fieldnames)
    write_csv(short_path, collision_shortlist, fieldnames)
    write_csv(reject_path, rejected, fieldnames)

    category_counts = Counter(r["record_category"] for r in deduped)
    decision_counts = Counter(r["decision"] for r in deduped)
    ext_counts = Counter(r["file_extension"] or "[no_extension]" for r in deduped)
    summary_path = refs / "strong_interaction_cern_delphi_record_file_candidates_summary_raw_003.txt"
    summary_path.write_text(
        "Strong_interaction CERN DELPHI record file candidate summary\n"
        "============================================================\n"
        f"Generated UTC: {utc_now()}\n"
        f"Script version: {SCRIPT_VERSION}\n\n"
        f"Record shortlist rows read: {len(shortlist_rows)}\n"
        f"Records found in saved search pages: {len(all_records)}\n"
        f"Unique file candidates: {len(deduped)}\n"
        f"Collision file download shortlist: {len(collision_shortlist)}\n"
        f"Rejected/review file candidates: {len(rejected)}\n\n"
        "Record category counts:\n" + "\n".join(f"- {k}: {v}" for k, v in category_counts.most_common()) + "\n\n"
        "Decision counts:\n" + "\n".join(f"- {k}: {v}" for k, v in decision_counts.most_common()) + "\n\n"
        "Top extension counts:\n" + "\n".join(f"- {k}: {v}" for k, v in ext_counts.most_common(20)) + "\n\n"
        "Interpretation:\n"
        "- Collision shortlist is the first priority for controlled raw download.\n"
        "- Simulation records are preserved but not prioritized for the first 10000+ real-data benchmark.\n"
        "- Do not download the full file list at once; use --limit in the next downloader.\n"
        f"All file candidates: {all_path}\n"
        f"Collision shortlist: {short_path}\n",
        encoding="utf-8",
    )

    print(f"[OK] all file candidates: {all_path}")
    print(f"[OK] collision shortlist: {short_path}")
    print(f"[OK] rejected: {reject_path}")
    print(f"[OK] summary: {summary_path}")
    print(f"[DONE] records={len(all_records)} file_candidates={len(deduped)} collision_shortlist={len(collision_shortlist)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
