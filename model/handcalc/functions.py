"""Cold plate hand calc functions.

A first cut estimate of thermal resistance and pressure drop for a parallel
microchannel or finned cold plate, used to sanity check the CFD. All inputs come from
spec.py. SI units throughout.

Chain:
  flow -> Reynolds -> Nusselt (developing laminar / turbulent) -> h
       -> fin efficiency -> convective resistance
  + TIM + base conduction + caloric -> total resistance and chip temperature
  + friction -> pressure drop and pumping power

Simplifications (this is a hand calc, not CFD):
  - Uniform parallel channels. The real manifold flow distribution is ignored.
  - Total power applied uniformly. The hotspot driven peak, the real R_th,max, is
    higher, and that is what CFD resolves.
  - 1D base conduction, no detailed spreading.
"""
import math


def analyze(channel_width, channel_height, wall_thickness, channel_length,
            n_channels, base_thickness, die_area, k_solid,
            rho, cp, k_fluid, mu,
            flow_lpm, power_total, tim_resistance_si, inlet_temp):
    Pr = mu * cp / k_fluid

    # flow
    flow_m3s = flow_lpm / 60_000.0
    flow_per_channel = flow_m3s / n_channels
    channel_area = channel_width * channel_height
    velocity = flow_per_channel / channel_area
    d_h = 2.0 * channel_width * channel_height / (channel_width + channel_height)
    Re = rho * velocity * d_h / mu

    # convection
    if Re < 2300.0:
        Gz = (d_h / channel_length) * Re * Pr
        Nu = 3.66 + (0.0668 * Gz) / (1.0 + 0.04 * Gz ** (2.0 / 3.0))
        regime = "laminar"
    else:
        Nu = 0.023 * Re ** 0.8 * Pr ** 0.4
        regime = "turbulent"
    h = Nu * k_fluid / d_h

    # fin efficiency (channel side walls treated as straight fins)
    m = math.sqrt(2.0 * h / (k_solid * wall_thickness))
    fin_eff = math.tanh(m * channel_height) / (m * channel_height)
    a_floor = n_channels * channel_width * channel_length
    a_fin = n_channels * 2.0 * channel_height * channel_length
    a_eff = a_floor + fin_eff * a_fin
    R_conv = 1.0 / (h * a_eff)

    # other resistances
    R_tim = tim_resistance_si / die_area          # area specific [m2-K/W] -> [K/W]
    R_base = base_thickness / (k_solid * die_area)
    mdot = rho * flow_m3s
    R_caloric = 1.0 / (2.0 * mdot * cp)
    R_total = R_conv + R_tim + R_base + R_caloric
    chip_temp = inlet_temp + power_total * R_total

    # pressure drop and pumping power
    f = 64.0 / Re if regime == "laminar" else 0.316 * Re ** -0.25
    dP = f * (channel_length / d_h) * 0.5 * rho * velocity ** 2
    pumping = dP * flow_m3s

    return {
        "regime": regime, "Re": Re, "Pr": Pr, "velocity": velocity, "Nu": Nu, "h": h,
        "fin_eff": fin_eff, "R_conv": R_conv, "R_tim": R_tim, "R_base": R_base,
        "R_caloric": R_caloric, "R_total": R_total, "chip_temp": chip_temp,
        "dP": dP, "pumping": pumping,
    }
