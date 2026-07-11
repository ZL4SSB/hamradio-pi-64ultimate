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
    latitude: float
    longitude: float


def maidenhead_to_coordinates(locator: str) -> Coordinates:
    grid = locator.strip().upper()

    if len(grid) not in (2, 4, 6, 8):
        raise WeatherError("Grid square must contain 2, 4, 6, or 8 characters.")

    if not ("A" <= grid[0] <= "R" and "A" <= grid[1] <= "R"):
        raise WeatherError("The first two grid characters must be letters A to R.")

    longitude = -180.0 + (ord(grid[0]) - ord("A")) * 20.0
    latitude = -90.0 + (ord(grid[1]) - ord("A")) * 10.0
    longitude_size = 20.0
    latitude_size = 10.0

    if len(grid) >= 4:
        if not (grid[2].isdigit() and grid[3].isdigit()):
            raise WeatherError("Grid characters 3 and 4 must be numbers.")
        longitude += int(grid[2]) * 2.0
        latitude += int(grid[3]) * 1.0
        longitude_size = 2.0
        latitude_size = 1.0

    if len(grid) >= 6:
        if not ("A" <= grid[4] <= "X" and "A" <= grid[5] <= "X"):
            raise WeatherError("Grid characters 5 and 6 must be letters A to X.")
        longitude += (ord(grid[4]) - ord("A")) * (2.0 / 24.0)
        latitude += (ord(grid[5]) - ord("A")) * (1.0 / 24.0)
        longitude_size = 2.0 / 24.0
        latitude_size = 1.0 / 24.0

    if len(grid) >= 8:
        if not (grid[6].isdigit() and grid[7].isdigit()):
            raise WeatherError("Grid characters 7 and 8 must be numbers.")
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
    if use_station_grid:
        if not station_grid.strip():
            raise WeatherError("Enter a station grid square first.")
        return maidenhead_to_coordinates(station_grid)

    try:
        latitude = float(exact_latitude.strip())
        longitude = float(exact_longitude.strip())
    except ValueError as error:
        raise WeatherError("Enter valid numeric latitude and longitude.") from error

    if not -90 <= latitude <= 90:
        raise WeatherError("Latitude must be between -90 and 90.")
    if not -180 <= longitude <= 180:
        raise WeatherError("Longitude must be between -180 and 180.")

    return Coordinates(latitude, longitude)


def _request_json(url: str, timeout: int = 12) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "HamRadio-Pi-Ultimate/0.3.4",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise WeatherError(f"Weather provider returned HTTP {error.code}.") from error
    except urllib.error.URLError as error:
        raise WeatherError(f"Weather service could not be reached: {error.reason}") from error
    except json.JSONDecodeError as error:
        raise WeatherError("Weather provider returned invalid data.") from error

    if not isinstance(data, dict):
        raise WeatherError("Weather provider returned unexpected data.")
    return data


def test_open_meteo(coordinates: Coordinates) -> str:
    query = urllib.parse.urlencode({
        "latitude": f"{coordinates.latitude:.6f}",
        "longitude": f"{coordinates.longitude:.6f}",
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "timezone": "auto",
    })
    data = _request_json(f"https://api.open-meteo.com/v1/forecast?{query}")
    current = data.get("current")
    if not isinstance(current, dict):
        raise WeatherError("Open-Meteo returned no current weather.")

    return (
        "Connection successful.\n\n"
        f"Latitude: {coordinates.latitude:.5f}\n"
        f"Longitude: {coordinates.longitude:.5f}\n"
        f"Temperature: {current.get('temperature_2m', '?')} °C\n"
        f"Humidity: {current.get('relative_humidity_2m', '?')} %\n"
        f"Wind: {current.get('wind_speed_10m', '?')} km/h"
    )


def test_openweather(coordinates: Coordinates, api_key: str) -> str:
    key = api_key.strip()
    if not key:
        raise WeatherError("OpenWeather requires an API key.")

    query = urllib.parse.urlencode({
        "lat": f"{coordinates.latitude:.6f}",
        "lon": f"{coordinates.longitude:.6f}",
        "appid": key,
        "units": "metric",
    })
    data = _request_json(f"https://api.openweathermap.org/data/2.5/weather?{query}")
    main = data.get("main")
    wind = data.get("wind")
    if not isinstance(main, dict):
        raise WeatherError("OpenWeather returned no current weather.")

    return (
        "Connection successful.\n\n"
        f"Temperature: {main.get('temp', '?')} °C\n"
        f"Humidity: {main.get('humidity', '?')} %\n"
        f"Wind: {wind.get('speed', '?') if isinstance(wind, dict) else '?'} m/s"
    )
