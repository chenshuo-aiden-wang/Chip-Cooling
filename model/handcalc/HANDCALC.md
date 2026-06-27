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
4. Resistance stack:
   `R_total = R_conv + R_tim + R_base + R_caloric`, where `R_conv = 1/(h A_eff)`,
   `R_tim` is the TIM area resistance divided by die area, `R_base` is 1D base conduction,
   and `R_caloric` is coolant bulk heating.
5. Chip temperature = inlet temperature + total power times `R_total`.
6. Pressure drop from the friction factor and the dynamic pressure; pumping power = dP times flow.

## Inputs

All in `spec.py`, each labeled `[K-16]` fixed by the guidance, `[DESIGN]` your variable, or
`[ASSUME]` to refine. Key K-16 values: PG-25 coolant, 1.2 L/min, 30 C inlet, 800 W total,
TIM 0.03 cm2 K/W, copper k 380, die 32.2 x 25.8 mm.

## Assumptions and limits

- Uniform parallel channels. The real manifold flow distribution is ignored.
- Total power applied uniformly. The hotspot driven peak, the real R_th,max, is higher, and
  only CFD resolves it.
- 1D base conduction, no detailed spreading.
- PG-25 properties are approximate; verify on a coolant datasheet.

This brackets the CFD. It does not replace it.
