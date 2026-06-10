"""Command-line interface for Shannon charge-safety calculations."""

from __future__ import annotations

import argparse
import json
from .core import calculate_charge_safety


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shannon-charge-safety",
        description="Calculate charge per phase, charge density, and Shannon k value.",
    )
    parser.add_argument("--current-ma", type=float, required=True, help="Stimulation current in mA")
    parser.add_argument("--pulse-width-us", type=float, required=True, help="Pulse width in microseconds")

    parser.add_argument("--area-mm2", type=float, help="Electrode surface area in mm^2")
    parser.add_argument("--diameter-mm", type=float, help="Cylindrical electrode diameter in mm")
    parser.add_argument("--height-mm", type=float, help="Exposed cylindrical electrode height in mm; area = pi * diameter * height")

    parser.add_argument("--json", action="store_true", help="Print output as JSON")
    return parser


def format_text(result) -> str:
    return "\n".join(
        [
            "Charge safety calculation",
            "-------------------------",
            f"Current:               {result.current_mA:g} mA",
            f"Pulse width:           {result.pulse_width_us:g} us",
            f"Surface area:          {result.surface_area_mm2:g} mm^2 ({result.surface_area_cm2:g} cm^2)",
            f"Charge per phase:      {result.charge_per_phase_uC:.6g} uC/phase",
            f"Charge density:        {result.charge_density_uC_per_cm2:.6g} uC/cm^2/phase",
            f"Shannon k:             {result.shannon_k:.6g}",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    kwargs = {
        "current_mA": args.current_ma,
        "pulse_width_us": args.pulse_width_us,
    }
    has_area = args.area_mm2 is not None
    has_dimensions = args.diameter_mm is not None or args.height_mm is not None
    if has_area and has_dimensions:
        parser.error("Provide either --area-mm2 OR both --diameter-mm and --height-mm, not both")
    if not has_area and not has_dimensions:
        parser.error("Provide --area-mm2 OR both --diameter-mm and --height-mm")
    if has_dimensions and (args.diameter_mm is None or args.height_mm is None):
        parser.error("Both --diameter-mm and --height-mm are required when using cylindrical dimensions")

    if has_area:
        kwargs["area_mm2"] = args.area_mm2
    else:
        kwargs["diameter_mm"] = args.diameter_mm
        kwargs["height_mm"] = args.height_mm

    result = calculate_charge_safety(**kwargs)

    if args.json:
        print(json.dumps(result.__dict__, indent=2))
    else:
        print(format_text(result))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
