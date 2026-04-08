# LIQUID ARCHITECTURE NOTES

## Current Dataset Reality

The liquid dataset in this project has:

- `500` total rows
- only `15` unique formulations
- many repeated rows for the same formulation at different temperatures

This means the liquid pipeline cannot be treated exactly like the solid pipeline.

## What the Liquid Side Must Learn

For liquid electrolytes, ionic conductivity depends on:

- salt identity
- solvent identity
- relative composition
- temperature

So the effective liquid input is:

`formulation + temperature`

not just a single formula string.

## Best Architecture Match to the User's Design

To stay close to the intended architecture:

1. User enters a liquid chemistry formulation.
2. Backend maps known components to molecular structures.
3. Backend builds a combined molecular/formulation graph.
4. Temperature is added as an extra numeric feature.
5. Liquid model predicts ionic conductivity.

## Equivalent to the Desired Flow

The liquid equivalent of:

`formula -> CIF -> graph -> ALIGNN -> prediction`

is:

`formulation -> molecular structure set -> graph -> liquid model -> prediction`

## Known Components Present in Current Data

The cleaned 500-row dataset currently contains formulations built from:

- `PC`
- `EC`
- `EMC`
- `LiPF6`

This is useful because a fixed component vocabulary makes the first liquid model easier to build.

## Important Limitation

Because there are only `15` unique formulations in the current 500-row file, a true deep graph model may overfit badly.

So the liquid side should likely be built in stages:

### Stage 1

- graph-ready formulation representation
- dataset-backed or lightweight learned model

### Stage 2

- structure-rich liquid dataset
- real liquid graph neural model

## Recommended Next Build Step

Create a liquid preprocessing pipeline that:

- parses formulation strings
- maps each known component to a canonical structure/SMILES
- combines component weights and temperature
- produces one graph-ready training sample per row

## Demo-Safe Summary

The solid side can follow the crystal-structure ALIGNN route directly.

The liquid side should follow a molecular-formulation graph route, because liquid electrolyte conductivity depends on mixture composition and temperature rather than a single crystal structure.
