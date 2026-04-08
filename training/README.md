# ALIGNN Training Notes

## Current Status

The app currently runs with dataset-backed fallback predictions.

True ALIGNN training has **not** started yet because the available datasets in this project contain:

- solid formulas and targets
- liquid formulation strings and targets

but they do **not** contain the atomistic structure files required by official ALIGNN workflows.

## Why This Blocks Real ALIGNN Training

Official ALIGNN training expects:

- an `id_prop.csv` file
- matching structure files such as `.cif`, `POSCAR`, `.xyz`, or `.pdb`

That means:

- the solid dataset needs a crystal structure file for each training row
- the liquid dataset needs a molecule/cluster structure file for each training row

Without those structures, we cannot truthfully train ALIGNN.

## What We Can Train Once Data Is Ready

### Solid

Feasible once each solid sample has a crystal structure file:

- `.cif` or POSCAR for every composition
- conductivity target per sample

### Liquid

Feasible once each liquid sample has molecular geometry:

- `.xyz`, `.pdb`, or another supported atomistic structure representation
- conductivity target per sample

## Training Files Added Here

- `solid_alignn_config.json`
- `liquid_alignn_config.json`

These are starter config templates for future training after structure-rich datasets are prepared.

## Solid Training Progress

The solid side can now move forward using a Materials Project API key plus the script:

- `training/scripts/prepare_solid_alignn_data.py`

This script maps solid formulas to Materials Project structures, writes CIF files, and creates an ALIGNN-style `id_prop.csv`.

Detailed run steps are in:

- `training/scripts/train_solid_alignn.md`
