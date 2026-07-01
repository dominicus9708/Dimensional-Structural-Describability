# Finite Square-Lattice Enumeration for Structural Admissibility

This directory contains the standard-library Python replication package for the exhaustive enumeration used in the manuscript:

> *Structural Admissibility: An Axiomatic Framework for Boundary-Compatible Descriptions*

## What is reproduced

The package exhaustively examines all `2^9 = 512` selected domains of the finite `3 x 3` square lattice. For a selected domain `S`, the manuscript's carrier-exact finite realization admits every subset of the induced relation set `R_S` and fixes the boundary label of every exposed relation to `blocked`. The package verifies:

- the induced-relation distribution `N_m`;
- the exhaustive total of `21,799` admissible configurations;
- the three finite failure-witness verdicts stated in the manuscript.

This repository material reproduces a finite computational enumeration. It does not replace the formal proofs of the general structural-admissibility criterion, structural-isomorphism invariance, or conditional closure results.

## Requirements

- Python 3.10 or later
- No third-party dependencies

## Run

From this directory:

```powershell
python src\enumerate_square_lattice.py --output-dir results
python src\verify_enumeration.py --results-dir results
python -m unittest discover -s tests -v
```

## Outputs

- `results/enumeration_summary.json`
- `results/enumeration_distribution.csv`
- `results/finite_failure_witnesses.json`

The expected total is `21,799` and the distribution is recorded in `results/enumeration_distribution.csv`.

## Scope

The finite square-lattice realization is explicitly **carrier-exact**: its active carrier equals its selected domain. The manuscript separately provides a two-element example to show that the general framework also allows a selected domain to contain inactive structural material, so that `C_p` can be a proper subset of `S_p`.
