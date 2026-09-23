# Looks up airport coordinates by code using the airportsdata package.
# Package docs: https://pypi.org/project/airportsdata/

import airportsdata

_AIRPORTS_BY_ICAO = airportsdata.load("ICAO")

class AirportNotFoundError(ValueError):
    # Raised when an airport code is invalid or unknown.
    pass


def get_airport_coordinates(code):
    # Return (latitude, longitude) for an ICAO airport code (e.g. "KJFK"). Raises AirportNotFoundError if the code
    # is not a string, is empty, or is not a known airport.
    if not isinstance(code, str) or not code.strip():
        raise AirportNotFoundError(
            f"Invalid airport code {code!r}: expected an ICAO airport code."
        )
    key = code.strip().upper()
    airport = _AIRPORTS_BY_ICAO.get(key)
    if airport is None:
        raise AirportNotFoundError(f"Unknown airport code {code!r}: no matching airport found.")
    return airport["lat"], airport["lon"]
