# Spec: K-16 Cold Plate

Baseline data for the design problem. Source: ASME K-16 / IEEE ITherm competition guidance
(`resources/`).

## Operating conditions

| Parameter | Value |
|---|---|
| Coolant | PG-25 (propylene glycol 25%) |
| Flow rate | 1.2 L/min |
| Inlet temperature | 30 C |
| Ambient temperature | 20 C |
| TIM resistance | 0.03 cm2 K/W |

## Power map (total 800 W)

| Zone | Size | Power | Flux |
|---|---|---|---|
| H | 8.6 x 32.2 mm | 400 W | 1.44 W/mm2 |
| BG1 | 8.6 x 32.2 mm | 200 W | 0.72 W/mm2 |
| BG2 | 8.6 x 32.2 mm | 200 W | 0.72 W/mm2 |

Die: 32.2 x 25.8 mm.

## Geometry and material

| Item | Value |
|---|---|
| Fin plate design space | 36 x 29 x 2 mm |
| Baseplate (fixed) | 53 x 46 x 2 mm |
| Material | Copper, k = 380 W/m K |
| Surface roughness | 1.5 um |
| Min feature | 0.10 mm |
| Max fin thickness (X-Y) | 0.50 mm |

## Figure of Merit

```
FoM = 0.7 (R_b - R) / R_b + 0.3 (dP_b - dP) / dP_b
R   = max(T_chip - T_inlet) / q_total
dP  = inlet to outlet pressure drop across the manifold
```

Subscript b is the provided baseline fin plate, simulated the same way.
