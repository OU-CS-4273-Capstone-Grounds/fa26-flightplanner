from datetime import date

import pytest
from fastapi.testclient import TestClient

from src.api import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


ENDPOINT = "/api/v1/calculations/density-altitude"
VALID_REQUEST = {
    "temperature_c": 20,
    "field_elevation_ft": 10000,
    "altimeter_inhg": 30.20,
}


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_density_altitude(client):
    response = client.post(ENDPOINT, json=VALID_REQUEST)
    assert response.status_code == 200
    assert response.json()["density_altitude_ft"] == pytest.approx(12652.8)


@pytest.mark.parametrize("altimeter", [28.0, 31.0])
def test_altimeter_boundaries(client, altimeter):
    response = client.post(ENDPOINT, json={**VALID_REQUEST, "altimeter_inhg": altimeter})
    assert response.status_code == 200


@pytest.mark.parametrize(
    "changes",
    [
        {"altimeter_inhg": 27.99},
        {"altimeter_inhg": 31.01},
        {"temperature_c": "warm"},
        {"temperature_c": "20"},
        {"temperature_c": True},
        {"field_elevation_ft": None},
        {"unexpected": 1},
    ],
)
def test_invalid_input(client, changes):
    response = client.post(ENDPOINT, json={**VALID_REQUEST, **changes})
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)


def test_missing_field(client):
    response = client.post(ENDPOINT, json={"temperature_c": 15})
    assert response.status_code == 422


def test_non_finite_number(client):
    response = client.post(
        ENDPOINT,
        content='{"temperature_c":1e400,"field_elevation_ft":0,"altimeter_inhg":29.92}',
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "temperature_c"]


def test_malformed_json(client):
    response = client.post(ENDPOINT, content="{", headers={"Content-Type": "application/json"})
    assert response.status_code == 422


def test_openapi_documents_calculation(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert ENDPOINT in response.json()["paths"]


# Additional calculation endpoints ---------------------------------------------

from src import calculations

CALCULATIONS = "/api/v1/calculations"
NORMAN = {"latitude": 35.2456, "longitude": -97.4721}
DALLAS = {"latitude": 32.8471, "longitude": -96.8518}
WICHITA = {"latitude": 37.6499, "longitude": -97.4331}
WIND_REQUEST = {
    "true_course_deg": 90,
    "true_airspeed_kt": 110,
    "wind_direction_deg": 180,
    "wind_speed_kt": 20,
}


def post(client, path, body):
    return client.post(f"{CALCULATIONS}/{path}", json=body)


def test_pressure_altitude(client):
    response = post(client, "pressure-altitude", {"field_elevation_ft": 1200, "altimeter_inhg": 29.42})
    assert response.status_code == 200
    assert response.json()["pressure_altitude_ft"] == pytest.approx(1700)


def test_pressure_altitude_rejects_bad_altimeter(client):
    response = post(client, "pressure-altitude", {"field_elevation_ft": 1200, "altimeter_inhg": 32})
    assert response.status_code == 422


def test_rate_of_climb(client):
    response = post(client, "rate-of-climb", {"density_altitude_ft": 3000})
    assert response.status_code == 200
    assert response.json()["rate_of_climb_fpm"] == pytest.approx(calculations.calculate_rate_of_climb(3000))


def test_true_airspeed(client):
    response = post(client, "true-airspeed", {"density_altitude_ft": 5000, "power_percent": 65})
    assert response.status_code == 200
    assert response.json()["true_airspeed_kt"] == pytest.approx(
        calculations.calculate_true_air_speed(5000, 65)
    )


@pytest.mark.parametrize("power", [49.9, 75.1])
def test_true_airspeed_rejects_power_out_of_range(client, power):
    response = post(client, "true-airspeed", {"density_altitude_ft": 5000, "power_percent": power})
    assert response.status_code == 422


def test_takeoff_distance(client):
    response = post(client, "takeoff-distance", {"density_altitude_ft": 2000})
    ground_run, over_obstacle = calculations.calculate_takeoff_distance(2000)
    assert response.status_code == 200
    assert response.json() == pytest.approx(
        {"ground_run_ft": ground_run, "over_50_ft_obstacle_ft": over_obstacle}
    )


def test_landing_distance(client):
    response = post(client, "landing-distance", {"density_altitude_ft": 2000})
    ground_roll, over_obstacle = calculations.calculate_landing_distance(2000)
    assert response.status_code == 200
    assert response.json() == pytest.approx(
        {"ground_roll_ft": ground_roll, "over_50_ft_obstacle_ft": over_obstacle}
    )


def test_route(client):
    response = post(client, "route", {"points": [DALLAS, NORMAN, WICHITA]})
    assert response.status_code == 200
    body = response.json()
    points = [(p["latitude"], p["longitude"]) for p in (DALLAS, NORMAN, WICHITA)]
    assert [leg["distance_nm"] for leg in body["legs"]] == pytest.approx(
        [calculations.distance_nm(points[0], points[1]), calculations.distance_nm(points[1], points[2])]
    )
    assert [leg["true_course_deg"] for leg in body["legs"]] == pytest.approx(
        calculations.route_bearings_deg(points)
    )
    assert body["total_distance_nm"] == pytest.approx(calculations.route_distance_nm(points))


@pytest.mark.parametrize(
    "points",
    [[NORMAN], [NORMAN, {"latitude": 91, "longitude": 0}], [NORMAN, {"latitude": 0, "longitude": 181}]],
)
def test_route_rejects_invalid_points(client, points):
    assert post(client, "route", {"points": points}).status_code == 422


def test_time_of_flight(client):
    response = post(client, "time-of-flight", {"legs": [
        {"distance_nm": 60, "ground_speed_kt": 120},
        {"distance_nm": 100, "ground_speed_kt": 100},
    ]})
    assert response.status_code == 200
    body = response.json()
    assert body["leg_minutes"] == pytest.approx([30, 60])
    assert body["total_hours"] == pytest.approx(1.5)
    assert body["total_minutes"] == pytest.approx(90)


@pytest.mark.parametrize(
    "legs",
    [[], [{"distance_nm": 10, "ground_speed_kt": 0}], [{"distance_nm": -1, "ground_speed_kt": 100}]],
)
def test_time_of_flight_rejects_invalid_legs(client, legs):
    assert post(client, "time-of-flight", {"legs": legs}).status_code == 422


def test_wind_triangle(client):
    response = post(client, "wind-triangle", WIND_REQUEST)
    args = tuple(WIND_REQUEST.values())
    assert response.status_code == 200
    assert response.json() == pytest.approx({
        "wind_correction_angle_deg": calculations.wind_correction_angle(*args),
        "true_heading_deg": calculations.true_heading(*args),
        "ground_speed_kt": calculations.ground_speed(*args),
    })


def test_wind_triangle_crosswind_too_strong(client):
    response = post(client, "wind-triangle", {**WIND_REQUEST, "wind_speed_kt": 150})
    assert response.status_code == 422
    assert "Crosswind" in response.json()["detail"][0]["msg"]


def test_magnetic_variation(client):
    response = post(client, "magnetic-variation", {**NORMAN, "date": "2026-06-01"})
    assert response.status_code == 200
    assert response.json()["variation_deg"] == pytest.approx(
        calculations.magnetic_variation((NORMAN["latitude"], NORMAN["longitude"]), date(2026, 6, 1))
    )


@pytest.mark.parametrize("bad_date", ["2026-13-01", 20260601, 1780012800])
def test_magnetic_variation_rejects_bad_date(client, bad_date):
    response = post(client, "magnetic-variation", {**NORMAN, "date": bad_date})
    assert response.status_code == 422


def test_magnetic_variation_date_outside_model(client):
    response = post(client, "magnetic-variation", {**NORMAN, "date": "2035-01-01"})
    assert response.status_code == 422


def test_compass_heading(client):
    card = [
        {"magnetic_heading_deg": 0, "correction_deg": 2},
        {"magnetic_heading_deg": 90, "correction_deg": -2},
        {"magnetic_heading_deg": 180, "correction_deg": 1},
        {"magnetic_heading_deg": 270, "correction_deg": 0},
    ]
    response = post(client, "compass-heading", {**WIND_REQUEST, "variation_deg": 3, "deviation_card": card})
    assert response.status_code == 200
    body = response.json()
    expected = calculations.compass_heading(
        *WIND_REQUEST.values(), 3, {e["magnetic_heading_deg"]: e["correction_deg"] for e in card}
    )
    assert body["compass_heading_deg"] == pytest.approx(expected)
    assert body["magnetic_heading_deg"] == pytest.approx(body["true_heading_deg"] - 3)


def test_compass_heading_rejects_large_deviation(client):
    card = [{"magnetic_heading_deg": 0, "correction_deg": 20}]
    response = post(client, "compass-heading", {**WIND_REQUEST, "variation_deg": 3, "deviation_card": card})
    assert response.status_code == 422


@pytest.mark.parametrize(
    "path",
    ["pressure-altitude", "rate-of-climb", "true-airspeed", "takeoff-distance", "landing-distance",
     "route", "time-of-flight", "wind-triangle", "magnetic-variation", "compass-heading"],
)
def test_openapi_documents_new_endpoints(client, path):
    assert f"{CALCULATIONS}/{path}" in client.get("/openapi.json").json()["paths"]


# Airport and weather endpoints -------------------------------------------------
# The weather functions are replaced with fakes so tests never call AviationWeather.gov.

from src import api
from src.weather import WeatherAPIError

METAR_KOUN = {
    "icao": "KOUN",
    "name": "Norman/Univ Oklahoma Arpt, OK, US",
    "observed": "2026-11-02T16:00:00.000Z",
    "raw_text": "METAR KOUN 021545Z VRB03KT 10SM SCT013 21/18 A2986",
    "temp_c": 21,
    "dewpoint_c": 18,
    "wind_dir_deg": "VRB",
    "wind_speed_kt": 3,
    "wind_gust_kt": None,
    "visibility_sm": "10+",
    "altimeter_hpa": 1011.3,
    "flight_category": "VFR",
    "clouds": [{"cover": "SCT", "base": 1300}],
}

TAF_KOUN = {
    "icao": "KOUN",
    "name": "Norman/Univ Oklahoma Arpt",
    "issued": "2026-11-02T14:30:00.000Z",
    "valid_from": 1793628000,
    "valid_to": 1793714400,
    "raw_text": "TAF KOUN 021430Z 0215/0312 16015G25KT P6SM SCT015",
    "forecast": [{
        "from": 1793628000,
        "to": 1793714400,
        "change_type": None,
        "probability": None,
        "wind_dir_deg": 160,
        "wind_speed_kt": 15,
        "wind_gust_kt": 25,
        "visibility_sm": "6+",
        "weather": None,
        "clouds": [{"cover": "SCT", "base": 1500}],
    }],
}


def test_airport(client):
    response = client.get("/api/v1/airports/koun")
    assert response.status_code == 200
    assert response.json() == {"icao": "KOUN", "latitude": 35.245556, "longitude": -97.472139}


def test_airport_unknown(client):
    response = client.get("/api/v1/airports/ZZZZ")
    assert response.status_code == 404
    assert "ZZZZ" in response.json()["detail"][0]["msg"]


@pytest.mark.parametrize("path", ["airports/KOU", "airports/K%21UN", "weather/metar/KOUNX", "weather/taf/K-UN"])
def test_invalid_icao(client, path):
    assert client.get(f"/api/v1/{path}").status_code == 422


def test_metar(client, monkeypatch):
    monkeypatch.setattr(api, "get_metar", lambda icao: METAR_KOUN)
    response = client.get("/api/v1/weather/metar/KOUN")
    assert response.status_code == 200
    assert response.json() == METAR_KOUN


def test_taf(client, monkeypatch):
    monkeypatch.setattr(api, "get_taf", lambda icao: TAF_KOUN)
    response = client.get("/api/v1/weather/taf/KOUN")
    assert response.status_code == 200
    assert response.json() == TAF_KOUN


@pytest.mark.parametrize("report", ["metar", "taf"])
def test_weather_no_report(client, monkeypatch, report):
    monkeypatch.setattr(api, f"get_{report}", lambda icao: None)
    response = client.get(f"/api/v1/weather/{report}/KOUN")
    assert response.status_code == 404


@pytest.mark.parametrize("report", ["metar", "taf"])
def test_weather_service_down(client, monkeypatch, report):
    def fail(icao):
        raise WeatherAPIError("Failed to fetch data: timed out")

    monkeypatch.setattr(api, f"get_{report}", fail)
    response = client.get(f"/api/v1/weather/{report}/KOUN")
    assert response.status_code == 502
    assert response.json()["detail"][0]["type"] == "weather_unavailable"
