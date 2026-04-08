# TRAINING STATUS

## Honest Status

This project is **not yet training a true ALIGNN model**.

## Reason

The current project datasets do not include atomistic structure files for each row.

ALIGNN needs per-sample structures:

- for solids: `.cif` or POSCAR-like crystal structures
- for liquids: `.xyz`, `.pdb`, or similar molecular structures

## What We Have Right Now

- a working frontend
- a working FastAPI backend
- phase-aware input validation
- cleaned target datasets
- starter ALIGNN config templates in the `training/` folder

## What Is Needed Next

1. Obtain structure-rich training data for solid samples.
2. Obtain structure-rich training data for liquid samples.
3. Create official ALIGNN training folders with:
   - structure files
   - `id_prop.csv`
4. Train the models in a Python 3.10 environment with DGL-compatible ALIGNN installation.
5. Export the best checkpoints into the `models/` folder.

## Environment Recommendation

The official ALIGNN installation guidance recommends a Python 3.10 conda environment with DGL installed alongside PyTorch.
