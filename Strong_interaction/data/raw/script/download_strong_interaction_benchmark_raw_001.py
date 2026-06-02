#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_strong_interaction_benchmark_raw_001.py

Strong_interaction raw-data preparation script for the Dimensional-Structural
Describability validation pipeline.

Author: Kwon Dominicus

Purpose
-------
This script prepares the raw reference layer for the strong-interaction benchmark
pipeline.  It writes source registries to:

    Strong_interaction/data/raw/references/

and downloads small reference/source files to:

    Strong_interaction/data/raw/source_tables/

The script intentionally avoids downloading multi-GB or TB-scale event files.
For the 10,000+ event benchmark stage, DELPHI open-data event files should be
added only after the exact CERN/OpenData record and file size are confirmed.
This script therefore prepares the reproducible reference registry, standard
constant tables, PDG mass-width support, and HEPData/arXiv search-reference layer.

Design rule
-----------
raw -> derived/cleaned_tables -> derived/input -> src -> results

The script belongs to raw/script and must not write directly to derived/input.
"""

from __future__ import annotations

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
from typing import Iterable, Optional


SCRIPT_VERSION = "001"
USER_AGENT = (
    "Dimensional-Structural-Describability/Strong_interaction benchmark raw script "
    "(Kwon Dominicus; reproducibility registry)"
)
TIMEOUT_SECONDS = 45
SLEEP_SECONDS = 1.0


@dataclass(frozen=True)
class SourceSpec:
    source_id: str
    source_kind: str
    title: str
    url: str
    output_filename: str
    expected_role: str
    download: bool
    notes: str


SOURCES: list[SourceSpec] = [
    SourceSpec(
        source_id="PDG_MASS_WIDTH_2025",
        source_kind="reference_table",
        title="PDG Monte Carlo particle numbering: mass-width table 2025",
        url="https://pdg.lbl.gov/2025/mcdata/mass_width_2025.txt",
        output_filename="pdg_mass_width_2025_raw_benchmark_001.txt",
        expected_role="particle_mass_width_reference",
        download=True,
        notes="Small reference table; supports particle identity, mass, and width fields.",
    ),
    SourceSpec(
        source_id="NIST_CODATA_2022_ALLASCII",
        source_kind="reference_table",
        title="NIST CODATA 2022 all-ASCII constants table",
        url="https://physics.nist.gov/cuu/Constants/Table/allascii.txt",
        output_filename="nist_codata_2022_allascii_raw_benchmark_001.txt",
        expected_role="physical_constants_and_unit_conversion_reference",
        download=True,
        notes="Small reference table; supports unit conversion and physical constants.",
    ),
    SourceSpec(
        source_id="DELPHI_OPEN_DATA_THRUST_EEC_NOTE_2025",
        source_kind="analysis_note_reference",
        title="Measurement of thrust and track energy-energy correlator in e+e- collisions at 91.2 GeV with DELPHI open data",
        url="https://arxiv.org/abs/2510.18762",
        output_filename="delphi_open_data_thrust_eec_arxiv_abs_2510_18762_raw_001.html",
        expected_role="primary_event_level_benchmark_candidate_reference",
        download=True,
        notes="Reference page for the DELPHI open-data benchmark candidate; not the event file itself.",
    ),
    SourceSpec(
        source_id="OPAL_EVENT_SHAPES_91_209GEV_2005",
        source_kind="benchmark_distribution_reference",
        title="OPAL event shape distributions and moments in e+e- -> hadrons at 91-209 GeV",
        url="https://arxiv.org/abs/hep-ex/0503051",
        output_filename="opal_event_shapes_arxiv_abs_hep_ex_0503051_raw_001.html",
        expected_role="standard_event_shape_distribution_reference",
        download=True,
        notes="Reference page for OPAL binned event-shape benchmark distributions.",
    ),
    SourceSpec(
        source_id="OPAL_EVENT_SHAPES_NNLO_2011",
        source_kind="benchmark_distribution_reference",
        title="OPAL hadronic event shapes at sqrt(s)=91-209 GeV with NNLO calculations",
        url="https://arxiv.org/abs/1101.1470",
        output_filename="opal_event_shapes_nnlo_arxiv_abs_1101_1470_raw_001.html",
        expected_role="standard_qcd_running_and_event_shape_crosscheck_reference",
        download=True,
        notes="Reference page for OPAL event-shape alpha_s cross-check.",
    ),
    SourceSpec(
        source_id="JADE_EVENT_SHAPES_22_44GEV",
        source_kind="benchmark_distribution_reference",
        title="JADE event-shape data in e+e- annihilation at 22-44 GeV",
        url="https://arxiv.org/abs/hep-ex/9708034",
        output_filename="jade_event_shapes_arxiv_abs_hep_ex_9708034_raw_001.html",
        expected_role="lower_energy_event_shape_scale_extension_reference",
        download=True,
        notes="Reference page for lower-energy e+e- event-shape benchmark extension.",
    ),
    SourceSpec(
        source_id="L3_FLAVOUR_TAGGED_EVENT_SHAPE_197GEV",
        source_kind="benchmark_distribution_reference",
        title="L3 flavour-tagged hadronic event-shape study near 197 GeV",
        url="https://arxiv.org/abs/0907.2658",
        output_filename="l3_flavour_tagged_event_shape_arxiv_abs_0907_2658_raw_001.html",
        expected_role="flavour_dependent_event_shape_extension_reference",
        download=True,
        notes="Reference page for light/heavy flavour structural extension.",
    ),
    SourceSpec(
        source_id="HEPDATA_CSV_FORMAT_REFERENCE",
        source_kind="service_reference",
        title="HEPData CSV format reference",
        url="https://www.hepdata.net/formats",
        output_filename="hepdata_csv_format_reference_raw_001.html",
        expected_role="hepdata_download_format_reference",
        download=True,
        notes="Service-level reference for later HEPData CSV acquisition.",
    ),
]


HEPDATA_SEARCH_QUERIES: dict[str, str] = {
    "hepdata_search_opal_event_shapes_91_209_raw_001.json": "OPAL event shape distributions moments e+e- hadrons 91 209 GeV",
    "hepdata_search_jade_event_shapes_22_44_raw_001.json": "JADE event shape e+e- annihilation 22 44 GeV",
    "hepdata_search_l3_flavour_event_shape_197_raw_001.json": "L3 flavour tagged event shape 197 GeV",
    "hepdata_search_delphi_open_data_thrust_eec_raw_001.json": "DELPHI open data thrust track energy energy correlator 91.2 GeV",
}


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def script_paths() -> tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    script_dir = pathlib.Path(__file__).resolve().parent
    raw_dir = script_dir.parent
    references_dir = raw_dir / "references"
    source_tables_dir = raw_dir / "source_tables"
    references_dir.mkdir(parents=True, exist_ok=True)
    source_tables_dir.mkdir(parents=True, exist_ok=True)
    return references_dir, source_tables_dir, script_dir


def safe_request(url: str) -> tuple[bool, Optional[bytes], Optional[str], Optional[int]]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status = getattr(response, "status", None)
            data = response.read()
            return True, data, None, status
    except urllib.error.HTTPError as exc:
        return False, None, f"HTTPError {exc.code}: {exc.reason}", exc.code
    except urllib.error.URLError as exc:
        return False, None, f"URLError: {exc.reason}", None
    except TimeoutError as exc:
        return False, None, f"TimeoutError: {exc}", None
    except Exception as exc:  # keep registry complete even on unusual network failures
        return False, None, f"{type(exc).__name__}: {exc}", None


def write_csv(path: pathlib.Path, rows: Iterable[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_reference_registry(references_dir: pathlib.Path) -> pathlib.Path:
    path = references_dir / f"strong_interaction_benchmark_reference_registry_raw_{SCRIPT_VERSION}.csv"
    rows = []
    for spec in SOURCES:
        row = asdict(spec)
        row["created_utc"] = utc_now()
        rows.append(row)
    write_csv(
        path,
        rows,
        [
            "source_id",
            "source_kind",
            "title",
            "url",
            "output_filename",
            "expected_role",
            "download",
            "notes",
            "created_utc",
        ],
    )
    return path


def download_sources(source_tables_dir: pathlib.Path) -> list[dict[str, object]]:
    manifest_rows: list[dict[str, object]] = []
    for spec in SOURCES:
        started = utc_now()
        output_path = source_tables_dir / spec.output_filename
        success = False
        error = ""
        status_code = ""
        size_bytes = 0

        if spec.download:
            ok, data, err, status = safe_request(spec.url)
            status_code = status if status is not None else ""
            if ok and data is not None:
                output_path.write_bytes(data)
                success = True
                size_bytes = len(data)
            else:
                error = err or "unknown_error"
        else:
            success = False
            error = "reference_only_not_downloaded"

        manifest_rows.append(
            {
                "source_id": spec.source_id,
                "url": spec.url,
                "attempted": bool(spec.download),
                "success": success,
                "http_status": status_code,
                "output_file_raw": str(output_path),
                "size_bytes": size_bytes,
                "error": error,
                "started_utc": started,
                "finished_utc": utc_now(),
            }
        )
        time.sleep(SLEEP_SECONDS)
    return manifest_rows


def normalize_hepdata_search_result(data: bytes, query: str, url: str) -> dict[str, object]:
    text = data.decode("utf-8", errors="replace")
    try:
        parsed = json.loads(text)
        record_count = len(parsed) if isinstance(parsed, list) else len(parsed.get("results", [])) if isinstance(parsed, dict) else ""
        return {
            "query": query,
            "url": url,
            "parse_status": "json",
            "record_count_guess": record_count,
            "content_preview": "",
        }
    except Exception:
        title_match = re.search(r"<title>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
        title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else ""
        return {
            "query": query,
            "url": url,
            "parse_status": "non_json",
            "record_count_guess": "",
            "content_preview": title[:300],
        }


def run_hepdata_searches(source_tables_dir: pathlib.Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for output_filename, query in HEPDATA_SEARCH_QUERIES.items():
        params = urllib.parse.urlencode({"q": query, "format": "json"})
        url = f"https://www.hepdata.net/search/?{params}"
        started = utc_now()
        ok, data, err, status = safe_request(url)
        output_path = source_tables_dir / output_filename
        summary_path = source_tables_dir / output_filename.replace(".json", "_summary.csv")

        if ok and data is not None:
            output_path.write_bytes(data)
            summary_row = normalize_hepdata_search_result(data, query, url)
            summary_row["source_id"] = output_filename.replace(".json", "").upper()
            summary_row["output_file_raw"] = str(output_path)
            summary_row["size_bytes"] = len(data)
            summary_row["success"] = True
            summary_row["http_status"] = status if status is not None else ""
            summary_row["error"] = ""
            summary_row["started_utc"] = started
            summary_row["finished_utc"] = utc_now()
            write_csv(
                summary_path,
                [summary_row],
                [
                    "source_id",
                    "query",
                    "url",
                    "parse_status",
                    "record_count_guess",
                    "content_preview",
                    "output_file_raw",
                    "size_bytes",
                    "success",
                    "http_status",
                    "error",
                    "started_utc",
                    "finished_utc",
                ],
            )
            rows.append(summary_row)
        else:
            rows.append(
                {
                    "source_id": output_filename.replace(".json", "").upper(),
                    "url": url,
                    "attempted": True,
                    "success": False,
                    "http_status": status if status is not None else "",
                    "output_file_raw": str(output_path),
                    "size_bytes": 0,
                    "error": err or "unknown_error",
                    "started_utc": started,
                    "finished_utc": utc_now(),
                }
            )
        time.sleep(SLEEP_SECONDS)
    return rows


def write_readme(references_dir: pathlib.Path, source_tables_dir: pathlib.Path) -> pathlib.Path:
    path = references_dir / f"strong_interaction_benchmark_raw_readme_{SCRIPT_VERSION}.txt"
    text = f"""Strong_interaction benchmark raw layer README
Generated UTC: {utc_now()}
Script version: {SCRIPT_VERSION}

This raw layer prepares references and small source tables for a 10,000+ event
strong-interaction benchmark pipeline.

Written directories:
- {references_dir}
- {source_tables_dir}

Important interpretation rules:
1. PDG and NIST are reference support tables, not event-level benchmark data.
2. arXiv pages are provenance references, not final numerical input.
3. HEPData search JSON files are discovery outputs; selected tables must later be
   cleaned into data/derived/cleaned_tables and then fixed under data/derived/input.
4. Do not place multi-GB event files in GitHub.
5. Do not write directly from this raw script into derived/input.
6. The theory-layer name should be confirmed before creating src/results theory-layer folders.

Recommended next stage:
- Inspect HEPData search outputs.
- Select OPAL/JADE/L3 binned event-shape tables.
- Confirm DELPHI open-data event-file source and file size.
- Create a separate cleaner script under data/derived/script or src/skeleton only after final source selection.
"""
    path.write_text(text, encoding="utf-8")
    return path


def main() -> int:
    references_dir, source_tables_dir, script_dir = script_paths()
    print(f"[INFO] script_dir: {script_dir}")
    print(f"[INFO] references_dir: {references_dir}")
    print(f"[INFO] source_tables_dir: {source_tables_dir}")

    registry_path = write_reference_registry(references_dir)
    print(f"[OK] reference registry: {registry_path}")

    manifest_rows = download_sources(source_tables_dir)
    hepdata_rows = run_hepdata_searches(source_tables_dir)

    manifest_path = references_dir / f"strong_interaction_benchmark_download_manifest_raw_{SCRIPT_VERSION}.csv"
    write_csv(
        manifest_path,
        manifest_rows,
        [
            "source_id",
            "url",
            "attempted",
            "success",
            "http_status",
            "output_file_raw",
            "size_bytes",
            "error",
            "started_utc",
            "finished_utc",
        ],
    )
    print(f"[OK] download manifest: {manifest_path}")

    hepdata_manifest_path = references_dir / f"strong_interaction_benchmark_hepdata_search_manifest_raw_{SCRIPT_VERSION}.csv"
    hepdata_fieldnames = sorted({key for row in hepdata_rows for key in row.keys()})
    write_csv(hepdata_manifest_path, hepdata_rows, hepdata_fieldnames)
    print(f"[OK] HEPData search manifest: {hepdata_manifest_path}")

    readme_path = write_readme(references_dir, source_tables_dir)
    print(f"[OK] raw README: {readme_path}")

    failures = [row for row in manifest_rows if not row.get("success")]
    hepdata_failures = [row for row in hepdata_rows if not row.get("success")]
    if failures or hepdata_failures:
        print(f"[WARN] source download failures: {len(failures)}")
        print(f"[WARN] HEPData search failures: {len(hepdata_failures)}")
        print("[WARN] Review manifest CSV files before moving to derived/cleaned_tables.")
        return 1

    print("[DONE] Raw benchmark reference/source layer prepared successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
