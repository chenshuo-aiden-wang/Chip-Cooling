"""K-16 cold plate hand calc: baseline fin plate.

Edit the values, then run:   python spec.py

Each value is labeled:
  [K-16]   fixed by the competition guidance, do not change
  [CAD]    read from the provided baseline plate geometry
  [ASSUME] a hand calc assumption, refine later

Computes the baseline plate thermal resistance R_b and pressure drop dP_b. See functions.py
for the method.
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
    ("H",   32.2e-3, 8.6e-3, 400.0),   # middle row
    ("BG1", 32.2e-3, 8.6e-3, 200.0),   # top row
    ("BG2", 32.2e-3, 8.6e-3, 200.0),   # bottom row
]

# ---------------------------------------------------------------------------
# Fin plate envelope: 36 x 29 x 2 mm.
# ---------------------------------------------------------------------------
PLATE_WIDTH  = 36e-3 # plate width            [m]       [K-16] envelope X
PLATE_LENGTH = 29e-3 # plate length           [m]       [K-16] envelope Y
PLATE_AREA   = PLATE_WIDTH * PLATE_LENGTH         # fin plate footprint [m2]
BASE_THICKNESS = 2.0e-3   # baseplate thickness [m]      [K-16] baseplate is 2 mm

# ---------------------------------------------------------------------------
# Baseline fin geometry, read from the provided baseline plate CAD.
# ---------------------------------------------------------------------------
CHANNEL_LENGTH = 29e-3   # fin channel length, flow direction [m] [CAD]
CHANNEL_WIDTH  = 15e-5   # channel (gap) width       [m] [CAD]
CHANNEL_HEIGHT = 2.0e-3  # channel / fin height      [m] [CAD] envelope Z
WALL_THICKNESS = 15e-5   # fin (wall) thickness      [m] [CAD]

# channels that fit across the plate width at this pitch
N_CHANNELS = int(PLATE_WIDTH / (CHANNEL_WIDTH + WALL_THICKNESS))   # [CAD] derived

# ---------------------------------------------------------------------------
# Reference for the Figure of Merit. Fill from the baseline CFD; None reports pending.
# ---------------------------------------------------------------------------
R_BASELINE  = None   # baseline thermal resistance  [K/W]   from baseline CFD
DP_BASELINE = None   # baseline pressure drop        [Pa]    from baseline CFD


def main():
    r = analyze(
        channel_width=CHANNEL_WIDTH, channel_height=CHANNEL_HEIGHT,
        wall_thickness=WALL_THICKNESS, channel_length=CHANNEL_LENGTH,
        n_channels=N_CHANNELS, base_thickness=BASE_THICKNESS,
        die_area=DIE_AREA, plate_area=PLATE_AREA, k_solid=K_SOLID,
        rho=RHO, cp=CP, k_fluid=K_FLUID, mu=MU,
        flow_lpm=FLOW_LPM, power_total=POWER_TOTAL,
        tim_resistance_si=TIM_CM2KW * 1e-4,   # cm2-K/W -> m2-K/W
        inlet_temp=INLET_TEMP,
    )

    print("K-16 cold plate hand calc: baseline fin plate")
    print("  power map:")
    for name, zx, zy, q in ZONES:
        area = zx * zy
        print(f"    {name:4s}: {zx*1e3:.1f} x {zy*1e3:.1f} mm, "
              f"{area*1e6:.1f} mm2, {q:.0f} W, {q/(area*1e6):.2f} W/mm2")
    z_area = sum(zx * zy for _, zx, zy, _ in ZONES)
    z_power = sum(q for *_, q in ZONES)
    print(f"    sum : {z_area*1e6:.1f} mm2 ({DIE_AREA*1e6:.1f} mm2 die), {z_power:.0f} W")
    print(f"  baseline : {CHANNEL_WIDTH*1e3:.2f} x {CHANNEL_HEIGHT*1e3:.2f} mm channels, "
          f"{WALL_THICKNESS*1e3:.2f} mm walls, {N_CHANNELS} channels, "
          f"{CHANNEL_LENGTH*1e3:.0f} mm flow length")
    print(f"  flow     : {r['regime']} (Re {r['Re']:.0f}, Pr {r['Pr']:.1f}), v {r['velocity']:.2f} m/s")
    print(f"  h, fin   : {r['h']:.0f} W/m2-K, fin efficiency {r['fin_eff']:.2f}")
    print(f"  R_conv   : {r['R_conv']:.4f} K/W")
    print(f"  R_tim    : {r['R_tim']:.4f} K/W")
    print(f"  R_spread : {r['R_spread']:.4f} K/W")
    print(f"  R_caloric: {r['R_caloric']:.4f} K/W")
    print(f"  R_total  : {r['R_total']:.4f} K/W   (R_b)")
    print(f"  chip temp: {r['chip_temp']:.1f} C")
    print(f"  dP       : {r['dP']:.0f} Pa   (dP_b)")
    print(f"  pumping  : {r['pumping']*1e3:.1f} mW")

    if R_BASELINE is not None and DP_BASELINE is not None:
        fom = figure_of_merit(r['R_total'], r['dP'], R_BASELINE, DP_BASELINE)
        print(f"  FoM      : {fom:+.3f}   (vs R_BASELINE {R_BASELINE:.4f} K/W, "
              f"DP_BASELINE {DP_BASELINE:.0f} Pa)")
    else:
        print("  FoM      : pending (set R_BASELINE and DP_BASELINE)")


if __name__ == "__main__":
    main()
