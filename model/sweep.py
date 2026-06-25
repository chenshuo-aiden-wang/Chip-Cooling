"""Cold plate design sweep.

Explores how the channel geometry and the flow rate set the thermal resistance (C/W) and the
pumping power, against the spec target in spec.py. Run from the model/ directory:

    python sweep.py

What it sweeps and why:
  - Channel WIDTH is the dominant lever. Narrower channels shrink the hydraulic diameter
    (so the heat transfer coefficient h rises, h ~ 1/D_h) and pack more channels onto the
    base (more wetted area). Two strong effects, so resistance drops steeply. Narrow
    channels also raise pumping power.
  - Channel HEIGHT is a weak lever. Taller channels add fin area, but tall thin fins lose
    efficiency, so resistance drops only a little.
  - FLOW rate helps through the developing flow entrance effect, but costs pumping power.

Wall thickness is held at a fixed machinable value (WALL), so changing channel width also
changes how many channels fit, which is the channel density. This is the realistic case:
you do not thin the walls just because the channels get narrower.

Figures written to figures/:
  - design_levers.png  : resistance vs width and vs height at the design flow (width dominates)
  - width_tradeoff.png : resistance and pumping power vs width, one curve per flow rate
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from coldplate import ColdPlate, analyze
import spec

FIG_DIR = "figures"
BASE_WIDTH = 20e-3        # cold plate width [m]
LENGTH = 20e-3           # flow length [m]
WALL = 0.5e-3            # fixed machinable wall thickness between channels [m]
MACHINABLE_MIN_MM = 0.5  # smallest channel width a standard mill can cut [mm]
FLOWS = [0.5, 1.0, 1.5, 2.0, 3.0]    # L/min, the family of curves
REF_HEIGHT_MM = 5.0      # fixed height when sweeping width
REF_WIDTH_MM = 0.5       # fixed width when sweeping height


def make_plate(width_mm, height_mm):
    """Build a plate; channel count follows from filling the base at the fixed wall thickness."""
    w = width_mm * 1e-3
    h = height_mm * 1e-3
    n = max(1, int(BASE_WIDTH / (w + WALL)))
    return ColdPlate(channel_width_m=w, channel_height_m=h, wall_thickness_m=WALL,
                     n_channels=n, channel_length_m=LENGTH)


def run(width_mm, height_mm, flow_lpm):
    return analyze(make_plate(width_mm, height_mm), flow_lpm=flow_lpm, Q=spec.Q,
                   A_die=spec.A_DIE, T_in=spec.T_IN, T_j_max=spec.T_J_MAX, R_tim=spec.R_TIM)


# --- figures ---------------------------------------------------------------

def fig_design_levers():
    """Show that width is a strong lever and height is a weak one, at the design flow."""
    f = spec.DESIGN_FLOW_LPM
    widths = [0.3, 0.4, 0.5, 0.6, 0.8, 1.0]
    heights = [2, 3, 4, 5, 6, 8, 10]

    fig, (axw, axh) = plt.subplots(1, 2, figsize=(11, 4.5))

    Rw = [run(w, REF_HEIGHT_MM, f).R_total for w in widths]
    axw.plot(widths, Rw, "o-")
    axw.axhline(spec.R_TARGET, color="k", ls="--", label=f"target {spec.R_TARGET:.3f}")
    axw.axvline(MACHINABLE_MIN_MM, color="grey", ls=":", label="mill limit")
    axw.set_xlabel("channel width (mm)")
    axw.set_ylabel("R_total (C/W)")
    axw.set_title(f"Width sweep (height {REF_HEIGHT_MM:.0f} mm): strong")
    axw.grid(True, alpha=0.3)
    axw.legend(fontsize=8)

    Rh = [run(REF_WIDTH_MM, h, f).R_total for h in heights]
    axh.plot(heights, Rh, "s-", color="tab:orange")
    axh.axhline(spec.R_TARGET, color="k", ls="--", label=f"target {spec.R_TARGET:.3f}")
    axh.set_xlabel("channel height (mm)")
    axh.set_ylabel("R_total (C/W)")
    axh.set_title(f"Height sweep (width {REF_WIDTH_MM:.1f} mm): weak")
    axh.grid(True, alpha=0.3)
    axh.legend(fontsize=8)

    fig.suptitle(f"Design levers at {f:.1f} L/min")
    fig.tight_layout()
    _save(fig, "design_levers.png")


def fig_width_tradeoff():
    """The main design chart: resistance and pumping power vs width, one curve per flow."""
    widths = [0.3, 0.4, 0.5, 0.6, 0.8, 1.0]
    fig, (axR, axP) = plt.subplots(1, 2, figsize=(11, 4.5))
    for flow in FLOWS:
        R = [run(w, REF_HEIGHT_MM, flow).R_total for w in widths]
        P = [run(w, REF_HEIGHT_MM, flow).pumping_power * 1e3 for w in widths]
        axR.plot(widths, R, "o-", label=f"{flow} L/min")
        axP.plot(widths, P, "o-", label=f"{flow} L/min")
    axR.axhline(spec.R_TARGET, color="k", ls="--", label=f"target {spec.R_TARGET:.3f}")
    axR.axvline(MACHINABLE_MIN_MM, color="grey", ls=":", label="mill limit")
    axR.set_xlabel("channel width (mm)")
    axR.set_ylabel("R_total (C/W)")
    axR.set_title("Thermal: resistance")
    axR.grid(True, alpha=0.3)
    axR.legend(fontsize=8)
    axP.set_xlabel("channel width (mm)")
    axP.set_ylabel("pumping power (mW)")
    axP.set_title("Hydraulic: pumping power")
    axP.grid(True, alpha=0.3)
    axP.legend(fontsize=8)
    fig.suptitle(f"Width tradeoff (height {REF_HEIGHT_MM:.0f} mm)")
    fig.tight_layout()
    _save(fig, "width_tradeoff.png")


def _save(fig, name):
    path = os.path.join(FIG_DIR, name)
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"  wrote {path}")


# --- analysis printed to the console --------------------------------------

def print_lever_comparison():
    """Quantify how much width matters versus height, at the design flow."""
    f = spec.DESIGN_FLOW_LPM
    r_wide = run(1.0, REF_HEIGHT_MM, f).R_total
    r_narrow = run(0.5, REF_HEIGHT_MM, f).R_total
    r_short = run(REF_WIDTH_MM, 3, f).R_total
    r_tall = run(REF_WIDTH_MM, 6, f).R_total
    print(f"  Dominant lever at {f:.1f} L/min:")
    print(f"    width  1.0 -> 0.5 mm : R_total {r_wide:.3f} -> {r_narrow:.3f} C/W "
          f"(drop {r_wide - r_narrow:.3f})")
    print(f"    height 3   -> 6   mm : R_total {r_short:.3f} -> {r_tall:.3f} C/W "
          f"(drop {r_short - r_tall:.3f})")
    print(f"    -> width is the lever; height barely moves it.")


def print_best():
    """Lowest resistance machinable design at the design flow (width and wall >= mill limit)."""
    f = spec.DESIGN_FLOW_LPM
    best = None
    for w in [0.5, 0.6, 0.8, 1.0]:
        for h in [3, 5, 8, 10]:
            res = run(w, h, f)
            if best is None or res.R_total < best[2].R_total:
                best = (w, h, res)
    w, h, res = best
    print(f"\n  Best machinable design at {f:.1f} L/min "
          f"(channel {w} x {h} mm, wall {WALL*1e3:.1f} mm):")
    print(res.report(f"channel {w} x {h} mm", spec.R_TARGET))


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    print("=" * 70)
    print("  COLD PLATE DESIGN SWEEP")
    print("=" * 70)
    print(f"  spec: Q = {spec.Q:.0f} W, die = {spec.A_DIE*1e4:.0f} cm^2, "
          f"water {spec.T_IN:.0f} C in, target R <= {spec.R_TARGET:.3f} C/W")
    print(f"  sweeping channel width and height vs R_total and pumping power, "
          f"flow {min(FLOWS)} to {max(FLOWS)} L/min")
    print(f"  wall fixed at {WALL*1e3:.1f} mm, so width also sets the channel count")
    print("-" * 70)
    print_lever_comparison()
    print_best()
    print("-" * 70)
    print("  Generating figures:")
    fig_design_levers()
    fig_width_tradeoff()
    print("=" * 70)


if __name__ == "__main__":
    main()
