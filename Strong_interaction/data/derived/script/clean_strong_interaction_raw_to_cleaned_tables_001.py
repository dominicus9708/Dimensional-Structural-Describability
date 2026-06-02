#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clean_strong_interaction_raw_to_cleaned_tables_001.py

Strong_interaction raw-to-derived cleaning pipeline for the
Dimensional-Structural Describability project.

Author: Kwon Dominicus

Purpose
-------
This script reads the raw files prepared under:

    Strong_interaction/data/raw/references/
    Strong_interaction/data/raw/source_tables/

and writes normalized derived outputs to a numbered, non-time-based folder:

    Strong_interaction/data/derived/cleaned_tables/01/

Important status
----------------
The arXiv HTML files downloaded in the raw stage are provenance/reference pages,
not numerical benchmark CSV tables. This script therefore extracts clean metadata
from those HTML files and marks them as `provenance_html`, not as final numerical
input.

The PDG and NIST TXT files are reference tables and are cleaned into CSV form.
They support later standard-baseline construction but are not event-level benchmark
data.

This script does not create data/derived/input. Final input must be selected only
after the cleaned tables and table manifests are reviewed.
"""

from __future__ import annotations

import csv
import datetime as _dt
import html
import json
import pathlib
import re
import sys
from dataclasses import dataclass
from typing import Iterable, Optional


SCRIPT_VERSION = "001"
OUTPUT_BATCH = "01"
EPSILON_NOTE = "not_used_in_cleaning_stage"


ARXIV_FILE_ROLES = {
    "delphi_open_data_thrust_eec_arxiv_abs_2510_18762_raw_001.html": {
        "source_id": "DELPHI_OPEN_DATA_THRUST_EEC_NOTE_2025",
        "candidate_role": "primary_event_level_benchmark_candidate_reference",
        "dataset_status": "provenance_html_not_event_data",
        "benchmark_priority": 1,
    },
    "opal_event_shapes_arxiv_abs_hep_ex_0503051_raw_001.html": {
        "source_id": "OPAL_EVENT_SHAPES_91_209GEV_2005",
        "candidate_role": "standard_event_shape_distribution_reference",
        "dataset_status": "provenance_html_not_numerical_table",
        "benchmark_priority": 2,
    },
    "opal_event_shapes_nnlo_arxiv_abs_1101_1470_raw_001.html": {
        "source_id": "OPAL_EVENT_SHAPES_NNLO_2011",
        "candidate_role": "standard_qcd_running_and_event_shape_crosscheck_reference",
        "dataset_status": "provenance_html_not_numerical_table",
        "benchmark_priority": 3,
    },
    "jade_event_shapes_arxiv_abs_hep_ex_9708034_raw_001.html": {
        "source_id": "JADE_EVENT_SHAPES_22_44GEV",
        "candidate_role": "lower_energy_event_shape_scale_extension_reference",
        "dataset_status": "provenance_html_not_numerical_table",
        "benchmark_priority": 4,
    },
    "l3_flavour_tagged_event_shape_arxiv_abs_0907_2658_raw_001.html": {
        "source_id": "L3_FLAVOUR_TAGGED_EVENT_SHAPE_197GEV",
        "candidate_role": "flavour_dependent_event_shape_extension_reference",
        "dataset_status": "provenance_html_not_numerical_table",
        "benchmark_priority": 5,
    },
    "hepdata_csv_format_reference_raw_001.html": {
        "source_id": "HEPDATA_CSV_FORMAT_REFERENCE",
        "candidate_role": "hepdata_download_format_reference",
        "dataset_status": "service_reference_html_not_numerical_table",
        "benchmark_priority": 99,
    },
}


KEY_NIST_QUANTITIES = {
    "speed of light in vacuum": "speed_of_light",
    "electron mass energy equivalent in MeV": "electron_mass_energy_equivalent_MeV",
    "proton mass energy equivalent in MeV": "proton_mass_energy_equivalent_MeV",
    "neutron mass energy equivalent in MeV": "neutron_mass_energy_equivalent_MeV",
    "atomic mass constant energy equivalent in MeV": "atomic_mass_constant_energy_equivalent_MeV",
    "joule-electron volt relationship": "joule_electron_volt_relationship",
    "electron volt": "electron_volt_joule",
    "Planck constant": "planck_constant",
    "reduced Planck constant": "reduced_planck_constant",
    "fine-structure constant": "fine_structure_constant",
    "strong coupling constant": "strong_coupling_constant_if_present",
}


@dataclass
class Paths:
    repo_root: pathlib.Path
    strong_root: pathlib.Path
    raw_references: pathlib.Path
    raw_source_tables: pathlib.Path
    output_dir: pathlib.Path


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def locate_paths() -> Paths:
    script_path = pathlib.Path(__file__).resolve()
    # Expected: Strong_interaction/data/derived/script/<script>.py
    strong_root = script_path.parents[3]
    repo_root = strong_root.parent
    raw_references = strong_root / "data" / "raw" / "references"
    raw_source_tables = strong_root / "data" / "raw" / "source_tables"
    output_dir = strong_root / "data" / "derived" / "cleaned_tables" / OUTPUT_BATCH
    output_dir.mkdir(parents=True, exist_ok=True)
    return Paths(repo_root, strong_root, raw_references, raw_source_tables, output_dir)


def read_text(path: pathlib.Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def write_csv(path: pathlib.Path, rows: Iterable[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def strip_tags(value: str) -> str:
    value = re.sub(r"<script.*?</script>", " ", value, flags=re.IGNORECASE | re.DOTALL)
    value = re.sub(r"<style.*?</style>", " ", value, flags=re.IGNORECASE | re.DOTALL)
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def meta_content(text: str, key: str, by: str = "name") -> str:
    # Handles both <meta name="..." content="..."> and single quotes in a simple way.
    pattern = rf'<meta\s+[^>]*{by}=["\']{re.escape(key)}["\'][^>]*content=["\'](.*?)["\'][^>]*>'
    m = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    if m:
        return html.unescape(m.group(1)).strip()
    pattern_rev = rf'<meta\s+[^>]*content=["\'](.*?)["\'][^>]*{by}=["\']{re.escape(key)}["\'][^>]*>'
    m = re.search(pattern_rev, text, flags=re.IGNORECASE | re.DOTALL)
    return html.unescape(m.group(1)).strip() if m else ""


def first_match(text: str, pattern: str) -> str:
    m = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    return html.unescape(m.group(1)).strip() if m else ""


def extract_arxiv_metadata(path: pathlib.Path) -> dict[str, object]:
    text = read_text(path)
    role = ARXIV_FILE_ROLES.get(path.name, {})

    title = meta_content(text, "citation_title") or meta_content(text, "og:title", by="property")
    abstract = meta_content(text, "citation_abstract") or meta_content(text, "og:description", by="property")
    arxiv_id = meta_content(text, "citation_arxiv_id")
    doi = meta_content(text, "citation_doi")
    pdf_url = meta_content(text, "citation_pdf_url")
    date = meta_content(text, "citation_date") or meta_content(text, "citation_online_date")
    canonical = first_match(text, r'<link\s+rel=["\']canonical["\']\s+href=["\'](.*?)["\']')

    authors = re.findall(r'<meta\s+[^>]*name=["\']citation_author["\'][^>]*content=["\'](.*?)["\'][^>]*>', text, flags=re.IGNORECASE | re.DOTALL)
    authors = [html.unescape(a).strip() for a in authors]

    # Extract visible arXiv abstract as fallback.
    if not abstract:
        block = first_match(text, r'<blockquote class=["\']abstract[^"\']*["\'].*?</span>(.*?)</blockquote>')
        abstract = strip_tags(block)

    # Extract useful broad observables from title/abstract.
    lowered = f"{title} {abstract}".lower()
    observable_flags = {
        "thrust": "thrust" in lowered,
        "track_energy_energy_correlator": "energy-energy correlator" in lowered or "energy energy correlator" in lowered,
        "event_shape": "event shape" in lowered,
        "moments": "moments" in lowered,
        "jet_broadening": "broadening" in lowered,
        "heavy_jet_mass": "heavy jet mass" in lowered,
        "durham_y23_or_2jet_rate": "durham" in lowered or "2-jet" in lowered,
        "flavour_tagged": "flavour" in lowered or "flavor" in lowered,
        "alpha_s": "alpha_s" in lowered or "αs" in lowered or "strong coupling" in lowered,
    }

    return {
        "source_id": role.get("source_id", path.stem.upper()),
        "raw_filename": path.name,
        "raw_file_type": "html",
        "cleaned_kind": role.get("dataset_status", "html_reference"),
        "candidate_role": role.get("candidate_role", "unknown_reference"),
        "benchmark_priority": role.get("benchmark_priority", ""),
        "title": strip_tags(title),
        "authors": "; ".join(authors),
        "date": date,
        "arxiv_id": arxiv_id,
        "doi": doi,
        "canonical_url": canonical,
        "pdf_url": pdf_url,
        "abstract": strip_tags(abstract),
        "has_thrust": observable_flags["thrust"],
        "has_track_eec": observable_flags["track_energy_energy_correlator"],
        "has_event_shape": observable_flags["event_shape"],
        "has_moments": observable_flags["moments"],
        "has_jet_broadening": observable_flags["jet_broadening"],
        "has_heavy_jet_mass": observable_flags["heavy_jet_mass"],
        "has_durham_y23_or_2jet_rate": observable_flags["durham_y23_or_2jet_rate"],
        "has_flavour_tagged": observable_flags["flavour_tagged"],
        "has_alpha_s": observable_flags["alpha_s"],
        "is_final_numerical_input": False,
        "cleaned_utc": utc_now(),
    }


def parse_number(raw: str) -> Optional[float]:
    raw = raw.strip()
    if not raw or raw == "(exact)":
        return None
    raw = raw.replace("...", "")
    raw = re.sub(r"\s+", "", raw)
    try:
        return float(raw)
    except ValueError:
        return None


def parse_nist_line(line: str) -> Optional[dict[str, object]]:
    if not line.strip() or line.startswith("-"):
        return None
    # NIST allascii uses wide fixed-ish columns, but quantity names may contain spaces.
    # Split by two or more spaces to separate quantity/value/uncertainty/unit.
    parts = re.split(r"\s{2,}", line.rstrip())
    if len(parts) < 2:
        return None
    quantity = parts[0].strip()
    value_raw = parts[1].strip() if len(parts) > 1 else ""
    uncertainty_raw = parts[2].strip() if len(parts) > 2 else ""
    unit_raw = parts[3].strip() if len(parts) > 3 else ""
    if quantity.lower() in {"quantity", "from:"}:
        return None
    if not value_raw or not re.search(r"[0-9]", value_raw):
        return None
    key = KEY_NIST_QUANTITIES.get(quantity)
    return {
        "constant_key": key or re.sub(r"[^a-z0-9]+", "_", quantity.lower()).strip("_"),
        "quantity": quantity,
        "value_raw": value_raw,
        "value_numeric": parse_number(value_raw),
        "uncertainty_raw": uncertainty_raw,
        "uncertainty_numeric": parse_number(uncertainty_raw),
        "unit_raw": unit_raw,
        "selected_for_strong_pipeline": bool(key),
        "cleaning_note": "NIST CODATA 2022 allascii parsed by two-or-more-space separation.",
        "cleaned_utc": utc_now(),
    }


def clean_nist(paths: Paths) -> tuple[pathlib.Path, pathlib.Path, int, int]:
    candidates = sorted(paths.raw_source_tables.glob("nist_codata*_raw*.txt"))
    if not candidates:
        return paths.output_dir / "nist_constants_cleaned_full_001.csv", paths.output_dir / "nist_constants_cleaned_selected_001.csv", 0, 0
    path = candidates[0]
    rows = []
    for line in read_text(path).splitlines():
        parsed = parse_nist_line(line)
        if parsed:
            parsed["source_file"] = path.name
            rows.append(parsed)
    selected = [r for r in rows if r.get("selected_for_strong_pipeline")]

    full_path = paths.output_dir / "nist_constants_cleaned_full_001.csv"
    selected_path = paths.output_dir / "nist_constants_cleaned_selected_001.csv"
    fieldnames = [
        "source_file", "constant_key", "quantity", "value_raw", "value_numeric",
        "uncertainty_raw", "uncertainty_numeric", "unit_raw", "selected_for_strong_pipeline",
        "cleaning_note", "cleaned_utc",
    ]
    write_csv(full_path, rows, fieldnames)
    write_csv(selected_path, selected, fieldnames)
    return full_path, selected_path, len(rows), len(selected)


def parse_float_slice(text: str) -> Optional[float]:
    text = text.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_pdg_line(line: str) -> Optional[dict[str, object]]:
    if not line.strip() or line.lstrip().startswith("*"):
        return None
    if not re.match(r"^\s*[-0-9]", line):
        return None

    # PDG file documents a fixed FORTRAN-like layout.
    # Use slices where possible, while also preserving raw line for audit.
    raw = line.rstrip("\n")
    padded = raw + " " * max(0, 140 - len(raw))
    id_fields = [padded[0:8], padded[8:16], padded[16:24], padded[24:32]]
    ids = [int(x.strip()) if x.strip() and re.match(r"^-?\d+$", x.strip()) else "" for x in id_fields]
    mass = parse_float_slice(padded[33:51])
    mass_pos = parse_float_slice(padded[52:60])
    mass_neg = parse_float_slice(padded[61:69])
    width = parse_float_slice(padded[70:88])
    width_pos = parse_float_slice(padded[89:97])
    width_neg = parse_float_slice(padded[98:106])
    name_charge = padded[107:128].strip()

    if not any(x != "" for x in ids):
        return None

    return {
        "source_id": "PDG_MASS_WIDTH_2025",
        "mc_id_1": ids[0],
        "mc_id_2": ids[1],
        "mc_id_3": ids[2],
        "mc_id_4": ids[3],
        "particle_name_raw": name_charge,
        "particle_name_norm": re.sub(r"\s+", " ", name_charge.lower()).strip(),
        "mass_GeV_c2": mass,
        "mass_MeV_c2": mass * 1000.0 if mass is not None else None,
        "mass_pos_error_GeV_c2": mass_pos,
        "mass_pos_error_MeV_c2": mass_pos * 1000.0 if mass_pos is not None else None,
        "mass_neg_error_GeV_c2": mass_neg,
        "mass_neg_error_MeV_c2": mass_neg * 1000.0 if mass_neg is not None else None,
        "width_GeV": width,
        "width_MeV": width * 1000.0 if width is not None else None,
        "width_pos_error_GeV": width_pos,
        "width_pos_error_MeV": width_pos * 1000.0 if width_pos is not None else None,
        "width_neg_error_GeV": width_neg,
        "width_neg_error_MeV": width_neg * 1000.0 if width_neg is not None else None,
        "unit_assumption": "PDG mass_width raw mass and width values treated as GeV; converted to MeV by multiplying by 1000.",
        "raw_line": raw,
        "cleaned_utc": utc_now(),
    }


def clean_pdg(paths: Paths) -> tuple[pathlib.Path, pathlib.Path, int, int]:
    candidates = sorted(paths.raw_source_tables.glob("pdg_mass_width*_raw*.txt"))
    if not candidates:
        return paths.output_dir / "pdg_mass_width_cleaned_full_001.csv", paths.output_dir / "pdg_particle_masses_selected_001.csv", 0, 0
    path = candidates[0]
    rows = []
    for line in read_text(path).splitlines():
        parsed = parse_pdg_line(line)
        if parsed:
            parsed["source_file"] = path.name
            rows.append(parsed)

    # A minimal support set useful for later e+e- and hadronization benchmark metadata.
    selected_ids = {11, -11, 22, 21, 1, 2, 3, 4, 5, 6, 111, 211, 221, 113, 213, 223, 333, 2212, 2112}
    selected = [
        r for r in rows
        if any(isinstance(r.get(f"mc_id_{i}"), int) and abs(int(r[f"mc_id_{i}"])) in {abs(x) for x in selected_ids} for i in range(1, 5))
    ]

    full_path = paths.output_dir / "pdg_mass_width_cleaned_full_001.csv"
    selected_path = paths.output_dir / "pdg_particle_masses_selected_001.csv"
    fieldnames = [
        "source_file", "source_id", "mc_id_1", "mc_id_2", "mc_id_3", "mc_id_4",
        "particle_name_raw", "particle_name_norm", "mass_GeV_c2", "mass_MeV_c2",
        "mass_pos_error_GeV_c2", "mass_pos_error_MeV_c2",
        "mass_neg_error_GeV_c2", "mass_neg_error_MeV_c2", "width_GeV", "width_MeV",
        "width_pos_error_GeV", "width_pos_error_MeV", "width_neg_error_GeV", "width_neg_error_MeV",
        "unit_assumption", "raw_line", "cleaned_utc",
    ]
    write_csv(full_path, rows, fieldnames)
    write_csv(selected_path, selected, fieldnames)
    return full_path, selected_path, len(rows), len(selected)


def clean_html_metadata(paths: Paths) -> tuple[pathlib.Path, int]:
    rows = []
    for filename in ARXIV_FILE_ROLES:
        path = paths.raw_source_tables / filename
        if path.exists():
            rows.append(extract_arxiv_metadata(path))
        else:
            role = ARXIV_FILE_ROLES[filename]
            rows.append({
                "source_id": role.get("source_id"),
                "raw_filename": filename,
                "raw_file_type": "html",
                "cleaned_kind": "missing_raw_file",
                "candidate_role": role.get("candidate_role"),
                "benchmark_priority": role.get("benchmark_priority"),
                "title": "",
                "authors": "",
                "date": "",
                "arxiv_id": "",
                "doi": "",
                "canonical_url": "",
                "pdf_url": "",
                "abstract": "",
                "has_thrust": False,
                "has_track_eec": False,
                "has_event_shape": False,
                "has_moments": False,
                "has_jet_broadening": False,
                "has_heavy_jet_mass": False,
                "has_durham_y23_or_2jet_rate": False,
                "has_flavour_tagged": False,
                "has_alpha_s": False,
                "is_final_numerical_input": False,
                "cleaned_utc": utc_now(),
            })

    path = paths.output_dir / "source_reference_metadata_cleaned_001.csv"
    fieldnames = [
        "source_id", "raw_filename", "raw_file_type", "cleaned_kind", "candidate_role",
        "benchmark_priority", "title", "authors", "date", "arxiv_id", "doi", "canonical_url",
        "pdf_url", "abstract", "has_thrust", "has_track_eec", "has_event_shape", "has_moments",
        "has_jet_broadening", "has_heavy_jet_mass", "has_durham_y23_or_2jet_rate",
        "has_flavour_tagged", "has_alpha_s", "is_final_numerical_input", "cleaned_utc",
    ]
    write_csv(path, rows, fieldnames)
    return path, len(rows)


def make_download_candidate_tables(paths: Paths) -> tuple[pathlib.Path, int]:
    # These are not final URLs guaranteed to resolve to records. They are auditable next-step candidates.
    rows = [
        {
            "candidate_id": "DELPHI_OPEN_DATA_EVENT_LEVEL_CANDIDATE_001",
            "priority": 1,
            "source_id": "DELPHI_OPEN_DATA_THRUST_EEC_NOTE_2025",
            "needed_data_type": "event_level_or_analysis_reproduction_files",
            "target_observables": "thrust; track_energy_energy_correlator; charged_tracks; angular_correlations",
            "current_raw_status": "arxiv_html_reference_only",
            "next_action": "Locate exact CERN/OpenData or analysis repository record; confirm file size before download.",
            "expected_use": "10000_plus_event_benchmark_primary_candidate",
            "write_to_raw_when_confirmed": "Strong_interaction/data/raw/source_tables/",
            "clean_to_derived_when_confirmed": "Strong_interaction/data/derived/cleaned_tables/02_or_later/",
        },
        {
            "candidate_id": "OPAL_HEPDATA_CSV_CANDIDATE_001",
            "priority": 2,
            "source_id": "OPAL_EVENT_SHAPES_91_209GEV_2005",
            "needed_data_type": "binned_event_shape_csv",
            "target_observables": "thrust; heavy_jet_mass; total_jet_broadening; wide_jet_broadening; C_parameter; Durham_y23; moments",
            "current_raw_status": "arxiv_html_reference_only",
            "next_action": "Find HEPData record by DOI or title; download record with ?format=json and selected tables with ?format=csv.",
            "expected_use": "standard_baseline_crosscheck",
            "write_to_raw_when_confirmed": "Strong_interaction/data/raw/source_tables/",
            "clean_to_derived_when_confirmed": "Strong_interaction/data/derived/cleaned_tables/02_or_later/",
        },
        {
            "candidate_id": "JADE_HEPDATA_CSV_CANDIDATE_001",
            "priority": 3,
            "source_id": "JADE_EVENT_SHAPES_22_44GEV",
            "needed_data_type": "binned_event_shape_csv",
            "target_observables": "thrust; heavy_jet_mass; jet_broadening; Durham_differential_2jet_rate; alpha_s_Q",
            "current_raw_status": "arxiv_html_reference_only",
            "next_action": "Find HEPData record by DOI or title; download selected CSV tables.",
            "expected_use": "lower_energy_scale_extension",
            "write_to_raw_when_confirmed": "Strong_interaction/data/raw/source_tables/",
            "clean_to_derived_when_confirmed": "Strong_interaction/data/derived/cleaned_tables/02_or_later/",
        },
        {
            "candidate_id": "L3_FLAVOUR_HEPDATA_CSV_CANDIDATE_001",
            "priority": 4,
            "source_id": "L3_FLAVOUR_TAGGED_EVENT_SHAPE_197GEV",
            "needed_data_type": "flavour_tagged_binned_event_shape_csv",
            "target_observables": "all_hadronic; light_flavour; b_flavour; event_shape_distributions; moments",
            "current_raw_status": "arxiv_html_reference_only",
            "next_action": "Find HEPData or journal supplementary tables; download selected CSV tables if available.",
            "expected_use": "flavour_structure_extension",
            "write_to_raw_when_confirmed": "Strong_interaction/data/raw/source_tables/",
            "clean_to_derived_when_confirmed": "Strong_interaction/data/derived/cleaned_tables/02_or_later/",
        },
    ]
    path = paths.output_dir / "benchmark_download_candidates_cleaned_001.csv"
    fieldnames = [
        "candidate_id", "priority", "source_id", "needed_data_type", "target_observables",
        "current_raw_status", "next_action", "expected_use", "write_to_raw_when_confirmed",
        "clean_to_derived_when_confirmed",
    ]
    write_csv(path, rows, fieldnames)
    return path, len(rows)


def copy_raw_manifests(paths: Paths) -> tuple[pathlib.Path, int]:
    rows = []
    for path in sorted(paths.raw_references.glob("*.csv")):
        rows.append({
            "raw_reference_file": path.name,
            "raw_reference_path": str(path),
            "size_bytes": path.stat().st_size,
            "copied_as_metadata_only": True,
            "cleaned_utc": utc_now(),
        })
    out = paths.output_dir / "raw_manifest_index_cleaned_001.csv"
    write_csv(out, rows, ["raw_reference_file", "raw_reference_path", "size_bytes", "copied_as_metadata_only", "cleaned_utc"])
    return out, len(rows)


def write_summary(paths: Paths, stats: list[dict[str, object]]) -> pathlib.Path:
    path = paths.output_dir / "cleaning_summary_001.txt"
    lines = [
        "Strong_interaction raw-to-derived cleaning summary",
        "=================================================",
        f"Generated UTC: {utc_now()}",
        f"Script version: {SCRIPT_VERSION}",
        f"Output batch: {OUTPUT_BATCH}",
        "",
        "Input directories:",
        f"- {paths.raw_references}",
        f"- {paths.raw_source_tables}",
        "",
        "Output directory:",
        f"- {paths.output_dir}",
        "",
        "Interpretation:",
        "- arXiv HTML files were cleaned as provenance metadata only.",
        "- PDG and NIST TXT files were cleaned as reference support tables.",
        "- No final numerical event-shape benchmark input was produced in this stage.",
        "- data/derived/input must be created only after actual HEPData CSV or event-level files are selected.",
        "",
        "Produced outputs:",
    ]
    for row in stats:
        lines.append(f"- {row['output_file']}: rows={row['row_count']} status={row['status']} notes={row['notes']}")
    lines.extend([
        "",
        "Recommended next stage:",
        "1. Locate HEPData record IDs for OPAL/JADE/L3, or exact DELPHI Open Data event files.",
        "2. Download actual CSV/event files into data/raw/source_tables.",
        "3. Run a second cleaner into cleaned_tables/02 or a later numbered folder.",
        "4. Only then select data/derived/input for skeleton/standard/structural execution.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    paths = locate_paths()
    print(f"[INFO] strong_root: {paths.strong_root}")
    print(f"[INFO] raw_references: {paths.raw_references}")
    print(f"[INFO] raw_source_tables: {paths.raw_source_tables}")
    print(f"[INFO] output_dir: {paths.output_dir}")

    stats: list[dict[str, object]] = []

    html_path, html_count = clean_html_metadata(paths)
    stats.append({"output_file": html_path.name, "row_count": html_count, "status": "success", "notes": "HTML provenance metadata cleaned; not numerical benchmark input."})

    nist_full, nist_selected, nist_count, nist_selected_count = clean_nist(paths)
    stats.append({"output_file": nist_full.name, "row_count": nist_count, "status": "success" if nist_count else "missing_input", "notes": "NIST full reference constants parsed."})
    stats.append({"output_file": nist_selected.name, "row_count": nist_selected_count, "status": "success" if nist_selected_count else "missing_or_empty_selected", "notes": "NIST selected support constants parsed."})

    pdg_full, pdg_selected, pdg_count, pdg_selected_count = clean_pdg(paths)
    stats.append({"output_file": pdg_full.name, "row_count": pdg_count, "status": "success" if pdg_count else "missing_input", "notes": "PDG mass-width support table parsed."})
    stats.append({"output_file": pdg_selected.name, "row_count": pdg_selected_count, "status": "success" if pdg_selected_count else "empty_selected", "notes": "PDG selected particle support set parsed."})

    candidates_path, candidates_count = make_download_candidate_tables(paths)
    stats.append({"output_file": candidates_path.name, "row_count": candidates_count, "status": "success", "notes": "Next-stage numerical data download candidates prepared."})

    raw_index_path, raw_index_count = copy_raw_manifests(paths)
    stats.append({"output_file": raw_index_path.name, "row_count": raw_index_count, "status": "success", "notes": "Raw manifest index created."})

    summary_path = write_summary(paths, stats)
    stats_path = paths.output_dir / "cleaning_manifest_001.csv"
    write_csv(stats_path, stats, ["output_file", "row_count", "status", "notes"])

    print(f"[OK] summary: {summary_path}")
    print(f"[OK] manifest: {stats_path}")
    print("[DONE] cleaned_tables/01 prepared.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
