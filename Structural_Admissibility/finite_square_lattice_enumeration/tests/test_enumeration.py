#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from enumerate_square_lattice import (  # noqa: E402
    EXPECTED_DISTRIBUTION,
    EXPECTED_TOTAL,
    enumerate_lattice,
    finite_failure_witnesses,
)


class FiniteSquareLatticeEnumerationTests(unittest.TestCase):
    def test_enumeration_matches_manuscript_values(self) -> None:
        result = enumerate_lattice()
        self.assertEqual(result["lattice_vertices"], 9)
        self.assertEqual(result["lattice_relations"], 12)
        self.assertEqual(result["selected_domains_examined"], 512)
        self.assertEqual(result["distribution"], EXPECTED_DISTRIBUTION)
        self.assertEqual(result["admissible_configuration_total"], EXPECTED_TOTAL)

    def test_failure_witnesses(self) -> None:
        self.assertTrue(all(finite_failure_witnesses().values()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
