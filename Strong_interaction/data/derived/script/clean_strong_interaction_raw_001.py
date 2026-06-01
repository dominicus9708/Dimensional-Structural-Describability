# data/derived/script/clean_strong_interaction_raw_001.py

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import csv
import math
import re
import sys


ROOT = Path(r"D:\Paper\Dimensional_Structural_Describability\Strong_interaction")

RAW_REFERENCES_DIR = ROOT / "data" / "raw" / "references"
RAW_SOURCE_TABLES_DIR = ROOT / "data" / "raw" / "source_tables"

DERIVED_SCRIPT_DIR = ROOT / "data" / "derived" / "script"
CLEANED_TABLES_DIR = ROOT / "data" / "derived" / "cleaned_tables"

RAW_REFERENCE_REGISTRY = RAW_REFERENCES_DIR / "reference_registry_raw_001.csv"
RAW_DOWNLOAD_MANIFEST = RAW_REFERENCES_DIR / "download_manifest_raw_001.csv"
RAW_PDG_MASS_WIDTH = RAW_SOURCE_TABLES_DIR / "pdg_mass_width_raw_001.csv"
RAW_NIST_CONSTANTS = RAW_SOURCE_TABLES_DIR / "nist_codata_constants_raw_001.csv"
RAW_SEED_CASES = RAW_SOURCE_TABLES_DIR / "strong_interaction_seed_cases_raw_001.csv"

OUT_REFERENCE_REGISTRY = CLEANED_TABLES_DIR / "reference_registry_cleaned_001.csv"
OUT_DOWNLOAD_MANIFEST = CLEANED_TABLES_DIR / "download_manifest_cleaned_001.csv"
OUT_PDG_FULL = CLEANED_TABLES_DIR / "pdg_mass_width_cleaned_full_001.csv"
OUT_PDG_SELECTED = CLEANED_TABLES_DIR / "pdg_particle_masses_selected_001.csv"
OUT_NIST_SELECTED = CLEANED_TABLES_DIR / "nist_constants_cleaned_selected_001.csv"
OUT_CASES_CLEANED = CLEANED_TABLES_DIR / "strong_interaction_cases_cleaned_001.csv"
OUT_CLEANING_MANIFEST = CLEANED_TABLES_DIR / "cleaning_manifest_001.csv"


# PDG mass_width 파일의 raw 질량값은 통상 GeV 단위로 취급한다.
# derived 단계에서는 반드시 GeV와 MeV를 함께 남겨 후속 단계에서 단위 혼동을 줄인다.
PDG_GEV_TO_MEV = 1000.0


SELECTED_PARTICLE_RULES = [
    {
        "particle_key": "photon",
        "match_any": ["gamma"],
        "standard_role": "free_radiation_baseline",
        "structural_role": "energy_present_but_no_individual_rest_mass",
    },
    {
        "particle_key": "gluon",
        "match_any": ["gluon"],
        "standard_role": "qcd_field_component",
        "structural_role": "massless_field_component_in_qcd_confinement_context",
    },
    {
        "particle_key": "electron",
        "match_any": ["e"],
        "standard_role": "annihilation_transition_baseline",
        "structural_role": "massive_fermionic_component",
    },
    {
        "particle_key": "proton",
        "match_any": ["p"],
        "standard_role": "qcd_confined_hadron_baseline",
        "structural_role": "bounded_qcd_hadron_mass_describability",
    },
    {
        "particle_key": "neutron",
        "match_any": ["n"],
        "standard_role": "qcd_confined_hadron_baseline",
        "structural_role": "bounded_qcd_hadron_mass_describability",
    },
    {
        "particle_key": "up_quark",
        "match_any": ["u quark"],
        "standard_role": "constituent_quark_mass_reference",
        "structural_role": "bare_or_running_quark_mass_reference_not_total_hadron_mass",
    },
    {
        "particle_key": "down_quark",
        "match_any": ["d quark"],
        "standard_role": "constituent_quark_mass_reference",
        "structural_role": "bare_or_running_quark_mass_reference_not_total_hadron_mass",
    },
    {
        "particle_key": "strange_quark",
        "match_any": ["s quark"],
        "standard_role": "constituent_quark_mass_reference",
        "structural_role": "bare_or_running_quark_mass_reference_not_total_hadron_mass",
    },
]


SELECTED_NIST_QUANTITY_RULES = [
    {
        "constant_key": "speed_of_light",
        "contains": "speed of light in vacuum",
        "standard_role": "unit_conversion_and_mass_energy_relation",
    },
    {
        "constant_key": "electron_mass_energy_equivalent_MeV",
        "contains": "electron mass energy equivalent in MeV",
        "standard_role": "electron_rest_energy_reference",
    },
    {
        "constant_key": "proton_mass_energy_equivalent_MeV",
        "contains": "proton mass energy equivalent in MeV",
        "standard_role": "proton_rest_energy_reference",
    },
    {
        "constant_key": "neutron_mass_energy_equivalent_MeV",
        "contains": "neutron mass energy equivalent in MeV",
        "standard_role": "neutron_rest_energy_reference",
    },
    {
        "constant_key": "atomic_mass_constant_energy_equivalent_MeV",
        "contains": "atomic mass constant energy equivalent in MeV",
        "standard_role": "mass_energy_unit_reference",
    },
    {
        "constant_key": "joule_electron_volt_relationship",
        "contains": "joule-electron volt relationship",
        "standard_role": "energy_unit_conversion_reference",
    },
]


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def ensure_dirs() -> None:
    DERIVED_SCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    CLEANED_TABLES_DIR.mkdir(parents=True, exist_ok=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Required input file not found: {path}")

    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def clean_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def normalize_particle_name(name: str) -> str:
    text = normalize_space(name)
    return text.lower()


def parse_float_maybe(value: object) -> float | None:
    text = clean_text(value)

    if not text:
        return None

    # NIST exact values sometimes contain "...".
    text = text.replace("...", "")
    text = text.replace(" ", "")
    text = text.replace(",", "")

    # PDG and NIST may use forms like 1.234e-5.
    try:
        result = float(text)
    except ValueError:
        return None

    if math.isnan(result) or math.isinf(result):
        return None

    return result


def format_float(value: float | None, digits: int = 12) -> str:
    if value is None:
        return ""
    return f"{value:.{digits}g}"


def clean_reference_registry() -> int:
    rows = read_csv(RAW_REFERENCE_REGISTRY)

    cleaned_rows: list[dict[str, object]] = []
    for row in rows:
        cleaned_rows.append(
            {
                "source_id": clean_text(row.get("source_id")),
                "source_type": clean_text(row.get("source_type")),
                "title": normalize_space(clean_text(row.get("title"))),
                "url": clean_text(row.get("url")),
                "local_output_raw": clean_text(row.get("local_output")),
                "role_in_project": normalize_space(clean_text(row.get("role_in_project"))),
                "status": clean_text(row.get("status")),
                "notes": normalize_space(clean_text(row.get("notes"))),
                "raw_created_utc": clean_text(row.get("created_utc")),
                "cleaned_utc": now_utc_iso(),
            }
        )

    write_csv(
        OUT_REFERENCE_REGISTRY,
        [
            "source_id",
            "source_type",
            "title",
            "url",
            "local_output_raw",
            "role_in_project",
            "status",
            "notes",
            "raw_created_utc",
            "cleaned_utc",
        ],
        cleaned_rows,
    )
    return len(cleaned_rows)


def clean_download_manifest() -> int:
    rows = read_csv(RAW_DOWNLOAD_MANIFEST)

    cleaned_rows: list[dict[str, object]] = []
    for row in rows:
        cleaned_rows.append(
            {
                "source_id": clean_text(row.get("source_id")),
                "url": clean_text(row.get("url")),
                "attempted": clean_text(row.get("attempted")).lower(),
                "success": clean_text(row.get("success")).lower(),
                "output_file_raw": clean_text(row.get("output_file")),
                "row_count_raw": clean_text(row.get("row_count")),
                "error": normalize_space(clean_text(row.get("error"))),
                "downloaded_utc": clean_text(row.get("downloaded_utc")),
                "cleaned_utc": now_utc_iso(),
            }
        )

    write_csv(
        OUT_DOWNLOAD_MANIFEST,
        [
            "source_id",
            "url",
            "attempted",
            "success",
            "output_file_raw",
            "row_count_raw",
            "error",
            "downloaded_utc",
            "cleaned_utc",
        ],
        cleaned_rows,
    )
    return len(cleaned_rows)


def clean_pdg_full() -> list[dict[str, object]]:
    rows = read_csv(RAW_PDG_MASS_WIDTH)
    cleaned_rows: list[dict[str, object]] = []

    for row in rows:
        particle_name_raw = normalize_space(clean_text(row.get("particle_name_raw")))
        particle_name_norm = normalize_particle_name(particle_name_raw)

        mass_gev = parse_float_maybe(row.get("mass_value_raw"))
        mass_pos_err_gev = parse_float_maybe(row.get("mass_pos_error_raw"))
        mass_neg_err_gev = parse_float_maybe(row.get("mass_neg_error_raw"))
        width_gev = parse_float_maybe(row.get("width_value_raw"))
        width_pos_err_gev = parse_float_maybe(row.get("width_pos_error_raw"))
        width_neg_err_gev = parse_float_maybe(row.get("width_neg_error_raw"))

        cleaned_rows.append(
            {
                "source_id": clean_text(row.get("source_id")),
                "mc_id_1": clean_text(row.get("mc_id_1")),
                "mc_id_2": clean_text(row.get("mc_id_2")),
                "mc_id_3": clean_text(row.get("mc_id_3")),
                "mc_id_4": clean_text(row.get("mc_id_4")),
                "particle_name_raw": particle_name_raw,
                "particle_name_norm": particle_name_norm,
                "mass_GeV_c2": format_float(mass_gev),
                "mass_MeV_c2": format_float(mass_gev * PDG_GEV_TO_MEV if mass_gev is not None else None),
                "mass_pos_error_GeV_c2": format_float(mass_pos_err_gev),
                "mass_pos_error_MeV_c2": format_float(mass_pos_err_gev * PDG_GEV_TO_MEV if mass_pos_err_gev is not None else None),
                "mass_neg_error_GeV_c2": format_float(mass_neg_err_gev),
                "mass_neg_error_MeV_c2": format_float(mass_neg_err_gev * PDG_GEV_TO_MEV if mass_neg_err_gev is not None else None),
                "width_GeV": format_float(width_gev),
                "width_MeV": format_float(width_gev * PDG_GEV_TO_MEV if width_gev is not None else None),
                "width_pos_error_GeV": format_float(width_pos_err_gev),
                "width_pos_error_MeV": format_float(width_pos_err_gev * PDG_GEV_TO_MEV if width_pos_err_gev is not None else None),
                "width_neg_error_GeV": format_float(width_neg_err_gev),
                "width_neg_error_MeV": format_float(width_neg_err_gev * PDG_GEV_TO_MEV if width_neg_err_gev is not None else None),
                "unit_assumption": "PDG mass_width raw mass and width values treated as GeV; converted to MeV by multiplying by 1000.",
                "raw_line": clean_text(row.get("raw_line")),
                "cleaned_utc": now_utc_iso(),
            }
        )

    write_csv(
        OUT_PDG_FULL,
        [
            "source_id",
            "mc_id_1",
            "mc_id_2",
            "mc_id_3",
            "mc_id_4",
            "particle_name_raw",
            "particle_name_norm",
            "mass_GeV_c2",
            "mass_MeV_c2",
            "mass_pos_error_GeV_c2",
            "mass_pos_error_MeV_c2",
            "mass_neg_error_GeV_c2",
            "mass_neg_error_MeV_c2",
            "width_GeV",
            "width_MeV",
            "width_pos_error_GeV",
            "width_pos_error_MeV",
            "width_neg_error_GeV",
            "width_neg_error_MeV",
            "unit_assumption",
            "raw_line",
            "cleaned_utc",
        ],
        cleaned_rows,
    )

    return cleaned_rows


def match_selected_particle(row: dict[str, object]) -> dict[str, str] | None:
    name_norm = clean_text(row.get("particle_name_norm")).lower()

    for rule in SELECTED_PARTICLE_RULES:
        for token in rule["match_any"]:
            token_norm = token.lower()

            # 정확히 같은 이름을 우선한다.
            if name_norm == token_norm:
                return rule

            # quark류처럼 이름이 명확한 경우만 포함 매칭을 허용한다.
            if "quark" in token_norm and token_norm in name_norm:
                return rule

    return None


def write_selected_pdg_particles(cleaned_full_rows: list[dict[str, object]]) -> int:
    selected_rows: list[dict[str, object]] = []
    seen_keys: set[str] = set()

    for row in cleaned_full_rows:
        rule = match_selected_particle(row)
        if rule is None:
            continue

        particle_key = rule["particle_key"]

        # 같은 particle_key가 여러 번 잡히면 첫 행을 우선 사용한다.
        # 필요하면 후속 버전에서 charge state별 분리로 확장한다.
        if particle_key in seen_keys:
            continue

        seen_keys.add(particle_key)

        selected_rows.append(
            {
                "particle_key": particle_key,
                "particle_name_raw": row.get("particle_name_raw", ""),
                "particle_name_norm": row.get("particle_name_norm", ""),
                "mc_id_1": row.get("mc_id_1", ""),
                "mass_GeV_c2": row.get("mass_GeV_c2", ""),
                "mass_MeV_c2": row.get("mass_MeV_c2", ""),
                "width_GeV": row.get("width_GeV", ""),
                "width_MeV": row.get("width_MeV", ""),
                "standard_role": rule["standard_role"],
                "structural_role": rule["structural_role"],
                "source_id": row.get("source_id", ""),
                "unit_assumption": row.get("unit_assumption", ""),
                "selection_note": "Minimal selected set for mass-bounded structural energy pipeline.",
                "cleaned_utc": now_utc_iso(),
            }
        )

    write_csv(
        OUT_PDG_SELECTED,
        [
            "particle_key",
            "particle_name_raw",
            "particle_name_norm",
            "mc_id_1",
            "mass_GeV_c2",
            "mass_MeV_c2",
            "width_GeV",
            "width_MeV",
            "standard_role",
            "structural_role",
            "source_id",
            "unit_assumption",
            "selection_note",
            "cleaned_utc",
        ],
        selected_rows,
    )

    return len(selected_rows)


def clean_nist_selected() -> int:
    rows = read_csv(RAW_NIST_CONSTANTS)
    selected_rows: list[dict[str, object]] = []

    for row in rows:
        quantity = normalize_space(clean_text(row.get("quantity")))
        quantity_norm = quantity.lower()

        matched_rule = None
        for rule in SELECTED_NIST_QUANTITY_RULES:
            if rule["contains"].lower() in quantity_norm:
                matched_rule = rule
                break

        if matched_rule is None:
            continue

        value_raw = clean_text(row.get("value_raw"))
        uncertainty_raw = clean_text(row.get("uncertainty_raw"))
        unit_raw = normalize_space(clean_text(row.get("unit_raw")))

        selected_rows.append(
            {
                "constant_key": matched_rule["constant_key"],
                "quantity": quantity,
                "value_raw": value_raw,
                "value_numeric": format_float(parse_float_maybe(value_raw), digits=16),
                "uncertainty_raw": uncertainty_raw,
                "uncertainty_numeric": format_float(parse_float_maybe(uncertainty_raw), digits=16),
                "unit_raw": unit_raw,
                "standard_role": matched_rule["standard_role"],
                "source_id": clean_text(row.get("source_id")),
                "raw_line": clean_text(row.get("raw_line")),
                "cleaning_note": "Selected NIST CODATA constants for standard mass-energy and unit conversion support.",
                "cleaned_utc": now_utc_iso(),
            }
        )

    write_csv(
        OUT_NIST_SELECTED,
        [
            "constant_key",
            "quantity",
            "value_raw",
            "value_numeric",
            "uncertainty_raw",
            "uncertainty_numeric",
            "unit_raw",
            "standard_role",
            "source_id",
            "raw_line",
            "cleaning_note",
            "cleaned_utc",
        ],
        selected_rows,
    )

    return len(selected_rows)


def clean_seed_cases() -> int:
    rows = read_csv(RAW_SEED_CASES)

    cleaned_rows: list[dict[str, object]] = []
    for row in rows:
        case_type = clean_text(row.get("case_type"))

        if case_type == "free_radiation":
            recommended_next_stage = "standard_check_massless_individual_component"
        elif case_type == "bounded_radiation_system":
            recommended_next_stage = "standard_check_system_invariant_mass"
        elif case_type == "qcd_confined_hadron":
            recommended_next_stage = "standard_check_hadron_mass_vs_constituent_reference"
        elif case_type == "annihilation_transition":
            recommended_next_stage = "standard_check_qed_baseline_only"
        else:
            recommended_next_stage = "manual_review"

        cleaned_rows.append(
            {
                "case_id": clean_text(row.get("case_id")),
                "case_type": case_type,
                "system_name": clean_text(row.get("system_name")),
                "standard_baseline": normalize_space(clean_text(row.get("standard_baseline"))),
                "structural_reading": normalize_space(clean_text(row.get("structural_reading"))),
                "data_status": clean_text(row.get("data_status")),
                "preferred_source_id": clean_text(row.get("preferred_source_id")),
                "recommended_next_stage": recommended_next_stage,
                "notes": normalize_space(clean_text(row.get("notes"))),
                "cleaning_note": "Cleaned seed case table. Still not measurement data.",
                "cleaned_utc": now_utc_iso(),
            }
        )

    write_csv(
        OUT_CASES_CLEANED,
        [
            "case_id",
            "case_type",
            "system_name",
            "standard_baseline",
            "structural_reading",
            "data_status",
            "preferred_source_id",
            "recommended_next_stage",
            "notes",
            "cleaning_note",
            "cleaned_utc",
        ],
        cleaned_rows,
    )

    return len(cleaned_rows)


def write_cleaning_manifest(rows: list[dict[str, object]]) -> None:
    write_csv(
        OUT_CLEANING_MANIFEST,
        [
            "stage",
            "input_file",
            "output_file",
            "row_count",
            "status",
            "notes",
            "created_utc",
        ],
        rows,
    )


def main() -> int:
    ensure_dirs()

    manifest_rows: list[dict[str, object]] = []

    try:
        reference_count = clean_reference_registry()
        manifest_rows.append(
            {
                "stage": "clean_reference_registry",
                "input_file": str(RAW_REFERENCE_REGISTRY),
                "output_file": str(OUT_REFERENCE_REGISTRY),
                "row_count": reference_count,
                "status": "success",
                "notes": "Reference registry normalized.",
                "created_utc": now_utc_iso(),
            }
        )

        download_manifest_count = clean_download_manifest()
        manifest_rows.append(
            {
                "stage": "clean_download_manifest",
                "input_file": str(RAW_DOWNLOAD_MANIFEST),
                "output_file": str(OUT_DOWNLOAD_MANIFEST),
                "row_count": download_manifest_count,
                "status": "success",
                "notes": "Download manifest normalized.",
                "created_utc": now_utc_iso(),
            }
        )

        pdg_full_rows = clean_pdg_full()
        manifest_rows.append(
            {
                "stage": "clean_pdg_full",
                "input_file": str(RAW_PDG_MASS_WIDTH),
                "output_file": str(OUT_PDG_FULL),
                "row_count": len(pdg_full_rows),
                "status": "success",
                "notes": "PDG mass-width table normalized. GeV to MeV conversion columns added.",
                "created_utc": now_utc_iso(),
            }
        )

        pdg_selected_count = write_selected_pdg_particles(pdg_full_rows)
        manifest_rows.append(
            {
                "stage": "select_pdg_particles",
                "input_file": str(OUT_PDG_FULL),
                "output_file": str(OUT_PDG_SELECTED),
                "row_count": pdg_selected_count,
                "status": "success",
                "notes": "Minimal selected particle set generated.",
                "created_utc": now_utc_iso(),
            }
        )

        nist_selected_count = clean_nist_selected()
        manifest_rows.append(
            {
                "stage": "select_nist_constants",
                "input_file": str(RAW_NIST_CONSTANTS),
                "output_file": str(OUT_NIST_SELECTED),
                "row_count": nist_selected_count,
                "status": "success",
                "notes": "Selected NIST constants generated.",
                "created_utc": now_utc_iso(),
            }
        )

        cases_count = clean_seed_cases()
        manifest_rows.append(
            {
                "stage": "clean_seed_cases",
                "input_file": str(RAW_SEED_CASES),
                "output_file": str(OUT_CASES_CLEANED),
                "row_count": cases_count,
                "status": "success",
                "notes": "Seed cases cleaned. Still not measurement data.",
                "created_utc": now_utc_iso(),
            }
        )

    except Exception as exc:
        manifest_rows.append(
            {
                "stage": "cleaning_pipeline",
                "input_file": "",
                "output_file": "",
                "row_count": "",
                "status": "failed",
                "notes": f"{type(exc).__name__}: {exc}",
                "created_utc": now_utc_iso(),
            }
        )
        write_cleaning_manifest(manifest_rows)
        print("Cleaning failed.")
        print(f"{type(exc).__name__}: {exc}")
        return 1

    write_cleaning_manifest(manifest_rows)

    print("Derived cleaning step complete.")
    print(f"Reference registry: {OUT_REFERENCE_REGISTRY}")
    print(f"Download manifest:  {OUT_DOWNLOAD_MANIFEST}")
    print(f"PDG full cleaned:   {OUT_PDG_FULL}")
    print(f"PDG selected:       {OUT_PDG_SELECTED}")
    print(f"NIST selected:      {OUT_NIST_SELECTED}")
    print(f"Cases cleaned:      {OUT_CASES_CLEANED}")
    print(f"Cleaning manifest:  {OUT_CLEANING_MANIFEST}")

    return 0


if __name__ == "__main__":
    sys.exit(main())