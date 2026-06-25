"""Thermal and hydraulic model of a single phase parallel microchannel cold plate.

Live version of the analysis in HANDCALC.md, extended with pressure drop, pumping power,
a developing flow Nusselt number, and a Yovanovich spreading resistance. All SI units
unless a name says otherwise.

Model chain:
    geometry + flow  ->  Re, Nu (Hausen developing laminar or Dittus Boelter), h
                     ->  fin efficiency (channel side walls as straight fins)
                     ->  R_convection
    spreading        ->  R_spreading (Yovanovich, die into the base)
    + R_TIM + R_caloric                       (resistance stack)
    ->  R_total, T_junction, dP, pumping power

Assumptions (see HANDCALC.md section 6): constant wall temperature entrance correlation,
adiabatic fin tips, uniform heat flux into the base. Refine with CFD.
"""

from __future__ import annotations
from dataclasses import dataclass
import math

from properties import FluidProperties, WATER_35C, K_COPPER
from spreading import spreading_resistance

RE_TURBULENT = 2300.0      # laminar to turbulent transition

@dataclass
class ColdPlate:
    """Rectangular parallel microchannel cold plate (water flows along length)."""
    channel_width_m: float       # w
    channel_height_m: float      # h_c
    wall_thickness_m: float      # t_wall between channels (the fin thickness)
    n_channels: int              # N
    channel_length_m: float      # L (flow direction)
    base_thickness_m: float = 2e-3   # copper floor between die and channels
    k_solid: float = K_COPPER        # fin and base conductivity

    def hydraulic_diameter(self) -> float:
        w, h = self.channel_width_m, self.channel_height_m
        return 2.0 * w * h / (w + h)

    def channel_area(self) -> float:
        return self.channel_width_m * self.channel_height_m

    def wetted_area(self) -> float:
        perim = 2.0 * (self.channel_width_m + self.channel_height_m)
        return perim * self.channel_length_m * self.n_channels

    def fin_area(self) -> float:
        return 2.0 * self.channel_height_m * self.channel_length_m * self.n_channels

    def base_area(self) -> float:
        """Plate footprint covered by channels and walls [m^2]."""
        width = self.n_channels * (self.channel_width_m + self.wall_thickness_m)
        return width * self.channel_length_m


@dataclass
class Result:
    velocity: float
    Re: float
    regime: str
    Nu: float
    h: float
    fin_efficiency: float
    A_effective: float
    R_conv: float
    R_tim: float
    R_spread: float
    R_caloric: float
    R_total: float
    T_junction: float
    dP: float
    pumping_power: float
    meets_target: bool

    def report(self, name: str, R_target: float) -> str:
        ok = "PASS" if self.meets_target else "FAIL"
        return (
            f"  {name}\n"
            f"    flow regime      : {self.regime} (Re = {self.Re:,.0f})\n"
            f"    Nu, h            : {self.Nu:.2f}, {self.h:,.0f} W/m^2-K\n"
            f"    fin efficiency   : {self.fin_efficiency:.2f}\n"
            f"    R_conv           : {self.R_conv:.4f} C/W\n"
            f"    R_spread (Yov.)  : {self.R_spread:.4f} C/W\n"
            f"    R_total          : {self.R_total:.4f} C/W   (target <= {R_target:.3f})  [{ok}]\n"
            f"    T_junction       : {self.T_junction:.1f} C\n"
            f"    pressure drop    : {self.dP:,.0f} Pa\n"
            f"    pumping power    : {self.pumping_power*1e3:.2f} mW\n"
        )


def nusselt(Re: float, Pr: float, D_h: float, L: float) -> tuple[float, str]:
    """Return (Nu, regime).

    Laminar: Hausen developing flow correlation (constant wall temperature), which
    raises Nu for short channels and higher flow through the Graetz number.
    Turbulent: Dittus Boelter.
    """
    if Re < RE_TURBULENT:
        Gz = (D_h / L) * Re * Pr
        Nu = 3.66 + (0.0668 * Gz) / (1.0 + 0.04 * Gz ** (2.0 / 3.0))
        return Nu, "laminar"
    return 0.023 * Re ** 0.8 * Pr ** 0.4, "turbulent"


def fin_efficiency(h: float, plate: ColdPlate) -> float:
    """Efficiency of the channel side walls treated as straight fins (adiabatic tip)."""
    m = math.sqrt(2.0 * h / (plate.k_solid * plate.wall_thickness_m))
    mL = m * plate.channel_height_m
    return math.tanh(mL) / mL


def analyze(
    plate: ColdPlate,
    flow_lpm: float,
    Q: float,
    A_die: float,
    T_in: float,
    T_j_max: float,
    R_tim: float,
    fluid: FluidProperties = WATER_35C,
) -> Result:
    """Run the full thermal and hydraulic model for one cold plate at one flow rate."""
    R_target = (T_j_max - T_in) / Q

    # flow
    flow_m3s = flow_lpm / 60_000.0
    flow_per_channel = flow_m3s / plate.n_channels
    velocity = flow_per_channel / plate.channel_area()
    D_h = plate.hydraulic_diameter()
    Re = fluid.rho * velocity * D_h / fluid.mu

    # convection
    Nu, regime = nusselt(Re, fluid.Pr, D_h, plate.channel_length_m)
    h = Nu * fluid.k / D_h
    eta = fin_efficiency(h, plate)
    A_wet = plate.wetted_area()
    A_fin = plate.fin_area()
    A_base_wetted = A_wet - A_fin
    A_eff = A_base_wetted + eta * A_fin
    R_conv = 1.0 / (h * A_eff)

    # spreading (Yovanovich), die into the base; film added separately above
    A_plate = plate.base_area()
    h_back = (h * A_eff) / A_plate
    R_spread = spreading_resistance(A_die, A_plate, plate.base_thickness_m,
                                    plate.k_solid, h_back)

    # caloric (coolant bulk heating, referenced to mean fluid temperature)
    mdot = fluid.rho * flow_m3s
    R_caloric = 1.0 / (2.0 * mdot * fluid.cp)

    # total and junction temperature
    R_total = R_conv + R_tim + R_spread + R_caloric
    T_junction = T_in + Q * R_total

    # pressure drop and pumping power
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
