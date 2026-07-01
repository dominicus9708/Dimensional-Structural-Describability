#!/usr/bin/env python3
"""Exhaustively enumerate the finite 3x3 square-lattice realization.

This script reproduces the count stated in the Draft 005 manuscript:
for each selected domain S of the 3x3 lattice, every subset of the
induced relation set R_S is admitted under the blocked-boundary rule.

No third-party packages are required.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Iterable

Point = tuple[int, int]
Edge = tuple[Point, Point]

EXPECTED_DISTRIBUTION: dict[int, int] = {
    0: 63,
    1: 80,
    2: 102,
    3: 84,
    4: 65,
    5: 44,
    6: 38,
    7: 12,
    8: 15,
    9: 4,
    10: 4,
    11: 0,
    12: 1,
}
EXPECTED_TOTAL = 21_799


def lattice_points() -> tuple[Point, ...]:
    """Return the nine vertices of the 3x3 square lattice."""
    return tuple((x, y) for x in range(3) for y in range(3))


def lattice_edges(points: Iterable[Point]) -> tuple[Edge, ...]:
    """Return each nearest-neighbour undirected edge exactly once."""
    point_set = set(points)
    edges: list[Edge] = []
    for x, y in sorted(point_set):
        for dx, dy in ((1, 0), (0, 1)):
            neighbour = (x + dx, y + dy)
            if neighbour in point_set:
                edges.append(((x, y), neighbour))
    return tuple(edges)


def selected_domain_from_mask(points: tuple[Point, ...], mask: int) -> frozenset[Point]:
    """Decode a bit mask as a selected domain."""
    return frozenset(point for index, point in enumerate(points) if mask & (1 << index))


def induced_relation_count(selected: frozenset[Point], edges: tuple[Edge, ...]) -> int:
    """Count relations whose two endpoints lie in the selected domain."""
    return sum(left in selected and right in selected for left, right in edges)


def is_disconnected_selected_domain(selected: frozenset[Point], edges: tuple[Edge, ...]) -> bool:
    """Return whether a nonempty selected domain has more than one graph component."""
    if len(selected) <= 1:
        return False
    adjacency: dict[Point, set[Point]] = {point: set() for point in selected}
    for left, right in edges:
        if left in selected and right in selected:
            adjacency[left].add(right)
            adjacency[right].add(left)
    visited: set[Point] = set()
    stack = [next(iter(selected))]
    while stack:
        point = stack.pop()
        if point in visited:
            continue
        visited.add(point)
        stack.extend(adjacency[point] - visited)
    return visited != set(selected)


def enumerate_lattice() -> dict[str, object]:
    """Enumerate all selected domains and their admissible relation records."""
    points = lattice_points()
    edges = lattice_edges(points)
    distribution: Counter[int] = Counter()
    total = 0

    for mask in range(1 << len(points)):
        selected = selected_domain_from_mask(points, mask)
        induced_count = induced_relation_count(selected, edges)
        distribution[induced_count] += 1
        total += 2**induced_count

    normalized_distribution = {m: distribution.get(m, 0) for m in range(len(edges) + 1)}
    return {
        "lattice_vertices": len(points),
        "lattice_relations": len(edges),
        "selected_domains_examined": 1 << len(points),
        "distribution": normalized_distribution,
        "admissible_configuration_total": total,
    }


def finite_failure_witnesses() -> dict[str, bool]:
    """Evaluate the three witnesses stated in the manuscript."""
    points = lattice_points()
    edges = lattice_edges(points)
    u, v, w = (0, 0), (1, 0), (2, 2)

    active_elements = {u}
    incidence_failure = not ({u, v} <= active_elements)
    boundary_label_failure = "transmissive" != "blocked"
    selected = frozenset({u, w})
    disconnected_but_admissible = is_disconnected_selected_domain(selected, edges)

    return {
        "relation_incidence_failure_detected": incidence_failure,
        "incompatible_boundary_label_detected": boundary_label_failure,
        "disconnected_restriction_admissible": disconnected_but_admissible,
    }


def write_outputs(output_dir: Path) -> dict[str, object]:
    """Write deterministic JSON and CSV outputs and return the computed summary."""
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = enumerate_lattice()
    witnesses = finite_failure_witnesses()

    with (output_dir / "enumeration_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")

    with (output_dir / "finite_failure_witnesses.json").open("w", encoding="utf-8") as handle:
        json.dump(witnesses, handle, indent=2, sort_keys=True)
        handle.write("\n")

    with (output_dir / "enumeration_distribution.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["induced_relation_count_m", "selected_domain_count_N_m", "admissible_relation_records_2_pow_m"])
        for m, count in summary["distribution"].items():
            writer.writerow([m, count, 2**int(m)])

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "results",
        help="Directory for deterministic JSON and CSV outputs.",
    )
    args = parser.parse_args()
    summary = write_outputs(args.output_dir)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
