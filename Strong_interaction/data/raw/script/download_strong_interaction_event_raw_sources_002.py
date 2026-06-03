#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_strong_interaction_event_raw_sources_002.py

Event-level raw-data discovery and download pipeline for the Strong_interaction
benchmark workflow in the Dimensional-Structural Describability project.

Author: Kwon Dominicus

Purpose
-------
This script tries to find and download event-level or analysis-output raw data
suitable for a 10,000+ event benchmark, prioritizing a single-paper DELPHI open
Data route associated with arXiv:2510.18762.

Placement:
    Strong_interaction/data/raw/script/

Inputs inspected:
    Strong_interaction/data/raw/source_tables/01/extracted_candidates/
    Strong_interaction/data/raw/references/01/
    public discovery endpoints, including CERN Open Data, INSPIRE, Zenodo, and GitHub search APIs

Outputs:
    Strong_interaction/data/raw/source_tables/02/
    Strong_interaction/data/raw/references/02/

Important status
----------------
This script is intentionally conservative. It does not treat arXiv abstract HTML,
search-result pages, or ordinary figures as event-level raw data. It first builds
a candidate registry. It downloads only candidates that look like real data files
(ROOT/HDF5/Parquet/CSV/JSON/YAML/YODA/NPZ/Numpy, tar/zip archives containing those),
and it labels whether a 10,000+ event count was verified from metadata.

If no verified event-level candidate is found, the script still writes discovery
manifests for audit and manual continuation.
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from typing import Any, Iterable, Optional


SCRIPT_VERSION = "002"
RAW_BATCH = "02"
USER_AGENT = (
    "Dimensional-Structural-Describability/Strong_interaction event raw downloader "
    "(Kwon Dominicus; 10000-event benchmark search)"
)
TIMEOUT_SECONDS = 120
SLEEP_SECONDS = 1.0
MAX_SIZE_MB_DEFAULT = 2000
MIN_EVENT_COUNT_DEFAULT = 10000

DATA_EXTENSIONS = {
    ".root", ".h5", ".hdf5", ".parquet", ".csv", ".tsv", ".json", ".jsonl",
    ".yaml", ".yml", ".yoda", ".npz", ".npy", ".dat", ".txt", ".zip", ".tar", ".gz", ".tgz"
}

EVENT_KEYWORDS = re.compile(
    r"(delphi|open\s*data|cern\s*open\s*data|event|events|root|ntupl|tuple|edm|aod|e\+e-|91\.2|z0|z\s*pole|hadron|thrust|energy[- ]energy|eec|track|particle|parquet|hdf5|h5|jsonl)",
    re.IGNORECASE,
)

URL_PATTERN = re.compile(r"https?://[^\s\)\]\}\>'\"\\]+", re.IGNORECASE)
EVENT_COUNT_PATTERN = re.compile(r"(?P<num>\d{1,3}(?:[, ]\d{3})+|\d{4,})(?:\s*)(?P<label>events?|entries|collisions|hadronic\s+events|selected\s+events)", re.IGNORECASE)


@dataclass
class Candidate:
    candidate_id: str
    source_id: str
    discovery_source: str
    source_url: str
    data_url: str
    candidate_kind: str
    file_extension: str
    title_or_context: str
    expected_data_kind: str
    detected_event_count: str
    event_count_verified: bool
    min_event_count_required: int
    download_selected: bool
    reason: str
    notes: str


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def locate_paths() -> dict[str, pathlib.Path]:
    script_path = pathlib.Path(__file__).resolve()
    strong_root = script_path.parents[3]
    return {
        "strong_root": strong_root,
        "source_tables_01": strong_root / "data" / "raw" / "source_tables" / "01",
        "extracted_candidates_01": strong_root / "data" / "raw" / "source_tables" / "01" / "extracted_candidates",
        "references_01": strong_root / "data" / "raw" / "references" / "01",
        "source_tables_02": strong_root / "data" / "raw" / "source_tables" / RAW_BATCH,
        "references_02": strong_root / "data" / "raw" / "references" / RAW_BATCH,
        "downloaded_events_02": strong_root / "data" / "raw" / "source_tables" / RAW_BATCH / "event_raw_candidates",
        "discovery_pages_02": strong_root / "data" / "raw" / "source_tables" / RAW_BATCH / "discovery_pages",
    }


def write_csv(path: pathlib.Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def decode_text(data: bytes) -> str:
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def safe_filename(value: str, default: str = "downloaded_raw_data") -> str:
    value = pathlib.PurePosixPath(urllib.parse.urlparse(value).path).name or value
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    return value[:180] or default


def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def file_extension_from_url(url: str) -> str:
    name = pathlib.PurePosixPath(urllib.parse.urlparse(url).path).name.lower()
    if name.endswith(".tar.gz"):
        return ".tar.gz"
    if name.endswith(".yoda.h5"):
        return ".yoda.h5"
    return pathlib.PurePosixPath(name).suffix.lower()


def infer_kind(url: str, context: str) -> str:
    ext = file_extension_from_url(url)
    lowered = f"{url} {context}".lower()
    if ext == ".root" or "root" in lowered:
        return "event_level_root_or_root_candidate"
    if ext in {".h5", ".hdf5", ".yoda.h5"}:
        return "hdf5_or_yoda_hdf5_candidate"
    if ext == ".parquet":
        return "event_level_parquet_candidate"
    if ext in {".jsonl", ".npz", ".npy"}:
        return "event_level_array_candidate"
    if ext in {".csv", ".tsv", ".json", ".yaml", ".yml", ".dat", ".txt"}:
        return "numeric_table_or_analysis_output_candidate"
    if ext in {".zip", ".tar", ".gz", ".tgz", ".tar.gz"}:
        return "compressed_data_archive_candidate"
    return "unknown_or_page_candidate"


def extract_event_count(text: str) -> tuple[str, bool]:
    counts = []
    for m in EVENT_COUNT_PATTERN.finditer(text):
        raw = m.group("num")
        try:
            n = int(re.sub(r"[,\s]", "", raw))
            counts.append(n)
        except ValueError:
            continue
    if not counts:
        return "", False
    return str(max(counts)), True


def safe_request(url: str, accept: Optional[str] = None, max_size_mb: Optional[int] = None) -> tuple[bool, bytes | None, str, int | str, dict[str, str]]:
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    response_headers: dict[str, str] = {}
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as res:
            status = getattr(res, "status", "")
            response_headers = {k: v for k, v in res.headers.items()}
            content_length = res.headers.get("Content-Length")
            if max_size_mb is not None and content_length:
                size_mb = int(content_length) / (1024 * 1024)
                if size_mb > max_size_mb:
                    return False, None, f"blocked_by_size_limit:{size_mb:.2f}MB>{max_size_mb}MB", status, response_headers
            if max_size_mb is None:
                data = res.read()
            else:
                data = res.read(max_size_mb * 1024 * 1024 + 1)
                if len(data) > max_size_mb * 1024 * 1024:
                    return False, None, f"blocked_by_size_limit_after_read:>{max_size_mb}MB", status, response_headers
            return True, data, "", status, response_headers
    except urllib.error.HTTPError as exc:
        return False, None, f"HTTPError {exc.code}: {exc.reason}", exc.code, response_headers
    except urllib.error.URLError as exc:
        return False, None, f"URLError: {exc.reason}", "", response_headers
    except Exception as exc:
        return False, None, f"{type(exc).__name__}: {exc}", "", response_headers


def scan_existing_extracted_candidates(paths: dict[str, pathlib.Path], min_event_count: int) -> list[Candidate]:
    candidates: list[Candidate] = []
    root = paths["extracted_candidates_01"]
    if not root.exists():
        return candidates
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix not in {".tex", ".txt", ".md", ".bib", ".bbl", ".json", ".yaml", ".yml", ".csv", ".dat"}:
            continue
        try:
            data = path.read_bytes()[:5_000_000]
        except Exception:
            continue
        text = decode_text(data)
        if not EVENT_KEYWORDS.search(text):
            continue
        count, count_ok = extract_event_count(text)
        urls = sorted(set(URL_PATTERN.findall(text)))
        for idx, url in enumerate(urls, start=1):
            ext = file_extension_from_url(url)
            kind = infer_kind(url, text[:1000])
            looks_data = ext in DATA_EXTENSIONS or any(token in url.lower() for token in ("download", "files", "record", "root", "parquet", "hdf5", "h5", "json", "csv"))
            if not looks_data:
                continue
            event_count_verified = count_ok and int(count) >= min_event_count if count else False
            candidates.append(Candidate(
                candidate_id=f"EXTRACTED01_{safe_filename(path.name)}_{idx:03d}",
                source_id="DELPHI_OPEN_DATA_THRUST_EEC_NOTE_2025" if "DELPHI_2025" in str(path) else "UNKNOWN_FROM_EXTRACTED_SOURCE",
                discovery_source=str(path),
                source_url=str(path),
                data_url=url,
                candidate_kind="url_found_in_extracted_candidate",
                file_extension=ext,
                title_or_context=text[:500].replace("\n", " "),
                expected_data_kind=kind,
                detected_event_count=count,
                event_count_verified=event_count_verified,
                min_event_count_required=min_event_count,
                download_selected=event_count_verified,
                reason="selected_if_event_count_verified_from_context",
                notes="URL found inside arXiv source extracted candidate; review before numerical use.",
            ))
    return candidates


def discovery_queries() -> list[tuple[str, str, str]]:
    """Return (discovery_id, url, accept_header)."""
    queries = [
        ("cern_opendata_api_delphi", "https://opendata.cern.ch/api/records/?q=DELPHI&size=50", "application/json"),
        ("cern_opendata_api_delphi_open_data", "https://opendata.cern.ch/api/records/?q=DELPHI%20open%20data&size=50", "application/json"),
        ("cern_opendata_api_delphi_thrust", "https://opendata.cern.ch/api/records/?q=DELPHI%20thrust&size=50", "application/json"),
        ("cern_opendata_search_delphi", "https://opendata.cern.ch/search?q=DELPHI&l=list&p=1&s=50", "text/html,application/json,*/*"),
        ("inspire_delphi_2510", "https://inspirehep.net/api/literature?q=arxiv:2510.18762&size=1", "application/json"),
        ("zenodo_delphi_2510", "https://zenodo.org/api/records?q=2510.18762%20DELPHI&size=25", "application/json"),
        ("zenodo_delphi_open_data", "https://zenodo.org/api/records?q=DELPHI%20open%20data%20thrust%20EEC&size=25", "application/json"),
        ("github_code_search_hint", "https://api.github.com/search/repositories?q=DELPHI+open+data+thrust+EEC", "application/json"),
    ]
    return queries


def flatten_json_for_urls(obj: Any, context_prefix: str = "") -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            key_ctx = f"{context_prefix}.{k}" if context_prefix else str(k)
            if isinstance(v, str):
                for url in URL_PATTERN.findall(v):
                    out.append((url, key_ctx + " " + v[:500]))
                # Invenio-style file keys may be relative URLs or links in file metadata.
                if k.lower() in {"uri", "url", "self", "download", "html", "bucket", "links"} and v.startswith("/"):
                    out.append(("https://opendata.cern.ch" + v, key_ctx))
            else:
                out.extend(flatten_json_for_urls(v, key_ctx))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(flatten_json_for_urls(v, f"{context_prefix}[{i}]"))
    return out


def candidates_from_discovery_page(discovery_id: str, url: str, data: bytes, min_event_count: int) -> list[Candidate]:
    text = decode_text(data)
    candidates: list[Candidate] = []
    contexts: list[tuple[str, str]] = []
    try:
        obj = json.loads(text)
        contexts.extend(flatten_json_for_urls(obj, discovery_id))
        # Also keep JSON string for event count extraction.
        text_for_count = json.dumps(obj, ensure_ascii=False)[:1_000_000]
    except Exception:
        contexts.extend((u, text[max(0, text.find(u)-300): text.find(u)+800]) for u in sorted(set(URL_PATTERN.findall(text))))
        text_for_count = text[:1_000_000]
    global_count, global_count_ok = extract_event_count(text_for_count)

    seen = set()
    for idx, (candidate_url, context) in enumerate(contexts, start=1):
        if candidate_url in seen:
            continue
        seen.add(candidate_url)
        lowered = f"{candidate_url} {context}".lower()
        ext = file_extension_from_url(candidate_url)
        is_data_like = ext in DATA_EXTENSIONS or any(token in lowered for token in ["/files/", "download", "root", "parquet", "hdf5", "h5", "jsonl", "opendata", "cern"])
        is_relevant = bool(EVENT_KEYWORDS.search(lowered)) or "delphi" in lowered
        if not (is_data_like and is_relevant):
            continue
        local_count, local_count_ok = extract_event_count(context)
        count = local_count or global_count
        count_ok = (local_count_ok or global_count_ok) and bool(count) and int(count) >= min_event_count
        candidates.append(Candidate(
            candidate_id=f"{discovery_id.upper()}_{idx:03d}",
            source_id="DELPHI_OPEN_DATA_THRUST_EEC_NOTE_2025" if "delphi" in lowered else "PUBLIC_DISCOVERY_ENDPOINT",
            discovery_source=discovery_id,
            source_url=url,
            data_url=candidate_url,
            candidate_kind="public_endpoint_candidate",
            file_extension=ext,
            title_or_context=context[:500].replace("\n", " "),
            expected_data_kind=infer_kind(candidate_url, context),
            detected_event_count=count,
            event_count_verified=count_ok,
            min_event_count_required=min_event_count,
            download_selected=count_ok,
            reason="selected_if_event_count_verified_from_endpoint_context",
            notes="Candidate discovered through public endpoint; verify license and content before numerical use.",
        ))
    return candidates


def run_discovery(paths: dict[str, pathlib.Path], min_event_count: int) -> tuple[list[Candidate], list[dict[str, Any]]]:
    candidates: list[Candidate] = []
    manifest_rows: list[dict[str, Any]] = []
    paths["discovery_pages_02"].mkdir(parents=True, exist_ok=True)
    for discovery_id, url, accept in discovery_queries():
        started = utc_now()
        ok, data, error, status, headers = safe_request(url, accept=accept, max_size_mb=50)
        output_file = ""
        candidate_count = 0
        if ok and data is not None:
            output_path = paths["discovery_pages_02"] / f"{discovery_id}_raw_{SCRIPT_VERSION}.dat"
            output_path.write_bytes(data)
            output_file = str(output_path)
            page_candidates = candidates_from_discovery_page(discovery_id, url, data, min_event_count)
            candidates.extend(page_candidates)
            candidate_count = len(page_candidates)
        manifest_rows.append({
            "discovery_id": discovery_id,
            "url": url,
            "success": ok,
            "http_status": status,
            "output_file": output_file,
            "candidate_count": candidate_count,
            "error": error,
            "started_utc": started,
            "finished_utc": utc_now(),
        })
        time.sleep(SLEEP_SECONDS)
    return candidates, manifest_rows


def accept_for_url(url: str) -> str:
    ext = file_extension_from_url(url)
    if ext in {".csv", ".tsv", ".txt", ".dat"}:
        return "text/csv,text/plain,application/octet-stream,*/*"
    if ext in {".json", ".jsonl"}:
        return "application/json,text/plain,application/octet-stream,*/*"
    if ext in {".yaml", ".yml"}:
        return "application/x-yaml,text/yaml,text/plain,*/*"
    return "application/octet-stream,*/*"


def download_candidates(paths: dict[str, pathlib.Path], candidates: list[Candidate], args: argparse.Namespace) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    paths["downloaded_events_02"].mkdir(parents=True, exist_ok=True)
    for cand in candidates:
        should_download = cand.download_selected or args.download_unverified
        started = utc_now()
        if not should_download:
            rows.append({
                "candidate_id": cand.candidate_id,
                "data_url": cand.data_url,
                "download_attempted": False,
                "success": False,
                "download_status": "not_selected_not_verified_10000_events",
                "event_count_verified": cand.event_count_verified,
                "detected_event_count": cand.detected_event_count,
                "output_file": "",
                "http_status": "",
                "size_bytes": 0,
                "sha256": "",
                "error": "",
                "started_utc": started,
                "finished_utc": utc_now(),
            })
            continue
        filename = safe_filename(cand.data_url, default=f"{cand.candidate_id}_raw_{SCRIPT_VERSION}.dat")
        output_path = paths["downloaded_events_02"] / f"{cand.candidate_id}__{filename}"
        ok, data, error, status, headers = safe_request(cand.data_url, accept=accept_for_url(cand.data_url), max_size_mb=args.max_size_mb)
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
        rows.append({
            "candidate_id": cand.candidate_id,
            "data_url": cand.data_url,
            "download_attempted": True,
            "success": ok,
            "download_status": download_status,
            "event_count_verified": cand.event_count_verified,
            "detected_event_count": cand.detected_event_count,
            "output_file": output_file,
            "http_status": status,
            "size_bytes": size,
            "sha256": digest,
            "error": error,
            "started_utc": started,
            "finished_utc": utc_now(),
        })
        time.sleep(SLEEP_SECONDS)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover and download event-level raw candidates for Strong_interaction benchmark.")
    parser.add_argument("--min-event-count", type=int, default=MIN_EVENT_COUNT_DEFAULT, help="Minimum verified event count required for automatic download. Default: 10000.")
    parser.add_argument("--max-size-mb", type=int, default=MAX_SIZE_MB_DEFAULT, help="Maximum file size per download. Default: 2000 MB.")
    parser.add_argument("--download-unverified", action="store_true", help="Download candidates even if 10000+ event count is not verified. Use with caution.")
    args = parser.parse_args()

    paths = locate_paths()
    for key in ("source_tables_02", "references_02", "downloaded_events_02", "discovery_pages_02"):
        paths[key].mkdir(parents=True, exist_ok=True)

    print(f"[INFO] source_tables_02: {paths['source_tables_02']}")
    print(f"[INFO] references_02: {paths['references_02']}")
    print(f"[INFO] min_event_count: {args.min_event_count}")

    extracted_candidates = scan_existing_extracted_candidates(paths, args.min_event_count)
    endpoint_candidates, discovery_manifest = run_discovery(paths, args.min_event_count)
    all_candidates = extracted_candidates + endpoint_candidates

    # Deduplicate by data_url while preserving first occurrence.
    deduped: list[Candidate] = []
    seen_urls = set()
    for cand in all_candidates:
        if cand.data_url in seen_urls:
            continue
        seen_urls.add(cand.data_url)
        deduped.append(cand)

    candidate_registry_path = paths["references_02"] / f"strong_interaction_event_raw_candidate_registry_raw_{SCRIPT_VERSION}.csv"
    write_csv(candidate_registry_path, [asdict(c) | {"created_utc": utc_now()} for c in deduped], [
        "candidate_id", "source_id", "discovery_source", "source_url", "data_url", "candidate_kind",
        "file_extension", "title_or_context", "expected_data_kind", "detected_event_count",
        "event_count_verified", "min_event_count_required", "download_selected", "reason", "notes", "created_utc"
    ])

    discovery_manifest_path = paths["references_02"] / f"strong_interaction_event_raw_discovery_manifest_raw_{SCRIPT_VERSION}.csv"
    write_csv(discovery_manifest_path, discovery_manifest, [
        "discovery_id", "url", "success", "http_status", "output_file", "candidate_count", "error", "started_utc", "finished_utc"
    ])

    download_manifest = download_candidates(paths, deduped, args)
    download_manifest_path = paths["references_02"] / f"strong_interaction_event_raw_download_manifest_raw_{SCRIPT_VERSION}.csv"
    write_csv(download_manifest_path, download_manifest, [
        "candidate_id", "data_url", "download_attempted", "success", "download_status", "event_count_verified",
        "detected_event_count", "output_file", "http_status", "size_bytes", "sha256", "error", "started_utc", "finished_utc"
    ])

    selected_count = sum(1 for c in deduped if c.download_selected)
    attempted_count = sum(1 for r in download_manifest if r.get("download_attempted") is True)
    success_count = sum(1 for r in download_manifest if r.get("success") is True)
    total_bytes = sum(int(r.get("size_bytes") or 0) for r in download_manifest)

    summary_path = paths["references_02"] / f"strong_interaction_event_raw_summary_raw_{SCRIPT_VERSION}.txt"
    summary_path.write_text(
        "Strong_interaction event-level raw discovery/download summary\n"
        "==========================================================\n"
        f"Generated UTC: {utc_now()}\n"
        f"Script version: {SCRIPT_VERSION}\n\n"
        f"Candidate URLs discovered: {len(deduped)}\n"
        f"Candidates with verified >= {args.min_event_count} events: {selected_count}\n"
        f"Download attempted: {attempted_count}\n"
        f"Downloaded successfully: {success_count}\n"
        f"Total downloaded bytes: {total_bytes}\n\n"
        "Interpretation:\n"
        "- Successful downloads in source_tables/02 are raw event/data candidates, not final numerical input.\n"
        "- If no candidate has verified 10000+ event count, inspect the candidate registry manually or rerun with --download-unverified only for reviewed URLs.\n"
        "- A later cleaner must inspect file structure and event counts before cleaned_tables/input promotion.\n\n"
        f"Candidate registry: {candidate_registry_path}\n"
        f"Discovery manifest: {discovery_manifest_path}\n"
        f"Download manifest: {download_manifest_path}\n"
        f"Downloaded data directory: {paths['downloaded_events_02']}\n",
        encoding="utf-8",
    )

    print(f"[OK] candidate registry: {candidate_registry_path}")
    print(f"[OK] discovery manifest: {discovery_manifest_path}")
    print(f"[OK] download manifest: {download_manifest_path}")
    print(f"[OK] summary: {summary_path}")
    print(f"[DONE] candidates={len(deduped)} verified_10000={selected_count} downloaded={success_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
