# Icepak materials for the K-16 cold plate

Material properties for the Icepak case. Values are from the competition guidance where stated,
otherwise from standard references (noted per row). See `../../SPEC.md` for the parts list.

Copper, silicon, FR-4, air, and water ship in the Icepak library; pick them and set copper k to
380. PG-25 is not in the library; add it.

## Assign these (in the heat path)

| Material | Part | k [W/m K] | density [kg/m3] | cp [J/kg K] | viscosity [Pa s] | Source |
|---|---|---|---|---|---|---|
| Copper (AM) | fin plate, baseplate | 380 | 8960 | 385 | n/a | k from guidance; density and cp standard copper |
| Silicon | die | 130 | 2330 | 712 | n/a | die is TTC-1002 silicon chips; k standard silicon |
| PG-25 | coolant | 0.48 | 1016 | 3970 | 2.1e-3 | ASHRAE / Melinder at 30 C |

PG-25 also takes a thermal expansion coefficient beta 3.9e-4 1/K (for buoyancy, negligible in this
pumped flow). Thermal diffusivity 1.19e-7 m2/s and molar mass 22.3 g/mol are derived or optional:
diffusivity is k / (rho cp), and molar mass is used only for the ideal gas law, not a liquid.

## Not in the heat path

| Item | Handling |
|---|---|
| TIM, TTV to plate | contact resistance 3.0e-6 m2 K/W (0.03 cm2 K/W), not a material |
| Manifold, tubes | adiabatic walls, no material needed; if a solid is required, plastic k ~0.2 |
| O-rings | exclude; if kept, elastomer k ~0.2 |
| Substrate | adiabatic or excluded, all power into the cold plate |
| Gasket | Silicone, k 0.2, density 1150, cp 1100 if modeled |

## Notes

- Copper k 380 is the as printed effective value, below bulk copper. Density and cp are standard.
- Silicon k is temperature dependent, about 148 at room temperature and near 130 at the operating
  temperature. The die thickness comes from the CAD.
- PG-25 properties are at ~30 C and vary with temperature. Confirm the 25 percent basis (mass or
  volume) and propylene glycol, not polypropylene glycol, with the organizers.
- Silicone, manifold, and O-ring values are assumed standard values; these parts sit outside the
  heat path, so the exact value has little effect.
