"""Fluid and material properties for the cold-plate model.

Water properties are hard-coded at a reference temperature (~35 C) so the model
runs with zero dependencies. If you install CoolProp, you can swap in
temperature-dependent values without changing the rest of the code.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class FluidProperties:
    rho: float   # density            [kg/m^3]
    cp: float    # specific heat       [J/kg-K]
    k: float     # thermal conductivity[W/m-K]
    mu: float    # dynamic viscosity   [Pa-s]

    @property
    def Pr(self) -> float:
        """Prandtl number."""
        return self.mu * self.cp / self.k


# Water at ~35 C, 1 atm. Good enough for a hand-calc; refine with CoolProp later.
WATER_35C = FluidProperties(rho=994.0, cp=4180.0, k=0.62, mu=7.2e-4)

# Solid conductivity
K_COPPER = 400.0     # [W/m-K]
K_ALUMINUM = 167.0   # [W/m-K]
