"""K-16 cold plate hand calc: spec data and run.

Edit the values, then run:   python spec.py

Each value is labeled:
  [K-16]   fixed by the competition guidance, do not change
  [DESIGN] your design variable, change these to try fin geometries
  [ASSUME] a hand calc assumption, refine later

This is a sanity check on the CFD, not a replacement. See functions.py for the method.
"""
from functions import analyze, figure_of_merit

# ---------------------------------------------------------------------------
# Fluid: PG-25, 25 percent propylene glycol, at about 30 C
# [K-16] the coolant is PG-25. Property values are from ASHRAE / Melinder glycol tables
# at ~30 C. Verify against the actual coolant datasheet; they vary with temperature and
# with the mass vs volume basis of the 25 percent.
# ---------------------------------------------------------------------------
RHO      = 1016.0    # density               [kg/m3]
CP       = 3970.0    # specific heat          [J/kg-K]
K_FLUID  = 0.48      # thermal conductivity   [W/m-K]
MU       = 2.1e-3    # dynamic viscosity      [Pa-s]

# ---------------------------------------------------------------------------
# Material: additively manufactured copper fin plate
# ---------------------------------------------------------------------------
K_SOLID  = 380.0     # thermal conductivity   [W/m-K]   [K-16] as-printed copper

# ---------------------------------------------------------------------------
# Operating conditions
# ---------------------------------------------------------------------------
FLOW_LPM     = 1.2   # coolant flow rate      [L/min]   [K-16]
INLET_TEMP   = 30.0  # coolant inlet temp     [C]       [K-16]
POWER_TOTAL  = 800.0 # total die power        [W]       [K-16] H 400 + BG1 200 + BG2 200
TIM_CM2KW    = 0.03  # TTV to plate TIM       [cm2-K/W] [K-16] area specific resistance

# ---------------------------------------------------------------------------
# Heated die (sets the TIM and spreading source areas)
# ---------------------------------------------------------------------------
DIE_X = 32.2e-3      # die length             [m]       [K-16]
DIE_Y = 25.8e-3      # die width              [m]       [K-16]
DIE_AREA = DIE_X * DIE_Y                          # die area [m2]

# ---------------------------------------------------------------------------
# Power map: three heater rows tiling the die (the guidance gives sizes and powers
# but not the areas; they are computed here). Each row is 8.6 x 32.2 mm. The three
# rows stack to 25.8 mm and sum to 800 W, so they cover the full die.
#   (name, width X [m], height Y [m], power [W])    [K-16]
# ---------------------------------------------------------------------------
ZONES = [
    ("H",   32.2e-3, 8.6e-3, 400.0),   # middle row, the hotspot
    ("BG1", 32.2e-3, 8.6e-3, 200.0),   # top row
    ("BG2", 32.2e-3, 8.6e-3, 200.0),   # bottom row
]

# ---------------------------------------------------------------------------
# Baseline fin plate, for the Figure of Merit.
# The competition baseline R_b and dP_b come from simulating the provided baseline plate.
# Until that CFD exists, set these to None and the run estimates them with this same hand
# calc on a simple straight-fin baseline (BASELINE_* below), giving a rough FoM. Once you
# have the baseline CFD, put R_b and dP_b here and they take over.
# ---------------------------------------------------------------------------
R_BASELINE  = None   # baseline thermal resistance  [K/W]   [K-16] from baseline CFD, else estimated
DP_BASELINE = None   # baseline pressure drop        [Pa]    [K-16] from baseline CFD, else estimated

# ---------------------------------------------------------------------------
# Fin plate
# Design envelope is 36 x 29 x 2 mm. The footprint is the area the die spreads into.
# ---------------------------------------------------------------------------
PLATE_WIDTH  = 36e-3 # plate width            [m]       [K-16] envelope X
PLATE_LENGTH = 29e-3 # plate length           [m]       [K-16] envelope Y
PLATE_AREA   = PLATE_WIDTH * PLATE_LENGTH         # fin plate footprint [m2]
BASE_THICKNESS = 2.0e-3   # baseplate thickness [m]      [K-16] baseplate is 2 mm

# ---------------------------------------------------------------------------
# Fin geometry (your design variables). Change these to try designs.
# ---------------------------------------------------------------------------
CHANNEL_LENGTH = 15e-3   # flow length over the fins [m] [ASSUME] split flow, about half of 29 mm
CHANNEL_WIDTH  = 0.30e-3 # channel width             [m] [DESIGN] AM range 0.10 to 0.50 mm
CHANNEL_HEIGHT = 2.0e-3  # channel / fin height      [m] [DESIGN] up to 2 mm (envelope Z)
WALL_THICKNESS = 0.30e-3 # fin (wall) thickness      [m] [DESIGN] AM range 0.10 to 0.50 mm

# channels that fit across the plate width at this pitch
N_CHANNELS = int(PLATE_WIDTH / (CHANNEL_WIDTH + WALL_THICKNESS))   # [DESIGN] derived

# ---------------------------------------------------------------------------
# Baseline straight-fin plate, used to estimate R_b and dP_b when no baseline CFD is set.
# A simple plate at the coarse end of the design rules (0.5 mm fins and channels), a stand
# in for the provided baseline. Replace with the real baseline once it is simulated.  [ASSUME]
# ---------------------------------------------------------------------------
BASE_CHANNEL_WIDTH  = 0.50e-3
BASE_CHANNEL_HEIGHT = 2.0e-3
BASE_WALL_THICKNESS = 0.50e-3
BASE_CHANNEL_LENGTH = 15e-3
BASE_N_CHANNELS = int(PLATE_WIDTH / (BASE_CHANNEL_WIDTH + BASE_WALL_THICKNESS))


def run(channel_width, channel_height, wall_thickness, channel_length, n_channels):
    """Run the hand calc for one fin geometry, with all the fixed K-16 inputs."""
    return analyze(
        channel_width=channel_width, channel_height=channel_height,
        wall_thickness=wall_thickness, channel_length=channel_length,
        n_channels=n_channels, base_thickness=BASE_THICKNESS,
        die_area=DIE_AREA, plate_area=PLATE_AREA, k_solid=K_SOLID,
        rho=RHO, cp=CP, k_fluid=K_FLUID, mu=MU,
        flow_lpm=FLOW_LPM, power_total=POWER_TOTAL,
        tim_resistance_si=TIM_CM2KW * 1e-4,   # cm2-K/W -> m2-K/W
        inlet_temp=INLET_TEMP,
    )


def main():
    r = run(CHANNEL_WIDTH, CHANNEL_HEIGHT, WALL_THICKNESS, CHANNEL_LENGTH, N_CHANNELS)

    print("K-16 cold plate hand calc")
    print("  power map:")
    for name, zx, zy, q in ZONES:
        area = zx * zy
        print(f"    {name:4s}: {zx*1e3:.1f} x {zy*1e3:.1f} mm, "
              f"{area*1e6:.1f} mm2, {q:.0f} W, {q/(area*1e6):.2f} W/mm2")
    z_area = sum(zx * zy for _, zx, zy, _ in ZONES)
    z_power = sum(q for *_, q in ZONES)
    print(f"    sum : {z_area*1e6:.1f} mm2 ({DIE_AREA*1e6:.1f} mm2 die), {z_power:.0f} W")
    print(f"  design   : {CHANNEL_WIDTH*1e3:.2f} x {CHANNEL_HEIGHT*1e3:.2f} mm channels, "
          f"{WALL_THICKNESS*1e3:.2f} mm walls, {N_CHANNELS} channels, "
          f"{CHANNEL_LENGTH*1e3:.0f} mm flow length")
    print(f"  flow     : {r['regime']} (Re {r['Re']:.0f}, Pr {r['Pr']:.1f}), v {r['velocity']:.2f} m/s")
    print(f"  h, fin   : {r['h']:.0f} W/m2-K, fin efficiency {r['fin_eff']:.2f}")
    print(f"  R_conv   : {r['R_conv']:.4f} K/W")
    print(f"  R_tim    : {r['R_tim']:.4f} K/W")
    print(f"  R_spread : {r['R_spread']:.4f} K/W")
    print(f"  R_caloric: {r['R_caloric']:.4f} K/W")
    print(f"  R_total  : {r['R_total']:.4f} K/W")
    print(f"  chip temp: {r['chip_temp']:.1f} C   (overall average; the hotspot peak is higher)")
    print(f"  dP       : {r['dP']:.0f} Pa")
    print(f"  pumping  : {r['pumping']*1e3:.1f} mW")

    if R_BASELINE is not None and DP_BASELINE is not None:
        r_b, dp_b, source = R_BASELINE, DP_BASELINE, "baseline CFD"
    else:
        b = run(BASE_CHANNEL_WIDTH, BASE_CHANNEL_HEIGHT, BASE_WALL_THICKNESS,
                BASE_CHANNEL_LENGTH, BASE_N_CHANNELS)
        r_b, dp_b, source = b['R_total'], b['dP'], "hand calc baseline, rough"
    fom = figure_of_merit(r['R_total'], r['dP'], r_b, dp_b)
    print(f"  baseline : R {r_b:.4f} K/W, dP {dp_b:.0f} Pa   ({source})")
    print(f"  FoM      : {fom:+.3f}   (both R use the average chip temp, not the peak)")


if __name__ == "__main__":
    main()
