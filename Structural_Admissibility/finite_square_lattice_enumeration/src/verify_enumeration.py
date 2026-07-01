#!/usr/bin/env python3
"""Verify the generated finite-lattice enumeration outputs against manuscript values."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from enumerate_square_lattice import EXPECTED_DISTRIBUTION, EXPECTED_TOTAL, finite_failure_witnesses


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "results",
        help="Directory containing enumeration_summary.json and finite_failure_witnesses.json.",
    )
    args = parser.parse_args()

    summary_path = args.results_dir / "enumeration_summary.json"
    witness_path = args.results_dir / "finite_failure_witnesses.json"
    if not summary_path.exists() or not witness_path.exists():
        raise SystemExit("Missing outputs. Run enumerate_square_lattice.py first.")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    witnesses = json.loads(witness_path.read_text(encoding="utf-8"))
    distribution = {int(key): int(value) for key, value in summary["distribution"].items()}

    assert summary["lattice_vertices"] == 9
    assert summary["lattice_relations"] == 12
    assert summary["selected_domains_examined"] == 512
    assert distribution == EXPECTED_DISTRIBUTION
    assert summary["admissible_configuration_total"] == EXPECTED_TOTAL
    assert witnesses == finite_failure_witnesses()
    assert all(witnesses.values())

    print("Verification passed: 512 domains, expected distribution, total 21799, and all finite witnesses.")


if __name__ == "__main__":
    main()
