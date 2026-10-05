"""
J.A.R.V.I.S. Real-Time Weather Subsystem
Fetches live weather and forecast data without requiring external API keys.
"""
from typing import Dict, Any, Optional
import requests
from core.utils.logger import log_info, log_error

class WeatherService:
    """Live weather and atmospheric condition query engine."""

    @staticmethod
    def get_current_weather(city: Optional[str] = None) -> Dict[str, Any]:
        """Fetch real-time atmospheric data."""
        try:
            target = f"https://wttr.in/{city if city else ''}?format=j1"
            headers = {"User-Agent": "curl/7.88.1"}
            res = requests.get(target, headers=headers, timeout=5)
            if res.status_code != 200:
                return {"error": "Unable to connect to meteorological services."}

            data = res.json()
            current = data.get("current_condition", [{}])[0]
            nearest_area = data.get("nearest_area", [{}])[0]

            location_name = city or nearest_area.get("areaName", [{}])[0].get("value", "your location")
            country = nearest_area.get("country", [{}])[0].get("value", "")
            temp_c = current.get("temp_C", "N/A")
            temp_f = current.get("temp_F", "N/A")
            feels_c = current.get("FeelsLikeC", "N/A")
            condition = current.get("weatherDesc", [{}])[0].get("value", "clear")
            humidity = current.get("humidity", "N/A")
            wind_speed = current.get("windspeedKmph", "N/A")

            speech = (
                f"Atmospheric conditions in {location_name} report {condition.lower()} "
                f"at {temp_c} degrees Celsius, feeling like {feels_c} degrees, "
                f"with {humidity} percent humidity, Sir."
            )

            return {
                "location": f"{location_name}, {country}".strip(", "),
                "condition": condition,
                "temp_c": temp_c,
                "temp_f": temp_f,
                "feels_like_c": feels_c,
                "humidity": f"{humidity}%",
                "wind": f"{wind_speed} km/h",
                "speech_text": speech
            }
        except Exception as e:
            log_error(f"Weather query failed: {e}")
            return {"error": str(e), "speech_text": "I am currently unable to retrieve the meteorological forecast, Sir."}
