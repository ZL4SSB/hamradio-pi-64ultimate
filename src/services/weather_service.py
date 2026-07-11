"""Weather and Maidenhead locator services."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


class WeatherError(RuntimeError):
    """Weather configuration or request failure."""


@dataclass(frozen=True)
class Coordinates:
    """Geographic coordinates."""

    latitude: float
    longitude: float


@dataclass(frozen=True)
class CurrentWeather:
    """Current weather values displayed on the dashboard."""

    temperature: float | None
    description: str
    wind_speed: float | None
    humidity: float | None
    provider: str
    observed_time: str


WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    56: "Freezing drizzle",
    57: "Heavy freezing drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    66: "Freezing rain",
    67: "Heavy freezing rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Light showers",
    81: "Showers",
    82: "Heavy showers",
    85: "Light snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Severe thunderstorm with hail",
}


def maidenhead_to_coordinates(locator: str) -> Coordinates:
    """Convert a 2, 4, 6, or 8-character Maidenhead locator to its centre."""

    grid = locator.strip().upper()

    if len(grid) not in (2, 4, 6, 8):
        raise WeatherError(
            "Grid square must contain 2, 4, 6, or 8 characters."
        )

    if not ("A" <= grid[0] <= "R" and "A" <= grid[1] <= "R"):
        raise WeatherError(
            "The first two grid characters must be letters A to R."
        )

    longitude = -180.0 + (ord(grid[0]) - ord("A")) * 20.0
    latitude = -90.0 + (ord(grid[1]) - ord("A")) * 10.0
    longitude_size = 20.0
    latitude_size = 10.0

    if len(grid) >= 4:
        if not (grid[2].isdigit() and grid[3].isdigit()):
            raise WeatherError(
                "Grid characters 3 and 4 must be numbers."
            )

        longitude += int(grid[2]) * 2.0
        latitude += int(grid[3])
        longitude_size = 2.0
        latitude_size = 1.0

    if len(grid) >= 6:
        if not ("A" <= grid[4] <= "X" and "A" <= grid[5] <= "X"):
            raise WeatherError(
                "Grid characters 5 and 6 must be letters A to X."
            )

        longitude += (ord(grid[4]) - ord("A")) * (2.0 / 24.0)
        latitude += (ord(grid[5]) - ord("A")) * (1.0 / 24.0)
        longitude_size = 2.0 / 24.0
        latitude_size = 1.0 / 24.0

    if len(grid) >= 8:
        if not (grid[6].isdigit() and grid[7].isdigit()):
            raise WeatherError(
                "Grid characters 7 and 8 must be numbers."
            )

        longitude += int(grid[6]) * ((2.0 / 24.0) / 10.0)
        latitude += int(grid[7]) * ((1.0 / 24.0) / 10.0)
        longitude_size = (2.0 / 24.0) / 10.0
        latitude_size = (1.0 / 24.0) / 10.0

    return Coordinates(
        latitude=latitude + latitude_size / 2.0,
        longitude=longitude + longitude_size / 2.0,
    )


def resolve_coordinates(
    use_station_grid: bool,
    station_grid: str,
    exact_latitude: str,
    exact_longitude: str,
) -> Coordinates:
    """Resolve exact coordinates or derive them from a grid square."""

    if use_station_grid:
        if not station_grid.strip():
            raise WeatherError(
                "Enter a station grid square before using grid weather."
            )

        return maidenhead_to_coordinates(station_grid)

    try:
        latitude = float(str(exact_latitude).strip())
        longitude = float(str(exact_longitude).strip())
    except ValueError as error:
        raise WeatherError(
            "Enter valid numeric latitude and longitude."
        ) from error

    if not -90.0 <= latitude <= 90.0:
        raise WeatherError("Latitude must be between -90 and 90.")

    if not -180.0 <= longitude <= 180.0:
        raise WeatherError(
            "Longitude must be between -180 and 180."
        )

    return Coordinates(latitude, longitude)


def _request_json(url: str, timeout: int = 12) -> dict[str, Any]:
    """Request JSON using Python's standard library."""

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "HamRadio-Pi-Ultimate/0.3.5",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout,
        ) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise WeatherError(
            f"Weather provider returned HTTP {error.code}."
        ) from error
    except urllib.error.URLError as error:
        raise WeatherError(
            f"Weather service could not be reached: {error.reason}"
        ) from error
    except json.JSONDecodeError as error:
        raise WeatherError(
            "Weather provider returned invalid data."
        ) from error

    if not isinstance(data, dict):
        raise WeatherError(
            "Weather provider returned unexpected data."
        )

    return data


def fetch_open_meteo(coordinates: Coordinates) -> CurrentWeather:
    """Fetch current conditions from Open-Meteo."""

    query = urllib.parse.urlencode(
        {
            "latitude": f"{coordinates.latitude:.6f}",
            "longitude": f"{coordinates.longitude:.6f}",
            "current": (
                "temperature_2m,relative_humidity_2m,"
                "weather_code,wind_speed_10m"
            ),
            "timezone": "auto",
        }
    )

    data = _request_json(
        f"https://api.open-meteo.com/v1/forecast?{query}"
    )
    current = data.get("current")

    if not isinstance(current, dict):
        raise WeatherError(
            "Open-Meteo returned no current weather."
        )

    weather_code = current.get("weather_code")
    description = WEATHER_CODES.get(
        weather_code,
        "Current conditions",
    )

    return CurrentWeather(
        temperature=_as_float(current.get("temperature_2m")),
        description=description,
        wind_speed=_as_float(current.get("wind_speed_10m")),
        humidity=_as_float(current.get("relative_humidity_2m")),
        provider="Open-Meteo",
        observed_time=str(current.get("time", "")),
    )


def fetch_openweather(
    coordinates: Coordinates,
    api_key: str,
) -> CurrentWeather:
    """Fetch current conditions from OpenWeather."""

    key = api_key.strip()

    if not key:
        raise WeatherError("OpenWeather requires an API key.")

    query = urllib.parse.urlencode(
        {
            "lat": f"{coordinates.latitude:.6f}",
            "lon": f"{coordinates.longitude:.6f}",
            "appid": key,
            "units": "metric",
        }
    )

    data = _request_json(
        f"https://api.openweathermap.org/data/2.5/weather?{query}"
    )

    main = data.get("main")
    wind = data.get("wind")
    weather_items = data.get("weather")

    if not isinstance(main, dict):
        raise WeatherError(
            "OpenWeather returned no current weather."
        )

    description = "Current conditions"

    if (
        isinstance(weather_items, list)
        and weather_items
        and isinstance(weather_items[0], dict)
    ):
        description = str(
            weather_items[0].get(
                "description",
                description,
            )
        ).capitalize()

    return CurrentWeather(
        temperature=_as_float(main.get("temp")),
        description=description,
        wind_speed=(
            _as_float(wind.get("speed"))
            if isinstance(wind, dict)
            else None
        ),
        humidity=_as_float(main.get("humidity")),
        provider="OpenWeather",
        observed_time="",
    )


def fetch_current_weather(
    settings: dict[str, Any],
    station: dict[str, Any],
) -> CurrentWeather:
    """Fetch current weather using saved settings."""

    weather = settings.get("weather")

    if not isinstance(weather, dict):
        raise WeatherError(
            "Weather is not configured. Open Settings → Data Sources."
        )

    use_grid = bool(
        weather.get(
            "use_station_grid",
            True,
        )
    )
    grid = str(
        station.get("grid_square")
        or weather.get("grid_square")
        or ""
    )

    coordinates = resolve_coordinates(
        use_station_grid=use_grid,
        station_grid=grid,
        exact_latitude=str(weather.get("latitude", "")),
        exact_longitude=str(weather.get("longitude", "")),
    )

    provider = str(
        weather.get(
            "provider",
            "Open-Meteo",
        )
    )

    if provider == "OpenWeather":
        return fetch_openweather(
            coordinates,
            str(weather.get("api_key", "")),
        )

    return fetch_open_meteo(coordinates)


def format_weather_summary(weather: CurrentWeather) -> str:
    """Return a compact dashboard summary."""

    parts: list[str] = []

    if weather.temperature is not None:
        parts.append(f"{weather.temperature:.1f}°C")

    parts.append(weather.description)

    if weather.wind_speed is not None:
        unit = (
            "m/s"
            if weather.provider == "OpenWeather"
            else "km/h"
        )
        parts.append(f"wind {weather.wind_speed:.1f} {unit}")

    return " · ".join(parts)


def test_open_meteo(coordinates: Coordinates) -> str:
    """Test Open-Meteo and return readable details."""

    weather = fetch_open_meteo(coordinates)

    return (
        "Connection successful.\n\n"
        f"Latitude: {coordinates.latitude:.5f}\n"
        f"Longitude: {coordinates.longitude:.5f}\n"
        f"Weather: {format_weather_summary(weather)}"
    )


def test_openweather(
    coordinates: Coordinates,
    api_key: str,
) -> str:
    """Test OpenWeather and return readable details."""

    weather = fetch_openweather(
        coordinates,
        api_key,
    )

    return (
        "Connection successful.\n\n"
        f"Latitude: {coordinates.latitude:.5f}\n"
        f"Longitude: {coordinates.longitude:.5f}\n"
        f"Weather: {format_weather_summary(weather)}"
    )


def _as_float(value: Any) -> float | None:
    """Convert provider values to float when possible."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return None
