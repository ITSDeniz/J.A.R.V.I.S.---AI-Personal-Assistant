"""
J.A.R.V.I.S. Fast Intent Parser (Offline Fallback & Instant Actions)
Flexible semantic token and regex matching for natural language commands.
"""
import re
from typing import Optional, Tuple, Dict, Any
from core.brain.tools import ToolRegistry

class IntentParser:
    """Matches flexible natural language spoken/typed commands directly to tools."""

    @staticmethod
    def match(text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        t = text.lower().strip()

        # 1. Highway to Hell / Stark protocol
        if (
            ("highway" in t and "hell" in t)
            or any(k in t for k in ["stark protocol", "ac/dc", "acdc", "rock and roll", "suit up"])
            or ("play" in t and ("highway" in t or "acdc" in t or "ac/dc" in t))
        ):
            res = ToolRegistry.play_highway_to_hell()
            return (
                "Initiating the Tony Stark protocol. Blasting Highway to Hell, Sir.",
                res
            )

        # 2. Pause / Stop Music (Flexible matching: 'pause this music', 'stop the song', 'pause', etc.)
        pause_verbs = ["pause", "stop", "halt", "quiet", "silence", "shut off", "cut the", "kill the"]
        media_nouns = ["music", "song", "audio", "track", "spotify", "playing", "sound", "playback"]
        
        if (
            t in ["pause", "stop", "halt", "pause it", "stop it", "shut up"]
            or (any(v in t for v in pause_verbs) and any(m in t for m in media_nouns))
        ):
            res = ToolRegistry.spotify_control("pause")
            return ("Pausing playback, Sir.", res)

        # 3. Resume / Play Music
        resume_verbs = ["resume", "unpause", "continue", "start playing", "keep playing"]
        if (
            t in ["resume", "unpause", "continue", "play"]
            or any(v in t for v in resume_verbs)
            or ("play" in t and any(m in t for m in media_nouns) and not any(k in t for k in ["highway", "hell", "ac/dc"]))
        ):
            res = ToolRegistry.spotify_control("play")
            return ("Resuming playback, Sir.", res)

        # 4. Next / Skip Track
        if (
            t in ["next", "skip", "next song", "skip song", "next track", "skip track"]
            or ("next" in t and any(m in t for m in ["song", "track", "music", "one"]))
            or ("skip" in t and any(m in t for m in ["song", "track", "music", "this", "it", "one"]))
        ):
            res = ToolRegistry.spotify_control("next")
            return ("Skipping to the next track, Sir.", res)

        # 5. Previous Track
        if (
            t in ["previous", "back", "previous song", "go back", "last song"]
            or ("previous" in t and any(m in t for m in ["song", "track", "music", "one"]))
            or ("go back" in t or "play previous" in t)
        ):
            res = ToolRegistry.spotify_control("previous")
            return ("Returning to the previous track, Sir.", res)

        # 6. Current Song Status
        if any(k in t for k in ["what's playing", "what is playing", "current song", "current track", "what song", "which song"]):
            res = ToolRegistry.spotify_control("status")
            track = res.get("current_track")
            if isinstance(track, dict):
                return (f"Currently playing {track['name']} by {track['artist']}, Sir.", res)
            return ("No track appears to be currently playing, Sir.", res)

        # 7. Battery / Power (Matches 'battery', 'how much charge', 'power level', etc.)
        if any(k in t for k in ["battery", "power level", "power core", "charge", "power status"]):
            res = ToolRegistry.get_battery()
            pct = res.get("percentage")
            charging = res.get("is_charging")
            if pct is not None:
                state = "charging" if charging else "on battery power"
                return (f"Power levels are currently at {pct} percent, and the unit is {state}, Sir.", res)
            return ("Unable to retrieve power telemetry at this moment, Sir.", res)

        # 8. Master Acoustic Volume
        # e.g., 'set volume to 80', 'volume 50', 'turn volume to 75', 'make volume 40'
        vol_match = re.search(r"(?:volume|sound|audio).*?(\d+)", t) or re.search(r"(\d+)\s*(?:percent|%)\s*(?:volume|sound)?", t)
        if vol_match:
            val = int(vol_match.group(1))
            res = ToolRegistry.set_volume(val)
            return (f"Master acoustic levels adjusted to {val} percent, Sir.", res)

        if "mute" in t or "silence volume" in t:
            res = ToolRegistry.set_volume(0)
            return ("Acoustic output has been muted, Sir.", res)

        # 9. Weather & Forecast (Matches 'weather', 'forecast', 'temperature', 'how is the weather in Paris')
        if any(k in t for k in ["weather", "forecast", "temperature", "how hot", "how cold", "is it raining"]):
            city = None
            city_match = re.search(r"in\s+([a-zA-Z\s]+)", t) or re.search(r"for\s+([a-zA-Z\s]+)", t)
            if city_match:
                city = city_match.group(1).strip()
            res = ToolRegistry.get_weather(city)
            return (res.get("speech_text", "Atmospheric telemetry is unavailable, Sir."), res)

        # 10. Time & Date
        if any(k in t for k in ["time", "clock", "what's the time", "what time"]):
            res = ToolRegistry.get_time_and_date()
            return (f"The time is currently {res['time']}, Sir.", res)

        if any(k in t for k in ["date", "what day", "what's the date", "today's date"]):
            res = ToolRegistry.get_time_and_date()
            return (f"Today is {res['date']}, Sir.", res)

        # 11. Application Launching (Matches 'open safari', 'launch terminal', 'start chrome', etc.)
        open_match = re.search(r"(?:open|launch|start)\s+([a-zA-Z0-9\s]+)", t)
        if open_match and not any(k in t for k in ["music", "spotify", "highway", "volume", "sound", "track"]):
            app_target = open_match.group(1).strip()
            res = ToolRegistry.open_app(app_target)
            if res.get("status") == "launched":
                return (f"Opening {app_target} now, Sir.", res)
            return (f"I attempted to launch {app_target}, but could not find the executable, Sir.", res)

        # 12. System Diagnostics / Telemetry
        if any(k in t for k in ["diagnostics", "system status", "status report", "telemetry", "system check"]):
            res = ToolRegistry.get_system_telemetry()
            batt = res.get("battery", "unknown")
            apps = res.get("running_apps", 0)
            return (f"System report: Power core at {batt} percent. {apps} applications are currently running. All primary protocols operational.", res)

        return None
