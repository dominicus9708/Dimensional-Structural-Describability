# data/derived/script/build_strong_interaction_input_001.py

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import csv
import math
import re
import sys


ROOT = Path(r"D:\Paper\Dimensional_Structural_Describability\Strong_interaction")

CLEANED_TABLES_DIR = ROOT / "data" / "derived" / "cleaned_tables"
INPUT_DIR = ROOT / "data" / "derived" / "input"

CLEANED_PDG_FULL = CLEANED_TABLES_DIR / "pdg_mass_width_cleaned_full_001.csv"
CLEANED_NIST_SELECTED = CLEANED_TABLES_DIR / "nist_constants_cleaned_selected_001.csv"
CLEANED_CASES = CLEANED_TABLES_DIR / "strong_interaction_cases_cleaned_001.csv"
CLEANED_REFERENCE_REGISTRY = CLEANED_TABLES_DIR / "reference_registry_cleaned_001.csv"
CLEANED_DOWNLOAD_MANIFEST = CLEANED_TABLES_DIR / "download_manifest_cleaned_001.csv"

OUT_MINIMAL_INPUT = INPUT_DIR / "strong_interaction_minimal_input.csv"
OUT_SELECTED_PARTICLES = INPUT_DIR / "strong_interaction_selected_particles_input_001.csv"
OUT_SELECTED_CONSTANTS = INPUT_DIR / "strong_interaction_selected_constants_input_001.csv"
OUT_INPUT_MANIFEST = INPUT_DIR / "strong_interaction_input_manifest_001.csv"


SELECTED_PARTICLE_SPECS = [
    {
        "particle_key": "photon",
        "expected_core": "gamma",
        "expected_charge": "0",
        "standard_role": "free_radiation_baseline",
        "structural_role": "energy_present_but_no_individual_rest_mass",
    },
    {
        "particle_key": "gluon",
        "expected_core": "g",
        "expected_charge": "0",
        "standard_role": "qcd_field_component",
        "structural_role": "massless_field_component_in_qcd_confinement_context",
    },
    {
        "particle_key": "electron",
        "expected_core": "e",
        "expected_charge": "-",
        "standard_role": "annihilation_transition_baseline",
        "structural_role": "massive_fermionic_component",
    },
    {
        "particle_key": "proton",
        "expected_core": "p",
        "expected_charge": "+",
        "standard_role": "qcd_confined_hadron_baseline",
        "structural_role": "bounded_qcd_hadron_mass_describability",
    },
    {
        "particle_key": "neutron",
        "expected_core": "n",
        "expected_charge": "0",
        "standard_role": "qcd_confined_hadron_baseline",
        "structural_role": "bounded_qcd_hadron_mass_describability",
    },
    {
        "particle_key": "up_quark",
        "expected_core": "u",
        "expected_charge": "+2/3",
        "standard_role": "constituent_quark_mass_reference",
        "structural_role": "quark_mass_reference_not_total_hadron_mass",
    },
    {
        "particle_key": "down_quark",
        "expected_core": "d",
        "expected_charge": "-1/3",
        "standard_role": "constituent_quark_mass_reference",
        "structural_role": "quark_mass_reference_not_total_hadron_mass",
    },
    {
        "particle_key": "strange_quark",
        "expected_core": "s",
        "expected_charge": "-1/3",
        "standard_role": "constituent_quark_mass_reference",
        "structural_role": "quark_mass_reference_not_total_hadron_mass",
    },
]


INPUT_COLUMNS = [
    "case_id",
    "case_type",
    "system_name",
    "input_status",
    "standard_baseline",
    "component_description",
    "constituent_keys",
    "total_energy_MeV",
    "invariant_mass_MeV_c2",
    "constituent_rest_mass_sum_MeV_c2",
    "mass_gap_MeV_c2",
    "mass_gap_fraction_of_system_mass",
    "standard_interpretation",
    "structural_boundedness_level",
    "mass_describability_class",
    "structural_reading",
    "source_ids",
    "source_note",
    "caution_note",
]


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def ensure_dirs() -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)


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


def parse_float(value: object) -> float | None:
    text = clean_text(value)
    if not text:
        return None

    text = text.replace("...", "")
    text = text.replace(" ", "")
    text = text.replace(",", "")

    try:
        result = float(text)
    except ValueError:
        return None

    if math.isnan(result) or math.isinf(result):
        return None

    return result


def fmt(value: float | None, digits: int = 12) -> str:
    if value is None:
        return ""
    return f"{value:.{digits}g}"


def split_pdg_particle_name(particle_name_norm: str) -> tuple[str, str]:
    """
    Examples:
    - 'gamma 0' -> ('gamma', '0')
    - 'g 0' -> ('g', '0')
    - 'e -' -> ('e', '-')
    - 'p +' -> ('p', '+')
    - 'n 0' -> ('n', '0')
    - 'u +2/3' -> ('u', '+2/3')
    """
    text = normalize_space(particle_name_norm.lower())
    if not text:
        return "", ""

    parts = text.split(" ")
    if len(parts) == 1:
        return parts[0], ""

    charge_candidate = parts[-1]
    known_charge_tokens = {
        "0",
        "+",
        "-",
        "+2/3",
        "-1/3",
        "+1/3",
        "-2/3",
        "+1",
        "-1",
        "+2",
        "-2",
    }

    if charge_candidate in known_charge_tokens:
        return " ".join(parts[:-1]), charge_candidate

    return text, ""


def build_selected_particles(pdg_full_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    selected_rows: list[dict[str, object]] = []

    for spec in SELECTED_PARTICLE_SPECS:
        matched = None

        for row in pdg_full_rows:
            particle_name_norm = clean_text(row.get("particle_name_norm")).lower()
            core, charge = split_pdg_particle_name(particle_name_norm)

            if core == spec["expected_core"] and charge == spec["expected_charge"]:
                matched = row
                break

        if matched is None:
            selected_rows.append(
                {
                    "particle_key": spec["particle_key"],
                    "particle_name_raw": "",
                    "particle_core": spec["expected_core"],
                    "charge_label": spec["expected_charge"],
                    "mc_id_1": "",
                    "mass_GeV_c2": "",
                    "mass_MeV_c2": "",
                    "width_GeV": "",
                    "width_MeV": "",
                    "standard_role": spec["standard_role"],
                    "structural_role": spec["structural_role"],
                    "source_id": "PDG_MASS_WIDTH_2025",
                    "selection_status": "missing_from_cleaned_pdg_full",
                    "selection_note": "Expected particle not found. Check PDG cleaned table and matching rule.",
                    "created_utc": now_utc_iso(),
                }
            )
            continue

        particle_name_norm = clean_text(matched.get("particle_name_norm")).lower()
        core, charge = split_pdg_particle_name(particle_name_norm)

        selected_rows.append(
            {
                "particle_key": spec["particle_key"],
                "particle_name_raw": clean_text(matched.get("particle_name_raw")),
                "particle_core": core,
                "charge_label": charge,
                "mc_id_1": clean_text(matched.get("mc_id_1")),
                "mass_GeV_c2": clean_text(matched.get("mass_GeV_c2")),
                "mass_MeV_c2": clean_text(matched.get("mass_MeV_c2")),
                "width_GeV": clean_text(matched.get("width_GeV")),
                "width_MeV": clean_text(matched.get("width_MeV")),
                "standard_role": spec["standard_role"],
                "structural_role": spec["structural_role"],
                "source_id": clean_text(matched.get("source_id")) or "PDG_MASS_WIDTH_2025",
                "selection_status": "selected",
                "selection_note": "Selected by particle core and charge label from cleaned PDG full table.",
                "created_utc": now_utc_iso(),
            }
        )

    return selected_rows


def build_selected_constants(nist_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    selected_rows: list[dict[str, object]] = []

    for row in nist_rows:
        selected_rows.append(
            {
                "constant_key": clean_text(row.get("constant_key")),
                "quantity": clean_text(row.get("quantity")),
                "value_raw": clean_text(row.get("value_raw")),
                "value_numeric": clean_text(row.get("value_numeric")),
                "uncertainty_raw": clean_text(row.get("uncertainty_raw")),
                "uncertainty_numeric": clean_text(row.get("uncertainty_numeric")),
                "unit_raw": clean_text(row.get("unit_raw")),
                "standard_role": clean_text(row.get("standard_role")),
                "source_id": clean_text(row.get("source_id")),
                "created_utc": now_utc_iso(),
            }
        )

    return selected_rows


def particle_mass(particle_map: dict[str, dict[str, object]], key: str) -> float | None:
    row = particle_map.get(key)
    if not row:
        return None
    return parse_float(row.get("mass_MeV_c2"))


def sum_values(values: list[float | None]) -> float | None:
    if any(value is None for value in values):
        return None
    return sum(value for value in values if value is not None)


def mass_gap(system_mass: float | None, constituent_sum: float | None) -> float | None:
    if system_mass is None or constituent_sum is None:
        return None
    return system_mass - constituent_sum


def mass_gap_fraction(system_mass: float | None, gap: float | None) -> float | None:
    if system_mass is None or gap is None:
        return None
    if system_mass == 0:
        return None
    return gap / system_mass


def make_minimal_input_rows(selected_particles: list[dict[str, object]], cases_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    particle_map = {
        clean_text(row.get("particle_key")): row
        for row in selected_particles
        if clean_text(row.get("selection_status")) == "selected"
    }

    photon_mass = particle_mass(particle_map, "photon")
    electron_mass = particle_mass(particle_map, "electron")
    proton_mass = particle_mass(particle_map, "proton")
    neutron_mass = particle_mass(particle_map, "neutron")
    up_mass = particle_mass(particle_map, "up_quark")
    down_mass = particle_mass(particle_map, "down_quark")

    proton_constituent_sum = sum_values([up_mass, up_mass, down_mass])
    neutron_constituent_sum = sum_values([up_mass, down_mass, down_mass])
    annihilation_initial_rest_sum = sum_values([electron_mass, electron_mass])

    proton_gap = mass_gap(proton_mass, proton_constituent_sum)
    neutron_gap = mass_gap(neutron_mass, neutron_constituent_sum)

    case_note_map = {
        clean_text(row.get("case_type")): row
        for row in cases_rows
    }

    rows: list[dict[str, object]] = []

    rows.append(
        {
            "case_id": "A001",
            "case_type": "free_radiation",
            "system_name": "single_photon",
            "input_status": "standard_baseline_ready",
            "standard_baseline": "massless individual radiation component; no rest frame",
            "component_description": "single photon baseline from PDG mass table",
            "constituent_keys": "photon",
            "total_energy_MeV": "",
            "invariant_mass_MeV_c2": fmt(photon_mass),
            "constituent_rest_mass_sum_MeV_c2": fmt(photon_mass),
            "mass_gap_MeV_c2": "0",
            "mass_gap_fraction_of_system_mass": "",
            "standard_interpretation": "Energy can be present in radiation, but an individual photon has no rest-mass description.",
            "structural_boundedness_level": "unbounded_or_free",
            "mass_describability_class": "energy_present_but_no_individual_rest_mass_description",
            "structural_reading": clean_text(case_note_map.get("free_radiation", {}).get("structural_reading")),
            "source_ids": "PDG_MASS_WIDTH_2025",
            "source_note": "PDG photon mass entry used only as standard baseline.",
            "caution_note": "No claim is made that photon mass is generated or modified.",
        }
    )

    rows.append(
        {
            "case_id": "B001",
            "case_type": "bounded_radiation_system",
            "system_name": "opposite_direction_photon_pair",
            "input_status": "requires_parameter_for_energy",
            "standard_baseline": "system invariant mass can be defined if total momentum is zero",
            "component_description": "two photons with opposite momenta; energy scale to be supplied in standard stage",
            "constituent_keys": "photon;photon",
            "total_energy_MeV": "",
            "invariant_mass_MeV_c2": "",
            "constituent_rest_mass_sum_MeV_c2": "0",
            "mass_gap_MeV_c2": "",
            "mass_gap_fraction_of_system_mass": "",
            "standard_interpretation": "A two-photon system may have a system-level invariant mass if its total momentum vanishes.",
            "structural_boundedness_level": "system_closed_momentum",
            "mass_describability_class": "system_mass_describable_after_energy_parameter",
            "structural_reading": clean_text(case_note_map.get("bounded_radiation_system", {}).get("structural_reading")),
            "source_ids": "PDG_MASS_WIDTH_2025;NIST_CODATA_2022_ALLASCII",
            "source_note": "Requires later standard calculation using supplied photon energies and energy-momentum relation.",
            "caution_note": "This is not individual photon rest mass; it is system invariant mass.",
        }
    )

    rows.append(
        {
            "case_id": "C001P",
            "case_type": "qcd_confined_hadron",
            "system_name": "proton",
            "input_status": "standard_baseline_ready",
            "standard_baseline": "proton rest mass compared with minimal u+u+d quark mass reference",
            "component_description": "QCD-confined hadronic structure; minimal quark mass reference only",
            "constituent_keys": "up_quark;up_quark;down_quark",
            "total_energy_MeV": "",
            "invariant_mass_MeV_c2": fmt(proton_mass),
            "constituent_rest_mass_sum_MeV_c2": fmt(proton_constituent_sum),
            "mass_gap_MeV_c2": fmt(proton_gap),
            "mass_gap_fraction_of_system_mass": fmt(mass_gap_fraction(proton_mass, proton_gap)),
            "standard_interpretation": "The proton mass is not exhausted by the minimal current-quark mass reference.",
            "structural_boundedness_level": "qcd_confined",
            "mass_describability_class": "rest_mass_confined_hadron",
            "structural_reading": "QCD-confined structural energy may be read as a bounded mass-describable configuration without replacing QCD.",
            "source_ids": "PDG_MASS_WIDTH_2025",
            "source_note": "PDG masses used as standard input. Quark masses are reference values, not a complete QCD decomposition.",
            "caution_note": "Do not treat the mass gap as a derived proof of the theory; it is a standard-baseline comparison variable.",
        }
    )

    rows.append(
        {
            "case_id": "C001N",
            "case_type": "qcd_confined_hadron",
            "system_name": "neutron",
            "input_status": "standard_baseline_ready",
            "standard_baseline": "neutron rest mass compared with minimal u+d+d quark mass reference",
            "component_description": "QCD-confined hadronic structure; minimal quark mass reference only",
            "constituent_keys": "up_quark;down_quark;down_quark",
            "total_energy_MeV": "",
            "invariant_mass_MeV_c2": fmt(neutron_mass),
            "constituent_rest_mass_sum_MeV_c2": fmt(neutron_constituent_sum),
            "mass_gap_MeV_c2": fmt(neutron_gap),
            "mass_gap_fraction_of_system_mass": fmt(mass_gap_fraction(neutron_mass, neutron_gap)),
            "standard_interpretation": "The neutron mass is not exhausted by the minimal current-quark mass reference.",
            "structural_boundedness_level": "qcd_confined",
            "mass_describability_class": "rest_mass_confined_hadron",
            "structural_reading": "QCD-confined structural energy may be read as a bounded mass-describable configuration without replacing QCD.",
            "source_ids": "PDG_MASS_WIDTH_2025",
            "source_note": "PDG masses used as standard input. Quark masses are reference values, not a complete QCD decomposition.",
            "caution_note": "Do not treat the mass gap as a derived proof of the theory; it is a standard-baseline comparison variable.",
        }
    )

    rows.append(
        {
            "case_id": "D001",
            "case_type": "annihilation_transition",
            "system_name": "electron_positron_annihilation_threshold",
            "input_status": "standard_baseline_ready",
            "standard_baseline": "QED baseline preserved; threshold rest-energy reference from electron mass",
            "component_description": "electron and positron rest-mass reference before radiative final-state description",
            "constituent_keys": "electron;positron_mass_equal_to_electron",
            "total_energy_MeV": fmt(annihilation_initial_rest_sum),
            "invariant_mass_MeV_c2": fmt(annihilation_initial_rest_sum),
            "constituent_rest_mass_sum_MeV_c2": fmt(annihilation_initial_rest_sum),
            "mass_gap_MeV_c2": "0",
            "mass_gap_fraction_of_system_mass": "0",
            "standard_interpretation": "At threshold, the initial rest-energy scale is twice the electron rest mass; QED is not replaced.",
            "structural_boundedness_level": "transition_case",
            "mass_describability_class": "bounded_massive_to_radiative_structure",
            "structural_reading": clean_text(case_note_map.get("annihilation_transition", {}).get("structural_reading")),
            "source_ids": "PDG_MASS_WIDTH_2025;NIST_CODATA_2022_ALLASCII",
            "source_note": "Electron mass used only for standard threshold reference.",
            "caution_note": "No claim is made about deriving QED, photon production rules, spin rules, or decay rates.",
        }
    )

    return rows


def build_manifest(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "stage": "build_selected_particles_input",
            "input_file": str(CLEANED_PDG_FULL),
            "output_file": str(OUT_SELECTED_PARTICLES),
            "row_count": sum(1 for row in rows if clean_text(row.get("case_type")) != ""),
            "status": "success",
            "notes": "Selected particle support table generated from cleaned PDG full table.",
            "created_utc": now_utc_iso(),
        },
    ]


def main() -> int:
    ensure_dirs()

    manifest_rows: list[dict[str, object]] = []

    try:
        pdg_full_rows = read_csv(CLEANED_PDG_FULL)
        nist_rows = read_csv(CLEANED_NIST_SELECTED)
        cases_rows = read_csv(CLEANED_CASES)

        # Presence checks for supporting cleaned files.
        # These are not directly joined here, but their presence is recorded
        # because they are part of the provenance chain.
        _reference_rows = read_csv(CLEANED_REFERENCE_REGISTRY)
        _download_manifest_rows = read_csv(CLEANED_DOWNLOAD_MANIFEST)

        selected_particles = build_selected_particles(pdg_full_rows)
        selected_constants = build_selected_constants(nist_rows)
        minimal_input_rows = make_minimal_input_rows(selected_particles, cases_rows)

        write_csv(
            OUT_SELECTED_PARTICLES,
            [
                "particle_key",
                "particle_name_raw",
                "particle_core",
                "charge_label",
                "mc_id_1",
                "mass_GeV_c2",
                "mass_MeV_c2",
                "width_GeV",
                "width_MeV",
                "standard_role",
                "structural_role",
                "source_id",
                "selection_status",
                "selection_note",
                "created_utc",
            ],
            selected_particles,
        )

        write_csv(
            OUT_SELECTED_CONSTANTS,
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
                "created_utc",
            ],
            selected_constants,
        )

        write_csv(
            OUT_MINIMAL_INPUT,
            INPUT_COLUMNS,
            minimal_input_rows,
        )

        selected_ok = sum(
            1 for row in selected_particles
            if clean_text(row.get("selection_status")) == "selected"
        )

        manifest_rows.extend(
            [
                {
                    "stage": "build_selected_particles_input",
                    "input_file": str(CLEANED_PDG_FULL),
                    "output_file": str(OUT_SELECTED_PARTICLES),
                    "row_count": len(selected_particles),
                    "status": "success" if selected_ok == len(SELECTED_PARTICLE_SPECS) else "partial",
                    "notes": f"Selected {selected_ok}/{len(SELECTED_PARTICLE_SPECS)} expected particles.",
                    "created_utc": now_utc_iso(),
                },
                {
                    "stage": "build_selected_constants_input",
                    "input_file": str(CLEANED_NIST_SELECTED),
                    "output_file": str(OUT_SELECTED_CONSTANTS),
                    "row_count": len(selected_constants),
                    "status": "success",
                    "notes": "Selected constants copied from cleaned selected constants table.",
                    "created_utc": now_utc_iso(),
                },
                {
                    "stage": "build_minimal_standard_input",
                    "input_file": f"{CLEANED_PDG_FULL};{CLEANED_NIST_SELECTED};{CLEANED_CASES}",
                    "output_file": str(OUT_MINIMAL_INPUT),
                    "row_count": len(minimal_input_rows),
                    "status": "success",
                    "notes": "Official minimal input table generated for standard-stage script.",
                    "created_utc": now_utc_iso(),
                },
            ]
        )

    except Exception as exc:
        manifest_rows.append(
            {
                "stage": "build_input_pipeline",
                "input_file": str(CLEANED_TABLES_DIR),
                "output_file": str(INPUT_DIR),
                "row_count": "",
                "status": "failed",
                "notes": f"{type(exc).__name__}: {exc}",
                "created_utc": now_utc_iso(),
            }
        )
        write_csv(
            OUT_INPUT_MANIFEST,
            [
                "stage",
                "input_file",
                "output_file",
                "row_count",
                "status",
                "notes",
                "created_utc",
            ],
            manifest_rows,
        )
        print("Input build failed.")
        print(f"{type(exc).__name__}: {exc}")
        return 1

    write_csv(
        OUT_INPUT_MANIFEST,
        [
            "stage",
            "input_file",
            "output_file",
            "row_count",
            "status",
            "notes",
            "created_utc",
        ],
        manifest_rows,
    )

    print("Input build step complete.")
    print(f"Official minimal input: {OUT_MINIMAL_INPUT}")
    print(f"Selected particles:      {OUT_SELECTED_PARTICLES}")
    print(f"Selected constants:      {OUT_SELECTED_CONSTANTS}")
    print(f"Input manifest:          {OUT_INPUT_MANIFEST}")

    return 0


if __name__ == "__main__":
    sys.exit(main())