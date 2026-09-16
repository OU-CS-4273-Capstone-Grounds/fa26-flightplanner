def calculate_pressure_altitude(altimeter_setting, field_elevation):
    """
    Calculate the pressure altitude.

    Parameters:
    altimeter_setting (float): The current altimeter setting in inches of mercury (inHg).
    field_elevation (float): The elevation of the airfield in feet.

    Returns:
    float: The pressure altitude in feet.
    """

    return field_elevation + (29.92 - altimeter_setting) * 1000

def calculate_density_altitude(temperature, field_elevation, altimeter_setting):
    """
    Calculate the density altitude.

    Parameters:
    temperature (float): The outside air temperature in degrees Celsius.
    field_elevation (float): The elevation of the airfield in feet.
    altimeter_setting (float): The current altimeter setting in inches of mercury (inHg).
    
    Returns:
    float: The density altitude in feet.
    """ 

    pressure_altitude = calculate_pressure_altitude(altimeter_setting, field_elevation)
    ISA_temperature = 15 - (pressure_altitude / 1000) * 2
    return pressure_altitude + (120 * (temperature - ISA_temperature))

def calculate_rate_of_climb(temperature, field_elevation, altimeter_setting):
    """
    Calculate the rate of climb based on the density altitude from the piper cherokee chart.

    Parameters:
    temperature (float): The outside air temperature in degrees Celsius.
    field_elevation (float): The elevation of the airfield in feet.
    altimeter_setting (float): The current altimeter setting in inches of mercury (inHg).

    Returns:
    float: The rate of climb in feet per minute.
    """

    slope = 25
    density_altitude = calculate_density_altitude(temperature, field_elevation, altimeter_setting)
    return (16500-density_altitude)/slope

def calculate_true_air_speed(temperature, field_elevation, altimeter_setting, power_setting):
    """
    Calculate the true air speed based on the density altitude and power setting.

    Parameters:
    temperature (float): The outside air temperature in degrees Celsius.
    field_elevation (float): The elevation of the airfield in feet.
    altimeter_setting (float): The current altimeter setting in inches of mercury (inHg).
    power_setting (float): The power setting as a percentage.

    Returns:
    float: The calculated true air speed in miles per hour (mph).
    """
    if power_setting < 50 or power_setting > 75:
        return "Power setting out of range (50-75)"
    
    density_altitude = calculate_density_altitude(temperature, field_elevation, altimeter_setting)
    y_intercept = 45.653
    mph_per_density_altitude = 0.0008722
    mph_per_percent_power = 1.0430
    return y_intercept + mph_per_density_altitude * density_altitude + mph_per_percent_power * power_setting

def calculate_landing_distance(temperature, field_elevation, altimeter_setting, ground_roll, over_50_feet_obstacle):
    """
    Calculate the landing distance based on the density altitude and the type of landing.

    Parameters:
    temperature (float): The outside air temperature in degrees Celsius.
    field_elevation (float): The elevation of the airfield in feet.
    altimeter_setting (float): The current altimeter setting in inches of mercury (inHg).
    ground_roll (bool): Whether to calculate the ground roll distance.
    over_50_feet_obstacle (bool): Whether to calculate the distance to clear a 50-feet obstacle.

    Returns:
    float or str: The calculated landing distance in feet, or an error message if both or neither options are selected.
    """

    density_altitude = calculate_density_altitude(temperature, field_elevation, altimeter_setting)
    if ground_roll and over_50_feet_obstacle:
        return "Cannot have both enabled"
    if ground_roll:
        y_intercept = 37500
        slope = 70
        return (density_altitude/slope) + (y_intercept/slope)
    if over_50_feet_obstacle:
        y_intercept = 43000
        slope = 40
        return (density_altitude/slope) + (y_intercept/slope)
    return "No option selected"

def calculate_takeoff_distance(temperature, field_elevation, altimeter_setting, ground_run, over_50_feet_obstacle):
    """
    Calculate the takeoff distance based on the density altitude and the type of takeoff.

    Parameters:
    temperature (float): The outside air temperature in degrees Celsius.
    field_elevation (float): The elevation of the airfield in feet.
    altimeter_setting (float): The current altimeter setting in inches of mercury (inHg).
    ground_run (bool): Whether to calculate the ground roll distance.
    over_50_feet_obstacle (bool): Whether to calculate the distance to clear a 50-feet obstacle.

    Returns:
    float or str: The calculated takeoff distance in feet, or an error message if both or neither options are selected.
    """

    density_altitude = calculate_density_altitude(temperature, field_elevation, altimeter_setting)
    if ground_run and over_50_feet_obstacle:
        return "Cannot have both enabled"
    if ground_run:
        slope = 14
        y_intercept = 11000
        return (density_altitude/slope) + (y_intercept/slope)
    if over_50_feet_obstacle:
        slope = 6
        y_intercept = 10000
        return (density_altitude/slope) + (y_intercept/slope)
    return "No option selected"
