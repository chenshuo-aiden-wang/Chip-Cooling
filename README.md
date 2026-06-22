# GPU Cold-Plate Test Bench

An engineering project that **designs, builds, and validates a direct-to-chip liquid
cold plate** for high-power chip cooling — the way it's done in industry:

> **Spec → CFD design → machine → instrument → measure → validate (CFD vs. data) → iterate.**

A CFD-designed cold plate is machined in copper, mounted on a calibrated **GPU-class heat
source**, and characterized by its **thermal resistance (°C/W)** — the metric on every
real cold-plate datasheet.

## Why it matters

Modern AI GPUs dissipate 1,000–2,300 W and can no longer be air-cooled. Direct-to-chip
liquid cold plates are now the mainstream solution. This project reproduces the full
industry design-and-validation loop on a benchtop, at GPU-class wattage.

## The spec (pass/fail)

See [`SPEC.md`](SPEC.md). Target: cool a ~500 W, ~4 cm² die and hold the junction below
85 °C with water cooling at a reasonable pumping power → **R_target ≈ 0.11 °C/W**.

## Repository structure

```
.
├── SPEC.md             # the thermal requirement + pass/fail target
├── model/              # Python: °C/W analytical model + heat-flux calculator   (coming)
├── cfd/                # Icepak (explore) + Fluent (validate) models & figures   (coming)
├── cad/                # cold-plate + emulator CAD                                (coming)
├── data/              # measured CSVs (°C/W vs. flow, etc.)                       (coming)
├── report/             # one-page thermal test report                            (coming)
└── resources/          # tutorials, papers, datasheets (Ansys, references)
```

## Tools

Ansys **Icepak** (rapid design exploration) + **Fluent** (high-fidelity CHT validation);
**Python** (NumPy/SciPy/CoolProp) for analytical models and data; fabrication at the UMN
Polaris student machine shop.

## Status

Phase 1 — writing the spec and building the analytical °C/W model before CFD.
