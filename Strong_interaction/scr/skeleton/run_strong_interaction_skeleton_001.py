# src/skeleton/run_strong_interaction_skeleton_001.py

from pathlib import Path
import csv
from datetime import datetime

ROOT = Path(r"D:\Paper\Dimensional_Structural_Describability\Strong_interaction")

REQUIRED_DIRS = [
    "data/raw/references",
    "data/raw/source_tables",
    "data/derived/cleaned_tables",
    "data/derived/input",
    "src/skeleton",
    "src/standard",
    "src/structural",
    "results/skeleton",
    "results/standard",
    "results/structural",
    "results/integration",
    "docs/notes",
    "docs/validation_summary",
    "figure",
]

INPUT_FILE = ROOT / "data" / "derived" / "input" / "strong_interaction_minimal_input.csv"


INPUT_COLUMNS = [
    "case_id",
    "case_type",
    "system_name",
    "component_description",
    "standard_baseline",
    "total_energy_MeV",
    "invariant_mass_MeV_c2",
    "constituent_rest_mass_sum_MeV_c2",
    "binding_or_field_energy_note",
    "structural_boundedness_level",
    "mass_describability_class",
    "source_note",
]


TEMPLATE_ROWS = [
    {
        "case_id": "A001",
        "case_type": "free_radiation",
        "system_name": "single_photon",
        "component_description": "single radiative component",
        "standard_baseline": "massless photon; no rest frame",
        "total_energy_MeV": "",
        "invariant_mass_MeV_c2": "0",
        "constituent_rest_mass_sum_MeV_c2": "0",
        "binding_or_field_energy_note": "free radiation; not a bounded rest structure",
        "structural_boundedness_level": "unbounded_or_free",
        "mass_describability_class": "energy_present_but_no_rest_mass_description",
        "source_note": "template row; replace with cited source later",
    },
    {
        "case_id": "B001",
        "case_type": "bounded_radiation_system",
        "system_name": "opposite_direction_photon_pair",
        "component_description": "two photons with opposite momenta",
        "standard_baseline": "system invariant mass may be defined when total momentum is zero",
        "total_energy_MeV": "",
        "invariant_mass_MeV_c2": "",
        "constituent_rest_mass_sum_MeV_c2": "0",
        "binding_or_field_energy_note": "system-level invariant mass, not individual photon rest mass",
        "structural_boundedness_level": "system_closed_momentum",
        "mass_describability_class": "system_mass_describable",
        "source_note": "template row; replace with cited source later",
    },
    {
        "case_id": "C001",
        "case_type": "qcd_confined_hadron",
        "system_name": "proton",
        "component_description": "QCD-confined hadronic structure",
        "standard_baseline": "hadron rest mass includes more than bare constituent quark masses",
        "total_energy_MeV": "",
        "invariant_mass_MeV_c2": "",
        "constituent_rest_mass_sum_MeV_c2": "",
        "binding_or_field_energy_note": "QCD field energy, confinement dynamics, and energy-momentum structure",
        "structural_boundedness_level": "qcd_confined",
        "mass_describability_class": "rest_mass_confined_hadron",
        "source_note": "template row; replace with PDG or literature source later",
    },
    {
        "case_id": "D001",
        "case_type": "annihilation_transition",
        "system_name": "electron_positron_annihilation",
        "component_description": "massive fermionic pair to radiative final state",
        "standard_baseline": "QED baseline preserved; no replacement claim",
        "total_energy_MeV": "",
        "invariant_mass_MeV_c2": "",
        "constituent_rest_mass_sum_MeV_c2": "",
        "binding_or_field_energy_note": "transition from massive particle description to radiative final-state description",
        "structural_boundedness_level": "transition_case",
        "mass_describability_class": "bounded_massive_to_radiative_structure",
        "source_note": "template row; replace with cited source later",
    },
]


def ensure_directories() -> list[str]:
    missing_or_created = []
    for relative_dir in REQUIRED_DIRS:
        path = ROOT / relative_dir
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            missing_or_created.append(str(path))
    return missing_or_created


def create_template_input_if_missing() -> bool:
    if INPUT_FILE.exists():
        return False

    INPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with INPUT_FILE.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=INPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(TEMPLATE_ROWS)

    return True


def validate_input_schema() -> tuple[bool, list[str], int]:
    if not INPUT_FILE.exists():
        return False, ["input file does not exist"], 0

    with INPUT_FILE.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        actual_columns = reader.fieldnames or []
        rows = list(reader)

    missing_columns = [col for col in INPUT_COLUMNS if col not in actual_columns]
    is_valid = len(missing_columns) == 0

    return is_valid, missing_columns, len(rows)


def write_summary(created_dirs: list[str], template_created: bool, schema_ok: bool, missing_columns: list[str], row_count: int) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = ROOT / "results" / "skeleton" / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_path = output_dir / "skeleton_summary.txt"

    lines = [
        "Strong Interaction Minimal Pipeline - Skeleton Summary",
        "=" * 60,
        f"Root: {ROOT}",
        f"Input file: {INPUT_FILE}",
        "",
        "Directory check:",
        f"- Created or recovered directories: {len(created_dirs)}",
    ]

    if created_dirs:
        lines.append("- Directory list:")
        lines.extend([f"  - {path}" for path in created_dirs])

    lines.extend([
        "",
        "Input check:",
        f"- Template input created: {template_created}",
        f"- Input schema valid: {schema_ok}",
        f"- Row count: {row_count}",
    ])

    if missing_columns:
        lines.append("- Missing columns:")
        lines.extend([f"  - {col}" for col in missing_columns])

    lines.extend([
        "",
        "Interpretation:",
        "- This is only a skeleton-stage check.",
        "- No empirical validation is claimed at this stage.",
        "- The current input template is a structural planning table, not final measured data.",
        "- The next stage should preserve the standard baseline before adding the structural interpretation layer.",
    ])

    summary_path.write_text("\n".join(lines), encoding="utf-8")

    handoff_path = ROOT / "docs" / "validation_summary" / "strong_interaction_handoff_summary.txt"
    handoff_path.write_text("\n".join(lines), encoding="utf-8")

    return summary_path


def main() -> None:
    created_dirs = ensure_directories()
    template_created = create_template_input_if_missing()
    schema_ok, missing_columns, row_count = validate_input_schema()

    summary_path = write_summary(
        created_dirs=created_dirs,
        template_created=template_created,
        schema_ok=schema_ok,
        missing_columns=missing_columns,
        row_count=row_count,
    )

    print("Skeleton check complete.")
    print(f"Root: {ROOT}")
    print(f"Input: {INPUT_FILE}")
    print(f"Schema valid: {schema_ok}")
    print(f"Rows: {row_count}")
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()