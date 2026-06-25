# Hand calc: GPU cold plate

**Rev:** 0.2 · **Date:** 2026-06-21 · Supports [`../SPEC.md`](../SPEC.md)

> Run `python sweep.py` in this folder to recompute these values and write the design curves to
> `figures/`. This document records the method and assumptions; the code is the source of truth for
> the numbers.

First principles feasibility analysis behind the spec targets. The values are estimates
to be refined by CFD (Icepak, Fluent) and measurement. The assumptions in section 6 set
the accuracy; read them before relying on any number.

---

## 0. Givens and fluid properties

| Quantity | Symbol | Value |
|---|---|---|
| Heat load | `Q` | 500 W |
| Heated die area | `A` | 4 cm² = 4×10⁻⁴ m² |
| Coolant inlet temperature | `T_in` | 30 °C |
| Junction limit | `T_j,max` | 85 °C |
| Design flow | `V̇` | 1.5 L/min = 2.5×10⁻⁵ m³/s |

Water properties (~35 °C): ρ = 994 kg/m³, cp = 4180 J/kg·K, k_w = 0.62 W/m·K,
μ = 7.2×10⁻⁴ Pa·s, Pr ≈ 4.8. Copper: k_cu = 400 W/m·K.

## 1. Heat flux
```
q'' = Q / A = 500 / 4 = 125 W/cm²   (1.25×10⁶ W/m²)
```
For reference, AI GPU dies operate near 50 to 125 W/cm².

## 2. Required total thermal resistance
```
R_total ≤ (T_j,max − T_in) / Q = (85 − 30) / 500 = 0.11 °C/W
```
Everything from chip to coolant inlet must sum to 0.11 °C/W or less. State of the art
direct to chip plates reach about 0.02 °C/W, so 0.11 is a relatively loose target.

## 3. Flow and caloric check
```
ṁ = ρ·V̇ = 0.0248 kg/s
ΔT_fluid = Q / (ṁ·cp) ≈ 4.8 °C
R_caloric = 1 / (2·ṁ·cp) ≈ 0.005 °C/W
```
The coolant rises about 5 °C, so 1.5 L/min is adequate and is not the limiting resistance.

## 4. Resistance budget
```
R_total = R_convection + R_TIM + R_spreading + R_caloric ≤ 0.11 °C/W
```
| Term | Value | Basis |
|---|---|---|
| `R_TIM` | ~0.025 °C/W | `t/(k·A)` = 50 µm / (5 W/m·K × 4×10⁻⁴ m²), estimate |
| `R_spreading` | ~0.0125 °C/W | Yovanovich model, `spreading.py` (die ≈ base, so mostly 1D base conduction) |
| `R_caloric` | ~0.005 °C/W | section 3 |
| `R_convection` (remaining) | ≤ ~0.068 °C/W | what the channels must deliver |

## 5. First cut channel sizing

```
R_conv = 1 / (h · A_eff),   h = Nu·k_w/D_h,   D_h = 2·w·h_c/(w + h_c)
A_eff = A_base + η_fin · A_fin      (channel side walls treated as straight fins)
```
The Nusselt number uses the **Hausen developing flow** correlation, not a fixed value.
For these short channels (L = 20 mm) the thermal entrance region raises Nu well above the
fully developed value of 3.66, and it grows with flow. Base width 20 mm, L = 20 mm.
Values come from the model in `coldplate.py` (run `sweep.py`).

| Design | Channels | w × h_c | D_h | Re | Nu | h (W/m²K) | η_fin | R_conv |
|---|---|---|---|---|---|---|---|---|
| A, moderate | 20 | 0.5 × 3 mm | 0.86 mm | 986 | 9.39 | 6,793 | 0.84 | 0.061 °C/W |
| B, aggressive | 25 | 0.4 × 5 mm | 0.74 mm | 511 | 7.04 | 5,896 | 0.65 | 0.047 °C/W |

Adding the budget terms from section 4 (R_TIM + R_spreading + R_caloric ≈ 0.043 °C/W):

| Design | R_total | T_junction | Result |
|---|---|---|---|
| A, moderate | 0.104 °C/W | 81.7 °C | Pass |
| B, aggressive | 0.089 °C/W | 74.5 °C | Pass |

## 6. Conclusions, assumptions, and limitations

With the developing flow Nusselt correlation and a computed (Yovanovich) spreading
resistance, both designs meet the 0.11 °C/W target. The earlier fully developed
assumption was too conservative for channels this short: the entrance region roughly
doubles the heat transfer coefficient. The parametric curves in `figures/` show the full
design space and the thermal versus pumping power trade off across flow rates.

Key assumptions to refine:

- Hausen developing flow Nu (constant wall temperature boundary). A chip is closer to
  constant heat flux; the two boundary conditions differ. CFD will settle it.
- `R_TIM` is an estimate. Replace with a paste datasheet value.
- `R_spreading` uses the Yovanovich single term model with the die spreading into the
  base. Here die and base areas are nearly equal, so it reduces to base conduction. A
  larger base relative to the die would add real spreading.
- Pressure drop and pumping power are computed in the scripts (tens of mW, negligible).

Next step: validate these predictions in Icepak and Fluent, then against measured data.
