import unittest
import math
import random
from datetime import date

from src.calculations import (
    EARTH_RADIUS_NM, fahrenheit_to_celsius, celsius_to_fahrenheit,
    knots_to_mph, mph_to_knots, knots_to_kmh, kmh_to_knots,
    knots_to_mps, mps_to_knots, mph_to_kmh, kmh_to_mph,
    mph_to_mps, mps_to_mph, kmh_to_mps, mps_to_kmh, distance_nm, 
    route_distance_nm, bearing_deg, route_bearings_deg, wind_angle_rad, 
    wind_correction_angle, true_heading, ground_speed,
    calculate_pressure_altitude,calculate_density_altitude, calculate_rate_of_climb,
    calculate_takeoff_distance, calculate_landing_distance, calculate_true_air_speed,
    MAX_DEVIATION_DEG, magnetic_variation, magnetic_course, magnetic_heading, compass_deviation, compass_heading,
    time_of_flight_hours, time_of_flight_minutes, route_time_of_flight_hours,
)
## coordinates for testing distance and bearing calculations (lat,lon)
JFK = (40.6413, -73.7781)
LAX = (33.9416, -118.4085)
ORD = (41.9742, -87.9073)

# Distance subtended by one degree of arc - spherical Earth model, instead of raw assumption
# Derived from geometry, rather than from calling the function under test
NM_PER_DEGREE = EARTH_RADIUS_NM * math.pi / 180 # ~60.04 nautical miles per degree
HALF_CIRCUM_NM = EARTH_RADIUS_NM * math.pi # longest possible great-cricle distance: d = R(pi)

## Added relative tolerance for unit concersions for the test to pass, instead of using delta 
# (rounding error due to absolute delta behaving inconsistently)
# conversion constants rounded to ~6 sig figs so they differ from the actual values by a small amount
# using 1e-5 accepts the rounding but catches any wrong constants. 
CONVERSION_RELATIVE_TOL = 1e-5

## Additional helpers when testing handpicked points to checking properties that must old everywhere

## Generates n (lat,lon) points globally, including southern/western hemispheres & near the poles, which
# the handpicked airports didn't cover (test failure). Used by tests that check rules which 
# must hold everywhere: symmetry, triangle inequalit, bearing range, max distance
def random_points(n, seed=4273):
    rand_num_gen = random.Random(seed) # seed value is arbitrary but consistent for reproducible results --> important for CI behavior
    return [(rand_num_gen.uniform(-90, 90), rand_num_gen.uniform(-180, 180)) for _ in range(n)]

## Base class for temp and speed test classes: checks relative tolerance rather than fixed delta, letting
# results that are effectively 0 pass, since a relative tolerance around 0 would otherwise require an exact 0.
# Failure message added to show the actual vs.expected value instead of default (personal choice in debugging)
class ConversionAssertions(unittest.TestCase):
    def assertRelClose(self, actual, expected, rel_tol=CONVERSION_RELATIVE_TOL, msg=None):
        self.assertTrue(math.isclose(actual, expected, rel_tol=rel_tol, abs_tol=1e-12),
            msg or f"{actual} is not within rel_tol={rel_tol} of {expected}",)

#--------------- Temperature ---------------------------------

class TestTemperatureConversion(ConversionAssertions):
    REFERENCE_POINTS = [
        (32, 0),            # water freezes
        (212, 100),         # water boils at sea level
        (-40, -40),         # the only point where both scales agree
        (59, 15),           # ISA standard sea-level temperature (used for density altitude)
        (98.6, 37),         # fractional input
        (-459.67, -273.15), # absolute zero
        (-4, -20),          # typical winter/high-altitude temperature below both zeros
    ]
    # F-->C at every reference point
    def test_fahrenheit_to_celsius_ref_pts(self):
        for f, c in self.REFERENCE_POINTS:
            with self.subTest(fahrenheit=f):
                self.assertAlmostEqual(fahrenheit_to_celsius(f), c, places=9)
    
    ## Checks C-->F at same reference points
    def test_celsius_to_fahrenheit_ref_pts(self):
         for f, c in self.REFERENCE_POINTS:
            with self.subTest(celsius=c):
                self.assertAlmostEqual(celsius_to_fahrenheit(c), f, places=9)
    
    ## Coverting between scales
    def test_round_trip_returns_original_value(self):
        for value in [-273.15, -56.5, -40, -0.5, 0, 0.1, 15, 37.77, 1000]:
            with self.subTest(value=value):
                self.assertAlmostEqual(celsius_to_fahrenheit(fahrenheit_to_celsius(value)), value, places=9)
                self.assertAlmostEqual(fahrenheit_to_celsius(celsius_to_fahrenheit(value)), value, places=9)
 
    def test_temperature_difference_scales_by_nine_fifths(self):
        # A 5 C change is always a 9 F change, regardless of starting point.
        # Catches a formula that gets the offset right but the slope wrong.
        for start_c in [-50, 0, 15, 40]:
            with self.subTest(start_c=start_c):
                delta_f = celsius_to_fahrenheit(start_c + 5) - celsius_to_fahrenheit(start_c)
                self.assertAlmostEqual(delta_f, 9, places=9)
                
    # warmer in one scale must be warmer in the other, catches a sign error in the conversion
    def test_conversion_is_increasing(self):
        # Warmer in one scale must be warmer in the other
        temps = [-100, -40, -1, 0, 1, 40, 100]
        converted = [fahrenheit_to_celsius(t) for t in temps]
        self.assertEqual(converted, sorted(converted))
    

class TestSpeedConversion(ConversionAssertions):
    # Every (forward, inverse) conversion pair, the tests will apply to all conversion loops
    PAIRS = [
        (knots_to_mph, mph_to_knots), (knots_to_kmh, kmh_to_knots),
        (knots_to_mps, mps_to_knots), (mph_to_kmh, kmh_to_mph),
        (mph_to_mps, mps_to_mph), (kmh_to_mps, mps_to_kmh),
    ]
    # Tests check each forward conversion against the exact unit definition, so
    # it is not being checked against itself.
    
    # 1 knot = 1852 m/h and 1 mile = 1609.344 m --> 1 kt = 1852/1609.344 mph
    def test_knots_to_mph(self):
        self.assertRelClose(knots_to_mph(100), 100 * 1852 / 1609.344)
    
    # 1 knot = 1.852 km/h exact
    def test_knots_to_kmh(self):
        self.assertRelClose(knots_to_kmh(100), 185.2)
            
    # 1 knot = 1852 m per 3600 s exact
    def test_knots_to_mps(self):
        self.assertRelClose(knots_to_mps(100), 100 * 1852 / 3600)
    
    # 1 mph = 1.609344 km/h exact
    def test_mph_to_kmh(self):
        self.assertRelClose(mph_to_kmh(100), 160.9344)
    
     # 1 mph = 1609.344 m per 3600 s = 0.44704 m/s exactly
    def test_mph_to_mps(self):
        self.assertRelClose(mph_to_mps(100), 44.704)
        
    # 1 km/h = 1000 m per 3600 s, so 36 km/h = 10 m/s exactly
    def test_kmh_to_mps(self):
        self.assertRelClose(kmh_to_mps(36), 10)
        
    # Check each inverse conversion against definition
    def test_inverse_conversions_match_definition(self):
        self.assertRelClose(mph_to_knots(100), 100 * 1609.344 / 1852)
        self.assertRelClose(kmh_to_knots(100), 100 / 1.852)
        self.assertRelClose(mps_to_knots(10), 10 * 3600 / 1852)
        self.assertRelClose(kmh_to_mph(100), 100 / 1.609344)
        self.assertRelClose(mps_to_mph(10), 10 / 0.44704)
        self.assertRelClose(mps_to_kmh(10), 36)
        
    # Boundary case: 0 speed must be exactly 0 in every unit
    def test_zero_speed_stays_zero(self):
        for forward, inverse in self.PAIRS:
            with self.subTest(conversion=forward.__name__):
                self.assertEqual(forward(0), 0)
                self.assertEqual(inverse(0), 0)
    # Conversion to and from must return original vaue, for all speed ranges (little-large)
    # with tighter tolerance 
    def test_round_trip_returns_original_value(self):
        for forward, inverse in self.PAIRS:
            for value in [0.001, 1, 65, 120.5, 250, 10_000]:
                with self.subTest(conversion=forward.__name__, value=value):
                    self.assertRelClose(inverse(forward(value)), value, rel_tol=1e-12)
                    
    # Wind (headwind/tailwind) can be negative, converting -x must give exactly the negative of converting x
    def test_neg_speeds_convert_linear(self):
        for forward, inverse in self.PAIRS:
            with self.subTest(conversion=forward.__name__):
                self.assertAlmostEqual(forward(-42.5), -forward(42.5), places=12)
                self.assertAlmostEqual(inverse(-42.5), -inverse(42.5), places=12)
                
    # Knots --> mph --> km/h must agree with going knots --> km/h or m/s directly
    def test_conversion_paths_agree(self):
        kt = 137
        self.assertRelClose(mph_to_kmh(knots_to_mph(kt)), knots_to_kmh(kt))
        self.assertRelClose(kmh_to_mps(knots_to_kmh(kt)), knots_to_mps(kt))
        self.assertRelClose(mph_to_mps(knots_to_mph(kt)), knots_to_mps(kt))
    
    # Same positive speed: the numbers must rank km/h > mph > knots > m/s (catches */ mix-up)
    def test_unit_magnitude_ordering(self):
        kt = 100
        self.assertGreater(knots_to_kmh(kt), knots_to_mph(kt))
        self.assertGreater(knots_to_mph(kt), kt)
        self.assertGreater(kt, knots_to_mps(kt))
        
#--------------------- Great-Circle distance between two points ----------------------
class TestDistanceCalculation(unittest.TestCase):
    
    # Moving 1 degree north along a meridian covers exactly 1 degree of arc
    def test_one_degree_latitude(self):
        self.assertAlmostEqual(distance_nm((0, 0), (1, 0)), NM_PER_DEGREE, places=6)
        
     # At the equator, 1 degree of longitude is also exactly 1 degree of arc
    def test_one_degree_longitude_at_equator(self):
        self.assertAlmostEqual(distance_nm((0, 0), (0, 1)), NM_PER_DEGREE, places=6)
        
    # Meridian converge toward the poles (1 deg long at 60N is ~0.5*length at equator)
    def test_one_degree_longitude_shrinks_toward_poles(self):
        self.assertAlmostEqual(distance_nm((60, 0), (60, 1)), NM_PER_DEGREE / 2, delta=0.05)
    
    # Equator-->North Pole is 90 degrees of arc: a quarter of the circum.
    def test_equator_to_pole_is_quarter_circumference(self):
        self.assertAlmostEqual(distance_nm((0, 0), (90, 0)), HALF_CIRCUM_NM / 2, places=6)
    
     # North-->South Pole is 180 degrees of arc: half the circumference
    def test_pole_to_pole_is_half_circumference(self):
        self.assertAlmostEqual(distance_nm((90, 0), (-90, 0)), HALF_CIRCUM_NM, places=6)
 
    # Opposite sides of the equator are also half the circumference apart
    def test_antipodal_points_on_equator(self):
        self.assertAlmostEqual(distance_nm((0, 0), (0, 180)), HALF_CIRCUM_NM, places=6)
    
    # Boundary: near antipodal points should not crash
    def test_near_antipodal_points_do_not_crash(self):
        self.assertAlmostEqual(distance_nm((-82, -179), (82, 1)), HALF_CIRCUM_NM, places=4)
    
    #--------- comparing to known values JFK-LAX-ORD, real-world application -------------------------
    
    def test_real_world_routes(self):
        for a, b, expected in [(JFK, LAX, 2151), (JFK, ORD, 643)]:
            with self.subTest(route=(a, b)):
                self.assertTrue(math.isclose(distance_nm(a, b), expected, rel_tol=0.005))

    ## Boundary: point has zero distance from self
    def test_same_point_is_zero(self):
        for point in [JFK, (0, 0), (90, 0), (-90, 0), (0, 180)]:
            with self.subTest(point=point):
                self.assertAlmostEqual(distance_nm(point, point), 0)
    
    # Longitude +180 and -180 are the same meridian, so these are one place
    def test_longitude_180_and_minus_180_are_same_place(self):
        self.assertAlmostEqual(distance_nm((0, 180), (0, -180)), 0, places=6)
        
    # Every long meets at a pole
    def test_all_longitudes_meet_at_the_pole(self):
        self.assertAlmostEqual(distance_nm((90, 0), (90, 123)), 0, places=6)
        self.assertAlmostEqual(distance_nm((-90, -45), (-90, 170)), 0, places=6)
    
    # +179 to -179 longitude is a short 2-degree hop across the date line,
    # not a 358-degree trip the long way around the world.
    def test_distance_across_international_date_line(self):
        self.assertAlmostEqual(distance_nm((0, 179), (0, -179)), 2 * NM_PER_DEGREE, places=6)
    
    # --- Properties distance functions must satisfy (run on random_points() to check many locations)----------
    
    # Distance A -> B must equal distance B -> A
    def test_distance_is_symmetric(self):
        points = random_points(40)
        for a, b in zip(points, points[1:]):
            with self.subTest(a=a, b=b):
                self.assertAlmostEqual(distance_nm(a, b), distance_nm(b, a), places=6)    
    
    # Distance never negative, and nothing is farther apart than 1/2 circumference
    def test_distance_is_non_negative_and_bounded(self):
        points = random_points(40)
        for a, b in zip(points, points[1:]):
            with self.subTest(a=a, b=b):
                d = distance_nm(a, b)
                self.assertGreaterEqual(d, 0)
                self.assertLessEqual(d, HALF_CIRCUM_NM + 1e-6)
    # Triangle inequality: a detour through a third point B can never be shorter than 
    # flying A -> C directly. Takes the random points in groups of three (a, b, c).
    def test_triangle_inequality(self):
        points = random_points(45)
        for a, b, c in zip(points[0::3], points[1::3], points[2::3]):
            with self.subTest(a=a, b=b, c=c):
                self.assertLessEqual(distance_nm(a, c), distance_nm(a, b) + distance_nm(b, c) + 1e-6)

##---------Total Distance (Multi-Leg) Route ---------------------------------------
class TestRouteDistance(unittest.TestCase):
    # Total route distance must = sum of the individual legs
    def test_route_is_sum_of_legs(self):
        route = [JFK, ORD, LAX]
        expected = distance_nm(JFK, ORD) + distance_nm(ORD, LAX)
        self.assertAlmostEqual(route_distance_nm(route), expected, places=9)
        
    # (0,0) -> (0,1) -> (1,1): each leg is exactly one degree of arc, so total is exactly two degrees of arc.
    def test_known_two_leg_route(self):
        self.assertAlmostEqual(route_distance_nm([(0, 0), (0, 1), (1, 1)]), 2 * NM_PER_DEGREE, places=6)
    
    # Flying there + back covers the distance twice.
    def test_out_and_back_is_double_not_zero(self):
        self.assertAlmostEqual(route_distance_nm([JFK, ORD, JFK]), 2 * distance_nm(JFK, ORD), places=9)
    
    # A waypoint that lies exactly on the direct path must not change the total. 
    # Splits a meridian leg at its midpoint to test this.
    def test_waypoint_on_the_great_circle_adds_nothing(self):
        direct = route_distance_nm([(10, 20), (30, 20)])
        split = route_distance_nm([(10, 20), (20, 20), (30, 20)])
        self.assertAlmostEqual(split, direct, places=6)
        
    # A waypoint off the direct path must make the route longer
    def test_waypoint_off_the_route_adds_distance(self):
        self.assertGreater(route_distance_nm([JFK, ORD, LAX]), distance_nm(JFK, LAX))
 
    # Flying the same route backwards covers the same total distance
    def test_reversed_route_has_same_distance(self):
        route = [JFK, ORD, LAX]
        self.assertAlmostEqual(route_distance_nm(route), route_distance_nm(route[::-1]), places=6)
    
    # Boundary: an empty route has no legs, zero distance
    def test_empty_route(self):
        self.assertEqual(route_distance_nm([]), 0)
 
    # Boundary: a single point has no legs, zero distance
    def test_single_point_route(self):
        self.assertEqual(route_distance_nm([(35, -97)]), 0)
 
    # A repeated waypoint creates a zero-length leg, total equals just one real leg: (0,0) -> (0,1), exactly 1 degree of arc
    def test_duplicate_consecutive_waypoints_add_zero(self):
        self.assertAlmostEqual(route_distance_nm([(0, 0), (0, 0), (0, 1)]), NM_PER_DEGREE, places=6)
    
##----------- True Bearing Between 2 Points ---------------------------------------
class TestBearingCalculations(unittest.TestCase):
    # From (0, 0), heading to each cardinal direction: N = 0, E = 90, S = 180, W = 270
    def test_cardinal_directions(self):
        cases = [((10, 0), 0), ((0, 10), 90), ((-10, 0), 180), ((0, -10), 270)]
        for destination, expected in cases:
            with self.subTest(destination=destination):
                self.assertAlmostEqual(bearing_deg((0, 0), destination), expected, places=6)
 
    # Small diagonal hops near the equator are almost exactly 45/135/225/315.
    # Catches swapped atan2 arguments: cardinal tests alone misses since some cardinal directions come out right when swapped
    def test_intercardinal_directions_near_equator(self):
        cases = [((1, 1), 45), ((-1, 1), 135), ((-1, -1), 225), ((1, -1), 315)]
        for destination, expected in cases:
            with self.subTest(destination=destination):
                self.assertAlmostEqual(bearing_deg((0, 0), destination), expected, delta=0.01)
 
    # From 45N,0E --> 45N,90E, a constant heading flat-map angle, heads due east (90), but shortest great-circle path starts off at
    # atan(sqrt(2)) ~ 54.74 degrees. Proves we compute a true great-circle bearing and not a flat-map angle.
    def test_great_circle_bearing_differs_from_rhumb_line(self):
        expected = math.degrees(math.atan(math.sqrt(2)))
        self.assertAlmostEqual(bearing_deg((45, 0), (45, 90)), expected, places=6)
 
    # LAX is SW of JFK, but the great-circle path bulges north, so the initial bearing is slightly N of due west (~274).
    def test_real_world_westbound_route_starts_north_of_west(self):
        bearing = bearing_deg(JFK, LAX)
        self.assertGreater(bearing, 270)
        self.assertLess(bearing, 280)
 
    # Along a meridian the return bearing is exactly opposite: north (0) out, south (180) back.
    def test_reverse_bearing_on_meridian_is_opposite(self):
        forward = bearing_deg((0, 0), (10, 0))
        reverse = bearing_deg((10, 0), (0, 0))
        self.assertAlmostEqual((reverse - forward) % 360, 180, places=6)
 
    # On a general great circle, the return bearing is NOT simply forward + 180
    # (JFK -> LAX starts ~274, LAX -> JFK starts ~66).
    def test_reverse_bearing_off_meridian_is_not_simply_opposite(self):
        forward = bearing_deg(JFK, LAX)
        reverse = bearing_deg(LAX, JFK)
        self.assertGreater(abs(((reverse - forward) % 360) - 180), 5)
 
    # From anywhere on Earth, the North Pole is due north (0)
    def test_bearing_toward_north_pole_is_always_north(self):
        for origin in [(0, 0), JFK, (-45, 170), (89, -60)]:
            with self.subTest(origin=origin):
                self.assertAlmostEqual(bearing_deg(origin, (90, 0)), 0, places=6)
 
    # From anywhere on Earth, the South Pole is due south (180)
    def test_bearing_toward_south_pole_is_always_south(self):
        for origin in [(0, 0), JFK, (45, -170)]:
            with self.subTest(origin=origin):
                self.assertAlmostEqual(bearing_deg(origin, (-90, 0)), 180, places=6)
 
    # Crossing the date line: +179 -> -179 is a short hop east (90), and -179 -> +179 is a short hop west (270)
    def test_bearing_across_international_date_line(self):
        self.assertAlmostEqual(bearing_deg((0, 179), (0, -179)), 90, places=6)
        self.assertAlmostEqual(bearing_deg((0, -179), (0, 179)), 270, places=6)
 
    # A heading just barely W of N makes atan2 return a tiny negative angle
    # Must turn it into a value just under 360, never 360 itself and never a negative num
    def test_bearing_just_west_of_north_does_not_wrap_to_360_or_negative(self):
        bearing = bearing_deg((0, 0), (10, -1e-6))
        self.assertGreater(bearing, 359.99)
        self.assertLess(bearing, 360)
 
    # Every bearing b/t random points across the globe must fall in range [0, 360): 0 included, 360 excluded.
    def test_bearing_always_in_range(self):
        points = random_points(60)
        for a, b in zip(points, points[1:]):
            with self.subTest(a=a, b=b):
                bearing = bearing_deg(a, b)
                self.assertGreaterEqual(bearing, 0)
                self.assertLess(bearing, 360)

                
##------------ Bearing For Each leg of a Multi-Leg Route ---------------------------------------    
class TestRouteBearings(unittest.TestCase):
    # Leg 1: (0,0) -> (0,10) heads east (90)
    # Leg 2: (0,10) -> (10,10) heads north (0)
    def test_known_route(self):
        bearings = route_bearings_deg([(0, 0), (0, 10), (10, 10)])
        self.assertEqual(len(bearings), 2)
        self.assertAlmostEqual(bearings[0], 90, places=6)
        self.assertAlmostEqual(bearings[1], 0, places=6)
    
    # A route of n points has n - 1 legs, so n - 1 bearings, and each bearing
    # must match its own leg in order. Catches off-by-one indexing errors.
    def test_one_bearing_per_leg_in_order(self):
        route = [JFK, ORD, LAX, JFK]
        bearings = route_bearings_deg(route)
        self.assertEqual(len(bearings), len(route) - 1)
        for i, bearing in enumerate(bearings):
            with self.subTest(leg=i):
                self.assertAlmostEqual(bearing, bearing_deg(route[i], route[i + 1]), places=9)
                  
    # Boundary: an empty route has no legs, so no bearings
    def test_empty_route(self):
        self.assertEqual(route_bearings_deg([]), [])
 
    # Boundary: a single point has no legs, so no bearings
    def test_single_point_route(self):
        self.assertEqual(route_bearings_deg([(35, -97)]), [])

##------------ Wind Triangle Functions ---------------------------------------
# Argument order for every function: (true_course, true_airspeed, wind_direction, wind_speed)
# Expected values are derived by hand (right-triangle trig or vector addition)

WIND_FUNCS = [wind_correction_angle, true_heading, ground_speed]

# wind_angle_rad: angle between the wind and the course (validation lives in the public functions)
class TestWindTriangle(unittest.TestCase):
    
    # Wind 90 degrees to the right of the course is +pi/2 radians
    def test_wind_from_right_is_positive_quarter_turn(self):
        self.assertAlmostEqual(wind_angle_rad(0, 90), math.pi / 2, places=12)
 
    # Wind 90 degrees to the left of the course is -pi/2 radians (sign carries the side)
    def test_wind_from_left_is_negative_quarter_turn(self):
        self.assertAlmostEqual(wind_angle_rad(90, 0), -math.pi / 2, places=12)
 
    # Wind straight down the nose is 0, wind straight from behind is pi
    def test_headwind_is_zero_and_tailwind_is_pi(self):
        self.assertAlmostEqual(wind_angle_rad(270, 270), 0, places=12)
        self.assertAlmostEqual(abs(wind_angle_rad(90, 270)), math.pi, places=12)
 
    # Boundary: zero wind is valid (calm), validation must use < 0, not <= 0
    def test_returns_radians_wind_minus_course(self):
        self.assertAlmostEqual(wind_angle_rad(10, 40), math.radians(30), places=12)

## Wind Correction Angle
class TestWindCorrectionAngle(unittest.TestCase):
 
    # Calm wind needs no correction, whatever the stated direction
    def test_calm_wind_has_no_correction(self):
        for course in [0, 90, 213, 359]:
            with self.subTest(course=course):
                self.assertAlmostEqual(wind_correction_angle(course, 110, 270, 0), 0, places=9)

# Wind straight down the nose or straight from behind has no crosswind, so no correction
    def test_pure_headwind_and_tailwind_have_no_correction(self):
        self.assertAlmostEqual(wind_correction_angle(90, 100, 90, 20), 0, places=9)
        self.assertAlmostEqual(wind_correction_angle(90, 100, 270, 20), 0, places=9)
 
    # 90 degree crosswind: whole wind is crosswind, WCA = asin(W / TAS)
    def test_direct_crosswind_from_right_is_positive(self):
        expected = math.degrees(math.asin(20 / 100))  # ~11.54
        self.assertAlmostEqual(wind_correction_angle(0, 100, 90, 20), expected, places=9)
 
    def test_direct_crosswind_from_left_is_negative(self):
        expected = math.degrees(math.asin(20 / 100))
        self.assertAlmostEqual(wind_correction_angle(0, 100, 270, 20), -expected, places=9)
 
    # Quartering headwind: course 090, TAS 120, wind 030 @ 20
    # crosswind = 20 sin(-60) ~ -17.32, WCA = asin(-17.32 / 120) ~ -8.2989
    def test_quartering_headwind_example(self):
        self.assertAlmostEqual(wind_correction_angle(90, 120, 30, 20), -8.2989, places=3)
 
    # Quartering tailwind: wind 210 @ 20, same course and TAS
    # crosswind = 20 sin(120) ~ +17.32, WCA ~ +8.2989 (headwind/tailwind doesn't change WCA)
    def test_quartering_tailwind_example(self):
        self.assertAlmostEqual(wind_correction_angle(90, 120, 210, 20), 8.2989, places=3)
 
    # Mirroring the wind across the course flips the WCA sign and keeps its size
    def test_mirrored_wind_flips_sign(self):
        course = 120
        for offset in [10, 45, 90, 135, 170]:
            with self.subTest(offset=offset):
                self.assertAlmostEqual(wind_correction_angle(course, 100, course + offset, 25),
                                       -wind_correction_angle(course, 100, course - offset, 25), places=9)
 
    # Directions 0 and 360 are the same, as are courses outside 0-360
    def test_equivalent_directions_give_same_wca(self):
        self.assertAlmostEqual(wind_correction_angle(360, 100, 45, 15),
                               wind_correction_angle(0, 100, 45, 15), places=9)
        self.assertAlmostEqual(wind_correction_angle(-90, 100, 45, 15),
                               wind_correction_angle(270, 100, 45, 15), places=9)
 
    # Boundary: crosswind exactly equal to TAS is a 90 degree crab, still solvable
    def test_crosswind_equal_to_airspeed_is_90_degree_crab(self):
        self.assertAlmostEqual(wind_correction_angle(0, 50, 90, 50), 90, places=9)
        
# Crab: flying with nose pointed partly into a crosswind so that plane is traveling "striaght" along its course

## True Heading
class TestTrueHeading(unittest.TestCase):
 
    # Calm wind: heading equals course
    def test_calm_wind_heading_equals_course(self):
        for course in [0, 90, 213, 359]:
            with self.subTest(course=course):
                self.assertAlmostEqual(true_heading(course, 110, 270, 0), course, places=9)
 
    # Wind from the right turns the nose right of the course
    def test_crosswind_from_right(self):
        expected = math.degrees(math.asin(20 / 100))
        self.assertAlmostEqual(true_heading(0, 100, 90, 20), expected, places=9)
 
    # Wind from the left on course 000: heading wraps to just below 360, not a negative number
    def test_crosswind_from_left_wraps_below_360(self):
        expected = 360 - math.degrees(math.asin(20 / 100))
        self.assertAlmostEqual(true_heading(0, 100, 270, 20), expected, places=9)
 
    # Course near 360 with wind from the right: heading wraps past north to a small value
    def test_heading_wraps_past_360(self):
        # Wind 090 is 95 degrees right of course 355: crosswind = 20 sin(95), WCA ~ +11.49
        heading = true_heading(355, 100, 90, 20)  # 355 + ~11.49 = ~006.49
        expected_wca = math.degrees(math.asin(20 * math.sin(math.radians(95)) / 100))
        self.assertAlmostEqual(heading, (355 + expected_wca) % 360, places=9)
 
    # Quartering headwind example: 090 + (-8.2989) = 081.7011
    def test_quartering_headwind_example(self):
        self.assertAlmostEqual(true_heading(90, 120, 30, 20), 81.7011, places=3)
 
    # Courses written outside 0-360 still give a heading in [0, 360)
    def test_course_outside_0_360_is_normalized(self):
        for unwrapped, wrapped in [(450, 90), (-90, 270), (720, 0)]:
            with self.subTest(course=unwrapped):
                heading = true_heading(unwrapped, 100, 45, 15)
                self.assertAlmostEqual(heading, true_heading(wrapped, 100, 45, 15), places=9)
                self.assertGreaterEqual(heading, 0)
                self.assertLess(heading, 360)
 
## Ground Speed
class TestGroundSpeed(unittest.TestCase):
 
    # Calm wind: ground speed equals true airspeed
    def test_calm_wind_ground_speed_equals_tas(self):
        self.assertAlmostEqual(ground_speed(213, 110, 270, 0), 110, places=9)
 
    # Direct headwind subtracts, direct tailwind adds
    def test_direct_headwind(self):
        self.assertAlmostEqual(ground_speed(90, 100, 90, 20), 80, places=9)
 
    def test_direct_tailwind(self):
        self.assertAlmostEqual(ground_speed(90, 100, 270, 20), 120, places=9)
 
    # A tailwind stronger than the airspeed is still a valid flight
    def test_tailwind_stronger_than_airspeed(self):
        self.assertAlmostEqual(ground_speed(0, 50, 180, 80), 130, places=9)
 
    # 90 degree crosswind: right triangle, GS = sqrt(TAS^2 - W^2)
    def test_direct_crosswind_right_triangle(self):
        self.assertAlmostEqual(ground_speed(0, 100, 90, 20), math.sqrt(100**2 - 20**2), places=9)
 
    # Quartering headwind: 120 cos(8.2989) - 20 cos(60) = 118.7434 - 10 = 108.7434
    def test_quartering_headwind_example(self):
        self.assertAlmostEqual(ground_speed(90, 120, 30, 20), 108.7434, places=3)
 
    # Quartering tailwind: 118.7434 + 10 = 128.7434
    def test_quartering_tailwind_example(self):
        self.assertAlmostEqual(ground_speed(90, 120, 210, 20), 128.7434, places=3)
 
    # Mirroring wind across the course leaves ground speed unchanged
    def test_mirrored_wind_same_ground_speed(self):
        course = 120
        for offset in [10, 45, 90, 135, 170]:
            with self.subTest(offset=offset):
                self.assertAlmostEqual(ground_speed(course, 100, course + offset, 25),
                                       ground_speed(course, 100, course - offset, 25), places=9)
 
    # Directions 0 and 360 are the same
    def test_360_and_0_are_same_direction(self):
        self.assertAlmostEqual(ground_speed(90, 100, 360, 15), ground_speed(90, 100, 0, 15), places=9)
 
 
## Independent check: heading + ground speed against plain vector addition
class TestWindTriangleVectors(unittest.TestCase):
    # Flying the computed heading at TAS, plus the wind vector, must produce a ground track
    # exactly along the course at the computed ground speed. Uses north/east components only.
    def test_heading_and_wind_vectors_sum_to_course_and_ground_speed(self):
        rand_num_gen = random.Random(4273)
        for _ in range(50):
            course = rand_num_gen.uniform(0, 360)
            tas = rand_num_gen.uniform(60, 200)
            wind_dir = rand_num_gen.uniform(0, 360)
            wind_speed = rand_num_gen.uniform(0, 0.9 * tas)
            with self.subTest(course=course, tas=tas, wind_dir=wind_dir, wind_speed=wind_speed):
                heading = math.radians(true_heading(course, tas, wind_dir, wind_speed))
                gs = ground_speed(course, tas, wind_dir, wind_speed)
 
                # Wind blows FROM wind_dir, so it pushes the aircraft toward wind_dir + 180
                wind_to = math.radians(wind_dir + 180)
                north = tas * math.cos(heading) + wind_speed * math.cos(wind_to)
                east = tas * math.sin(heading) + wind_speed * math.sin(wind_to)
 
                track = math.degrees(math.atan2(east, north)) % 360
                track_error = (track - course + 180) % 360 - 180
                self.assertAlmostEqual(track_error, 0, places=6)
                self.assertAlmostEqual(math.hypot(north, east), gs, places=6)
 
 
## Invalid input: every function validates through wind_angle_rad
class TestWindTriangleInvalidInput(unittest.TestCase):
    # Zero or negative airspeed is meaningless
    def test_non_positive_airspeed_raises(self):
        for func in WIND_FUNCS:
            for tas in [0, -50]:
                with self.subTest(func=func.__name__, tas=tas):
                    with self.assertRaisesRegex(ValueError, "airspeed must be greater than 0"):
                        func(90, tas, 0, 10)
 
    # Negative wind speed is invalid (direction already encodes where it comes from)
    def test_negative_wind_speed_raises(self):
        for func in WIND_FUNCS:
            with self.subTest(func=func.__name__):
                with self.assertRaisesRegex(ValueError, "Wind speed cannot be negative"):
                    func(90, 100, 0, -10)
 
    # Crosswind faster than the airspeed: no heading can hold the course
    def test_crosswind_exceeding_airspeed_raises(self):
        for func in [wind_correction_angle, true_heading, ground_speed]:
            with self.subTest(func=func.__name__):
                with self.assertRaisesRegex(ValueError, "Crosswind"):
                    func(0, 50, 90, 60)
                    
    def test_crosswind_error_message_includes_values(self):
        with self.assertRaisesRegex(ValueError, r"\(60\.0 kt\).*\(50\.0 kt\)"):
            wind_correction_angle(0, 50, 90, 60)
 
    # Headwind at or above airspeed: no forward progress
    def test_headwind_at_or_above_airspeed_raises(self):
        for wind_speed in [100, 120]:
            with self.subTest(wind_speed=wind_speed):
                with self.assertRaisesRegex(ValueError, "Headwind"):
                    ground_speed(0, 100, 0, wind_speed)
 
    # Boundary: at a 90 degree crab the heading is solvable, but the aircraft points
    # sideways and makes no progress along the course, so ground speed raises
    def test_90_degree_crab_heading_ok_but_ground_speed_raises(self):
        self.assertAlmostEqual(true_heading(0, 50, 90, 50), 90, places=9)
        with self.assertRaises(ValueError):
            ground_speed(0, 50, 90, 50)
 
    # Headwind just below airspeed = still valid (boundary on the other side)
    def test_headwind_just_below_airspeed_is_valid(self):
        self.assertAlmostEqual(ground_speed(0, 100, 0, 99), 1, places=9)

## Magnetic Variation (World Magnetic Model)
# Fixed date so expected values don't drift as the magnetic field changes
WMM_TEST_DATE = date(2026, 1, 1)
NORMAN = (35.2456, -97.4721)

class TestMagneticVariation(unittest.TestCase):

    # Known declinations (NOAA WMM2025): East coast is West variation, West coast is East
    def test_known_airports_within_half_degree(self):
        for name, point, expected in [("JFK", JFK, -12.6), ("LAX", LAX, 11.4),
                                      ("ORD", ORD, -4.0), ("Norman", NORMAN, 3.0)]:
            with self.subTest(airport=name):
                self.assertAlmostEqual(magnetic_variation(point, WMM_TEST_DATE), expected, delta=0.5)

    # Defaults to today's date when none is given
    def test_defaults_to_today(self):
        self.assertAlmostEqual(magnetic_variation(NORMAN),
                               magnetic_variation(NORMAN, date.today()), places=9)

    # Cruise altitude barely changes variation
    def test_altitude_has_small_effect(self):
        self.assertAlmostEqual(magnetic_variation(JFK, WMM_TEST_DATE, 10000),
                               magnetic_variation(JFK, WMM_TEST_DATE), delta=0.1)

    # Plugs straight into magnetic_course: Norman ~3E turns 090 true into ~087 magnetic
    def test_feeds_magnetic_course(self):
        variation = magnetic_variation(NORMAN, WMM_TEST_DATE)
        self.assertAlmostEqual(magnetic_course(90, variation), 90 - variation, places=9)

    # Dates outside the model's 5-year lifespan raise
    def test_date_outside_model_lifespan_raises(self):
        with self.assertRaises(ValueError):
            magnetic_variation(NORMAN, date(2031, 1, 1))


## Magnetic Course and Heading
class TestMagneticCourseAndHeading(unittest.TestCase):

    # Zero variation: magnetic equals true
    def test_zero_variation_magnetic_equals_true(self):
        self.assertAlmostEqual(magnetic_course(213, 0), 213, places=9)
        self.assertAlmostEqual(magnetic_heading(90, 120, 30, 20, 0),
                               true_heading(90, 120, 30, 20), places=9)

    # East is least: 10E turns 090 true into 080 magnetic
    def test_east_variation_subtracts(self):
        self.assertAlmostEqual(magnetic_course(90, 10), 80, places=9)

    # West is best: 10W turns 090 true into 100 magnetic
    def test_west_variation_adds(self):
        self.assertAlmostEqual(magnetic_course(90, -10), 100, places=9)

    # Results wrap into [0, 360) in both directions
    def test_variation_wraps_past_north(self):
        self.assertAlmostEqual(magnetic_course(5, 10), 355, places=9)
        self.assertAlmostEqual(magnetic_course(355, -10), 5, places=9)

    # Magnetic heading is the wind corrected true heading minus variation
    def test_magnetic_heading_applies_wca_then_variation(self):
        # Quartering headwind example: TH 081.7011, 5E variation -> MH 076.7011
        self.assertAlmostEqual(magnetic_heading(90, 120, 30, 20, 5), 76.7011, places=3)

    # Calm wind: magnetic heading equals magnetic course
    def test_calm_wind_heading_equals_magnetic_course(self):
        for course in [0, 90, 213, 359]:
            with self.subTest(course=course):
                self.assertAlmostEqual(magnetic_heading(course, 110, 270, 0, -7),
                                       magnetic_course(course, -7), places=9)

    # Variation boundary: 180 is allowed, values past it are not
    def test_variation_out_of_range_raises(self):
        self.assertAlmostEqual(magnetic_course(0, 180), 180, places=9)
        for variation in [-180, 181, -200]:
            with self.subTest(variation=variation):
                with self.assertRaisesRegex(ValueError, "Magnetic variation"):
                    magnetic_course(0, variation)
                with self.assertRaisesRegex(ValueError, "Magnetic variation"):
                    magnetic_heading(0, 100, 0, 0, variation)

    # Wind validation still runs through magnetic_heading
    def test_invalid_wind_inputs_still_raise(self):
        with self.assertRaisesRegex(ValueError, "airspeed must be greater than 0"):
            magnetic_heading(90, 0, 0, 10, 5)


## Compass Deviation
# Sample card every 30 degrees: {"for" magnetic heading: correction}
SAMPLE_CARD = {0: -1, 30: 1, 60: 2, 90: 2, 120: 0, 150: -2,
               180: -2, 210: -1, 240: 0, 270: 1, 300: 1, 330: 0}

class TestCompassDeviation(unittest.TestCase):

    # On a card heading: exact entry is returned
    def test_card_heading_returns_entry(self):
        for heading, correction in SAMPLE_CARD.items():
            with self.subTest(heading=heading):
                self.assertAlmostEqual(compass_deviation(heading, SAMPLE_CARD), correction, places=9)

    # Halfway between two entries: average of their corrections
    def test_interpolates_between_entries(self):
        self.assertAlmostEqual(compass_deviation(15, SAMPLE_CARD), 0, places=9)
        self.assertAlmostEqual(compass_deviation(135, SAMPLE_CARD), -1, places=9)
        self.assertAlmostEqual(compass_deviation(40, SAMPLE_CARD), 1 + 1 / 3, places=9)

    # Between the last entry (330) and north (000): interpolation wraps through 360
    def test_interpolates_across_north(self):
        self.assertAlmostEqual(compass_deviation(345, SAMPLE_CARD), -0.5, places=9)
        self.assertAlmostEqual(compass_deviation(360, SAMPLE_CARD), -1, places=9)

    # Card that doesn't start at 000: headings before the first entry wrap from the last
    def test_card_not_starting_at_north(self):
        card = {90: 2, 270: -2}
        self.assertAlmostEqual(compass_deviation(0, card), 0, places=9)
        self.assertAlmostEqual(compass_deviation(180, card), 0, places=9)
        self.assertAlmostEqual(compass_deviation(45, card), 1, places=9)

    # Single entry card: same correction on every heading
    def test_single_entry_card(self):
        for heading in [0, 90, 359]:
            with self.subTest(heading=heading):
                self.assertAlmostEqual(compass_deviation(heading, {0: 2}), 2, places=9)

    # Invalid cards raise
    def test_empty_card_raises(self):
        with self.assertRaisesRegex(ValueError, "Deviation card cannot be empty"):
            compass_deviation(90, {})

    def test_card_heading_out_of_range_raises(self):
        for heading in [-30, 360]:
            with self.subTest(heading=heading):
                with self.assertRaisesRegex(ValueError, "Deviation card heading"):
                    compass_deviation(90, {0: 0, heading: 1})

    def test_correction_too_large_raises(self):
        compass_deviation(90, {0: MAX_DEVIATION_DEG})  # boundary is allowed
        with self.assertRaisesRegex(ValueError, "check the compass card"):
            compass_deviation(90, {0: 0, 90: MAX_DEVIATION_DEG + 1})


## Compass Heading
class TestCompassHeading(unittest.TestCase):

    # No variation and an all-zero card: compass heading equals true heading
    def test_zero_corrections_equal_true_heading(self):
        card = {heading: 0 for heading in range(0, 360, 30)}
        self.assertAlmostEqual(compass_heading(90, 120, 30, 20, 0, card),
                               true_heading(90, 120, 30, 20), places=9)

    # Full chain, calm wind: TC 100 -> MH 090 (10E) -> CH 092 (card +2 at 090)
    def test_full_chain_calm_wind(self):
        self.assertAlmostEqual(compass_heading(100, 110, 0, 0, 10, SAMPLE_CARD), 92, places=9)

    # Deviation is looked up at the magnetic heading, not the true heading
    def test_deviation_uses_magnetic_heading(self):
        # TH 120, 30W -> MH 150 (card -2) -> CH 148; using TH 120 (card 0) would give 150
        self.assertAlmostEqual(compass_heading(120, 110, 0, 0, -30, SAMPLE_CARD), 148, places=9)

    # Compass heading wraps past north
    def test_compass_heading_wraps(self):
        # TC 005, 5E -> MH 000, card -1 -> CH 359
        self.assertAlmostEqual(compass_heading(5, 110, 0, 0, 5, SAMPLE_CARD), 359, places=9)
#--------------- Time of Flight ------------------------------

class TestTimeOfFlight(unittest.TestCase):
    def test_basic_example(self):
        # 120 nm at 120 kt should be exactly 1 hour
        self.assertAlmostEqual(time_of_flight_hours(120, 120), 1.0, places=9)

    def test_minutes_example(self):
        # 90 nm at 120 kt = 0.75 hr = 45 min
        self.assertAlmostEqual(time_of_flight_minutes(90, 120), 45, places=9)

    def test_minutes_is_sixty_times_hours(self):
        for distance, speed in [(50, 100), (250, 110), (1, 90)]:
            with self.subTest(distance=distance, speed=speed):
                self.assertAlmostEqual(time_of_flight_minutes(distance, speed),
                                       time_of_flight_hours(distance, speed) * 60, places=9)

    def test_zero_distance(self):
        self.assertEqual(time_of_flight_hours(0, 100), 0)

    def test_scaling(self):
        # 100 nm at 100 kt is 1 hr, so twice the distance should be 2 hr
        # and twice the speed should be 0.5 hr
        self.assertAlmostEqual(time_of_flight_hours(200, 100), 2.0, places=9)
        self.assertAlmostEqual(time_of_flight_hours(100, 200), 0.5, places=9)

    def test_invalid_ground_speed_raises(self):
        with self.assertRaises(ValueError):
            time_of_flight_hours(100, 0)
        with self.assertRaises(ValueError):
            time_of_flight_hours(100, -50)

    def test_negative_distance_raises(self):
        with self.assertRaises(ValueError):
            time_of_flight_hours(-10, 100)


class TestRouteTimeOfFlight(unittest.TestCase):
    def test_known_route(self):
        # 60 nm at 120 kt (0.5 hr) + 100 nm at 100 kt (1 hr) = 1.5 hr
        self.assertAlmostEqual(route_time_of_flight_hours([60, 100], [120, 100]), 1.5, places=9)

    def test_total_is_sum_of_legs(self):
        distances = [45, 80, 120]
        speeds = [110, 95, 130]
        expected = 0
        for i in range(len(distances)):
            expected += time_of_flight_hours(distances[i], speeds[i])
        self.assertAlmostEqual(route_time_of_flight_hours(distances, speeds), expected, places=9)

    def test_single_leg(self):
        self.assertAlmostEqual(route_time_of_flight_hours([150], [100]),
                               time_of_flight_hours(150, 100), places=9)

    def test_empty_route(self):
        self.assertEqual(route_time_of_flight_hours([], []), 0)

    def test_mismatched_lengths_raise(self):
        with self.assertRaises(ValueError):
            route_time_of_flight_hours([60, 100], [120])

    def test_with_route_distance(self):
        # use the existing distance functions for JFK -> ORD -> LAX at 120 kt the whole way
        route = [JFK, ORD, LAX]
        leg_distances = [distance_nm(route[0], route[1]), distance_nm(route[1], route[2])]
        expected = route_distance_nm(route) / 120
        self.assertAlmostEqual(route_time_of_flight_hours(leg_distances, [120, 120]), expected, places=9)


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
        expected = 107.65
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
