"""Spreading (constriction) resistance from the Lee, Song, Au, Moran, Yovanovich model.

Circular source on a circular plate of finite thickness with a convective back side.
Rectangular areas are converted to equivalent radii (a = sqrt(A / pi)). The result is
the conduction spreading plus 1D resistance from the source to the back face. The film
(convection) resistance is added separately by the caller.

Reference: Lee, Song, Au, Moran, Yovanovich, "Constriction/Spreading Resistance Model
for Electronics Packaging," ASME/JSME Thermal Engineering Conference, 1995.

Limit check: when source area equals plate area (eps = 1) the spreading term vanishes
and the result reduces to 1D conduction t / (k * A).
"""
from __future__ import annotations
import math


def spreading_resistance(A_source: float, A_plate: float, t_plate: float,
                         k: float, h_back: float) -> float:

    """Spreading plus 1D conduction resistance [C/W].

    A_source : heated die area              [m^2]
    A_plate  : plate (base) footprint area  [m^2]  (>= A_source)
    t_plate  : plate thickness under the channels [m]
    k        : plate conductivity           [W/m-K]
    h_back   : effective heat transfer coefficient on the cooled side [W/m^2-K]
    """

    a = math.sqrt(A_source / math.pi)        # equivalent source radius
    b = math.sqrt(A_plate / math.pi)         # equivalent plate radius
    eps = min(a / b, 1.0)                     # die no larger than base: no spreading
    tau = t_plate / b
    Bi = h_back * b / k

    lam = math.pi + 1.0 / (eps * math.sqrt(math.pi))
    phi = (math.tanh(lam * tau) + lam / Bi) / (1.0 + (lam / Bi) * math.tanh(lam * tau))
    psi = (eps * tau) / math.sqrt(math.pi) + (1.0 / math.sqrt(math.pi)) * (1.0 - eps) ** 1.5 * phi

    return psi / (k * a * math.sqrt(math.pi))
