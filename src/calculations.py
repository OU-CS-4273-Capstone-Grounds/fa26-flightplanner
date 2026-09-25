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

def calculate_pressure_altitude(altimeter_setting, field_elevation_in_ft):
    """
    Calculate the pressure altitude.

    Parameters:
    altimeter_setting (float): The current altimeter setting in inches of mercury (inHg).
    field_elevation_in_ft (float): The elevation of the airfield in feet.

    Returns:
    float: The pressure altitude in feet.
    """
    if altimeter_setting < 28.00 or altimeter_setting > 31.00:
        raise ValueError("Altimeter setting out of range (28.00-31.00 inHg)")

    return field_elevation_in_ft + (29.92 - altimeter_setting) * 1000

def calculate_density_altitude(temperature_in_c, field_elevation_in_ft, altimeter_setting):
    """
    Calculate the density altitude.

    Parameters:
    temperature_in_c (float): The outside air temperature in degrees Celsius.
    field_elevation_in_ft (float): The elevation of the airfield in feet.
    altimeter_setting (float): The current altimeter setting in inches of mercury (inHg).
    
    Returns:
    float: The density altitude in feet.
    """ 

    sea_base_line = 15
    lapse_rate = 2

    pressure_altitude = calculate_pressure_altitude(altimeter_setting, field_elevation_in_ft)
    ISA_temperature = sea_base_line - (pressure_altitude / 1000) * lapse_rate
    
    return pressure_altitude + (120 * (temperature_in_c - ISA_temperature))

def calculate_rate_of_climb(density_altitude):
    """
    Calculate the rate of climb based on the density altitude from the piper cherokee chart.

    Parameters:
    density_altitude (float): The density altitude in feet.

    Returns:
    float: The rate of climb in feet per minute.
    """
    slope = 25
    y_intercept = 16500
    
    return (y_intercept-density_altitude)/slope

def calculate_true_air_speed(density_altitude, power_setting):
    """
    Calculate the true air speed based on the density altitude and power setting.

    Parameters:
    density_altitude (float): The density altitude in feet.
    power_setting (float): The power setting as a percentage.

    Returns:
    float: The calculated true air speed in knots.
    """
    if power_setting < 50 or power_setting > 75:
        raise Exception("Power setting out of range (50-75)")
    
    y_intercept = 45.653
    mph_per_density_altitude = 0.0008722
    mph_per_percent_power = 1.0430 

    return mph_to_knots(y_intercept + mph_per_density_altitude * density_altitude + mph_per_percent_power * power_setting)

def calculate_landing_distance(density_altitude):
    """
    Calculate the landing distance based on the density altitude and the type of landing.

    Parameters:
    density_altitude (float): The density altitude in feet.

    Returns:
    ground_roll (float): The calculated ground roll distance in feet.
    over_50_feet_obstacle (float): The calculated distance to clear a 50-feet obstacle in feet.
    """

    y_intercept_ground_roll = 37500
    slope_ground_roll = 70
    y_intercept_over_50_feet_obstacle = 43000
    slope_over_50_feet_obstacle = 40

    ground_roll = (density_altitude/slope_ground_roll) + (y_intercept_ground_roll/slope_ground_roll)
    over_50_feet_obstacle = (density_altitude/slope_over_50_feet_obstacle) + (y_intercept_over_50_feet_obstacle/slope_over_50_feet_obstacle)

    return ground_roll, over_50_feet_obstacle

def calculate_takeoff_distance(density_altitude):
    """
    Calculate the takeoff distance based on the density altitude and the type of takeoff.

    Parameters:
    density_altitude (float): The density altitude in feet.

    Returns:
    float or str: The calculated takeoff distance in feet, or an error message if both or neither options are selected.
    """
    slope_ground_run = 14
    y_intercept_ground_run = 11000
    slope_over_50_feet_obstacle = 6
    y_intercept_over_50_feet_obstacle = 10000

    ground_run = (density_altitude/slope_ground_run) + (y_intercept_ground_run/slope_ground_run)
    over_50_feet_obstacle =(density_altitude/slope_over_50_feet_obstacle) + (y_intercept_over_50_feet_obstacle/slope_over_50_feet_obstacle)

    return ground_run, over_50_feet_obstacle
