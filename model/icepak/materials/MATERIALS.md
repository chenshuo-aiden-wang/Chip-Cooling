# Icepak materials for the K-16 cold plate

Material properties for this project, collected in one place for the Icepak case. Values come
from the competition guidance where stated, and from standard references otherwise (each row
notes its source). See `../../../SPEC.md` for the parts list.

## How to use this

- Copper, silicon, FR-4, air, and water already ship in the Icepak / AEDT material library. You
  do not download those; pick them from the library, then adjust copper k to 380 (see below).
- PG-25 is not in the library. Add it as a new material with the values below.
- The TIM is not a material. Apply it as a thermal contact resistance at the TTV to cold plate
  interface, value 3.0e-6 m2 K/W (0.03 cm2 K/W).
- `materials.csv` has the same values in one table. `add_materials.py` adds the custom materials
  to an open Icepak project through PyAEDT.

## Materials in the conduction path (assign these)

| Material | Use | k [W/m K] | density [kg/m3] | cp [J/kg K] | viscosity [Pa s] | Source |
|---|---|---|---|---|---|---|
| Copper (AM) | fin plate, baseplate | 380 | 8960 | 385 | n/a | k: guidance. density, cp: standard copper |
| Silicon | die | 130 | 2330 | 712 | n/a | die is TTC-1002 silicon chips; k standard silicon |
| PG-25 | coolant | 0.48 | 1016 | 3970 | 2.1e-3 | ASHRAE / Melinder, ~30 C |

## Materials outside the main path (optional)

| Material | Use | k [W/m K] | density [kg/m3] | cp [J/kg K] | Source |
|---|---|---|---|---|---|
| Silicone | gasket above fin plate | 0.2 | 1150 | 1100 | standard silicone rubber, assumed |
| FR-4 | substrate, if modeled | 0.3 | 1900 | 1150 | standard FR-4, through plane |

Manifold and tubes carry no heat if their walls are treated as adiabatic, so they need no
material. The substrate can be left out or set adiabatic, which puts all 800 W into the cold
plate.

## Notes

- Copper k 380 is the as printed effective value from the guidance, below bulk copper (~400).
  Density and cp are standard copper; the guidance does not give them.
- The die is silicon: the TTV-4103 die is an array of TEA TTC-1002 thermal test chips (silicon,
  2.5 mm unit cells). TEA does not publish a conductivity; silicon k is temperature dependent,
  about 148 at room temperature and lower near 130 at the operating temperature. Take the die
  thickness from the CAD; TEA thins the wafers on a custom basis.
- PG-25 properties are temperature dependent. Approximate values:

  | Temperature [C] | k [W/m K] | density [kg/m3] | cp [J/kg K] | viscosity [Pa s] |
  |---|---|---|---|---|
  | 30 | 0.48 | 1016 | 3970 | 2.1e-3 |
  | 40 | 0.49 | 1012 | 3990 | 1.7e-3 |

  For a single value fluid, the 30 C row is fine. Confirm whether the 25 percent is by mass or
  volume, and confirm propylene glycol (not polypropylene glycol) with the organizers.

  Additional PG-25 properties at ~30 C:

  | Property | Value | Basis |
  |---|---|---|
  | Thermal expansion coefficient, beta | 3.9e-4 1/K | from the density gradient, -(1/rho)(drho/dT) |
  | Thermal diffusivity, alpha | 1.19e-7 m2/s | k / (rho cp), derived |
  | Molecular mass | 22.3 g/mol | mixture average, 25 percent by mass |

  beta is used for buoyancy, which is negligible in this pumped forced flow. alpha is derived from
  k, rho, and cp and is not a separate input. Molecular mass is used only for the ideal gas density
  law, not for an incompressible liquid.
- Silicone properties are assumed standard values; the guidance gives none. The gasket is a low
  conductivity seal outside the main path, so the exact value has little effect.
