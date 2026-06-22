"""Thermal + hydraulic model of a single-phase parallel-microchannel cold plate.

Live version of the hand-calc in HANDCALC.md, extended with pressure drop and
pumping power. All SI units unless a name says otherwise.

Model chain:
    geometry + flow  ->  Re, Nu, h            (convection)
                     ->  fin efficiency        (tall thin channel walls act as fins)
                     ->  R_convection
    + R_TIM + R_spreading + R_caloric         (resistance stack)
    ->  R_total, T_junction, dP, pumping power

Assumptions (see HANDCALC.md sec 6): fully-developed flow, constant laminar Nu,
adiabatic fin tips, uniform heat flux. Refine with CFD.
"""
from __future__ import annotations
from dataclasses import dataclass
import math

from properties import FluidProperties, WATER_35C, K_COPPER

LAMINAR_NU = 4.36          # fully-developed, ~constant heat flux (duct approximation)
RE_TURBULENT = 2300.0      # laminar/turbulent transition


@dataclass
class ColdPlate:
    """Rectangular parallel-microchannel cold plate (water flows along length)."""
    channel_width_m: float      # w
    channel_height_m: float     # h_c
    wall_thickness_m: float     # t_wall between channels -> fin thickness
    n_channels: int             # N
    channel_length_m: float     # L (flow direction)
    k_solid: float = K_COPPER   # fin/solid conductivity

    # --- geometry ---
    def hydraulic_diameter(self) -> float:
        w, h = self.channel_width_m, self.channel_height_m
        return 2.0 * w * h / (w + h)

    def channel_area(self) -> float:
        """Cross-section of one channel [m^2]."""
        return self.channel_width_m * self.channel_height_m

    def wetted_area(self) -> float:
        """Total wetted area of all channels [m^2] (full rectangular perimeter)."""
        perim = 2.0 * (self.channel_width_m + self.channel_height_m)
        return perim * self.channel_length_m * self.n_channels

    def fin_area(self) -> float:
        """Side-wall (fin) area of all channels [m^2]."""
        return 2.0 * self.channel_height_m * self.channel_length_m * self.n_channels


@dataclass
class Result:
    # flow / convection
    velocity: float
    Re: float
    regime: str
    Nu: float
    h: float
    fin_efficiency: float
    A_effective: float
    # resistances [C/W]
    R_conv: float
    R_tim: float
    R_spread: float
    R_caloric: float
    R_total: float
    # outputs
    T_junction: float          # [C]
    dP: float                  # [Pa]
    pumping_power: float       # [W]
    meets_target: bool

    def report(self, name: str, R_target: float) -> str:
        ok = "PASS" if self.meets_target else "FAIL"
        return (
            f"  {name}\n"
            f"    flow regime      : {self.regime} (Re = {self.Re:,.0f})\n"
            f"    velocity         : {self.velocity:.2f} m/s\n"
            f"    h                : {self.h:,.0f} W/m^2-K\n"
            f"    fin efficiency   : {self.fin_efficiency:.2f}\n"
            f"    R_conv           : {self.R_conv:.4f} C/W\n"
            f"    R_total          : {self.R_total:.4f} C/W   (target <= {R_target:.3f})  [{ok}]\n"
            f"    T_junction       : {self.T_junction:.1f} C\n"
            f"    pressure drop    : {self.dP:,.0f} Pa\n"
            f"    pumping power    : {self.pumping_power*1e3:.2f} mW\n"
        )


def nusselt(Re: float, Pr: float) -> tuple[float, str]:
    """Return (Nu, regime). Dittus-Boelter for turbulent, constant for laminar."""
    if Re < RE_TURBULENT:
        return LAMINAR_NU, "laminar"
    return 0.023 * Re ** 0.8 * Pr ** 0.4, "turbulent"


def fin_efficiency(h: float, plate: ColdPlate) -> float:
    """Efficiency of the channel side-walls treated as straight fins (adiabatic tip)."""
    m = math.sqrt(2.0 * h / (plate.k_solid * plate.wall_thickness_m))
    mL = m * plate.channel_height_m
    return math.tanh(mL) / mL


def analyze(
    plate: ColdPlate,
    flow_lpm: float,
    Q: float,
    T_in: float,
    T_j_max: float,
    R_tim: float,
    R_spread: float,
    fluid: FluidProperties = WATER_35C,
) -> Result:
    """Run the full thermal + hydraulic model for one cold plate at one flow rate."""
    R_target = (T_j_max - T_in) / Q

    # --- flow ---
    flow_m3s = flow_lpm / 60_000.0                 # L/min -> m^3/s
    flow_per_channel = flow_m3s / plate.n_channels
    velocity = flow_per_channel / plate.channel_area()
    D_h = plate.hydraulic_diameter()
    Re = fluid.rho * velocity * D_h / fluid.mu

    # --- convection ---
    Nu, regime = nusselt(Re, fluid.Pr)
    h = Nu * fluid.k / D_h
    eta = fin_efficiency(h, plate)
    A_wet = plate.wetted_area()
    A_fin = plate.fin_area()
    A_base = A_wet - A_fin
    A_eff = A_base + eta * A_fin
    R_conv = 1.0 / (h * A_eff)

    # --- caloric (coolant bulk heating, referenced to mean fluid temp) ---
    mdot = fluid.rho * flow_m3s
    R_caloric = 1.0 / (2.0 * mdot * fluid.cp)

    # --- total + junction temp ---
    R_total = R_conv + R_tim + R_spread + R_caloric
    T_junction = T_in + Q * R_total

    # --- pressure drop + pumping power ---
    f = 64.0 / Re if regime == "laminar" else 0.316 * Re ** -0.25
    dP = f * (plate.channel_length_m / D_h) * 0.5 * fluid.rho * velocity ** 2
    pumping_power = dP * flow_m3s

    return Result(
        velocity=velocity, Re=Re, regime=regime, Nu=Nu, h=h,
        fin_efficiency=eta, A_effective=A_eff,
        R_conv=R_conv, R_tim=R_tim, R_spread=R_spread, R_caloric=R_caloric,
        R_total=R_total, T_junction=T_junction, dP=dP, pumping_power=pumping_power,
        meets_target=(R_total <= R_target),
    )
