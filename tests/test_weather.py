import pytest

from src import weather

# Sample API responses. These mimic the JSON that AviationWeather.gov
# returns, so the tests never have to make a real network request.

# Current weather (METAR) for JFK.
METAR_KJFK = {
    "icaoId": "KJFK",
    "name": "New York/JF Kennedy Intl, NY, US",
    "reportTime": "2026-09-17T15:00:00.000Z",
    "rawOb": "METAR KJFK 171451Z 21008KT 10SM BKN043 24/19 A3025",
    "temp": 24.4,
    "dewp": 19.4,
    "wdir": 210,
    "wspd": 8,
    "wgst": None,
    "visib": "10+",
    "altim": 1024.5,
    "fltCat": "VFR",
    "clouds": [{"cover": "BKN", "base": 4300}],
}

# Current weather (METAR) for LAX, used to test multiple airports.
METAR_KLAX = {
    "icaoId": "KLAX",
    "name": "Los Angeles Intl, CA, US",
    "reportTime": "2026-09-17T15:00:00.000Z",
    "rawOb": "METAR KLAX 171453Z 24005KT 10SM FEW015 21/15 A3008",
    "temp": 21.1,
    "dewp": 15.0,
    "wdir": 240,
    "wspd": 5,
    "wgst": None,
    "visib": "10+",
    "altim": 1018.7,
    "fltCat": "VFR",
    "clouds": [{"cover": "FEW", "base": 1500}],
}

# Forecast (TAF) for JFK with a single forecast period.
TAF_KJFK = {
    "icaoId": "KJFK",
    "name": "New York/JF Kennedy Intl",
    "issueTime": "2026-09-17T14:30:00.000Z",
    "validTimeFrom": 1789657200,
    "validTimeTo": 1789754400,
    "rawTAF": "TAF KJFK 171430Z 1715/1818 20009KT P6SM SCT050",
    "fcsts": [
        {
            "timeFrom": 1789657200,
            "timeTo": 1789675200,
            "fcstChange": None,
            "probability": None,
            "wdir": 200,
            "wspd": 9,
            "wgst": None,
            "visib": "6+",
            "wxString": None,
            "clouds": [{"cover": "SCT", "base": 5000}],
        }
    ],
}


# Stand-in for a requests.Response so tests can control the status code
# and JSON body that requests.get() appears to return.
class FakeResponse:
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code

    def raise_for_status(self):
        # Like the real one, raise on 4xx/5xx status codes.
        if self.status_code >= 400:
            raise weather.requests.HTTPError(f"{self.status_code} error")

    def json(self):
        return self._json_data


def test_ids_param_single_string():
    # A single airport code should be converted to uppercase.
    assert weather._ids_param("kjfk") == "KJFK"


def test_ids_param_list():
    # Multiple codes should be uppercased and joined with commas.
    assert weather._ids_param(["kjfk", "klax"]) == "KJFK,KLAX"


def test_get_metar_single_airport(monkeypatch):
    # A single airport code should return one dictionary with the
    # METAR fields renamed to the ones the app uses.
    def fake_get(url, params=None, timeout=None):
        # Check the request is built correctly, then return fake data.
        assert params == {"ids": "KJFK", "format": "json"}
        return FakeResponse([METAR_KJFK])

    # Replace the real requests.get() with our fake for this test only.
    monkeypatch.setattr(weather.requests, "get", fake_get)

    result = weather.get_metar("KJFK")

    assert result["icao"] == "KJFK"
    assert result["temp_c"] == 24.4
    assert result["wind_dir_deg"] == 210
    assert result["wind_speed_kt"] == 8
    assert result["flight_category"] == "VFR"


def test_get_metar_multiple_airports(monkeypatch):
    # A list of airport codes should return a list of dictionaries,
    # in the same order the API sent them back.
    def fake_get(url, params=None, timeout=None):
        assert params == {"ids": "KJFK,KLAX", "format": "json"}
        return FakeResponse([METAR_KJFK, METAR_KLAX])

    monkeypatch.setattr(weather.requests, "get", fake_get)

    result = weather.get_metar(["KJFK", "KLAX"])

    assert isinstance(result, list)
    assert [r["icao"] for r in result] == ["KJFK", "KLAX"]


def test_get_metar_no_data_returns_none(monkeypatch):
    # The API returns an empty list for an unknown airport. A single
    # airport with no data should give back None instead of crashing.
    monkeypatch.setattr(weather.requests, "get", lambda *a, **kw: FakeResponse([]))

    assert weather.get_metar("ZZZZ") is None


def test_get_metar_http_error_raises_weather_api_error(monkeypatch):
    # A 500 response from the server should turn into our own
    # WeatherAPIError, not a raw requests error.
    monkeypatch.setattr(weather.requests, "get", lambda *a, **kw: FakeResponse([], status_code=500))

    with pytest.raises(weather.WeatherAPIError):
        weather.get_metar("KJFK")


def test_get_taf_single_airport(monkeypatch):
    # A single airport code should return one forecast dictionary,
    # including its list of parsed forecast periods.
    def fake_get(url, params=None, timeout=None):
        assert params == {"ids": "KJFK", "format": "json"}
        return FakeResponse([TAF_KJFK])

    monkeypatch.setattr(weather.requests, "get", fake_get)

    result = weather.get_taf("KJFK")

    assert result["icao"] == "KJFK"
    assert result["raw_text"].startswith("TAF KJFK")
    # The one period in the fake data should be parsed with renamed fields.
    assert len(result["forecast"]) == 1
    assert result["forecast"][0]["wind_dir_deg"] == 200
    assert result["forecast"][0]["wind_speed_kt"] == 9


def test_get_taf_multiple_airports(monkeypatch):
    # Same as above, but for a list of airports instead of just one.
    TAF_KLAX = {**TAF_KJFK, "icaoId": "KLAX", "name": "Los Angeles Intl"}

    def fake_get(url, params=None, timeout=None):
        assert params == {"ids": "KJFK,KLAX", "format": "json"}
        return FakeResponse([TAF_KJFK, TAF_KLAX])

    monkeypatch.setattr(weather.requests, "get", fake_get)

    result = weather.get_taf(["KJFK", "KLAX"])

    assert isinstance(result, list)
    assert [r["icao"] for r in result] == ["KJFK", "KLAX"]


def test_get_metar_no_data_for_list_returns_empty_list(monkeypatch):
    # A list input with no matches should return an empty list, not None.
    # None is only used when a single airport has no match.
    monkeypatch.setattr(weather.requests, "get", lambda *a, **kw: FakeResponse([]))

    result = weather.get_metar(["ZZZZ", "YYYY"])

    assert result == []


def test_get_metar_partial_match_does_not_align_with_request(monkeypatch):
    # If an airport has no data, the API just leaves it out of the
    # response instead of sending a placeholder. So the result list can
    # come back shorter than the list you asked for, and it won't line up
    # by position with your original airport list.
    def fake_get(url, params=None, timeout=None):
        # Only KJFK has data. ZZZZ isn't a real airport.
        return FakeResponse([METAR_KJFK])

    monkeypatch.setattr(weather.requests, "get", fake_get)

    result = weather.get_metar(["KJFK", "ZZZZ"])

    assert len(result) == 1
    assert result[0]["icao"] == "KJFK"


def test_get_metar_network_error_raises_weather_api_error(monkeypatch):
    # Simulates a connection failure (no internet, DNS error, etc.),
    # where requests.get() raises before we even get a response back.
    # This should still turn into our own WeatherAPIError, not a raw
    # requests error.
    def fake_get(*args, **kwargs):
        raise weather.requests.ConnectionError("network is unreachable")

    monkeypatch.setattr(weather.requests, "get", fake_get)

    with pytest.raises(weather.WeatherAPIError):
        weather.get_metar("KJFK")


def test_get_metar_invalid_json_raises_weather_api_error(monkeypatch):
    # Simulates a 200 response with a broken/non-JSON body. This should
    # also turn into a WeatherAPIError instead of crashing with a
    # raw ValueError.
    class BadJSONResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            raise ValueError("not valid JSON")

    monkeypatch.setattr(weather.requests, "get", lambda *a, **kw: BadJSONResponse())

    with pytest.raises(weather.WeatherAPIError):
        weather.get_metar("KJFK")


def test_ids_param_single_item_list_matches_string_form():
    # A list with one airport should work the same as passing a plain string.
    assert weather._ids_param(["kjfk"]) == weather._ids_param("kjfk") == "KJFK"
