# GPU Cold Plate Test Bench

This project designs, builds, and validates a direct to chip liquid cold plate that keeps a GPU class chip within its thermal limit at high power.

**Goal:** deliver a copper cold plate that holds a 500 W, 4 cm² die below 85 °C junction temperature on water cooling, and prove it with measured data that matches CFD prediction.

The target metric is **thermal resistance (°C/W)**, the same figure published on every commercial cold plate datasheet.

## Objective

Modern AI GPUs dissipate 1,000 to 2,300 W and cannot be air cooled. Direct to chip liquid cold plates are the mainstream solution. This project produces a working, characterized cold plate at GPU class wattage and validates its performance end to end.

## Workflow

Spec → CFD design → machine → instrument → measure → validate (CFD vs. data) → iterate.

A CFD designed cold plate is machined in copper, mounted on a calibrated GPU class heat source, and characterized by its thermal resistance across flow rate.

## Target spec

See [`SPEC.md`](SPEC.md) for the full pass/fail requirement. Headline target: cool a 500 W, 4 cm² die and hold the junction below 85 °C on water cooling at a reasonable pumping power, giving **R_target ≈ 0.11 °C/W**.

## Repository structure

```
.
├── SPEC.md             # thermal requirement + pass/fail target
├── model/              # Python: °C/W analytical model + hand-calc (run_handcalc.py)
├── cfd/                # Icepak (explore) + Fluent (validate) models & figures   (coming)
├── cad/                # cold plate + emulator CAD                               (coming)
├── data/               # measured CSVs (°C/W vs. flow, etc.)                     (coming)
├── report/             # one page thermal test report                           (coming)
└── resources/          # tutorials, papers, datasheets (Ansys, references)
```

## Tools

Ansys **Icepak** for rapid design exploration and **Fluent** for high fidelity CHT validation. **Python** (NumPy/SciPy/CoolProp) for analytical models and data analysis. Fabrication at the UMN Polaris student machine shop.

## Status

Phase 1: spec written and analytical °C/W model built (`model/run_handcalc.py`). Next: CFD design in Icepak/Fluent.
