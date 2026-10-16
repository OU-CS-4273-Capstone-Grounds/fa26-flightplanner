"""HTTP entry point. Calculation logic stays in the shared calculations module."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from .calculations import calculate_density_altitude


app = FastAPI(title="Flight Planner API", version="0.1.0")


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    # Do not echo raw inputs: non-finite numbers cannot be serialized as JSON.
    return JSONResponse(
        status_code=422,
        content={"detail": [
            {key: error[key] for key in ("loc", "msg", "type")}
            for error in exc.errors()
        ]},
    )


class DensityAltitudeRequest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", allow_inf_nan=False)

    temperature_c: float = Field(description="Outside air temperature in degrees Celsius")
    field_elevation_ft: float = Field(description="Airfield elevation in feet")
    altimeter_inhg: float = Field(
        ge=28.0, le=31.0, description="Altimeter setting in inches of mercury"
    )


class DensityAltitudeResponse(BaseModel):
    density_altitude_ft: float


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Report that the API is running; no external services are contacted."""
    return {"status": "ok"}


@app.post(
    "/api/v1/calculations/density-altitude",
    response_model=DensityAltitudeResponse,
    tags=["calculations"],
)
def density_altitude(request: DensityAltitudeRequest) -> DensityAltitudeResponse:
    """Calculate density altitude using the existing shared function."""
    return DensityAltitudeResponse(
        density_altitude_ft=calculate_density_altitude(
            request.temperature_c,
            request.field_elevation_ft,
            request.altimeter_inhg,
        )
    )
