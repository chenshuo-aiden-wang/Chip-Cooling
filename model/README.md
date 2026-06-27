# Model

All analysis for the K-16 cold plate problem. The workflow runs hand calc, then Icepak, then
Fluent, with the geometry in `cad/` and the outputs in `results/`.

## Folders

| Folder | What it holds |
|---|---|
| `cad/` | Geometry. The original competition STEP, the cleaned STEP, SpaceClaim files, the extracted fluid volume, and the fin plate designs. |
| `handcalc/` | Python analytical estimate of thermal resistance and pressure drop, a sanity check on the CFD. `functions.py`, `spec.py`, `HANDCALC.md`. |
| `icepak/` | Icepak project files. Design exploration: run several fin architectures and rank them by Figure of Merit. |
| `fluent/` | Fluent cases and results. High fidelity validation of the chosen design. |
| `results/` | Figure of Merit values, comparison tables, and the figures for the write up. |

## Workflow

1. `cad`: clean the geometry and extract the fluid volume.
2. `handcalc`: get a ballpark resistance and pressure drop to check the CFD against.
3. `icepak`: simulate the baseline and the candidate fin designs, compute the Figure of Merit, down select.
4. `fluent`: validate the chosen design at high fidelity.
5. `results`: collect the Figure of Merit numbers and the figures.

The problem data and the Figure of Merit are in `../SPEC.md`.
