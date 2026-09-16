import unittest
 
from src.calculations import (
    calculate_pressure_altitude,
    calculate_density_altitude,
    calculate_rate_of_climb,
    calculate_takeoff_distance,
    calculate_landing_distance,
    calculate_true_air_speed,
)

class TestCalculations(unittest.TestCase):
 
    def test_calculate_pressure_altitude(self):
        altimeter_setting = 30.20
        field_elevation = 1000
        expected_pressure_altitude = 720
        self.assertAlmostEqual(
            calculate_pressure_altitude(altimeter_setting, field_elevation),
            expected_pressure_altitude,
            places=2,
        )
 
    def test_calculate_density_altitude(self):
        temperature = 20
        field_elevation = 10000
        altimeter_setting = 30.20
        expected_density_altitude = 12652.80
        self.assertAlmostEqual(
            calculate_density_altitude(temperature, field_elevation, altimeter_setting),
            expected_density_altitude,
            places=2,
        )
 
    def test_calculate_rate_of_climb(self):
        temperature = 20
        field_elevation = 10000
        altimeter_setting = 30.20
        expected_rate_of_climb = 153.89
        self.assertAlmostEqual(
            calculate_rate_of_climb(temperature, field_elevation, altimeter_setting),
            expected_rate_of_climb,
            places=2,
        )
 
    def test_calculate_takeoff_distance_ground_run(self):
        temperature = 15
        field_elevation = 0
        altimeter_setting = 29.92
        expected = 785.71
        self.assertAlmostEqual(
            calculate_takeoff_distance(temperature, field_elevation, altimeter_setting, True, False),
            expected,
            places=2,
        )
 
    def test_calculate_takeoff_distance_over_50_feet_obstacle(self):
        temperature = 15
        field_elevation = 0
        altimeter_setting = 29.92
        expected = 1666.67
        self.assertAlmostEqual(
            calculate_takeoff_distance(temperature, field_elevation, altimeter_setting, False, True),
            expected,
            places=2,
        )
 
    def test_calculate_takeoff_distance_both_enabled(self):
        temperature = 15
        field_elevation = 0
        altimeter_setting = 29.92
        self.assertEqual(
            calculate_takeoff_distance(temperature, field_elevation, altimeter_setting, True, True),
            "Cannot have both enabled",
        )
 
    def test_calculate_takeoff_distance_neither_enabled(self):
        temperature = 15
        field_elevation = 0
        altimeter_setting = 29.92
        self.assertEqual(
            calculate_takeoff_distance(temperature, field_elevation, altimeter_setting, False, False),
            "No option selected",
        )
 
    def test_calculate_landing_distance_ground_roll(self):
        temperature = 15
        field_elevation = 0
        altimeter_setting = 29.92
        expected = 535.71
        self.assertAlmostEqual(
            calculate_landing_distance(temperature, field_elevation, altimeter_setting, True, False),
            expected,
            places=2,
        )
 
    def test_calculate_landing_distance_over_50_feet_obstacle(self):
        temperature = 15
        field_elevation = 0
        altimeter_setting = 29.92
        expected = 1075.0
        self.assertAlmostEqual(
            calculate_landing_distance(temperature, field_elevation, altimeter_setting, False, True),
            expected,
            places=2,
        )
 
    def test_calculate_landing_distance_both_enabled(self):
        temperature = 15
        field_elevation = 0
        altimeter_setting = 29.92
        self.assertEqual(
            calculate_landing_distance(temperature, field_elevation, altimeter_setting, True, True),
            "Cannot have both enabled",
        )
 
    def test_calculate_landing_distance_neither_enabled(self):
        temperature = 15
        field_elevation = 0
        altimeter_setting = 29.92
        self.assertEqual(
            calculate_landing_distance(temperature, field_elevation, altimeter_setting, False, False),
            "No option selected",
        )
 
    def test_calculate_true_air_speed(self):
        temperature = 15
        field_elevation = 0
        altimeter_setting = 29.92
        power_setting = 75
        expected = 123.88
        self.assertAlmostEqual(
            calculate_true_air_speed(temperature, field_elevation, altimeter_setting, power_setting),
            expected,
            places=2,
        )
 
if __name__ == "__main__":
    unittest.main()
