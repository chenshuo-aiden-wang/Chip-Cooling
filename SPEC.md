# Thermal Spec — GPU Cold-Plate Test Bench

**Rev:** 0.1 (draft) · **Date:** 2026-06-21 · **Owner:** Aiden Wang

> This is the pass/fail. Fill in / adjust the numbers; everything downstream (CFD,
> hardware, validation) aims at these targets.

---

## 1. Objective

Design, build, and validate a **single-phase, direct-to-chip liquid cold plate** that
cools a calibrated **GPU-class heat source** below its junction limit, and validate the
measured **thermal resistance (°C/W)** against CFD.

## 2. Requirements

| # | Parameter | Symbol | Target | Rationale                                                |
|---|---|---|---|----------------------------------------------------------|
| R1 | Heat load | `Q` | **500 W** | GPU-class; also matched to heater hardware               |
| R2 | Heated die area | `A` | **4 cm²** (2×2 cm) | → heat flux ≈ **125 W/cm²** (GPU-realistic)              |
| R3 | Coolant | — | **Water** | Cheap, safe, well-characterized - single phase           |
| R4 | Coolant inlet temp | `T_in` | **30 °C** | Controlled by reservoir/ice bath (a setting, not a guess) |
| R5 | Junction limit (ceiling) | `T_j,max` | **≤ 85 °C** | GPUs throttle ~85 °C — must stay under                   |
| R6 | Flow rate | `V̇` | **1–2 L/min** | Within a cheap pump; ≥ caloric minimum (see §3)          |
| R7 | Pumping power | — | "sane" (low ΔP) | Finer channels cool better but cost pressure drop        |

## 3. Derived targets (the hand calc — these are *computed*)

> **Full hand-calc package** — channel sizing, feasibility check, and stated assumptions:
> see [`HANDCALC.md`](HANDCALC.md). (Headline: the 0.11 °C/W target is *feasible but tight* —
> it needs aggressive microchannels; a naive design misses.)

**Required total thermal resistance:**
```
R_target = (T_j,max − T_in) / Q = (85 − 30) / 500 = 0.11 °C/W
```
→ **The cold plate (+ TIM + spreading) must come in under 0.11 °C/W.**
(Reference: state-of-the-art DTC plates ≈ 0.02 °C/W, so 0.11 is a forgiving first target.)

**Minimum flow (so the coolant itself doesn't heat up > ~10 °C):**
```
ṁ_min = Q / (cp · ΔT_fluid) = 500 / (4180 · 10) ≈ 0.012 kg/s ≈ 0.7 L/min
```
→ Design for **1–2 L/min** for margin (R6).

**Resistance budget (how the 0.11 °C/W is "spent"):**
```
R_total = R_TIM + R_spreading + R_convection   ≤ 0.11 °C/W
```
- `R_TIM` ≈ 0.02–0.03 °C/W (good paste over 4 cm²) — *estimated, refine later*
- `R_spreading` — from CFD / FEA
- `R_convection` — **what your channel design must deliver (the bulk of the budget)**

## 4. Constraints

- **Machinable** at UMN Polaris (CNC mill / waterjet) — no metal 3D printing.
- **Safety:** GFCI, over-temp cutoff, EHS/faculty sign-off before powering up.
- Single-phase only (no boiling/CHF risk) for the core bench.

## 5. Pass / Fail

| Criterion | Pass condition |
|---|---|
| Cools the load | Measured `T_j` < 85 °C at Q = 500 W |
| Meets target | Measured `R_total` ≤ 0.11 °C/W |
| CFD validated | Measured °C/W within ~±15% of Icepak/Fluent prediction |
| Energy balance | Electrical watts in ≈ conduction heat flux (cross-check closes) |
| Design verdict | Clear result: does "my design" beat the straight-channel baseline? |

## 6. Open assumptions to refine (estimated from references, not invented)

- TIM conductivity / bond-line thickness → from paste datasheet.
- Convection correlation constants → from Incropera; replaced by CFD.
- Water properties at ~40 °C → from CoolProp.

## 7. Revision log

| Rev | Date | Change |
|---|---|---|
| 0.1 | 2026-06-21 | Initial draft target (500 W, 85 °C, 0.11 °C/W) |
