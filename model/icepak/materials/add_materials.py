"""Add the K-16 custom materials to an open Icepak project via PyAEDT.

Requires PyAEDT (pip install pyaedt) and Ansys Electronics Desktop. Set AEDT_VERSION to your
installed version. Open the Icepak project first, then run:  python add_materials.py

Values match materials.csv. Copper, silicon, FR-4 already exist in the AEDT library; this script
adds the as printed copper and PG-25, which are not in the library, and silicone.
"""
try:
    from ansys.aedt.core import Icepak          # PyAEDT 0.9 and newer
except ImportError:
    from pyaedt import Icepak                   # older PyAEDT

AEDT_VERSION = "2025.1"

# name -> (k [W/m K], density [kg/m3], cp [J/kg K], viscosity [Pa s] or None, beta [1/K] or None)
MATERIALS = {
    "Copper_AM": (380.0, 8960.0, 385.0, None, None),
    "Silicon_die": (130.0, 2330.0, 712.0, None, None),
    "Silicone_gasket": (0.2, 1150.0, 1100.0, None, None),
    "PG-25": (0.48, 1016.0, 3970.0, 2.1e-3, 3.9e-4),
}


def main():
    ipk = Icepak(version=AEDT_VERSION, new_desktop=False)   # attach to the open session

    for name, (k, rho, cp, mu, beta) in MATERIALS.items():
        mat = ipk.materials.add_material(name)
        mat.thermal_conductivity = k
        mat.mass_density = rho
        mat.specific_heat = cp
        if mu is not None:
            mat.viscosity = mu
        if beta is not None:
            mat.thermal_expansion_coefficient = beta

    ipk.save_project()
    ipk.release_desktop(close_projects=False, close_desktop=False)


if __name__ == "__main__":
    main()
