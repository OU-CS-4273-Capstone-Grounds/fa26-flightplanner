import airportsdata
from .airports import _AIRPORTS_BY_ICAO, get_airport_coordinates
from .weather import get_metar, get_taf, WeatherAPIError
from .calculations import distance_nm

airports = _AIRPORTS_BY_ICAO

#Function to check if the inputted ICAO ID is a valid ICAO ID
def is_valid_icao_id(icao_id):
    #Returns true if the input format matches those of ICAO IDs. 
    #Uses regular expressions to do the checking by making sure the input is comprised only of letters A-Z and has a length of 4.
    return icao_id in airports

#Function to interact with the weather class and use it to display the weather information for a specific ICAO ID.
def display_weather_information(icao_id):
    print(f"\n--- Weather for {icao_id} ---")
    
    #Attempts to get the metar data for that ICAO ID
    try:
        metar = get_metar(icao_id)
        
        #If metar data was obtained, then use the information that gets stored in the metar variable to display
        #all of the current metar data for the airport with that ICAO ID.
        if metar:
            print("Current Weather (METAR):")
            print(f"Temperature: {metar['temp_c']} °C")
            print(f"Wind Direction: {metar['wind_dir_deg']}°")
            print(f"Wind Speed: {metar['wind_speed_kt']} knots")
            print(f"Visibility: {metar['visibility_sm']} miles")
            print(f"Altimeter Setting: {metar['altimeter_hpa']} hPa")
            print(f"Flight Category: {metar['flight_category']}")
            print(f"Raw METAR: {metar['raw_text']}")
        #If metar data could not be obtained, then inform the user that no current weather data is available
        #for the airport with that ICAO ID.
        else:
            print("No current weather data is available for this ICAO ID.")       
    #Catches any errors which may be caused by trying to interact with the weather API, being sure to inform the
    #user of the error which was encountered.
    except WeatherAPIError as e:
        print(f"Unable to retrieve METAR: {e}")
        
    #Attempts to get the taf data for the airport with the matching ICAO ID.
    try:
        taf = get_taf(icao_id)
        
        #If taf data coule be obtained, then use the information that gets stored in the taf variable to display
        #all of the current taf data from the airport with the matching ICAO ID.
        if taf:
            print("\nForecast (TAF):")
            print(f"Issued: {taf['issued']}")
            print(f"Valid From: {taf['valid_from']}")
            print(f"Valid To: {taf['valid_to']}")
            print(f"Raw TAF: {taf['raw_text']}")
        #If taf data could not be obtained, then inform the user that no current forecast data is available
        #for the airport with that ICAO ID.
        else:
            print("No forecast data available for this ICAO ID.")
    #Catches any errors which may be caused by trying to interact with the weather API, being sure to inform the
    #user of the error which was encountered.
    except WeatherAPIError as e:
        print(f"Unable to retreive TAF: {e}")

#Function to run the command line interface.
def run_cli():
    #Collects the departure ICAO ID from the user and makes use of the .strip() and .upper() functions to
    #ensure that the user input is properly collected and formatted for checking with is_valid_icao_id().
    departure_ICAO = input("Enter your departure ICAO identifier: ").strip().upper()
    
    #Collects the destinatiom ICAO ID from the user and makes use of the .strip() and .upper() functions to
    #ensure that the user input is properly collected and formatted for checking with is_valid_icao_id().
    destination_ICAO = input("Enter your destination ICAO identifier: ").strip().upper()
    
    print()
    
    #Creates a new empty list to collect all of the error messages which the user input may have caused in order to
    #display them all to the user.
    errors = []
    
    #Adds a message informing the user that their departure ICAO ID input was blank to the errors list if the input was
    #found to be blank.
    if not departure_ICAO:
        errors.append("Departure ICAO identifier cannot be empty.")
        
    #Adds a message informing the user that the departure ICAO ID was invalid to the errors list if the input fails
    #to be found a valid ICAO ID by is_valid_icao_id.
    elif not is_valid_icao_id(departure_ICAO):
        errors.append("Departure ICAO identifier is not a valid airport.")
        
    #Adds a message informing the user that their destination ICAO ID input was blank to the errors list if the input was
    #found to be blank.
    if not destination_ICAO:
        errors.append("Destination ICAO identifier cannot be empty.")
        
    #Adds a message informing the user that the destination ICAO ID was invalid to the errors list if the input fails
    #to be found a valid ICAO ID by is_valid_icao_id.
    elif not is_valid_icao_id(destination_ICAO):
        errors.append("Destination ICAO identifier is not a valid airport.")
            
    #Informs the user of any errors with their input by checking if the errors list has any items in it. If it does then
    #it will work through each error and display them individually so that the user has a clear understanding of why their
    #inputs didn't work.
    if errors:
        for error in errors:
            print(error)
        return
    
    #Pulls from airportsdata to store the departure and destination airports for future use in the CLI code.
    departure_airport = airports[departure_ICAO]
    destination_airport = airports[destination_ICAO]
    
    #Uses the departure_airport variable to collect the latitude and longitude as coordinated for use in the
    #distance calculations.
    departure_coordinates = get_airport_coordinates(departure_ICAO)
    
    #Uses the destination_airport variable to collect the latitude and longitude as coordinated for use in the
    #distance calculations.
    destination_coordiantes = get_airport_coordinates(destination_ICAO)
    
    #Calculates the distance between the departure and destination airports by using the coordinates which were
    #collected for the two airports.
    distance = distance_nm(departure_coordinates, destination_coordiantes)
    
    #If no errors are found with the user's input, print out a statement which shows the user's inputs clearly displayed.
    print(f"Enjoy your flight from {departure_ICAO} to {destination_ICAO}!")
    
    #Displays the more in depth flight information for the user to look over before their flight.
    print("\n--- Flight Information ---")
    print(f"Departure Airport: {departure_airport['name']}")
    print(f"Destination Airport: {destination_airport['name']}")
    #Displays the distance information in nautical miles, rounding to 2 decimal places.
    print(f"Distance Between Airports: {distance:.2f} nautical miles")
    #Calls the display_weather_information for the departure airport to display the metar and taf data
    #to the user.
    display_weather_information(departure_ICAO)
    #Calls the display_weather_information for the destination airport to display the metar and taf data
    #to the user.
    display_weather_information(destination_ICAO)