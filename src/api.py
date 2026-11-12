"""HTTP entry point. Calculation logic stays in the shared calculations module."""

from datetime import date as Date

from fastapi import FastAPI, HTTPException, Path
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .airports import AirportNotFoundError, get_airport_coordinates
from .calculations import (
    bearing_deg,
    calculate_density_altitude,
    calculate_landing_distance,
    calculate_pressure_altitude,
    calculate_rate_of_climb,
    calculate_takeoff_distance,
    calculate_true_air_speed,
    compass_deviation,
    distance_nm,
    distance_to_climb_nm,
    ground_speed,
    magnetic_course,
    magnetic_variation,
    time_of_flight_hours,
    time_to_climb_minutes,
    top_of_descent_nm,
    true_heading,
    wind_correction_angle,
    total_air_time,
)
from .weather import WeatherAPIError, get_metar, get_taf


app = FastAPI(title="Flight Planner API", version="0.1.0")

CALCULATIONS = "/api/v1/calculations"
AIRPORTS = "/api/v1/airports"
WEATHER = "/api/v1/weather"

# Path parameter shared by the airport and weather endpoints
IcaoPath = Path(pattern="^[A-Za-z0-9]{4}$", description="ICAO airport code, e.g. KOUN")


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


def _calculate(function, *args):
    # Calculations raise ValueError for inputs that are well-formed but cannot be
    # flown (e.g. crosswind stronger than airspeed); report them like validation errors.
    try:
        return function(*args)
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body"], "msg": str(error), "type": "value_error"}],
        )


def _not_found(message):
    return HTTPException(
        status_code=404,
        detail=[{"loc": ["path", "icao"], "msg": message, "type": "not_found"}],
    )


def _fetch_weather(function, icao):
    # Weather outages are the upstream service's fault, so report them as 502 Bad Gateway.
    try:
        report = function(icao)
    except WeatherAPIError as error:
        raise HTTPException(
            status_code=502,
            detail=[{"loc": ["path", "icao"], "msg": str(error), "type": "weather_unavailable"}],
        )
    if report is None:
        raise _not_found(f"No current report available for {icao.upper()}")
    return report


class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", allow_inf_nan=False)


# Requests --------------------------------------------------------------------

class PressureAltitudeRequest(StrictModel):
    field_elevation_ft: float = Field(description="Airfield elevation in feet")
    altimeter_inhg: float = Field(
        ge=28.0, le=31.0, description="Altimeter setting in inches of mercury"
    )


class DensityAltitudeRequest(PressureAltitudeRequest):
    temperature_c: float = Field(description="Outside air temperature in degrees Celsius")


class PerformanceRequest(StrictModel):
    density_altitude_ft: float = Field(description="Density altitude in feet")


class TrueAirspeedRequest(PerformanceRequest):
    power_percent: float = Field(ge=50, le=75, description="Engine power setting in percent")


class Point(StrictModel):
    latitude: float = Field(ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(ge=-180, le=180, description="Longitude in decimal degrees")

    def as_tuple(self) -> tuple[float, float]:
        return self.latitude, self.longitude


class RouteRequest(StrictModel):
    points: list[Point] = Field(
        min_length=2, description="Ordered route: origin, waypoints, destination"
    )


class TimeOfFlightLeg(StrictModel):
    distance_nm: float = Field(ge=0, description="Leg distance in nautical miles")
    ground_speed_kt: float = Field(gt=0, description="Leg ground speed in knots")


class TimeOfFlightRequest(StrictModel):
    legs: list[TimeOfFlightLeg] = Field(min_length=1)


class ClimbRequest(StrictModel):
    start_density_altitude_ft: float = Field(description="Density altitude at the start of the climb in feet")
    cruise_density_altitude_ft: float = Field(description="Density altitude at cruise in feet")
    ground_speed_kt: float = Field(gt=0, description="Ground speed during the climb in knots")


class TopOfDescentRequest(StrictModel):
    cruise_altitude_ft: float = Field(description="Cruise altitude in feet")
    destination_altitude_ft: float = Field(description="Destination altitude in feet")
    ground_speed_kt: float = Field(gt=0, description="Ground speed during the descent in knots")
    descent_rate_fpm: float = Field(default=500, gt=0, description="Descent rate in feet per minute")


class WindTriangleRequest(StrictModel):
    true_course_deg: float = Field(ge=0, lt=360, description="True course in degrees")
    true_airspeed_kt: float = Field(gt=0, description="True airspeed in knots")
    wind_direction_deg: float = Field(
        ge=0, le=360, description="Direction the wind is blowing from, degrees true"
    )
    wind_speed_kt: float = Field(ge=0, description="Wind speed in knots")


class MagneticVariationRequest(Point):
    # Strict mode only accepts date objects, but JSON sends dates as ISO strings
    date: Date | None = Field(
        default=None, strict=False, description="ISO date (YYYY-MM-DD), defaults to today"
    )
    altitude_ft: float = Field(default=0, description="Altitude in feet")

    @field_validator("date", mode="before")
    @classmethod
    def date_must_be_string(cls, value):
        # Non-strict dates also accept Unix timestamps; only allow ISO strings
        if value is not None and not isinstance(value, str):
            raise ValueError("Date must be an ISO string (YYYY-MM-DD)")
        return value


class DeviationCardEntry(StrictModel):
    magnetic_heading_deg: float = Field(ge=0, lt=360, description="Heading on the card")
    correction_deg: float = Field(description="Steer minus for, in degrees")


class CompassHeadingRequest(WindTriangleRequest):
    variation_deg: float = Field(
        gt=-180, le=180, description="Magnetic variation, East positive / West negative"
    )
    deviation_card: list[DeviationCardEntry] = Field(
        min_length=1, description="Entries read off the aircraft's compass card"
    )
class TotalAirTimeRequest(StrictModel):
    power_setting: int = Field(ge=50, le=75, description="Power setting as a percentage (50-75)")
    usable_fuel_gallons: float = Field(gt=0, description="Usable fuel in gallons (non negative)")


# Responses -------------------------------------------------------------------

class PressureAltitudeResponse(BaseModel):
    pressure_altitude_ft: float


class DensityAltitudeResponse(BaseModel):
    density_altitude_ft: float


class RateOfClimbResponse(BaseModel):
    rate_of_climb_fpm: float


class TrueAirspeedResponse(BaseModel):
    true_airspeed_kt: float


class TakeoffDistanceResponse(BaseModel):
    ground_run_ft: float
    over_50_ft_obstacle_ft: float


class LandingDistanceResponse(BaseModel):
    ground_roll_ft: float
    over_50_ft_obstacle_ft: float


class RouteLeg(BaseModel):
    distance_nm: float
    true_course_deg: float


class RouteResponse(BaseModel):
    legs: list[RouteLeg]
    total_distance_nm: float


class TimeOfFlightResponse(BaseModel):
    leg_minutes: list[float]
    total_hours: float
    total_minutes: float


class ClimbResponse(BaseModel):
    time_to_climb_min: float
    distance_to_climb_nm: float


class TopOfDescentResponse(BaseModel):
    top_of_descent_nm: float


class WindTriangleResponse(BaseModel):
    wind_correction_angle_deg: float
    true_heading_deg: float
    ground_speed_kt: float


class MagneticVariationResponse(BaseModel):
    variation_deg: float


class CompassHeadingResponse(BaseModel):
    true_heading_deg: float
    magnetic_heading_deg: float
    deviation_deg: float
    compass_heading_deg: float

class TotalAirTimeResponse(BaseModel):
    total_air_time_minutes: float


class AirportResponse(BaseModel):
    icao: str
    latitude: float
    longitude: float


# Weather values are passed through from AviationWeather.gov as reported, so some are
# not plain numbers: wind direction can be "VRB" and visibility can be "10+".
class MetarResponse(BaseModel):
    icao: str | None
    name: str | None
    observed: str | None
    raw_text: str | None
    temp_c: float | None
    dewpoint_c: float | None
    wind_dir_deg: float | str | None
    wind_speed_kt: float | None
    wind_gust_kt: float | None
    visibility_sm: float | str | None
    altimeter_hpa: float | None
    flight_category: str | None
    clouds: list[dict]


class TafPeriod(BaseModel):
    from_: int | None = Field(alias="from")
    to: int | None
    change_type: str | None
    probability: int | None
    wind_dir_deg: float | str | None
    wind_speed_kt: float | None
    wind_gust_kt: float | None
    visibility_sm: float | str | None
    weather: str | None
    clouds: list[dict]


class TafResponse(BaseModel):
    icao: str | None
    name: str | None
    issued: str | None
    valid_from: int | None
    valid_to: int | None
    raw_text: str | None
    forecast: list[TafPeriod]


# Endpoints -------------------------------------------------------------------

@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Report that the API is running; no external services are contacted."""
    return {"status": "ok"}


@app.post(
    f"{CALCULATIONS}/pressure-altitude",
    response_model=PressureAltitudeResponse,
    tags=["calculations"],
)
def pressure_altitude(request: PressureAltitudeRequest) -> PressureAltitudeResponse:
    """Calculate pressure altitude from field elevation and altimeter setting."""
    return PressureAltitudeResponse(
        pressure_altitude_ft=calculate_pressure_altitude(
            request.altimeter_inhg,
            request.field_elevation_ft,
        )
    )


@app.post(
    f"{CALCULATIONS}/density-altitude",
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


@app.post(
    f"{CALCULATIONS}/rate-of-climb",
    response_model=RateOfClimbResponse,
    tags=["performance"],
)
def rate_of_climb(request: PerformanceRequest) -> RateOfClimbResponse:
    """Rate of climb from the Piper Cherokee chart at a density altitude."""
    return RateOfClimbResponse(
        rate_of_climb_fpm=calculate_rate_of_climb(request.density_altitude_ft)
    )


@app.post(
    f"{CALCULATIONS}/true-airspeed",
    response_model=TrueAirspeedResponse,
    tags=["performance"],
)
def true_airspeed(request: TrueAirspeedRequest) -> TrueAirspeedResponse:
    """True airspeed at a density altitude and power setting."""
    return TrueAirspeedResponse(
        true_airspeed_kt=calculate_true_air_speed(
            request.density_altitude_ft,
            request.power_percent,
        )
    )


@app.post(
    f"{CALCULATIONS}/takeoff-distance",
    response_model=TakeoffDistanceResponse,
    tags=["performance"],
)
def takeoff_distance(request: PerformanceRequest) -> TakeoffDistanceResponse:
    """Takeoff ground run and distance to clear a 50 ft obstacle."""
    ground_run, over_obstacle = calculate_takeoff_distance(request.density_altitude_ft)
    return TakeoffDistanceResponse(ground_run_ft=ground_run, over_50_ft_obstacle_ft=over_obstacle)


@app.post(
    f"{CALCULATIONS}/landing-distance",
    response_model=LandingDistanceResponse,
    tags=["performance"],
)
def landing_distance(request: PerformanceRequest) -> LandingDistanceResponse:
    """Landing ground roll and distance over a 50 ft obstacle."""
    ground_roll, over_obstacle = calculate_landing_distance(request.density_altitude_ft)
    return LandingDistanceResponse(ground_roll_ft=ground_roll, over_50_ft_obstacle_ft=over_obstacle)


@app.post(f"{CALCULATIONS}/route", response_model=RouteResponse, tags=["navigation"])
def route(request: RouteRequest) -> RouteResponse:
    """Great-circle distance and initial true course for each leg of a route."""
    points = [point.as_tuple() for point in request.points]
    legs = [
        RouteLeg(distance_nm=distance_nm(start, end), true_course_deg=bearing_deg(start, end))
        for start, end in zip(points, points[1:])
    ]
    return RouteResponse(legs=legs, total_distance_nm=sum(leg.distance_nm for leg in legs))


@app.post(
    f"{CALCULATIONS}/time-of-flight",
    response_model=TimeOfFlightResponse,
    tags=["navigation"],
)
def time_of_flight(request: TimeOfFlightRequest) -> TimeOfFlightResponse:
    """Time en route for each leg and for the whole route."""
    leg_hours = [
        _calculate(time_of_flight_hours, leg.distance_nm, leg.ground_speed_kt)
        for leg in request.legs
    ]
    total_hours = sum(leg_hours)
    return TimeOfFlightResponse(
        leg_minutes=[hours * 60 for hours in leg_hours],
        total_hours=total_hours,
        total_minutes=total_hours * 60,
    )


@app.post(f"{CALCULATIONS}/climb", response_model=ClimbResponse, tags=["performance"])
def climb(request: ClimbRequest) -> ClimbResponse:
    """Time and distance to the top of climb."""
    time_min = _calculate(
        time_to_climb_minutes,
        request.start_density_altitude_ft,
        request.cruise_density_altitude_ft,
    )
    return ClimbResponse(
        time_to_climb_min=time_min,
        distance_to_climb_nm=_calculate(distance_to_climb_nm, time_min, request.ground_speed_kt),
    )


@app.post(
    f"{CALCULATIONS}/top-of-descent",
    response_model=TopOfDescentResponse,
    tags=["performance"],
)
def top_of_descent(request: TopOfDescentRequest) -> TopOfDescentResponse:
    """Distance before the destination to start the descent."""
    return TopOfDescentResponse(
        top_of_descent_nm=_calculate(
            top_of_descent_nm,
            request.cruise_altitude_ft,
            request.destination_altitude_ft,
            request.ground_speed_kt,
            request.descent_rate_fpm,
        )
    )


@app.post(
    f"{CALCULATIONS}/wind-triangle",
    response_model=WindTriangleResponse,
    tags=["navigation"],
)
def wind_triangle(request: WindTriangleRequest) -> WindTriangleResponse:
    """Wind correction angle, true heading, and ground speed for a course."""
    args = (
        request.true_course_deg,
        request.true_airspeed_kt,
        request.wind_direction_deg,
        request.wind_speed_kt,
    )
    return WindTriangleResponse(
        wind_correction_angle_deg=_calculate(wind_correction_angle, *args),
        true_heading_deg=_calculate(true_heading, *args),
        ground_speed_kt=_calculate(ground_speed, *args),
    )


@app.post(
    f"{CALCULATIONS}/magnetic-variation",
    response_model=MagneticVariationResponse,
    tags=["navigation"],
)
def variation(request: MagneticVariationRequest) -> MagneticVariationResponse:
    """Magnetic variation from the World Magnetic Model (East positive)."""
    return MagneticVariationResponse(
        variation_deg=_calculate(
            magnetic_variation, request.as_tuple(), request.date, request.altitude_ft
        )
    )


@app.post(
    f"{CALCULATIONS}/compass-heading",
    response_model=CompassHeadingResponse,
    tags=["navigation"],
)
def compass(request: CompassHeadingRequest) -> CompassHeadingResponse:
    """True, magnetic, and compass headings: TC -> TH -> MH -> CH."""
    heading = _calculate(
        true_heading,
        request.true_course_deg,
        request.true_airspeed_kt,
        request.wind_direction_deg,
        request.wind_speed_kt,
    )
    mag_heading = _calculate(magnetic_course, heading, request.variation_deg)
    card = {entry.magnetic_heading_deg: entry.correction_deg for entry in request.deviation_card}
    deviation = _calculate(compass_deviation, mag_heading, card)
    return CompassHeadingResponse(
        true_heading_deg=heading,
        magnetic_heading_deg=mag_heading,
        deviation_deg=deviation,
        compass_heading_deg=(mag_heading + deviation) % 360,
    )

@app.post(
    f"{CALCULATIONS}/total-air-time",
    response_model=TotalAirTimeResponse,
    tags=["performance"],
)
def total_air_time_endpoint(request: TotalAirTimeRequest) -> TotalAirTimeResponse:
    """Calculate total air time based on power setting and usable fuel."""
    return TotalAirTimeResponse(
        total_air_time_minutes=_calculate(
            total_air_time, request.power_setting, request.usable_fuel_gallons
        )
    )


# Airport and weather endpoints -------------------------------------------------

@app.get(f"{AIRPORTS}/{{icao}}", response_model=AirportResponse, tags=["airports"])
def airport(icao: str = IcaoPath) -> AirportResponse:
    """Coordinates of an airport, for use with the route and magnetic variation endpoints."""
    try:
        latitude, longitude = get_airport_coordinates(icao)
    except AirportNotFoundError as error:
        raise _not_found(str(error))
    return AirportResponse(icao=icao.upper(), latitude=latitude, longitude=longitude)


@app.get(f"{WEATHER}/metar/{{icao}}", response_model=MetarResponse, tags=["weather"])
def metar(icao: str = IcaoPath) -> MetarResponse:
    """Current weather observation (METAR) from AviationWeather.gov."""
    return MetarResponse(**_fetch_weather(get_metar, icao))


@app.get(
    f"{WEATHER}/taf/{{icao}}",
    response_model=TafResponse,
    response_model_by_alias=True,
    tags=["weather"],
)
def taf(icao: str = IcaoPath) -> TafResponse:
    """Terminal forecast (TAF) from AviationWeather.gov."""
    return TafResponse(**_fetch_weather(get_taf, icao))
