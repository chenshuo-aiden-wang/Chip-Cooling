"""Live hand-calc: compare candidate cold plates against the spec.

This is the runnable version of HANDCALC.md. Run from the model/ directory:

    python run_handcalc.py

Edit the `DESIGNS` dict to try your own geometries.
"""
from coldplate import ColdPlate, analyze
import spec

# Candidate cold-plate designs (channel sizes in metres).
DESIGNS = {
    "A - moderate":   ColdPlate(channel_width_m=0.5e-3, channel_height_m=3.0e-3,
                                wall_thickness_m=0.5e-3, n_channels=20,
                                channel_length_m=20e-3),
    "B - aggressive": ColdPlate(channel_width_m=0.4e-3, channel_height_m=5.0e-3,
                                wall_thickness_m=0.4e-3, n_channels=25,
                                channel_length_m=20e-3),
}


def main() -> None:
    print("=" * 64)
    print("  GPU COLD-PLATE HAND-CALC  (see SPEC.md / HANDCALC.md)")
    print("=" * 64)
    print(f"  Q = {spec.Q:.0f} W | die = {spec.A_DIE*1e4:.0f} cm^2 "
          f"| water {spec.T_IN:.0f} C in | T_j,max = {spec.T_J_MAX:.0f} C")
    print(f"  flux = {spec.Q / (spec.A_DIE*1e4):.0f} W/cm^2 "
          f"| flow = {spec.DESIGN_FLOW_LPM:.1f} L/min")
    print(f"  TARGET: R_total <= {spec.R_TARGET:.3f} C/W "
          f"(R_TIM={spec.R_TIM}, R_spread={spec.R_SPREADING} assumed)")
    print("-" * 64)

    for name, plate in DESIGNS.items():
        res = analyze(
            plate, flow_lpm=spec.DESIGN_FLOW_LPM, Q=spec.Q,
            T_in=spec.T_IN, T_j_max=spec.T_J_MAX,
            R_tim=spec.R_TIM, R_spread=spec.R_SPREADING,
        )
        print(res.report(name, spec.R_TARGET))

    print("-" * 64)
    print("  Verdict: see which design meets R_target. A naive design misses;")
    print("  aggressive microchannels are needed. Refine in Icepak/Fluent.")
    print("=" * 64)


if __name__ == "__main__":
    main()
