"""Cold plate hand calc functions.

Thermal resistance and pressure drop for a parallel microchannel or finned cold plate. All
inputs come from spec.py. SI units.

Chain:
  flow -> Reynolds -> Nusselt (developing laminar / turbulent) -> h
       -> fin efficiency -> convective resistance
  + TIM + spreading (Yovanovich) + caloric -> total resistance and chip temperature
  + friction -> pressure drop and pumping power

Assumptions:
  - Uniform parallel channels.
  - Total power applied uniformly.
"""
import math


def figure_of_merit(R, dP, R_baseline, dP_baseline):
    """Figure of Merit.

        FoM = 0.7 (R_b - R) / R_b + 0.3 (dP_b - dP) / dP_b

    R_baseline and dP_baseline are the baseline fin plate values.
    """
    return 0.7 * (R_baseline - R) / R_baseline + 0.3 * (dP_baseline - dP) / dP_baseline


def spreading_resistance(A_source, A_plate, t_plate, k, h_back):
    """Yovanovich spreading plus 1D conduction resistance, die into the plate [K/W].

    Lee, Song, Au, Moran, Yovanovich (1995). Circular source on a circular plate of finite
    thickness with a convective back side; rectangular areas are converted to equivalent radii.
    When the source area equals the plate area it reduces to 1D conduction t / (k A).
    """
    a = math.sqrt(A_source / math.pi)        # equivalent source radius
    b = math.sqrt(A_plate / math.pi)         # equivalent plate radius
    eps = min(a / b, 1.0)                     # source no larger than plate
    tau = t_plate / b
    Bi = h_back * b / k
    lam = math.pi + 1.0 / (eps * math.sqrt(math.pi))
    phi = (math.tanh(lam * tau) + lam / Bi) / (1.0 + (lam / Bi) * math.tanh(lam * tau))
    psi = (eps * tau) / math.sqrt(math.pi) + (1.0 / math.sqrt(math.pi)) * (1.0 - eps) ** 1.5 * phi
    return psi / (k * a * math.sqrt(math.pi))


def analyze(channel_width, channel_height, wall_thickness, channel_length,
            n_channels, base_thickness, die_area, plate_area, k_solid,
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

    # spreading (Yovanovich): die into the plate, with the channel convection as the back side film
    h_back = (h * a_eff) / plate_area
    R_spread = spreading_resistance(die_area, plate_area, base_thickness, k_solid, h_back)

    # interface and caloric
    R_tim = tim_resistance_si / die_area          # area specific [m2-K/W] -> [K/W]
    mdot = rho * flow_m3s
    R_caloric = 1.0 / (2.0 * mdot * cp)

    R_total = R_conv + R_tim + R_spread + R_caloric
    chip_temp = inlet_temp + power_total * R_total

    # pressure drop and pumping power
    f = 64.0 / Re if regime == "laminar" else 0.316 * Re ** -0.25
    dP = f * (channel_length / d_h) * 0.5 * rho * velocity ** 2
    pumping = dP * flow_m3s

    return {
        "regime": regime, "Re": Re, "Pr": Pr, "velocity": velocity, "Nu": Nu, "h": h,
        "fin_eff": fin_eff, "R_conv": R_conv, "R_tim": R_tim, "R_spread": R_spread,
        "R_caloric": R_caloric, "R_total": R_total, "chip_temp": chip_temp,
        "dP": dP, "pumping": pumping,
    }
