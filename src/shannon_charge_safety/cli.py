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

    area = parser.add_mutually_exclusive_group(required=True)
    area.add_argument("--area-mm2", type=float, help="Electrode surface area in mm^2")
    area.add_argument(
        "--dimensions-mm",
        nargs=2,
        type=float,
        metavar=("WIDTH", "HEIGHT"),
        help="Electrode surface width and height in mm; area = width * height",
    )

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
    if args.area_mm2 is not None:
        kwargs["area_mm2"] = args.area_mm2
    else:
        kwargs["width_mm"], kwargs["height_mm"] = args.dimensions_mm

    result = calculate_charge_safety(**kwargs)

    if args.json:
        print(json.dumps(result.__dict__, indent=2))
    else:
        print(format_text(result))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
