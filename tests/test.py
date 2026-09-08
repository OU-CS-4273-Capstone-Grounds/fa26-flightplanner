import pytest
from performance import calculate_density_altitude  # not implemented yet

def test_calculate_density_altitude_basic():
    result = calculate_density_altitude(pressure_altitude=2500, oat_celsius=25)
    assert result == pytest.approx(4300, abs=1)