# model

Analytical thermal and hydraulic model of a single phase microchannel cold plate.
It computes thermal resistance (°C/W), junction temperature, pressure drop, and
pumping power for a given channel geometry and flow rate. It implements the analysis
documented in HANDCALC.md.

## Files

| File | Description |
|---|---|
| `properties.py` | Water and copper material properties. Water is fixed at ~35 °C; CoolProp can replace it for temperature dependent values. |
| `coldplate.py` | The model. `ColdPlate` holds the geometry; `analyze()` returns the full result (convection, fins, pressure drop, resistance stack). |
| `spec.py` | Spec values (heat load, die area, inlet temperature, junction limit, flow, estimated R_TIM and R_spreading). Mirrors `../SPEC.md`. |
| `run_handcalc.py` | Entry point. Evaluates the candidate designs in `DESIGNS` against the spec target and prints the results. |
| `HANDCALC.md` | The written analysis (method and assumptions) that this code implements. |
| `requirements.txt` | Optional packages for planned extensions (sweeps, plots, fluid properties). |

## Requirements

The core model uses only the Python standard library (`math`, `dataclasses`), so
`run_handcalc.py` runs with no installation. The packages in `requirements.txt`
(numpy, matplotlib, CoolProp) are for the planned extensions below.

## How to run

```bash
cd model
python run_handcalc.py
```

It prints the spec targets and the computed results for each design in the `DESIGNS`
dictionary in `run_handcalc.py`. Edit that dictionary to evaluate other geometries.

## Model description

`coldplate.analyze()` computes, in order:

1. Flow. Converts volumetric flow to per channel velocity and Reynolds number.
2. Convection. Nusselt number (constant for laminar, Dittus Boelter for turbulent)
   gives the heat transfer coefficient `h`.
3. Fins. The channel side walls are treated as straight fins; fin efficiency reduces
   the effective wetted area.
4. Resistance stack. `R_total = R_convection + R_TIM + R_spreading + R_caloric`.
5. Outputs. Junction temperature `T_in + Q * R_total`, pressure drop (friction factor
   times dynamic pressure), and pumping power (`dP * flow`).

A design passes if `R_total` is at or below the spec target `(T_j_max - T_in) / Q`.

## Assumptions

Fully developed flow, constant laminar Nusselt number, adiabatic fin tips, uniform
heat flux, and estimated TIM and spreading resistances. See HANDCALC.md section 6.
These are first cut values to be refined with CFD and measured data.

## Planned extensions

- Parameter sweep over channel geometry and flow rate, with plots.
- 1D conduction calculator that converts test thermocouple readings to measured °C/W.
- CoolProp integration for temperature dependent fluid properties.
