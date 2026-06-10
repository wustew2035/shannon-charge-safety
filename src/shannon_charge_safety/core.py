"""Core calculations for electrical stimulation charge safety.

Units:
- Current: mA
- Pulse width: microseconds (us)
- Charge per phase: microcoulombs/phase (uC/phase)
- Electrode area: mm^2 or cm^2
- Charge density: microcoulombs/cm^2/phase (uC/cm^2/phase)

Shannon k is computed as:
    k = log10(Q) + log10(D)
where Q is charge per phase in uC/phase and D is charge density in
uC/cm^2/phase.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ChargeSafetyResult:
    """Container for charge-safety calculation outputs."""

    current_mA: float
    pulse_width_us: float
    surface_area_mm2: float
    surface_area_cm2: float
    charge_per_phase_uC: float
    charge_density_uC_per_cm2: float
    shannon_k: float


def _require_positive(name: str, value: float) -> float:
    try:
        value = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if value <= 0:
        raise ValueError(f"{name} must be > 0")
    return value


def surface_area_mm2_from_diameter_height(diameter_mm: float, height_mm: float) -> float:
    """Return lateral cylindrical electrode surface area in mm^2.

    The exposed lateral surface area of a cylinder is:
        area = pi * diameter * height
    """
    diameter_mm = _require_positive("diameter_mm", diameter_mm)
    height_mm = _require_positive("height_mm", height_mm)
    return math.pi * diameter_mm * height_mm


def surface_area_mm2_from_width_height(width_mm: float, height_mm: float) -> float:
    """Deprecated alias for cylindrical area using diameter and height.

    Use surface_area_mm2_from_diameter_height(diameter_mm, height_mm).
    The first argument is interpreted as diameter_mm and the second as height_mm.
    """
    return surface_area_mm2_from_diameter_height(width_mm, height_mm)


def surface_area_cm2_from_mm2(area_mm2: float) -> float:
    """Convert surface area from mm^2 to cm^2.

    1 cm^2 = 100 mm^2, so mm^2 / 100 = cm^2.
    """
    area_mm2 = _require_positive("area_mm2", area_mm2)
    return area_mm2 / 100.0


def charge_per_phase_uC(current_mA: float, pulse_width_us: float) -> float:
    """Calculate charge per phase in uC/phase.

    Because 1 mA * 1 us = 0.001 uC, Q_uC = I_mA * PW_us / 1000.
    """
    current_mA = _require_positive("current_mA", current_mA)
    pulse_width_us = _require_positive("pulse_width_us", pulse_width_us)
    return current_mA * pulse_width_us / 1000.0


def charge_density_uC_per_cm2(charge_uC: float, area_cm2: float) -> float:
    """Calculate charge density in uC/cm^2/phase."""
    charge_uC = _require_positive("charge_uC", charge_uC)
    area_cm2 = _require_positive("area_cm2", area_cm2)
    return charge_uC / area_cm2


def shannon_k(charge_uC: float, charge_density: float) -> float:
    """Calculate Shannon k = log10(Q) + log10(D)."""
    charge_uC = _require_positive("charge_uC", charge_uC)
    charge_density = _require_positive("charge_density", charge_density)
    return math.log10(charge_uC) + math.log10(charge_density)


def calculate_charge_safety(
    *,
    current_mA: float,
    pulse_width_us: float,
    area_mm2: float | None = None,
    diameter_mm: float | None = None,
    height_mm: float | None = None,
) -> ChargeSafetyResult:
    """Calculate charge per phase, charge density, and Shannon k.

    Provide electrode surface area using exactly one of:
    1. area_mm2=<surface area in mm^2>
    2. diameter_mm=<cylinder diameter in mm> and height_mm=<exposed cylinder height in mm>
    """
    has_area = area_mm2 is not None
    has_dimensions = diameter_mm is not None or height_mm is not None

    if has_area and has_dimensions:
        raise ValueError("Provide either area_mm2 OR diameter_mm and height_mm, not both")
    if not has_area and not has_dimensions:
        raise ValueError("Provide area_mm2 OR diameter_mm and height_mm")
    if has_dimensions and (diameter_mm is None or height_mm is None):
        raise ValueError("Both diameter_mm and height_mm are required when using cylindrical dimensions")

    if area_mm2 is None:
        area_mm2 = surface_area_mm2_from_diameter_height(diameter_mm, height_mm)  # type: ignore[arg-type]
    else:
        area_mm2 = _require_positive("area_mm2", area_mm2)

    area_cm2 = surface_area_cm2_from_mm2(area_mm2)
    q_uC = charge_per_phase_uC(current_mA, pulse_width_us)
    density = charge_density_uC_per_cm2(q_uC, area_cm2)
    k = shannon_k(q_uC, density)

    return ChargeSafetyResult(
        current_mA=float(current_mA),
        pulse_width_us=float(pulse_width_us),
        surface_area_mm2=area_mm2,
        surface_area_cm2=area_cm2,
        charge_per_phase_uC=q_uC,
        charge_density_uC_per_cm2=density,
        shannon_k=k,
    )
