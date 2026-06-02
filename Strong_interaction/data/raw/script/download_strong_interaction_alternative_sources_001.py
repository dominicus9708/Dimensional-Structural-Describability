#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_strong_interaction_alternative_sources_001.py

Alternative source acquisition script for the Strong_interaction benchmark
pipeline in the Dimensional-Structural Describability project.

Author: Kwon Dominicus

Purpose
-------
The previous HEPData JSON-search stage may fail with HTTP 403.  This script
therefore records and, where possible, downloads alternative source material:

1. INSPIRE-HEP API metadata by arXiv identifier.
2. arXiv e-print/source archives.
3. DOI, journal, INSPIRE, HEPData search, and Rivet/YODA manual follow-up URLs.

Outputs are written to:

    Strong_interaction/data/raw/references/
    Strong_interaction/data/raw/source_tables/

This is still a raw acquisition stage.  It does not create final input and does
not promote any HTML/metadata/source archive into benchmark numerical data.
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
from dataclasses import dataclass, asdict
from typing import Any, Iterable, Optional


SCRIPT_VERSION = "001"
USER_AGENT = (
    "Dimensional-Structural-Describability/Strong_interaction alternative sources "
    "(Kwon Dominicus; source registry stage)"
)
TIMEOUT_SECONDS = 60
SLEEP_SECONDS = 1.0


@dataclass(frozen=True)
class AlternativeSourceSpec:
    source_id: str
    arxiv_id: str
    normalized_arxiv_id: str
    title_short: str
    priority: int
    role: str
    doi: str
    journal_hint: str
    notes: str


SOURCES: list[AlternativeSourceSpec] = [
    AlternativeSourceSpec(
        source_id="OPAL_EVENT_SHAPES_91_209GEV_2005",
        arxiv_id="hep-ex/0503051",
        normalized_arxiv_id="hep-ex_0503051",
        title_short="opal_event_shapes_91_209gev_2005",
        priority=1,
        role="standard_event_shape_distribution_reference",
        doi="10.1140/epjc/s2005-02120-6",
        journal_hint="Eur.Phys.J.C40:287-316,2005",
        notes="Primary OPAL binned event-shape benchmark candidate. Need numerical tables from HEPData, journal supplement, or arXiv source if available.",
    ),
    AlternativeSourceSpec(
        source_id="OPAL_EVENT_SHAPES_NNLO_2011",
        arxiv_id="1101.1470",
        normalized_arxiv_id="1101_1470",
        title_short="opal_event_shapes_nnlo_91_209gev_2011",
        priority=2,
        role="standard_qcd_running_and_event_shape_crosscheck_reference",
        doi="10.1140/epjc/s10052-011-1733-z",
        journal_hint="Eur.Phys.J.C71:1733,2011",
        notes="OPAL NNLO/NNLO+NLLA cross-check candidate. May share underlying distributions with OPAL 2005.",
    ),
    AlternativeSourceSpec(
        source_id="JADE_EVENT_SHAPES_22_44GEV",
        arxiv_id="hep-ex/9708034",
        normalized_arxiv_id="hep-ex_9708034",
        title_short="jade_event_shapes_22_44gev_1997",
        priority=3,
        role="lower_energy_event_shape_scale_extension_reference",
        doi="10.1007/s100520050096",
        journal_hint="Eur.Phys.J.C1:461-478,1998",
        notes="Lower-energy PETRA/JADE event-shape extension. Need binned distributions or tables.",
    ),
    AlternativeSourceSpec(
        source_id="L3_FLAVOUR_TAGGED_EVENT_SHAPE_197GEV",
        arxiv_id="0907.2658",
        normalized_arxiv_id="0907_2658",
        title_short="l3_flavour_event_shape_197gev_2009",
        priority=4,
        role="flavour_dependent_event_shape_extension_reference",
        doi="10.1186/1754-0410-2-6",
        journal_hint="PMC Phys.A2:6,2008",
        notes="Flavour-tagged extension. Use after standard baseline is stable.",
    ),
    AlternativeSourceSpec(
        source_id="DELPHI_OPEN_DATA_THRUST_EEC_NOTE_2025",
        arxiv_id="2510.18762",
        normalized_arxiv_id="2510_18762",
        title_short="delphi_open_data_thrust_eec_91_2gev_2025",
        priority=5,
        role="primary_event_level_benchmark_candidate_reference",
        doi="10.48550/arXiv.2510.18762",
        journal_hint="arXiv analysis note",
        notes="Most relevant for 10000+ event benchmark. Need CERN Open Data record or analysis repository, not just arXiv abstract.",
    ),
]


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def locate_paths() -> tuple[pathlib.Path, pathlib.Path, pathlib.Path, pathlib.Path]:
    script_path = pathlib.Path(__file__).resolve()
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
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as res:
            return True, res.read(), "", getattr(res, "status", "")
    except urllib.error.HTTPError as exc:
        return False, None, f"HTTPError {exc.code}: {exc.reason}", exc.code
    except urllib.error.URLError as exc:
        return False, None, f"URLError: {exc.reason}", ""
    except Exception as exc:
        return False, None, f"{type(exc).__name__}: {exc}", ""


def sanitize_filename(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")
    return value[:180]


def inspire_api_url(arxiv_id: str) -> str:
    return "https://inspirehep.net/api/literature?" + urllib.parse.urlencode({"q": f"arxiv:{arxiv_id}", "size": 1})


def arxiv_abs_url(arxiv_id: str) -> str:
    return f"https://arxiv.org/abs/{arxiv_id}"


def arxiv_pdf_url(arxiv_id: str) -> str:
    return f"https://arxiv.org/pdf/{arxiv_id}"


def arxiv_eprint_url(arxiv_id: str) -> str:
    return f"https://arxiv.org/e-print/{arxiv_id}"


def arxiv_src_url(arxiv_id: str) -> str:
    return f"https://arxiv.org/src/{arxiv_id}"


def doi_url(doi: str) -> str:
    if not doi:
        return ""
    return f"https://doi.org/{doi}"


def inspire_literature_url(arxiv_id: str) -> str:
    return "https://inspirehep.net/literature?" + urllib.parse.urlencode({"sort": "mostrecent", "size": 25, "page": 1, "q": f"arxiv:{arxiv_id}"})


def hepdata_manual_search_url(spec: AlternativeSourceSpec) -> str:
    query = f"{spec.arxiv_id} {spec.title_short.replace('_', ' ')}"
    return "https://www.hepdata.net/search/?" + urllib.parse.urlencode({"q": query})


def rivet_manual_search_url(spec: AlternativeSourceSpec) -> str:
    query = f"Rivet {spec.title_short.replace('_', ' ')} {spec.arxiv_id}"
    return "https://www.google.com/search?" + urllib.parse.urlencode({"q": query})


def run(download_arxiv_source: bool, download_inspire: bool) -> int:
    strong_root, raw_root, references_dir, source_tables_dir = locate_paths()
    print(f"[INFO] strong_root: {strong_root}")
    print(f"[INFO] references_dir: {references_dir}")
    print(f"[INFO] source_tables_dir: {source_tables_dir}")

    manual_rows: list[dict[str, Any]] = []
    download_rows: list[dict[str, Any]] = []

    for spec in SOURCES:
        base = sanitize_filename(spec.title_short)
        manual_rows.append({
            "source_id": spec.source_id,
            "priority": spec.priority,
            "role": spec.role,
            "arxiv_id": spec.arxiv_id,
            "doi": spec.doi,
            "journal_hint": spec.journal_hint,
            "arxiv_abs_url": arxiv_abs_url(spec.arxiv_id),
            "arxiv_pdf_url": arxiv_pdf_url(spec.arxiv_id),
            "arxiv_eprint_url": arxiv_eprint_url(spec.arxiv_id),
            "arxiv_src_url": arxiv_src_url(spec.arxiv_id),
            "inspire_api_url": inspire_api_url(spec.arxiv_id),
            "inspire_manual_url": inspire_literature_url(spec.arxiv_id),
            "doi_url": doi_url(spec.doi),
            "hepdata_manual_search_url": hepdata_manual_search_url(spec),
            "rivet_manual_search_url": rivet_manual_search_url(spec),
            "current_status": "alternative_source_candidate_not_final_input",
            "notes": spec.notes,
            "created_utc": utc_now(),
        })

        if download_inspire:
            url = inspire_api_url(spec.arxiv_id)
            out = source_tables_dir / f"inspire_api_{base}_raw_{SCRIPT_VERSION}.json"
            started = utc_now()
            ok, data, error, status = safe_request(url, accept="application/json")
            if ok and data is not None:
                out.write_bytes(data)
            download_rows.append({
                "source_id": spec.source_id,
                "download_kind": "inspire_api_json",
                "url": url,
                "output_file": str(out),
                "success": ok,
                "http_status": status,
                "size_bytes": len(data) if data else 0,
                "error": error,
                "started_utc": started,
                "finished_utc": utc_now(),
            })
            time.sleep(SLEEP_SECONDS)

        if download_arxiv_source:
            # arXiv source archives may be TeX tarballs, raw TeX, or unavailable.
            for kind, url in (("arxiv_eprint_source", arxiv_eprint_url(spec.arxiv_id)),):
                out = source_tables_dir / f"{kind}_{base}_raw_{SCRIPT_VERSION}.bin"
                started = utc_now()
                ok, data, error, status = safe_request(url, accept="application/octet-stream, application/x-eprint-tar, */*")
                if ok and data is not None:
                    out.write_bytes(data)
                download_rows.append({
                    "source_id": spec.source_id,
                    "download_kind": kind,
                    "url": url,
                    "output_file": str(out),
                    "success": ok,
                    "http_status": status,
                    "size_bytes": len(data) if data else 0,
                    "error": error,
                    "started_utc": started,
                    "finished_utc": utc_now(),
                })
                time.sleep(SLEEP_SECONDS)

    manual_path = references_dir / f"strong_interaction_alternative_source_registry_raw_{SCRIPT_VERSION}.csv"
    write_csv(manual_path, manual_rows, [
        "source_id", "priority", "role", "arxiv_id", "doi", "journal_hint",
        "arxiv_abs_url", "arxiv_pdf_url", "arxiv_eprint_url", "arxiv_src_url",
        "inspire_api_url", "inspire_manual_url", "doi_url", "hepdata_manual_search_url",
        "rivet_manual_search_url", "current_status", "notes", "created_utc",
    ])

    download_manifest_path = references_dir / f"strong_interaction_alternative_source_download_manifest_raw_{SCRIPT_VERSION}.csv"
    write_csv(download_manifest_path, download_rows, [
        "source_id", "download_kind", "url", "output_file", "success", "http_status",
        "size_bytes", "error", "started_utc", "finished_utc",
    ])

    readme_path = references_dir / f"strong_interaction_alternative_source_readme_raw_{SCRIPT_VERSION}.txt"
    readme_path.write_text(
        "Strong_interaction alternative source acquisition stage\n"
        "=====================================================\n"
        f"Generated UTC: {utc_now()}\n"
        f"Script version: {SCRIPT_VERSION}\n\n"
        "Purpose:\n"
        "- Preserve alternative source routes after HEPData JSON search failure.\n"
        "- Record INSPIRE, DOI, arXiv source, HEPData manual search, and Rivet/YODA search routes.\n"
        "- Optionally download INSPIRE JSON and arXiv source archives.\n\n"
        "Important status:\n"
        "- These files are not final numerical benchmark input.\n"
        "- Use them to locate real binned CSV/YODA/event-level data.\n"
        "- Promote only reviewed numerical tables into data/derived/input.\n\n"
        "Outputs:\n"
        f"- {manual_path}\n"
        f"- {download_manifest_path}\n",
        encoding="utf-8",
    )

    print(f"[OK] alternative source registry: {manual_path}")
    print(f"[OK] alternative download manifest: {download_manifest_path}")
    print(f"[OK] readme: {readme_path}")
    print("[DONE] Alternative source routes prepared.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare alternative source routes for the Strong_interaction benchmark.")
    parser.add_argument("--download-arxiv-source", action="store_true", help="Try downloading arXiv e-print/source archives.")
    parser.add_argument("--download-inspire", action="store_true", help="Try downloading INSPIRE-HEP API JSON metadata.")
    args = parser.parse_args()
    return run(download_arxiv_source=args.download_arxiv_source, download_inspire=args.download_inspire)


if __name__ == "__main__":
    sys.exit(main())
