# Hand calc method

A first cut estimate of cold plate thermal resistance and pressure drop for the K-16 problem,
used to sanity check the CFD before trusting it. Implemented in `functions.py`; inputs in
`spec.py`. Run: `python spec.py`.

## Method

For a representative parallel channel fin geometry:

1. Flow. The volumetric flow split across the channels gives the channel velocity, the
   hydraulic diameter, and the Reynolds number.
2. Convection. A developing flow Nusselt number (Hausen for laminar, Dittus Boelter for
   turbulent) gives the heat transfer coefficient h.
3. Fins. The channel side walls are treated as straight fins; fin efficiency reduces the
   effective wetted area.
4. Spreading. A Yovanovich spreading resistance for the die conducting into the fin plate
   (Lee, Yovanovich 1995); it reduces to 1D base conduction when the die and plate areas match.
5. Resistance stack:
   `R_total = R_conv + R_tim + R_spread + R_caloric`, where `R_conv = 1/(h A_eff)`, `R_tim` is
   the TIM area resistance divided by die area, and `R_caloric` is coolant bulk heating.
6. Chip temperature = inlet temperature + total power times `R_total`.
7. Pressure drop from the friction factor and the dynamic pressure; pumping power = dP times flow.
8. Figure of Merit, `0.7 (R_b - R)/R_b + 0.3 (dP_b - dP)/dP_b`, against the baseline fin plate. If
   `R_BASELINE` and `DP_BASELINE` are set from the baseline CFD, those are used. Otherwise the same
   hand calc is run on a simple straight-fin baseline (`BASELINE_*` in `spec.py`) to give a rough
   FoM. Both sides use the same method, so the systematic errors partly cancel in the ratio, but the
   number is only as good as the assumed baseline and uses average rather than peak resistance.

The power map is listed as three heater rows (H, BG1, BG2) tiling the die; the guidance gives the
sizes and powers but not the areas, so they are computed and cross checked against the die area and
the 800 W total. The stack itself still applies the total power uniformly.

## Inputs

All in `spec.py`, each labeled `[K-16]` fixed by the guidance, `[DESIGN]` your variable, or
`[ASSUME]` to refine. Key K-16 values: PG-25 coolant, 1.2 L/min, 30 C inlet, 800 W total,
TIM 0.03 cm2 K/W, copper k 380, die 32.2 x 25.8 mm.

## Assumptions and limits

- Uniform parallel channels. The real manifold flow distribution is ignored.
- Total power applied uniformly. The hotspot driven peak, the real R_th,max, is higher, and
  only CFD resolves it.
- Yovanovich spreading from the die into the plate; reduces to 1D conduction when the areas match.
- PG-25 properties from ASHRAE / Melinder glycol tables at ~30 C; verify on the coolant datasheet.

This brackets the CFD. It does not replace it.
