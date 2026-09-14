import math

# Temperature Conversion Functions 

# Fahrenheit --> Celsius Conversion
def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5/9

# Celsius --> Fahrenheit Conversion
def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32
#-----------------------------------------------

# Speed Conversion Functions

KNOTS_TO_MPH = 1.15078
KNOTS_TO_KMH = 1.852
KNOTS_TO_MPS = 0.514444
MPH_TO_KMH = 1.60934
MPH_TO_MPS = 0.44704
KMH_TO_MPS = 0.277778

# Knots --> Miles per Hour Conversion
def knots_to_mph(knots):
    return knots * KNOTS_TO_MPH

# Miles per Hour --> Knots Conversion
def mph_to_knots(mph):
    return mph / KNOTS_TO_MPH

# Knots --> Kilometers per Hour Conversion
def knots_to_kmh(knots):
    return knots * KNOTS_TO_KMH

# Kilometers per Hour --> Knots Conversion
def kmh_to_knots(kmh):
    return kmh / KNOTS_TO_KMH

# Knots --> Meters per Second Conversion
def knots_to_mps(knots):
    return knots * KNOTS_TO_MPS

# Meters per Second --> Knots Conversion
def mps_to_knots(mps):
    return mps / KNOTS_TO_MPS

# Miles per Hour --> Kilometers per Hour Conversion
def mph_to_kmh(mph):
    return mph * MPH_TO_KMH

# Kilometers per Hour --> Miles per Hour Conversion
def kmh_to_mph(kmh):
    return kmh / MPH_TO_KMH

# Miles per Hour --> Meters per Second Conversion
def mph_to_mps(mph):
    return mph * MPH_TO_MPS

# Meters per Second --> Miles per Hour Conversion
def mps_to_mph(mps):
    return mps / MPH_TO_MPS

# Kilometers per Hour --> Meters per Second Conversion
def kmh_to_mps(kmh):
    return kmh * KMH_TO_MPS

# Meters per Second --> Kilometers per Hour Conversion
def mps_to_kmh(mps):
    return mps / KMH_TO_MPS
#-----------------------------------------------

# Distance Calculation Functions

EARTH_RADIUS_NM = 3440.065  # Earth's mean radius in nautical miles

# Great-circle distance between two lat/lon points, in nautical miles
def distance_nm(point1, point2):
    lat1, lon1 = point1
    lat2, lon2 = point2

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (math.sin(delta_lat / 2) ** 2
         + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_NM * c

# Total route distance across an ordered list of (lat, lon) points
# e.g. [origin, waypoint_1, waypoint_2, ..., destination]
def route_distance_nm(points):
    total = 0
    for i in range(len(points) - 1):
        total += distance_nm(points[i], points[i + 1])
    return total

# KEEPING DECOUPLED FROM not-yet-built origin/waypoint/destination objects
# once they exist, just extract (lat, lon) from each and pass them in.
#-----------------------------------------------

# Direction Calculation Functions

# True North Bearing
# Initial great-circle bearing from point1 to point2, in degrees (0-360, true north)
def bearing_deg(point1, point2):
    lat1, lon1 = point1
    lat2, lon2 = point2

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lon = math.radians(lon2 - lon1)

    x = math.sin(delta_lon) * math.cos(lat2_rad)
    y = (math.cos(lat1_rad) * math.sin(lat2_rad)
         - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon))

    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360

# Bearing for each leg across an ordered list of (lat, lon) points
# e.g. [origin, waypoint_1, waypoint_2, ..., destination]
def route_bearings_deg(points):
    bearings = []
    for i in range(len(points) - 1):
        bearings.append(bearing_deg(points[i], points[i + 1]))
    return bearings


#-----------------------------------------------

