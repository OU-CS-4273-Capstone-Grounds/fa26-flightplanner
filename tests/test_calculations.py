import unittest

from src.calculations import (
    fahrenheit_to_celsius, celsius_to_fahrenheit,
    knots_to_mph, mph_to_knots, knots_to_kmh, kmh_to_knots,
    knots_to_mps, mps_to_knots, mph_to_kmh, kmh_to_mph,
    mph_to_mps, mps_to_mph, kmh_to_mps, mps_to_kmh,
    distance_nm, route_distance_nm, bearing_deg, route_bearings_deg,
    calculate_pressure_altitude,calculate_density_altitude, calculate_rate_of_climb,
    calculate_takeoff_distance, calculate_landing_distance, calculate_true_air_speed,
)
## coordinates for testing distance and bearing calculations
JFK = (40.6413, -73.7781)
LAX = (33.9416, -118.4085)
ORD = (41.9742, -87.9073)

class TestTemperatureConversion(unittest.TestCase):
    def test_fahrenheit_to_celsius(self):
        self.assertAlmostEqual(fahrenheit_to_celsius(32), 0)
        self.assertAlmostEqual(fahrenheit_to_celsius(212), 100)

    def test_celsius_to_fahrenheit(self):
        self.assertAlmostEqual(celsius_to_fahrenheit(0), 32)
        self.assertAlmostEqual(celsius_to_fahrenheit(100), 212)


class TestSpeedConversion(unittest.TestCase):
    def test_knots_to_mph(self):
        self.assertAlmostEqual(knots_to_mph(100), 115.078)

    def test_mph_to_knots(self):
        self.assertAlmostEqual(mph_to_knots(115.078), 100)

    def test_knots_to_kmh(self):
        self.assertAlmostEqual(knots_to_kmh(100), 185.2)

    def test_kmh_to_knots(self):
        self.assertAlmostEqual(kmh_to_knots(185.2), 100)

    def test_knots_to_mps(self):
        self.assertAlmostEqual(knots_to_mps(100), 51.4444)

    def test_mps_to_knots(self):
        self.assertAlmostEqual(mps_to_knots(51.4444), 100)

    def test_mph_to_kmh(self):
        self.assertAlmostEqual(mph_to_kmh(100), 160.934)

    def test_kmh_to_mph(self):
        self.assertAlmostEqual(kmh_to_mph(160.934), 100)

    def test_mph_to_mps(self):
        self.assertAlmostEqual(mph_to_mps(100), 44.704)

    def test_mps_to_mph(self):
        self.assertAlmostEqual(mps_to_mph(44.704), 100)

    def test_kmh_to_mps(self):
        self.assertAlmostEqual(kmh_to_mps(100), 27.7778)

    def test_mps_to_kmh(self):
        self.assertAlmostEqual(mps_to_kmh(27.7778), 100)


class TestDistanceCalculation(unittest.TestCase):
    def test_distance_nm_known_route(self):
        # JFK -> LAX great-circle distance is ~2145 nm
        self.assertAlmostEqual(distance_nm(JFK, LAX), 2145, delta=20)

    def test_distance_nm_same_point_is_zero(self):
        self.assertAlmostEqual(distance_nm(JFK, JFK), 0)

    def test_route_distance_nm_sums_legs(self):
        total = route_distance_nm([JFK, ORD, LAX])
        expected = distance_nm(JFK, ORD) + distance_nm(ORD, LAX)
        self.assertAlmostEqual(total, expected)


class TestDirectionCalculation(unittest.TestCase):
    def test_bearing_deg_due_east(self):
        self.assertAlmostEqual(bearing_deg((0, 0), (0, 10)), 90, delta=0.5)

    def test_bearing_deg_due_north(self):
        self.assertAlmostEqual(bearing_deg((0, 0), (10, 0)), 0, delta=0.5)

    def test_bearing_deg_in_range(self):
        bearing = bearing_deg(JFK, LAX)
        self.assertTrue(0 <= bearing < 360)

    def test_route_bearings_deg_matches_bearing_deg(self):
        bearings = route_bearings_deg([JFK, ORD, LAX])
        self.assertEqual(bearings, [bearing_deg(JFK, ORD), bearing_deg(ORD, LAX)])

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
    def test_calculate_pressure_altitude_altimeter_setting_out_of_range(self):
        altimeter_setting = 27.50
        field_elevation = 1000
        with self.assertRaises(ValueError):
            calculate_pressure_altitude(altimeter_setting, field_elevation)
 
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
        density_altitude = 12652.80
        expected_rate_of_climb = 153.89
        self.assertAlmostEqual(
            calculate_rate_of_climb(density_altitude),
            expected_rate_of_climb,
            places=2,
        )
 
    def test_calculate_takeoff_distance_ground_run(self):
        density_altitude = 0
        expected = 785.71, 1666.67
        self.assertAlmostEqual(
            calculate_takeoff_distance(density_altitude)[0],
            expected[0],
            places=2,
        )
        self.assertAlmostEqual(
            calculate_takeoff_distance(density_altitude)[1],
            expected[1],
            places=2,
        )
 
    def test_calculate_landing_distance(self):
        density_altitude = 0
        expected = 535.71, 1075.0
        self.assertAlmostEqual(
            calculate_landing_distance(density_altitude)[0],
            expected[0],
            places=2,
        )
        self.assertAlmostEqual(
            calculate_landing_distance(density_altitude)[1],
            expected[1],
            places=2,
        )
 
    def test_calculate_true_air_speed(self):
        density_altitude = 0
        power_setting = 75
        expected = 123.88
        self.assertAlmostEqual(
            calculate_true_air_speed(density_altitude, power_setting),
            expected,
            places=2,
        )
    def test_calculate_true_air_speed_power_setting_out_of_range(self):
        density_altitude = 0
        power_setting = 45
        with self.assertRaises(Exception):
            calculate_true_air_speed(density_altitude, power_setting)

if __name__ == "__main__":
    unittest.main()
