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
        expected_density_altitude = 3720
        self.assertAlmostEqual(
            calculate_density_altitude(temperature, field_elevation, altimeter_setting),
            expected_density_altitude,
            places=2,
        )
 
    def test_calculate_rate_of_climb(self):
        temperature = 20
        field_elevation = 10000
        altimeter_setting = 30.20
        expected_rate_of_climb = 260
        self.assertAlmostEqual(
            calculate_rate_of_climb(temperature, field_elevation, altimeter_setting),
            expected_rate_of_climb,
            places=2,
        )
 
    def test_calculate_takeoff_distance_ground_run(self):
        expected = 11000 / 14  # 785.71
        self.assertAlmostEqual(
            calculate_takeoff_distance(15, 0, 29.92, True, False),
            expected,
            places=2,
        )
 
    def test_calculate_takeoff_distance_over_50_feet_obstacle(self):
        expected = 10000 / 6  # 1666.67
        self.assertAlmostEqual(
            calculate_takeoff_distance(15, 0, 29.92, False, True),
            expected,
            places=2,
        )
 
    def test_calculate_takeoff_distance_both_enabled(self):
        self.assertEqual(
            calculate_takeoff_distance(15, 0, 29.92, True, True),
            "Cannot have both enabled",
        )
 
    def test_calculate_takeoff_distance_neither_enabled(self):
        self.assertEqual(
            calculate_takeoff_distance(15, 0, 29.92, False, False),
            "No option selected",
        )
 
    def test_calculate_landing_distance_ground_roll(self):
        expected = 37500 / 70  # 535.71
        self.assertAlmostEqual(
            calculate_landing_distance(15, 0, 29.92, True, False),
            expected,
            places=2,
        )
 
    def test_calculate_landing_distance_over_50_feet_obstacle(self):
        expected = 43000 / 40  # 1075.0
        self.assertAlmostEqual(
            calculate_landing_distance(15, 0, 29.92, False, True),
            expected,
            places=2,
        )
 
    def test_calculate_landing_distance_both_enabled(self):
        self.assertEqual(
            calculate_landing_distance(15, 0, 29.92, True, True),
            "Cannot have both enabled",
        )
 
    def test_calculate_landing_distance_neither_enabled(self):
        self.assertEqual(
            calculate_landing_distance(15, 0, 29.92, False, False),
            "No option selected",
        )
 
    def test_calculate_true_air_speed(self):
        expected = 45.653 + 0.0008722 * 0 + 1.0430 * 75  # 123.878
        self.assertAlmostEqual(
            calculate_true_air_speed(15, 0, 29.92, 75),
            expected,
            places=2,
        )
 
if __name__ == "__main__":
    unittest.main()
