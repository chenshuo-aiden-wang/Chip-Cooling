"""K-16 cold plate hand calc: spec data and run.

Edit the values, then run:   python spec.py

Each value is labeled:
  [K-16]   fixed by the competition guidance, do not change
  [DESIGN] your design variable, change these to try fin geometries
  [ASSUME] a hand calc assumption, refine later

This is a sanity check on the CFD, not a replacement. See functions.py for the method.
"""
from functions import analyze

# ---------------------------------------------------------------------------
# Fluid: PG-25, 25 percent propylene glycol, at about 30 C
# [K-16] the coolant is PG-25. [ASSUME] the property values (verify on a datasheet).
# ---------------------------------------------------------------------------
RHO      = 1018.0     # density               [kg/m3]   [ASSUME]
CP       = 3950.0     # specific heat          [J/kg-K]  [ASSUME]
K_FLUID  = 0.49       # thermal conductivity   [W/m-K]   [ASSUME]
MU       = 2.2e-3     # dynamic viscosity      [Pa-s]    [ASSUME]

# ---------------------------------------------------------------------------
# Material: additively manufactured copper fin plate
# ---------------------------------------------------------------------------
K_SOLID  = 380.0      # thermal conductivity   [W/m-K]   [K-16] as-printed copper

# ---------------------------------------------------------------------------
# Operating conditions
# ---------------------------------------------------------------------------
FLOW_LPM     = 1.2    # coolant flow rate      [L/min]   [K-16]
INLET_TEMP   = 30.0   # coolant inlet temp     [C]       [K-16]
POWER_TOTAL  = 800.0  # total die power        [W]       [K-16] H 400 + BG1 200 + BG2 200
TIM_CM2KW    = 0.03   # TTV to plate TIM       [cm2-K/W] [K-16] area specific resistance

# ---------------------------------------------------------------------------
# Heated die (sets the TIM and base areas)
# ---------------------------------------------------------------------------
DIE_X = 32.2e-3       # die length             [m]       [K-16]
DIE_Y = 25.8e-3       # die width              [m]       [K-16]
DIE_AREA = DIE_X * DIE_Y                          # die area [m2]

# ---------------------------------------------------------------------------
# Fin plate geometry
# Design envelope is 36 x 29 x 2 mm. Change the channel sizes to try designs.
# ---------------------------------------------------------------------------
PLATE_WIDTH    = 36e-3   # plate width across the flow [m] [K-16] envelope X
CHANNEL_LENGTH = 15e-3   # flow length over the fins   [m] [ASSUME] split flow, about half of 29 mm
CHANNEL_WIDTH  = 0.30e-3 # channel width               [m] [DESIGN] AM range 0.10 to 0.50 mm
CHANNEL_HEIGHT = 2.0e-3  # channel / fin height        [m] [DESIGN] up to 2 mm (envelope Z)
WALL_THICKNESS = 0.30e-3 # fin (wall) thickness        [m] [DESIGN] AM range 0.10 to 0.50 mm
BASE_THICKNESS = 2.0e-3  # baseplate thickness         [m] [K-16] baseplate is 2 mm

# channels that fit across the plate width at this pitch
N_CHANNELS = int(PLATE_WIDTH / (CHANNEL_WIDTH + WALL_THICKNESS))   # [DESIGN] derived


def main():
    r = analyze(
        channel_width=CHANNEL_WIDTH, channel_height=CHANNEL_HEIGHT,
        wall_thickness=WALL_THICKNESS, channel_length=CHANNEL_LENGTH,
        n_channels=N_CHANNELS, base_thickness=BASE_THICKNESS, die_area=DIE_AREA,
        k_solid=K_SOLID, rho=RHO, cp=CP, k_fluid=K_FLUID, mu=MU,
        flow_lpm=FLOW_LPM, power_total=POWER_TOTAL,
        tim_resistance_si=TIM_CM2KW * 1e-4,   # cm2-K/W -> m2-K/W
        inlet_temp=INLET_TEMP,
    )

    print("K-16 cold plate hand calc")
    print(f"  design   : {CHANNEL_WIDTH*1e3:.2f} x {CHANNEL_HEIGHT*1e3:.2f} mm channels, "
          f"{WALL_THICKNESS*1e3:.2f} mm walls, {N_CHANNELS} channels, "
          f"{CHANNEL_LENGTH*1e3:.0f} mm flow length")
    print(f"  flow     : {r['regime']} (Re {r['Re']:.0f}, Pr {r['Pr']:.1f}), v {r['velocity']:.2f} m/s")
    print(f"  h, fin   : {r['h']:.0f} W/m2-K, fin efficiency {r['fin_eff']:.2f}")
    print(f"  R_conv   : {r['R_conv']:.4f} K/W")
    print(f"  R_tim    : {r['R_tim']:.4f} K/W")
    print(f"  R_base   : {r['R_base']:.4f} K/W")
    print(f"  R_caloric: {r['R_caloric']:.4f} K/W")
    print(f"  R_total  : {r['R_total']:.4f} K/W")
    print(f"  chip temp: {r['chip_temp']:.1f} C   (overall average; the hotspot peak is higher)")
    print(f"  dP       : {r['dP']:.0f} Pa")
    print(f"  pumping  : {r['pumping']*1e3:.1f} mW")


if __name__ == "__main__":
    main()
