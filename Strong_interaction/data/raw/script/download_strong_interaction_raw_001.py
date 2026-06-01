# data/raw/script/download_strong_interaction_raw_001.py

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import csv
import re
import sys


ROOT = Path(r"D:\Paper\Dimensional_Structural_Describability\Strong_interaction")

RAW_SCRIPT_DIR = ROOT / "data" / "raw" / "script"
REFERENCES_DIR = ROOT / "data" / "raw" / "references"
SOURCE_TABLES_DIR = ROOT / "data" / "raw" / "source_tables"

REFERENCE_REGISTRY_CSV = REFERENCES_DIR / "reference_registry_raw_001.csv"
DOWNLOAD_MANIFEST_CSV = REFERENCES_DIR / "download_manifest_raw_001.csv"

PDG_OUTPUT_CSV = SOURCE_TABLES_DIR / "pdg_mass_width_raw_001.csv"
NIST_OUTPUT_CSV = SOURCE_TABLES_DIR / "nist_codata_constants_raw_001.csv"
SEED_CASES_CSV = SOURCE_TABLES_DIR / "strong_interaction_seed_cases_raw_001.csv"

SOURCES = [
    {
        "source_id": "PDG_MASS_WIDTH_2025",
        "source_type": "data_table",
        "title": "PDG masses, widths, and Monte Carlo particle ID numbers from 2025 RPP",
        "url": "https://pdg.lbl.gov/2025/mcdata/mass_width_2025.txt",
        "local_output": str(PDG_OUTPUT_CSV),
        "role_in_project": "particle mass-width source table; raw standard-baseline data",
        "status": "active_download",
        "notes": "Fixed-width PDG table. Values are raw PDG file values; unit interpretation must be checked before derived physical use.",
    },
    {
        "source_id": "NIST_CODATA_2022_ALLASCII",
        "source_type": "data_table",
        "title": "NIST CODATA 2022 fundamental physical constants complete ASCII listing",
        "url": "https://physics.nist.gov/cuu/Constants/Table/allascii.txt",
        "local_output": str(NIST_OUTPUT_CSV),
        "role_in_project": "fundamental constants source table; c and unit conversion support",
        "status": "active_download",
        "notes": "Complete ASCII listing from NIST constants database.",
    },
    {
        "source_id": "HEPDATA_CSV_FORMAT_REFERENCE",
        "source_type": "reference",
        "title": "HEPData file formats, including CSV",
        "url": "https://www.hepdata.net/formats",
        "local_output": "",
        "role_in_project": "future candidate source for publication-level experimental tables",
        "status": "reference_only",
        "notes": "No HEPData table is downloaded in this minimal script. Add specific HEPData table URLs later if needed.",
    },
    {
        "source_id": "PDG_API_REFERENCE",
        "source_type": "reference",
        "title": "PDG API documentation and machine-readable access",
        "url": "https://pdgweb.lbl.gov/2025/api/index.html",
        "local_output": "",
        "role_in_project": "future candidate source for structured PDG access",
        "status": "reference_only",
        "notes": "This minimal script uses the fixed-width mass_width file instead of the PDG API.",
    },
]


SEED_CASE_ROWS = [
    {
        "case_id": "A001",
        "case_type": "free_radiation",
        "system_name": "single_photon",
        "standard_baseline": "massless individual radiation component; no rest frame",
        "structural_reading": "energy present but not mass-describable as a bounded rest structure",
        "data_status": "seed_template_not_measurement",
        "preferred_source_id": "PDG_MASS_WIDTH_2025",
        "notes": "Use as conceptual contrast case. Do not treat as validation result.",
    },
    {
        "case_id": "B001",
        "case_type": "bounded_radiation_system",
        "system_name": "opposite_direction_photon_pair",
        "standard_baseline": "system invariant mass can be defined if total momentum is zero",
        "structural_reading": "massless components may form a system-level mass-describable configuration",
        "data_status": "seed_template_not_measurement",
        "preferred_source_id": "NIST_CODATA_2022_ALLASCII",
        "notes": "Requires later derived calculation using energy-momentum relation.",
    },
    {
        "case_id": "C001",
        "case_type": "qcd_confined_hadron",
        "system_name": "proton",
        "standard_baseline": "hadron rest mass is not merely the sum of bare constituent quark masses",
        "structural_reading": "QCD-confined structural energy can be read as rest-mass describability of a bounded field configuration",
        "data_status": "seed_template_not_measurement",
        "preferred_source_id": "PDG_MASS_WIDTH_2025",
        "notes": "Later standard step should preserve PDG hadron masses and avoid QCD replacement claims.",
    },
    {
        "case_id": "D001",
        "case_type": "annihilation_transition",
        "system_name": "electron_positron_annihilation",
        "standard_baseline": "QED baseline preserved; no derivation or replacement claim",
        "structural_reading": "transition from massive particle description to radiative final-state description",
        "data_status": "seed_template_not_measurement",
        "preferred_source_id": "PDG_MASS_WIDTH_2025",
        "notes": "Keep as subordinate case under mass-boundedness discussion.",
    },
]


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def ensure_dirs() -> None:
    for path in [RAW_SCRIPT_DIR, REFERENCES_DIR, SOURCE_TABLES_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def download_text(url: str, timeout: int = 30) -> tuple[bool, str, str]:
    request = Request(
        url,
        headers={
            "User-Agent": "Dimensional-Structural-Describability-Minimal-Pipeline/0.1"
        },
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read()
            encoding = response.headers.get_content_charset() or "utf-8"
            text = raw.decode(encoding, errors="replace")
            return True, text, ""
    except HTTPError as exc:
        return False, "", f"HTTPError {exc.code}: {exc.reason}"
    except URLError as exc:
        return False, "", f"URLError: {exc.reason}"
    except TimeoutError:
        return False, "", "TimeoutError"
    except Exception as exc:
        return False, "", f"{type(exc).__name__}: {exc}"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_reference_registry() -> None:
    fieldnames = [
        "source_id",
        "source_type",
        "title",
        "url",
        "local_output",
        "role_in_project",
        "status",
        "notes",
        "created_utc",
    ]

    rows = []
    for source in SOURCES:
        row = dict(source)
        row["created_utc"] = now_utc_iso()
        rows.append(row)

    write_csv(REFERENCE_REGISTRY_CSV, fieldnames, rows)


def parse_pdg_mass_width(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")

        if not line.strip():
            continue
        if line.lstrip().startswith("*"):
            continue
        if len(line) < 70:
            continue

        # PDG file fixed-width layout is documented inside the file:
        # 1-8, 9-16, 17-24, 25-32: MC IDs / charge states
        # 34-51: mass central value
        # 53-60: mass positive error
        # 62-69: mass negative error
        # 71-88: width central value
        # 90-97: width positive error
        # 99-106: width negative error
        # 108-128: particle name
        mc_ids = [
            line[0:8].strip(),
            line[8:16].strip(),
            line[16:24].strip(),
            line[24:32].strip(),
        ]

        row = {
            "source_id": "PDG_MASS_WIDTH_2025",
            "mc_id_1": mc_ids[0],
            "mc_id_2": mc_ids[1],
            "mc_id_3": mc_ids[2],
            "mc_id_4": mc_ids[3],
            "mass_value_raw": line[33:51].strip(),
            "mass_pos_error_raw": line[52:60].strip(),
            "mass_neg_error_raw": line[61:69].strip(),
            "width_value_raw": line[70:88].strip(),
            "width_pos_error_raw": line[89:97].strip(),
            "width_neg_error_raw": line[98:106].strip(),
            "particle_name_raw": line[107:128].strip(),
            "raw_line": line,
            "unit_note": "Raw PDG mass_width file values. Confirm units before derived use.",
        }

        if any(row[key] for key in ["mc_id_1", "mass_value_raw", "particle_name_raw"]):
            rows.append(row)

    return rows


def parse_nist_allascii(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")
        stripped = line.strip()

        if not stripped:
            continue
        if stripped.startswith("Fundamental Physical Constants"):
            continue
        if stripped.startswith("From:"):
            continue
        if stripped.startswith("Quantity"):
            continue
        if set(stripped) <= {"-", " "}:
            continue

        parts = re.split(r"\s{2,}", stripped)

        if len(parts) < 3:
            continue

        quantity = parts[0].strip()
        value = parts[1].strip() if len(parts) > 1 else ""
        uncertainty = parts[2].strip() if len(parts) > 2 else ""
        unit = " ".join(parts[3:]).strip() if len(parts) > 3 else ""

        rows.append(
            {
                "source_id": "NIST_CODATA_2022_ALLASCII",
                "quantity": quantity,
                "value_raw": value,
                "uncertainty_raw": uncertainty,
                "unit_raw": unit,
                "raw_line": line,
            }
        )

    return rows


def write_seed_cases() -> None:
    fieldnames = [
        "case_id",
        "case_type",
        "system_name",
        "standard_baseline",
        "structural_reading",
        "data_status",
        "preferred_source_id",
        "notes",
    ]
    write_csv(SEED_CASES_CSV, fieldnames, SEED_CASE_ROWS)


def main() -> int:
    ensure_dirs()
    write_reference_registry()
    write_seed_cases()

    manifest_rows: list[dict[str, str]] = []

    for source in SOURCES:
        if source["status"] != "active_download":
            manifest_rows.append(
                {
                    "source_id": source["source_id"],
                    "url": source["url"],
                    "attempted": "false",
                    "success": "",
                    "output_file": source["local_output"],
                    "row_count": "",
                    "error": "reference_only",
                    "downloaded_utc": now_utc_iso(),
                }
            )
            continue

        success, text, error = download_text(source["url"])

        row_count = 0

        if success and source["source_id"] == "PDG_MASS_WIDTH_2025":
            parsed = parse_pdg_mass_width(text)
            row_count = len(parsed)
            write_csv(
                PDG_OUTPUT_CSV,
                [
                    "source_id",
                    "mc_id_1",
                    "mc_id_2",
                    "mc_id_3",
                    "mc_id_4",
                    "mass_value_raw",
                    "mass_pos_error_raw",
                    "mass_neg_error_raw",
                    "width_value_raw",
                    "width_pos_error_raw",
                    "width_neg_error_raw",
                    "particle_name_raw",
                    "raw_line",
                    "unit_note",
                ],
                parsed,
            )

        elif success and source["source_id"] == "NIST_CODATA_2022_ALLASCII":
            parsed = parse_nist_allascii(text)
            row_count = len(parsed)
            write_csv(
                NIST_OUTPUT_CSV,
                [
                    "source_id",
                    "quantity",
                    "value_raw",
                    "uncertainty_raw",
                    "unit_raw",
                    "raw_line",
                ],
                parsed,
            )

        manifest_rows.append(
            {
                "source_id": source["source_id"],
                "url": source["url"],
                "attempted": "true",
                "success": str(success).lower(),
                "output_file": source["local_output"],
                "row_count": str(row_count),
                "error": error,
                "downloaded_utc": now_utc_iso(),
            }
        )

    write_csv(
        DOWNLOAD_MANIFEST_CSV,
        [
            "source_id",
            "url",
            "attempted",
            "success",
            "output_file",
            "row_count",
            "error",
            "downloaded_utc",
        ],
        manifest_rows,
    )

    print("Raw download step complete.")
    print(f"Reference registry: {REFERENCE_REGISTRY_CSV}")
    print(f"Download manifest:  {DOWNLOAD_MANIFEST_CSV}")
    print(f"PDG source table:   {PDG_OUTPUT_CSV}")
    print(f"NIST source table:  {NIST_OUTPUT_CSV}")
    print(f"Seed cases table:   {SEED_CASES_CSV}")

    failures = [row for row in manifest_rows if row["attempted"] == "true" and row["success"] != "true"]
    if failures:
        print("\nSome downloads failed. Check download_manifest_raw_001.csv.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())