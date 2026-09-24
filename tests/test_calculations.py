import unittest
import math
import random

from src.calculations import (
    EARTH_RADIUS_NM, fahrenheit_to_celsius, celsius_to_fahrenheit,
    knots_to_mph, mph_to_knots, knots_to_kmh, kmh_to_knots,
    knots_to_mps, mps_to_knots, mph_to_kmh, kmh_to_mph,
    mph_to_mps, mps_to_mph, kmh_to_mps, mps_to_kmh, distance_nm, 
    route_distance_nm, bearing_deg, route_bearings_deg,
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
    def test_mps_to_kmh(self):
        self.assertRelClose(mph_to_kmh(100), 160.9344)
    
     # 1 mph = 1609.344 m per 3600 s = 0.44704 m/s exactly
    def test_mps_to_mph(self):
        self.assertRelClose(mph_to_mps(100), 44.704)
        
    # 1 km/h = 1000 m per 3600 s, so 36 km/h = 10 m/s exactly
    def test_kmh_to_mph(self):
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
        self.assertAlmostEqual(distance_nm((0, 0), (90, 0)), HALF_CIRCUMFERENCE_NM / 2, places=6)
    
     # North-->South Pole is 180 degrees of arc: half the circumference
    def test_pole_to_pole_is_half_circumference(self):
        self.assertAlmostEqual(distance_nm((90, 0), (-90, 0)), HALF_CIRCUMFERENCE_NM, places=6)
 
    # Opposite sides of the equator are also half the circumference apart
    def test_antipodal_points_on_equator(self):
        self.assertAlmostEqual(distance_nm((0, 0), (0, 180)), HALF_CIRCUMFERENCE_NM, places=6)
    
    # Boundary: near antipodal points should not crash
    def test_near_antipodal_points_do_not_crash(self):
        self.assertAlmostEqual(distance_nm((-82, -179), (82, 1)), HALF_CIRCUMFERENCE_NM, places=4)
    
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
                self.assertLessEqual(d, HALF_CIRCUMFERENCE_NM + 1e-6)
    # Triangle inequality: a detour through a third point B can never be shorter than 
    # flying A -> C directly. Takes the random points in groups of three (a, b, c).
    def test_triangle_inequality(self):
        points = random_points(45)
        for a, b, c in zip(points[0::3], points[1::3], points[2::3]):
            with self.subTest(a=a, b=b, c=c):
                self.assertLessEqual(distance_nm(a, c), distance_nm(a, b) + distance_nm(b, c) + 1e-6)

##---------Total Distance (Multi-Leg) Route ---------------------------------------
class TestRouteDirection(unittest.TestCase):
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
            

if __name__ == "__main__":
    unittest.main()
