import re

#Function to check if the inputted ICAO ID is a valid ICAO ID
def is_valid_icao_id(icao_id):
    #Returns true if the input format matches those of ICAO IDs. 
    #Uses regular expressions to do the checking by making sure the input is comprised only of letters A-Z and has a length of 4.
    return bool(re.fullmatch(r"[A-Z]{4}", icao_id))

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
    #Currently this only checks that the input message is 4 characters long, all of which belong to the english alphabet.
    if not is_valid_icao_id(departure_ICAO):
        errors.append("Departure ICAO identifier must contain exactly 4 letters.")
        
    #Adds a message informing the user that their destination ICAO ID input was blank to the errors list if the input was
    #found to be blank.
    if not destination_ICAO:
        errors.append("Destination ICAO identifier cannot be empty.")
        
    #Adds a message informing the user that the destination ICAO ID was invalid to the errors list if the input fails
    #to be found a valid ICAO ID by is_valid_icao_id.
    #Currently this only checks that the input message is 4 characters long, all of which belong to the english alphabet.
    if not is_valid_icao_id(destination_ICAO):
            errors.append("Destination ICAO identifier must contain exactly 4 letters.")
            
    #Informs the user of any errors with their input by checking if the errors list has any items in it. If it does then
    #it will work through each error and display them individually so that the user has a clear understanding of why their
    #inputs didn't work.
    if errors:
        for error in errors:
            print(error)
        return
    
    #If no errors are found with the user's input, print out a statement which shows the user's inputs clearly displayed.
    print(f"Enjoy your flight from {departure_ICAO} to {destination_ICAO}!")