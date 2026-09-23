# Gets current weather (METAR) and forecasts (TAF) for airports from
# the AviationWeather.gov API and extracts the fields used by the app.
# API docs: https://aviationweather.gov/data/api/

import requests

BASE_URL = "https://aviationweather.gov/api/data"
DEFAULT_TIMEOUT = 10  # seconds


class WeatherAPIError(Exception):
    # Raised when a weather API request fails.
    pass


# Helpers
def _ids_param(airports):
    # Convert one airport code or a list of codes to uppercase and join
    # multiple codes with commas for the API (e.g. "KJFK,KLAX").
    if isinstance(airports, str):
        return airports.upper()
    return ",".join(code.upper() for code in airports)


def _request(endpoint, airports, timeout):
    # Request weather data and return the JSON, or raise WeatherAPIError
    # if the request fails or the response is not valid JSON.
    params = {"ids": _ids_param(airports), "format": "json"}
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        raise WeatherAPIError(f"Failed to fetch {endpoint} data: {e}") from e

    try:
        return response.json()
    except ValueError as e:
        raise WeatherAPIError(f"Invalid JSON response for {endpoint}: {e}") from e


# METAR (current observations)
def _parse_metar(raw):
    # Extract the current weather fields from one airport's METAR report.
    return {
        "icao": raw.get("icaoId"),
        "name": raw.get("name"),
        "observed": raw.get("reportTime"),
        "raw_text": raw.get("rawOb"),
        "temp_c": raw.get("temp"),
        "dewpoint_c": raw.get("dewp"),
        "wind_dir_deg": raw.get("wdir"),
        "wind_speed_kt": raw.get("wspd"),
        "wind_gust_kt": raw.get("wgst"),
        "visibility_sm": raw.get("visib"),
        "altimeter_hpa": raw.get("altim"),
        "flight_category": raw.get("fltCat"),
        "clouds": raw.get("clouds", []),
    }


def get_metar(airports, timeout=DEFAULT_TIMEOUT):
    # Fetch current weather for one airport code or a list of codes.
    # Return a dictionary (or None if no data) for a single code,
    # or a list of dictionaries in API order for a list of codes.
    data = _request("metar", airports, timeout)
    parsed = [_parse_metar(raw) for raw in data]

    if isinstance(airports, str):
        return parsed[0] if parsed else None
    return parsed


# TAF (forecasts)
def _parse_taf_period(period):
    # Extract the weather and start/end times for one forecast period.
    return {
        "from": period.get("timeFrom"),
        "to": period.get("timeTo"),
        "change_type": period.get("fcstChange"),
        "probability": period.get("probability"),
        "wind_dir_deg": period.get("wdir"),
        "wind_speed_kt": period.get("wspd"),
        "wind_gust_kt": period.get("wgst"),
        "visibility_sm": period.get("visib"),
        "weather": period.get("wxString"),
        "clouds": period.get("clouds", []),
    }


def _parse_taf(raw):
    # Extract an airport's forecast details and parse each forecast period.
    return {
        "icao": raw.get("icaoId"),
        "name": raw.get("name"),
        "issued": raw.get("issueTime"),
        "valid_from": raw.get("validTimeFrom"),
        "valid_to": raw.get("validTimeTo"),
        "raw_text": raw.get("rawTAF"),
        "forecast": [_parse_taf_period(p) for p in raw.get("fcsts", [])],
    }


def get_taf(airports, timeout=DEFAULT_TIMEOUT):
    # Fetch forecasts for one airport code or a list of codes.
    # Return a dictionary (or None if no data) for a single code,
    # or a list of dictionaries in API order for a list of codes.
    data = _request("taf", airports, timeout)
    parsed = [_parse_taf(raw) for raw in data]

    if isinstance(airports, str):
        return parsed[0] if parsed else None
    return parsed
