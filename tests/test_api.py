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
