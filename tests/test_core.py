import math
import pytest

from shannon_charge_safety import (
    calculate_charge_safety,
    charge_per_phase_uC,
    surface_area_cm2_from_mm2,
    surface_area_mm2_from_diameter_length,
)


def test_charge_per_phase():
    assert charge_per_phase_uC(3, 60) == pytest.approx(0.18)


def test_area_from_dimensions():
    area = math.pi * 0.8 * 1.5
    assert surface_area_mm2_from_diameter_length(0.8, 1.5) == pytest.approx(area)
    assert surface_area_cm2_from_mm2(area) == pytest.approx(area / 100)


def test_calculation_with_area_mm2():
    result = calculate_charge_safety(current_mA=3, pulse_width_us=60, area_mm2=1.2)
    assert result.charge_per_phase_uC == pytest.approx(0.18)
    assert result.charge_density_uC_per_cm2 == pytest.approx(15.0)
    assert result.shannon_k == pytest.approx(math.log10(0.18) + math.log10(15.0))


def test_calculation_with_dimensions():
    result = calculate_charge_safety(current_mA=6, pulse_width_us=60, diameter_mm=0.8, length_mm=1.5)
    expected_area = math.pi * 0.8 * 1.5
    expected_density = 0.36 / (expected_area / 100)
    assert result.surface_area_mm2 == pytest.approx(expected_area)
    assert result.charge_per_phase_uC == pytest.approx(0.36)
    assert result.charge_density_uC_per_cm2 == pytest.approx(expected_density)


def test_area_modes_are_mutually_exclusive():
    with pytest.raises(ValueError):
        calculate_charge_safety(current_mA=3, pulse_width_us=60, area_mm2=1.2, diameter_mm=0.8, length_mm=1.5)


def test_positive_values_required():
    with pytest.raises(ValueError):
        calculate_charge_safety(current_mA=0, pulse_width_us=60, area_mm2=1.2)
