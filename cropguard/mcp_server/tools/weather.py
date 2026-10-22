from __future__ import annotations

import json
from urllib import error, parse, request


OFFLINE_WEATHER = {
    "tomato": "Warm and humid conditions favor fungal leaf diseases.",
    "wheat": "Cool to mild conditions can promote rust and mildew pressure.",
    "cotton": "Dry to moderate weather with dew can increase stress and disease risk."
}


def get_weather(location, days=3):
    if not location or not str(location).strip():
        return {"status": "error", "message": "Location is required."}

    city = str(location).strip()
    geocode_url = (
        "https://geocoding-api.open-meteo.com/v1/search?name="
        + parse.quote(city)
        + "&count=1&language=en&format=json"
    )
    try:
        with request.urlopen(geocode_url, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if not payload.get("results"):
            raise ValueError("Location not found")
        result = payload["results"][0]
        lat = result["latitude"]
        lon = result["longitude"]
        forecast_url = (
            "https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,precipitation&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
            "&timezone=auto&forecast_days={days}"
        ).format(lat=lat, lon=lon, days=days)
        with request.urlopen(forecast_url, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))

        current = data.get("current", {})
        temp = current.get("temperature_2m")
        humidity = current.get("relative_humidity_2m")
        precipitation = current.get("precipitation")
        summary = f"Current conditions in {city}: {temp}°C, {humidity}% humidity, {precipitation} mm rain."
        return {"status": "ok", "location": city, "summary": summary, "raw": data}
    except (error.URLError, ValueError, TimeoutError, json.JSONDecodeError):
        crop_hint = city.lower()
        weather_text = OFFLINE_WEATHER.get(crop_hint, "Local conditions are variable; field scouting is still recommended.")
        return {
            "status": "ok",
            "location": city,
            "summary": weather_text,
            "raw": {"offline": True},
        }
