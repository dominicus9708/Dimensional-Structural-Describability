# src/standard/script/run_strong_interaction_standard_001.py

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import argparse
import csv
import math
import sys


ROOT = Path(r"D:\Paper\Dimensional_Structural_Describability\Strong_interaction")

INPUT_DIR = ROOT / "data" / "derived" / "input"
STANDARD_SCRIPT_DIR = ROOT / "src" / "standard" / "script"
RESULTS_STANDARD_DIR = ROOT / "results" / "standard"

MINIMAL_INPUT_CSV = INPUT_DIR / "strong_interaction_minimal_input.csv"
SELECTED_PARTICLES_CSV = INPUT_DIR / "strong_interaction_selected_particles_input_001.csv"
SELECTED_CONSTANTS_CSV = INPUT_DIR / "strong_interaction_selected_constants_input_001.csv"
INPUT_MANIFEST_CSV = INPUT_DIR / "strong_interaction_input_manifest_001.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return [dict(row) for row in csv.DictReader(f)]


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


def parse_float(value: object) -> float | None:
    text = clean_text(value)
    if not text:
        return None

    text = text.replace(",", "").replace(" ", "")
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


def nearly_equal(a: float | None, b: float | None, rel_tol: float = 1e-6, abs_tol: float = 1e-9) -> bool:
    if a is None or b is None:
        return False
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


def get_particle_map(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {
        clean_text(row.get("particle_key")): row
        for row in rows
        if clean_text(row.get("particle_key"))
    }


def particle_mass_mev(particle_map: dict[str, dict[str, str]], key: str) -> float | None:
    row = particle_map.get(key)
    if not row:
        return None
    return parse_float(row.get("mass_MeV_c2"))


def build_standard_case_summary(
    minimal_rows: list[dict[str, str]],
    particle_rows: list[dict[str, str]],
    two_photon_each_energy_mev: float,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    particle_map = get_particle_map(particle_rows)

    electron_mass = particle_mass_mev(particle_map, "electron")
    proton_mass = particle_mass_mev(particle_map, "proton")
    neutron_mass = particle_mass_mev(particle_map, "neutron")
    up_mass = particle_mass_mev(particle_map, "up_quark")
    down_mass = particle_mass_mev(particle_map, "down_quark")

    case_summary: list[dict[str, object]] = []
    numeric_checks: list[dict[str, object]] = []

    for row in minimal_rows:
        case_id = clean_text(row.get("case_id"))
        case_type = clean_text(row.get("case_type"))
        system_name = clean_text(row.get("system_name"))

        invariant_mass = parse_float(row.get("invariant_mass_MeV_c2"))
        constituent_sum = parse_float(row.get("constituent_rest_mass_sum_MeV_c2"))
        mass_gap = parse_float(row.get("mass_gap_MeV_c2"))
        gap_fraction = parse_float(row.get("mass_gap_fraction_of_system_mass"))

        status = "pass"
        standard_result = ""
        warning_note = ""
        computed_value = None
        computed_label = ""

        if case_id == "A001":
            computed_label = "single_photon_rest_mass_MeV_c2"
            computed_value = invariant_mass

            if nearly_equal(invariant_mass, 0.0):
                standard_result = "Photon massless baseline preserved."
            else:
                status = "warning"
                standard_result = "Photon massless baseline not preserved."
                warning_note = "Expected photon invariant mass to be zero."

        elif case_id == "B001":
            # 주의점:
            # B001은 입력 CSV에 에너지 매개변수가 비어 있으므로,
            # 여기서는 표준 진단용 기본값을 사용한다.
            # 이것은 측정값이나 이론 검증값이 아니다.
            photon_pair_total_energy = 2.0 * two_photon_each_energy_mev

            # Natural-unit diagnostic:
            # For two photons with equal opposite momenta, p_total = 0,
            # therefore M_system c^2 = E_total.
            computed_label = "two_photon_system_invariant_mass_MeV_c2_diagnostic"
            computed_value = photon_pair_total_energy

            status = "diagnostic"
            standard_result = (
                "Two-photon opposite-momentum system has a system-level invariant mass "
                "when total momentum is zero."
            )
            warning_note = (
                "Diagnostic value only. Each photon energy was supplied by script parameter, "
                "not by measured input data."
            )

        elif case_id == "C001P":
            expected_constituent_sum = None
            if up_mass is not None and down_mass is not None:
                expected_constituent_sum = up_mass + up_mass + down_mass

            computed_label = "proton_mass_gap_fraction"
            computed_value = gap_fraction

            if proton_mass is None or expected_constituent_sum is None:
                status = "warning"
                standard_result = "Missing proton or quark reference mass."
                warning_note = "Cannot perform standard baseline gap check."
            else:
                expected_gap = proton_mass - expected_constituent_sum
                expected_fraction = expected_gap / proton_mass if proton_mass else None

                numeric_checks.append(
                    {
                        "check_id": "C001P_gap_recompute",
                        "case_id": case_id,
                        "quantity": "proton_mass_minus_uud_reference_sum",
                        "input_value": fmt(mass_gap),
                        "recomputed_value": fmt(expected_gap),
                        "difference": fmt((mass_gap - expected_gap) if mass_gap is not None else None),
                        "status": "pass" if nearly_equal(mass_gap, expected_gap, rel_tol=1e-9) else "warning",
                        "note": "Current quark mass reference is not a full QCD decomposition.",
                    }
                )

                if expected_fraction is not None and expected_fraction > 0.9:
                    standard_result = "Proton mass is not exhausted by the minimal u+u+d quark mass reference."
                else:
                    status = "warning"
                    standard_result = "Proton mass gap fraction is not in expected qualitative range."
                    warning_note = "Check PDG quark mass convention and input units."

        elif case_id == "C001N":
            expected_constituent_sum = None
            if up_mass is not None and down_mass is not None:
                expected_constituent_sum = up_mass + down_mass + down_mass

            computed_label = "neutron_mass_gap_fraction"
            computed_value = gap_fraction

            if neutron_mass is None or expected_constituent_sum is None:
                status = "warning"
                standard_result = "Missing neutron or quark reference mass."
                warning_note = "Cannot perform standard baseline gap check."
            else:
                expected_gap = neutron_mass - expected_constituent_sum
                expected_fraction = expected_gap / neutron_mass if neutron_mass else None

                numeric_checks.append(
                    {
                        "check_id": "C001N_gap_recompute",
                        "case_id": case_id,
                        "quantity": "neutron_mass_minus_udd_reference_sum",
                        "input_value": fmt(mass_gap),
                        "recomputed_value": fmt(expected_gap),
                        "difference": fmt((mass_gap - expected_gap) if mass_gap is not None else None),
                        "status": "pass" if nearly_equal(mass_gap, expected_gap, rel_tol=1e-9) else "warning",
                        "note": "Current quark mass reference is not a full QCD decomposition.",
                    }
                )

                if expected_fraction is not None and expected_fraction > 0.9:
                    standard_result = "Neutron mass is not exhausted by the minimal u+d+d quark mass reference."
                else:
                    status = "warning"
                    standard_result = "Neutron mass gap fraction is not in expected qualitative range."
                    warning_note = "Check PDG quark mass convention and input units."

        elif case_id == "D001":
            expected_threshold = 2.0 * electron_mass if electron_mass is not None else None
            input_total_energy = parse_float(row.get("total_energy_MeV"))

            computed_label = "electron_positron_threshold_energy_MeV"
            computed_value = expected_threshold

            numeric_checks.append(
                {
                    "check_id": "D001_threshold_recompute",
                    "case_id": case_id,
                    "quantity": "2_times_electron_mass",
                    "input_value": fmt(input_total_energy),
                    "recomputed_value": fmt(expected_threshold),
                    "difference": fmt((input_total_energy - expected_threshold) if input_total_energy is not None and expected_threshold is not None else None),
                    "status": "pass" if nearly_equal(input_total_energy, expected_threshold, rel_tol=1e-9) else "warning",
                    "note": "Threshold reference only. QED transition rules are not derived or replaced.",
                }
            )

            if nearly_equal(input_total_energy, expected_threshold, rel_tol=1e-9):
                standard_result = "Electron-positron threshold rest-energy reference preserved."
            else:
                status = "warning"
                standard_result = "Electron-positron threshold rest-energy reference mismatch."
                warning_note = "Check electron mass input and D001 total_energy_MeV."

        else:
            status = "manual_review"
            standard_result = "Unknown case type or case_id."
            warning_note = "Manual review required."

        case_summary.append(
            {
                "case_id": case_id,
                "case_type": case_type,
                "system_name": system_name,
                "standard_status": status,
                "computed_label": computed_label,
                "computed_value": fmt(computed_value),
                "invariant_mass_MeV_c2": clean_text(row.get("invariant_mass_MeV_c2")),
                "constituent_rest_mass_sum_MeV_c2": clean_text(row.get("constituent_rest_mass_sum_MeV_c2")),
                "mass_gap_MeV_c2": clean_text(row.get("mass_gap_MeV_c2")),
                "mass_gap_fraction_of_system_mass": clean_text(row.get("mass_gap_fraction_of_system_mass")),
                "standard_result": standard_result,
                "warning_note": warning_note,
                "caution_note": clean_text(row.get("caution_note")),
            }
        )

    return case_summary, numeric_checks


def write_summary_txt(
    path: Path,
    output_dir: Path,
    case_summary: list[dict[str, object]],
    numeric_checks: list[dict[str, object]],
    two_photon_each_energy_mev: float,
) -> None:
    pass_count = sum(1 for row in case_summary if row["standard_status"] == "pass")
    diagnostic_count = sum(1 for row in case_summary if row["standard_status"] == "diagnostic")
    warning_count = sum(1 for row in case_summary if row["standard_status"] == "warning")
    manual_count = sum(1 for row in case_summary if row["standard_status"] == "manual_review")

    lines = [
        "Strong Interaction Minimal Pipeline - Standard Stage Summary",
        "=" * 70,
        f"Output directory: {output_dir}",
        f"Input directory: {INPUT_DIR}",
        "",
        "Stage interpretation:",
        "- This is a standard-baseline check only.",
        "- No Dimensional-Structural Describability validation is claimed here.",
        "- No QED, QCD, or mass-energy relation replacement is claimed.",
        "- B001 uses a diagnostic photon energy parameter because measured photon-pair energy was not supplied in the input.",
        "",
        "B001 diagnostic parameter:",
        f"- each photon energy: {two_photon_each_energy_mev} MeV",
        f"- two-photon total energy: {2.0 * two_photon_each_energy_mev} MeV",
        "- For equal opposite momenta, the system-level invariant mass diagnostic is M = E_total in natural units.",
        "",
        "Case status counts:",
        f"- pass: {pass_count}",
        f"- diagnostic: {diagnostic_count}",
        f"- warning: {warning_count}",
        f"- manual_review: {manual_count}",
        "",
        "Case summaries:",
    ]

    for row in case_summary:
        lines.extend(
            [
                f"- {row['case_id']} | {row['system_name']} | {row['standard_status']}",
                f"  result: {row['standard_result']}",
                f"  computed: {row['computed_label']} = {row['computed_value']}",
            ]
        )
        if row.get("warning_note"):
            lines.append(f"  warning: {row['warning_note']}")
        if row.get("caution_note"):
            lines.append(f"  caution: {row['caution_note']}")

    lines.extend(
        [
            "",
            "Numeric checks:",
        ]
    )

    if not numeric_checks:
        lines.append("- No numeric checks generated.")
    else:
        for row in numeric_checks:
            lines.extend(
                [
                    f"- {row['check_id']} | {row['status']}",
                    f"  quantity: {row['quantity']}",
                    f"  input: {row['input_value']}",
                    f"  recomputed: {row['recomputed_value']}",
                    f"  difference: {row['difference']}",
                    f"  note: {row['note']}",
                ]
            )

    lines.extend(
        [
            "",
            "Next stage:",
            "- The structural stage may use this output as preserved standard baseline.",
            "- Structural interpretation must not overwrite the standard values.",
            "- QCD hadron mass gaps should be treated as standard-baseline comparison variables, not proof of the theory.",
        ]
    )

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run standard-baseline checks for the Strong_interaction minimal pipeline."
    )
    parser.add_argument(
        "--two-photon-each-energy-mev",
        type=float,
        default=1.0,
        help="Diagnostic energy assigned to each photon in B001. Default: 1.0 MeV.",
    )
    args = parser.parse_args()

    STANDARD_SCRIPT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = RESULTS_STANDARD_DIR / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        minimal_rows = read_csv(MINIMAL_INPUT_CSV)
        particle_rows = read_csv(SELECTED_PARTICLES_CSV)
        constant_rows = read_csv(SELECTED_CONSTANTS_CSV)
        manifest_rows = read_csv(INPUT_MANIFEST_CSV)

        case_summary, numeric_checks = build_standard_case_summary(
            minimal_rows=minimal_rows,
            particle_rows=particle_rows,
            two_photon_each_energy_mev=args.two_photon_each_energy_mev,
        )

        write_csv(
            output_dir / "standard_case_summary_001.csv",
            [
                "case_id",
                "case_type",
                "system_name",
                "standard_status",
                "computed_label",
                "computed_value",
                "invariant_mass_MeV_c2",
                "constituent_rest_mass_sum_MeV_c2",
                "mass_gap_MeV_c2",
                "mass_gap_fraction_of_system_mass",
                "standard_result",
                "warning_note",
                "caution_note",
            ],
            case_summary,
        )

        write_csv(
            output_dir / "standard_numeric_checks_001.csv",
            [
                "check_id",
                "case_id",
                "quantity",
                "input_value",
                "recomputed_value",
                "difference",
                "status",
                "note",
            ],
            numeric_checks,
        )

        run_manifest = [
            {
                "stage": "standard_baseline_check",
                "input_file": str(MINIMAL_INPUT_CSV),
                "output_file": str(output_dir / "standard_case_summary_001.csv"),
                "row_count": len(case_summary),
                "status": "success",
                "note": "Standard-baseline case summary generated.",
                "created_at": timestamp,
            },
            {
                "stage": "standard_numeric_checks",
                "input_file": str(SELECTED_PARTICLES_CSV),
                "output_file": str(output_dir / "standard_numeric_checks_001.csv"),
                "row_count": len(numeric_checks),
                "status": "success",
                "note": "Numeric standard consistency checks generated.",
                "created_at": timestamp,
            },
            {
                "stage": "input_support_files_loaded",
                "input_file": f"{SELECTED_CONSTANTS_CSV};{INPUT_MANIFEST_CSV}",
                "output_file": "",
                "row_count": len(constant_rows) + len(manifest_rows),
                "status": "success",
                "note": "Selected constants and input manifest were loaded for provenance check.",
                "created_at": timestamp,
            },
        ]

        write_csv(
            output_dir / "standard_run_manifest_001.csv",
            [
                "stage",
                "input_file",
                "output_file",
                "row_count",
                "status",
                "note",
                "created_at",
            ],
            run_manifest,
        )

        write_summary_txt(
            path=output_dir / "standard_summary_001.txt",
            output_dir=output_dir,
            case_summary=case_summary,
            numeric_checks=numeric_checks,
            two_photon_each_energy_mev=args.two_photon_each_energy_mev,
        )

    except Exception as exc:
        error_path = output_dir / "standard_error_001.txt"
        error_path.write_text(
            f"Standard stage failed.\n{type(exc).__name__}: {exc}\n",
            encoding="utf-8",
        )
        print("Standard stage failed.")
        print(f"{type(exc).__name__}: {exc}")
        print(f"Error log: {error_path}")
        return 1

    print("Standard stage complete.")
    print(f"Output directory: {output_dir}")
    print(f"Case summary:     {output_dir / 'standard_case_summary_001.csv'}")
    print(f"Numeric checks:   {output_dir / 'standard_numeric_checks_001.csv'}")
    print(f"Run manifest:     {output_dir / 'standard_run_manifest_001.csv'}")
    print(f"Summary txt:      {output_dir / 'standard_summary_001.txt'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())