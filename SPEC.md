# Spec: K-16 Cold Plate

Baseline data for the design problem. Source: ASME K-16 / IEEE ITherm competition guidance
(`resources/`).

## Operating conditions

| Parameter | Value |
|---|---|
| Flow rate | 1.2 L/min |
| Inlet temperature | 30 C |
| Ambient temperature | 20 C |

## Power map (total 800 W)

Three heater rows tiling the 32.2 x 25.8 mm die (830 mm2).

| Zone | Size | Power | Flux |
|---|---|---|---|
| H | 8.6 x 32.2 mm | 400 W | 1.44 W/mm2 |
| BG1 | 8.6 x 32.2 mm | 200 W | 0.72 W/mm2 |
| BG2 | 8.6 x 32.2 mm | 200 W | 0.72 W/mm2 |

Scoring uses the maximum temperature within each zone.

## Parts and materials

| Part | Dimensions | Material | Notes |
|---|---|---|---|
| Fin plate | 36 x 29 x 2 mm | Copper (AM), k 380 W/m K | design space |
| Baseplate | 53 x 46 x 2 mm | Copper (AM), k 380 W/m K | fixed geometry |
| Manifold | per CAD | not specified | fixed geometry |
| Gasket | 2 mm thick | Silicone | above fin plate; k not given |
| Coolant | n/a | PG-25 | properties not given |
| Die | 32.2 x 25.8 mm | Silicon | heat source; TTC-1002 chip array, see note |
| Substrate | 81 x 75 mm | not specified | TTV-4103 board |
| Tube, inlet and outlet | 3/8 in ID | not specified | |
| TIM, TTV to plate | interface | 0.03 cm2 K/W | area specific contact resistance |

Notes:
- Copper k 380 W/m K is the as printed effective value. Density and cp are not in the guidance; take them from the Icepak copper library.
- Page 1 prints the coolant as "Polypropylene Glycol 25%". PG-25 conventionally denotes propylene glycol 25%. Confirm with the organizers.
- PG-25 fluid properties (density, cp, k, viscosity) are not in the guidance; source from a coolant datasheet or ASHRAE / Melinder glycol tables.
- The die is silicon: the TTV-4103 die is an array of TEA TTC-1002 thermal test chips (silicon, 2.5 mm unit cells). This is from the TTV / TTC-1002 documentation, not the K-16 guidance. TEA does not publish a conductivity; use standard silicon (k about 130 W/m K at operating temperature). Take the die thickness from the CAD.

## Manufacturing constraints

| Item | Value |
|---|---|
| Surface roughness | 1.5 um |
| Min feature | 0.10 mm |
| Max feature, X-Y | 0.50 mm |
| Max feature, Z | 3 mm |
| Voxel, X-Y | 33.33 um |
| Min layer, Z | 0.030 mm |
| Min overhang | 20 deg from XY plane |
| File format | STEP |

## Figure of Merit

```
FoM = 0.7 (R_b - R) / R_b + 0.3 (dP_b - dP) / dP_b
R   = max(T_chip - T_inlet) / q_total
dP  = inlet to outlet pressure drop across the manifold
```

Subscript b is the provided baseline fin plate, simulated the same way.
