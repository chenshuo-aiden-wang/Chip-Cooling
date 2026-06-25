# model

Analytical thermal and hydraulic model of a single phase microchannel cold plate. It computes
thermal resistance (C/W), junction temperature, pressure drop, and pumping power for a given
channel geometry and flow rate. It implements the analysis documented in HANDCALC.md.

## Files

| File | Description |
|---|---|
| `properties.py` | Water and copper material properties. Water is fixed at ~35 C; CoolProp can replace it for temperature dependent values. |
| `coldplate.py` | The model. `ColdPlate` holds the geometry; `analyze()` returns the full result (convection, fins, spreading, pressure drop, resistance stack). Uses a developing flow Nusselt number. |
| `spreading.py` | Yovanovich spreading resistance (die into the base), used by `analyze()`. |
| `spec.py` | Spec values (heat load, die area, inlet temperature, junction limit, flow, estimated R_TIM). Mirrors `../SPEC.md`. |
| `sweep.py` | Entry point. Sweeps channel geometry and flow against the spec target, prints the dominant lever and the best machinable design, and writes design curves to `figures/`. |
| `HANDCALC.md` | The written analysis (method and assumptions) that this code implements. |
| `requirements.txt` | numpy, matplotlib, CoolProp for the sweep plots and planned extensions. |

## How to run

```bash
cd model
python sweep.py
```

The model core uses only the Python standard library (`math`, `dataclasses`). `sweep.py` needs
matplotlib (see `requirements.txt`) for the figures. Edit the sweep ranges or `spec.py` to explore
other conditions.

## Model description

`coldplate.analyze()` computes, in order:

1. Flow. Converts volumetric flow to per channel velocity and Reynolds number.
2. Convection. Developing flow Nusselt number (Hausen for laminar, Dittus Boelter for turbulent)
   gives the heat transfer coefficient `h`.
3. Fins. The channel side walls are treated as straight fins; fin efficiency reduces the effective
   wetted area.
4. Spreading. Yovanovich spreading resistance from the die into the base (`spreading.py`).
5. Resistance stack. `R_total = R_convection + R_TIM + R_spreading + R_caloric`.
6. Outputs. Junction temperature `T_in + Q * R_total`, pressure drop, and pumping power.

A design passes if `R_total` is at or below the spec target `(T_j_max - T_in) / Q`.

## Assumptions

Developing flow Nusselt (constant wall temperature), adiabatic fin tips, uniform heat flux into the
base, an estimated TIM resistance, and the Yovanovich single term spreading model. See HANDCALC.md
section 6. These are first cut values to be refined with CFD and measured data.

## Planned extensions

- 1D conduction calculator that converts test thermocouple readings to measured C/W.
- CoolProp integration for temperature dependent fluid properties.
- A thin web front end (the validated design tool), built last and time boxed.
