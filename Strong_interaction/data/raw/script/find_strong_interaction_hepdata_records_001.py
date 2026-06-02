#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
find_strong_interaction_hepdata_records_001.py

Strong_interaction HEPData record discovery script for the
Dimensional-Structural Describability validation pipeline.

Author: Kwon Dominicus

Purpose
-------
This script searches HEPData for numerical table records corresponding to the
strong-interaction benchmark candidates prepared in cleaned_tables/01.

It writes discovery outputs to:

    Strong_interaction/data/raw/references/
    Strong_interaction/data/raw/source_tables/

By default, the script DOES NOT download record-level CSV tables. It creates
auditable JSON search outputs and candidate manifests first. To try downloading
record-level CSV files for candidate records, pass:

    --download-record-csv

This is intentionally conservative because arXiv HTML provenance pages are not
numerical benchmark tables, and HEPData records must be selected before the
final data/derived/input stage.
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Iterable, Optional


SCRIPT_VERSION = "001"
USER_AGENT = (
    "Dimensional-Structural-Describability/Strong_interaction HEPData discovery "
    "(Kwon Dominicus; record candidate stage)"
)
TIMEOUT_SECONDS = 60
SLEEP_SECONDS = 1.0
MAX_RECORDS_PER_QUERY = 8


@dataclass(frozen=True)
class SearchSpec:
    search_id: str
    source_id: str
    query: str
    expected_role: str
    priority: int
    notes: str


SEARCH_SPECS: list[SearchSpec] = [
    SearchSpec(
        search_id="OPAL_2005_EVENT_SHAPE_91_209",
        source_id="OPAL_EVENT_SHAPES_91_209GEV_2005",
        query="Measurement of event shape distributions and moments in e+e- hadrons 91 209 GeV OPAL",
        expected_role="standard_event_shape_distribution_reference",
        priority=1,
        notes="Primary OPAL binned event-shape benchmark candidate.",
    ),
    SearchSpec(
        search_id="OPAL_2011_NNLO_EVENT_SHAPE_91_209",
        source_id="OPAL_EVENT_SHAPES_NNLO_2011",
        query="Determination of alphaS using OPAL hadronic event shapes 91 209 GeV NNLO",
        expected_role="standard_qcd_running_and_event_shape_crosscheck_reference",
        priority=2,
        notes="OPAL NNLO/NNLO+NLLA event-shape cross-check candidate.",
    ),
    SearchSpec(
        search_id="JADE_1997_EVENT_SHAPE_22_44",
        source_id="JADE_EVENT_SHAPES_22_44GEV",
        query="JADE event shapes alpha_s e+e- annihilations 22 44 GeV thrust heavy jet mass broadening Durham",
        expected_role="lower_energy_event_shape_scale_extension_reference",
        priority=3,
        notes="Lower-energy e+e- event-shape scale-extension candidate.",
    ),
    SearchSpec(
        search_id="L3_FLAVOUR_EVENT_SHAPE_197",
        source_id="L3_FLAVOUR_TAGGED_EVENT_SHAPE_197GEV",
        query="L3 flavour tagged hadronic event shape e+e- annihilation 197 GeV",
        expected_role="flavour_dependent_event_shape_extension_reference",
        priority=4,
        notes="Flavour-tagged light/heavy event-shape extension candidate.",
    ),
    SearchSpec(
        search_id="DELPHI_OPEN_DATA_THRUST_EEC_91_2",
        source_id="DELPHI_OPEN_DATA_THRUST_EEC_NOTE_2025",
        query="DELPHI open data thrust track energy energy correlator 91.2 GeV",
        expected_role="primary_event_level_benchmark_candidate_reference",
        priority=5,
        notes="DELPHI open-data event-level or analysis output candidate; may not be in HEPData.",
    ),
]


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def locate_paths() -> tuple[pathlib.Path, pathlib.Path, pathlib.Path, pathlib.Path]:
    script_path = pathlib.Path(__file__).resolve()
    # Expected: Strong_interaction/data/raw/script/<script>.py
    strong_root = script_path.parents[3]
    raw_root = strong_root / "data" / "raw"
    references_dir = raw_root / "references"
    source_tables_dir = raw_root / "source_tables"
    references_dir.mkdir(parents=True, exist_ok=True)
    source_tables_dir.mkdir(parents=True, exist_ok=True)
    return strong_root, raw_root, references_dir, source_tables_dir


def write_csv(path: pathlib.Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def safe_request(url: str, accept: Optional[str] = None) -> tuple[bool, bytes | None, str, int | str]:
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status = getattr(response, "status", "")
            return True, response.read(), "", status
    except urllib.error.HTTPError as exc:
        return False, None, f"HTTPError {exc.code}: {exc.reason}", exc.code
    except urllib.error.URLError as exc:
        return False, None, f"URLError: {exc.reason}", ""
    except Exception as exc:
        return False, None, f"{type(exc).__name__}: {exc}", ""


def sanitize_filename(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")
    return value[:160] if len(value) > 160 else value


def hepdata_search_url(query: str, page: int = 1, size: int = 25) -> str:
    params = urllib.parse.urlencode({"q": query, "page": page, "size": size, "format": "json"})
    return f"https://www.hepdata.net/search/?{params}"


def extract_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in ("results", "hits", "records", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict)]
        # Some HEPData JSON views are dicts with nested search results.
        if isinstance(payload.get("results"), dict):
            inner = payload["results"].get("results")
            if isinstance(inner, list):
                return [x for x in inner if isinstance(x, dict)]
    return []


def get_first(record: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        if key in record and record[key] not in (None, ""):
            return record[key]
    return ""


def record_url_from_candidate(record: dict[str, Any]) -> str:
    url = get_first(record, ["url", "record_url", "hepdata_url", "recid_url"])
    if isinstance(url, str) and url.startswith("http"):
        return url
    recid = get_first(record, ["recid", "id", "record_id"])
    if recid != "":
        return f"https://www.hepdata.net/record/{recid}"
    doi = get_first(record, ["doi", "data_doi"])
    if isinstance(doi, str) and doi:
        return f"https://www.hepdata.net/record/{doi}"
    return ""


def normalize_record(spec: SearchSpec, rank: int, record: dict[str, Any]) -> dict[str, Any]:
    title = get_first(record, ["title", "name"])
    if isinstance(title, list):
        title = "; ".join(str(x) for x in title)
    collaboration = get_first(record, ["collaboration", "collaborations"])
    if isinstance(collaboration, list):
        collaboration = "; ".join(str(x) for x in collaboration)
    recid = get_first(record, ["recid", "id", "record_id"])
    doi = get_first(record, ["doi", "data_doi"])
    inspire_id = get_first(record, ["inspire_id", "inspire_record", "inspire"])
    record_url = record_url_from_candidate(record)
    json_url = f"{record_url}?format=json" if record_url else ""
    light_json_url = f"{record_url}?format=json&light=true" if record_url else ""
    csv_url = f"{record_url}?format=csv" if record_url else ""
    yaml_url = f"{record_url}?format=yaml" if record_url else ""

    return {
        "search_id": spec.search_id,
        "source_id": spec.source_id,
        "query": spec.query,
        "rank": rank,
        "priority": spec.priority,
        "expected_role": spec.expected_role,
        "title": title,
        "collaboration": collaboration,
        "recid": recid,
        "doi": doi,
        "inspire_id": inspire_id,
        "record_url": record_url,
        "json_url": json_url,
        "light_json_url": light_json_url,
        "record_csv_url": csv_url,
        "record_yaml_url": yaml_url,
        "selection_status": "candidate_unreviewed",
        "download_csv_by_default": False,
        "notes": spec.notes,
        "discovered_utc": utc_now(),
    }


def try_download(url: str, output_path: pathlib.Path, accept: Optional[str] = None) -> dict[str, Any]:
    started = utc_now()
    ok, data, error, status = safe_request(url, accept=accept)
    size = 0
    if ok and data is not None:
        output_path.write_bytes(data)
        size = len(data)
    return {
        "url": url,
        "output_file": str(output_path),
        "success": ok,
        "http_status": status,
        "size_bytes": size,
        "error": error,
        "started_utc": started,
        "finished_utc": utc_now(),
    }


def run(download_record_csv: bool) -> int:
    strong_root, raw_root, references_dir, source_tables_dir = locate_paths()
    print(f"[INFO] strong_root: {strong_root}")
    print(f"[INFO] references_dir: {references_dir}")
    print(f"[INFO] source_tables_dir: {source_tables_dir}")

    all_candidates: list[dict[str, Any]] = []
    download_manifest: list[dict[str, Any]] = []
    query_manifest: list[dict[str, Any]] = []

    for spec in SEARCH_SPECS:
        url = hepdata_search_url(spec.query)
        safe_id = sanitize_filename(spec.search_id.lower())
        search_output = source_tables_dir / f"hepdata_search_{safe_id}_raw_{SCRIPT_VERSION}.json"
        print(f"[INFO] search {spec.search_id}: {url}")
        started = utc_now()
        ok, data, error, status = safe_request(url, accept="application/json")
        record_count = 0
        if ok and data is not None:
            search_output.write_bytes(data)
            try:
                payload = json.loads(data.decode("utf-8", errors="replace"))
                records = extract_records(payload)
            except Exception as exc:
                payload = None
                records = []
                error = f"json_parse_error: {exc}"
            for rank, record in enumerate(records[:MAX_RECORDS_PER_QUERY], start=1):
                candidate = normalize_record(spec, rank, record)
                all_candidates.append(candidate)
                record_count += 1
                # Save light JSON metadata for each candidate if record_url is available.
                if candidate.get("light_json_url"):
                    out = source_tables_dir / f"hepdata_record_{sanitize_filename(str(candidate.get('recid') or candidate.get('rank')))}_{safe_id}_light_raw_{SCRIPT_VERSION}.json"
                    download_manifest.append(try_download(str(candidate["light_json_url"]), out, accept="application/json"))
                    time.sleep(SLEEP_SECONDS)
                if download_record_csv and candidate.get("record_csv_url"):
                    out = source_tables_dir / f"hepdata_record_{sanitize_filename(str(candidate.get('recid') or candidate.get('rank')))}_{safe_id}_record_csv_raw_{SCRIPT_VERSION}.csv"
                    download_manifest.append(try_download(str(candidate["record_csv_url"]), out, accept="text/csv, text/plain, */*"))
                    time.sleep(SLEEP_SECONDS)
        query_manifest.append({
            "search_id": spec.search_id,
            "source_id": spec.source_id,
            "query": spec.query,
            "search_url": url,
            "search_output_file": str(search_output),
            "success": ok,
            "http_status": status,
            "record_count_extracted": record_count,
            "error": error,
            "started_utc": started,
            "finished_utc": utc_now(),
        })
        time.sleep(SLEEP_SECONDS)

    candidates_path = references_dir / f"strong_interaction_hepdata_record_candidates_raw_{SCRIPT_VERSION}.csv"
    candidate_fields = [
        "search_id", "source_id", "query", "rank", "priority", "expected_role", "title",
        "collaboration", "recid", "doi", "inspire_id", "record_url", "json_url", "light_json_url",
        "record_csv_url", "record_yaml_url", "selection_status", "download_csv_by_default",
        "notes", "discovered_utc",
    ]
    write_csv(candidates_path, all_candidates, candidate_fields)

    query_manifest_path = references_dir / f"strong_interaction_hepdata_search_manifest_raw_{SCRIPT_VERSION}.csv"
    write_csv(query_manifest_path, query_manifest, [
        "search_id", "source_id", "query", "search_url", "search_output_file", "success",
        "http_status", "record_count_extracted", "error", "started_utc", "finished_utc",
    ])

    download_manifest_path = references_dir / f"strong_interaction_hepdata_download_manifest_raw_{SCRIPT_VERSION}.csv"
    write_csv(download_manifest_path, download_manifest, [
        "url", "output_file", "success", "http_status", "size_bytes", "error", "started_utc", "finished_utc",
    ])

    readme_path = references_dir / f"strong_interaction_hepdata_discovery_readme_raw_{SCRIPT_VERSION}.txt"
    readme_path.write_text(
        "Strong_interaction HEPData discovery stage\n"
        "==========================================\n"
        f"Generated UTC: {utc_now()}\n"
        f"Script version: {SCRIPT_VERSION}\n\n"
        "Purpose:\n"
        "- Search HEPData for OPAL/JADE/L3/DELPHI benchmark candidates.\n"
        "- Store JSON search outputs and candidate record manifests.\n"
        "- Default mode does not treat any record as final input.\n\n"
        "Outputs:\n"
        f"- {candidates_path}\n"
        f"- {query_manifest_path}\n"
        f"- {download_manifest_path}\n\n"
        "Next stage:\n"
        "- Review candidate records.\n"
        "- If candidate CSV files were downloaded, run the derived cleaner into cleaned_tables/02.\n"
        "- Final input must still be selected manually after row/column inspection.\n",
        encoding="utf-8",
    )

    print(f"[OK] candidates: {candidates_path}")
    print(f"[OK] query manifest: {query_manifest_path}")
    print(f"[OK] download manifest: {download_manifest_path}")
    print(f"[DONE] HEPData candidates discovered: {len(all_candidates)}")
    return 0 if all(q.get("success") for q in query_manifest) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Find HEPData records for Strong_interaction benchmark candidates.")
    parser.add_argument(
        "--download-record-csv",
        action="store_true",
        help="Try downloading record-level CSV files for candidate HEPData records. Default is discovery only.",
    )
    args = parser.parse_args()
    return run(download_record_csv=args.download_record_csv)


if __name__ == "__main__":
    sys.exit(main())
