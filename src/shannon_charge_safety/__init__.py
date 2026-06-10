"""Utilities for neurostimulation charge-density and Shannon k calculations."""

from .core import (
    ChargeSafetyResult,
    calculate_charge_safety,
    charge_density_uC_per_cm2,
    charge_per_phase_uC,
    medtronic_segment_area_fraction,
    shannon_k,
    surface_area_cm2_from_mm2,
    surface_area_mm2_from_diameter_height,
    surface_area_mm2_from_width_height,
)

__all__ = [
    "ChargeSafetyResult",
    "calculate_charge_safety",
    "charge_density_uC_per_cm2",
    "charge_per_phase_uC",
    "medtronic_segment_area_fraction",
    "shannon_k",
    "surface_area_cm2_from_mm2",
    "surface_area_mm2_from_diameter_height",
    "surface_area_mm2_from_width_height",
]
