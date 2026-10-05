"""
J.A.R.V.I.S. Fast Intent Parser (Offline Fallback & Instant Actions)
Ensures zero-latency responses for system commands without network overhead.
"""
import re
from typing import Optional, Tuple, Dict, Any
from core.brain.tools import ToolRegistry

class IntentParser:
    """Matches common voice/text commands directly to tools with authentic Jarvis responses."""

    @staticmethod
    def match(text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        t = text.lower().strip()

        # Highway to Hell / Stark protocol
        if any(k in t for k in ["highway to hell", "stark protocol", "ac/dc", "acdc", "rock and roll", "suit up"]):
            res = ToolRegistry.play_highway_to_hell()
            return (
                "Initiating the Tony Stark protocol. Blasting Highway to Hell, Sir.",
                res
            )

        # Spotify / Music Controls
        if any(k in t for k in ["pause music", "stop music", "pause audio", "stop audio", "pause spotify", "hold the music"]):
            res = ToolRegistry.spotify_control("pause")
            return ("Pausing playback, Sir.", res)

        if any(k in t for k in ["resume music", "play music", "unpause", "continue music"]):
            res = ToolRegistry.spotify_control("play")
            return ("Resuming playback, Sir.", res)

        if any(k in t for k in ["next song", "next track", "skip song", "skip track"]):
            res = ToolRegistry.spotify_control("next")
            return ("Skipping to the next track, Sir.", res)

        if any(k in t for k in ["previous song", "previous track", "go back"]):
            res = ToolRegistry.spotify_control("previous")
            return ("Returning to the previous track, Sir.", res)

        if any(k in t for k in ["what's playing", "current song", "what song is this"]):
            res = ToolRegistry.spotify_control("status")
            track = res.get("current_track")
            if isinstance(track, dict):
                return (f"Currently playing {track['name']} by {track['artist']}, Sir.", res)
            return ("No track appears to be currently playing, Sir.", res)

        # Battery
        if any(k in t for k in ["battery", "power level", "power core", "charge level"]):
            res = ToolRegistry.get_battery()
            pct = res.get("percentage")
            charging = res.get("is_charging")
            if pct is not None:
                state = "charging" if charging else "on battery power"
                return (f"Power levels are currently at {pct} percent, and the unit is {state}, Sir.", res)
            return ("Unable to retrieve power telemetry at this moment, Sir.", res)

        # Volume
        vol_match = re.search(r"(?:set|change|turn)?\s*(?:volume|sound)\s*(?:to)?\s*(\d+)", t)
        if vol_match:
            val = int(vol_match.group(1))
            res = ToolRegistry.set_volume(val)
            return (f"Master acoustic levels adjusted to {val} percent, Sir.", res)

        if "mute" in t:
            res = ToolRegistry.set_volume(0)
            return ("Acoustic output has been muted, Sir.", res)

        # Weather & Forecast
        if any(k in t for k in ["weather", "forecast", "temperature", "how hot", "how cold", "is it raining"]):
            city = None
            city_match = re.search(r"in\s+([a-zA-Z\s]+)", t)
            if city_match:
                city = city_match.group(1).strip()
            res = ToolRegistry.get_weather(city)
            return (res.get("speech_text", "Atmospheric telemetry is unavailable, Sir."), res)

        # Time & Date
        if any(k in t for k in ["what time", "current time", "what's the time"]):
            res = ToolRegistry.get_time_and_date()
            return (f"The time is currently {res['time']}, Sir.", res)

        if any(k in t for k in ["what date", "today's date", "what day is it"]):
            res = ToolRegistry.get_time_and_date()
            return (f"Today is {res['date']}, Sir.", res)

        # App Launching
        open_match = re.search(r"(?:open|launch|start)\s+([a-zA-Z0-9\s]+)", t)
        if open_match and not any(k in t for k in ["music", "spotify", "highway", "volume"]):
            app_target = open_match.group(1).strip()
            res = ToolRegistry.open_app(app_target)
            if res.get("status") == "launched":
                return (f"Opening {app_target} now, Sir.", res)
            return (f"I attempted to launch {app_target}, but could not find the executable, Sir.", res)

        # System Diagnostics
        if any(k in t for k in ["diagnostics", "system status", "status report", "telemetry"]):
            res = ToolRegistry.get_system_telemetry()
            batt = res.get("battery", "unknown")
            apps = res.get("running_apps", 0)
            return (f"System report: Power core at {batt} percent. {apps} applications are currently running. All primary protocols operational.", res)

        return None
