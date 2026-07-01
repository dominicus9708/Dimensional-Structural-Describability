# Reproducibility Record

## Formal input

The input is fully specified by the manuscript's finite square-lattice realization:

- vertices: `X = {0,1,2} x {0,1,2}`;
- relations: twelve undirected nearest-neighbour lattice edges;
- selected domains: all `512` subsets of `X`;
- admissible recorded relations: every subset of the induced edge set for the selected domain;
- boundary rule: the unique permitted label for every exposed relation is `blocked`.

No external dataset, random seed, numerical tolerance, or network resource is used.

## Determinism

The scripts use only Python's standard library and deterministic finite iteration. Re-running the commands in `README.md` overwrites the output files with the same contents.

## Expected checks

1. `selected_domains_examined = 512`.
2. The induced-edge distribution agrees with the manuscript appendix.
3. `admissible_configuration_total = 21799`.
4. All three finite witness checks return `true`.
