# Hand-Calc Package — GPU Cold-Plate Test Bench

**Rev:** 0.1 · **Date:** 2026-06-21 · Supports [`../SPEC.md`](../SPEC.md)

> **Now live code:** run `python run_handcalc.py` in this folder for up-to-date numbers.
> This document is the *method + assumptions*; the script is the source of truth for values.

First-principles feasibility analysis behind the spec targets. Everything here is a
*hand estimate* to be refined by CFD (Icepak/Fluent) and measurement. Assumptions and
limitations are stated in §6 — read them; the numbers are only as good as those.

---

## 0. Givens & fluid properties

| Quantity | Symbol | Value |
|---|---|---|
| Heat load | `Q` | 500 W |
| Heated die area | `A` | 4 cm² = 4×10⁻⁴ m² |
| Coolant inlet temp | `T_in` | 30 °C |
| Junction limit | `T_j,max` | 85 °C |
| Design flow | `V̇` | 1.5 L/min = 2.5×10⁻⁵ m³/s |

Water properties (~35 °C): ρ = 994 kg/m³, cp = 4180 J/kg·K, k_w = 0.62 W/m·K,
μ = 7.2×10⁻⁴ Pa·s, Pr ≈ 4.8. Copper: k_cu = 400 W/m·K.

## 1. Heat flux
```
q'' = Q / A = 500 / 4 = 125 W/cm²   (1.25×10⁶ W/m²)
```
GPU-realistic localized flux. (For reference, real AI dies run ~50–125+ W/cm².)

## 2. Required total thermal resistance
```
R_total ≤ (T_j,max − T_in) / Q = (85 − 30) / 500 = 0.11 °C/W
```
**Everything from chip to coolant inlet must sum to ≤ 0.11 °C/W.**
(State-of-the-art DTC plates ≈ 0.02 °C/W, so 0.11 is a forgiving first target.)

## 3. Flow / caloric check
Coolant bulk temperature rise:
```
ṁ = ρ·V̇ = 994 × 2.5×10⁻⁵ = 0.0248 kg/s
ΔT_fluid = Q / (ṁ·cp) = 500 / (0.0248 × 4180) ≈ 4.8 °C
```
Caloric resistance (referenced to inlet, using mean fluid temp):
```
R_caloric = 1 / (2·ṁ·cp) = 1 / (2 × 0.0248 × 4180) ≈ 0.005 °C/W
```
→ Coolant rises only ~5 °C; flow of 1.5 L/min is adequate and **not** the bottleneck. ✓

## 4. Resistance budget
```
R_total = R_TIM + R_spreading + R_convection + R_caloric ≤ 0.11 °C/W
```
| Term | Estimate | Basis |
|---|---|---|
| `R_TIM` | ~0.025 °C/W | `t/(k·A)` = 50 µm / (5 W/m·K × 4×10⁻⁴ m²) |
| `R_spreading` | ~0.015 °C/W | rough estimate; refine in CFD/FEA |
| `R_caloric` | ~0.005 °C/W | §3 |
| **`R_convection` (remaining)** | **≤ ~0.065 °C/W** | **what the channels must deliver** |

## 5. First-cut channel sizing — does R_conv ≤ 0.065 work?

`R_conv = 1/(h·A_wet)`, with `h = Nu·k_w/D_h`, `D_h = 2·w·h_c/(w+h_c)`,
`A_wet = 2·(w+h_c)·L·N`. Base width 20 mm, flow length L = 20 mm, laminar `Nu ≈ 4.5`.

| Design | Channels | w × h_c | D_h | Re | h (W/m²K) | A_wet | **R_conv** |
|---|---|---|---|---|---|---|---|
| **A — moderate** | 20 | 0.5 × 3 mm | 0.86 mm | ~990 (laminar) | ~3,240 | 28 cm² | **~0.11 °C/W** |
| **B — aggressive** | 25 | 0.4 × 5 mm | 0.74 mm | ~570 (laminar) | ~3,830 | 54 cm² | **~0.05 °C/W** |

**Verdict:**
- **Design A misses:** total ≈ 0.11 + 0.025 + 0.015 + 0.005 = **0.155 °C/W > 0.11**. ✗
- **Design B makes it (ideal):** total ≈ 0.05 + 0.045 = **~0.095 °C/W < 0.11**. ✓
  - *But* with **fin efficiency** (tall 5 mm × 0.4 mm copper fins, η ≈ 0.73), `R_conv` rises
    to ~0.067 → total ~0.11 °C/W → **marginal**.

## 6. Conclusions, assumptions & limitations

**Conclusion:** The 0.11 °C/W target is **feasible but tight** — it requires *aggressive
microchannels* (fine, tall). A naive/moderate channel design **fails** the spec. This is
exactly why CFD design + iteration is needed, and it tells you where to spend effort:
maximizing channel surface area and `h` while watching fin efficiency and pressure drop.

**Key assumptions (refine these):**
- Laminar fully-developed `Nu ≈ 4.5` (rectangular duct, const flux) — real entrance effects
  raise `h`; turbulence (higher flow) raises it more.
- Ignored **fin efficiency** in the table (noted separately for Design B) — CFD captures it.
- `R_TIM`, `R_spreading` are estimates — replace with datasheet + CFD/FEA values.
- Uniform heat flux assumed — the **hotspot** case (non-uniform) is harder; model later.
- Pressure drop / pumping power **not yet computed** — add next (finer channels cost ΔP).

**Next:** turn this into a Python tool (`model/`) so geometry → (°C/W, ΔP, pumping power)
is instant, then validate against Icepak/Fluent.
