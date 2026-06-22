"""Project spec values — mirrors SPEC.md (single source of truth for targets).

Update these here and in SPEC.md together if the spec changes.
"""

# --- defined requirements (design choices) ---
Q = 500.0            # heat load                 [W]
A_DIE = 4e-4         # heated die area           [m^2]  (4 cm^2)
T_IN = 30.0          # coolant inlet temperature [C]
T_J_MAX = 85.0       # junction limit (ceiling)  [C]
DESIGN_FLOW_LPM = 1.5  # design flow rate        [L/min]

# --- derived target ---
R_TARGET = (T_J_MAX - T_IN) / Q     # [C/W]  -> 0.11

# --- estimated stack resistances (refine with datasheet / CFD) ---
R_TIM = 0.025        # thermal interface material [C/W]
R_SPREADING = 0.015  # spreading resistance       [C/W]
