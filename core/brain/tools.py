"""
J.A.R.V.I.S. Tool & Capability Registry
Defines functions the AI can execute to control macOS, media, and system utilities.
"""
from datetime import datetime
from typing import Dict, Any, Callable
from config import settings
from core.system.macos import (
    get_battery_status,
    get_system_volume,
    set_system_volume,
    launch_application,
    get_running_apps,
    get_quick_diagnostics,
)
from core.system.spotify import SpotifyController
from core.system.audio_player import StarkAudioPlayer

class ToolRegistry:
    """Registry of system actions callable by JARVIS."""

    @staticmethod
    def play_highway_to_hell() -> Dict[str, Any]:
        """Activate the Tony Stark Highway to Hell protocol."""
        return StarkAudioPlayer.play_highway_to_hell(volume=settings.spotify.default_volume)

    @staticmethod
    def spotify_control(action: str) -> Dict[str, Any]:
        """Control Spotify: 'play', 'pause', 'toggle', 'next', 'previous', or 'status'."""
        act = action.lower().strip()
        if act == "play":
            SpotifyController.play()
            return {"status": "resumed playback"}
        elif act == "pause":
            SpotifyController.pause()
            return {"status": "paused playback"}
        elif act in ("toggle", "playpause"):
            SpotifyController.toggle_play()
            return {"status": "toggled playback"}
        elif act in ("next", "skip"):
            SpotifyController.next_track()
            return {"status": "skipped to next track"}
        elif act in ("previous", "back"):
            SpotifyController.previous_track()
            return {"status": "skipped to previous track"}
        elif act in ("status", "current"):
            track = SpotifyController.get_current_track()
            return {"current_track": track or "No track playing"}
        return {"error": f"Unknown action '{action}'"}

    @staticmethod
    def get_battery() -> Dict[str, Any]:
        """Get power core / battery status and charging level."""
        return get_battery_status()

    @staticmethod
    def set_volume(level: int) -> Dict[str, Any]:
        """Set system acoustic volume between 0 and 100."""
        success = set_system_volume(level)
        return {"status": "success" if success else "failed", "volume": level}

    @staticmethod
    def get_volume() -> Dict[str, Any]:
        """Get current system volume level."""
        vol = get_system_volume()
        return {"volume": vol}

    @staticmethod
    def open_app(app_name: str) -> Dict[str, Any]:
        """Launch an application on macOS."""
        success = launch_application(app_name)
        return {"status": "launched" if success else "failed to launch", "app": app_name}

    @staticmethod
    def get_time_and_date() -> Dict[str, str]:
        """Get the current time, day, and date."""
        now = datetime.now()
        return {
            "time": now.strftime("%I:%M %p"),
            "date": now.strftime("%A, %B %d, %Y")
        }

    @staticmethod
    def get_system_telemetry() -> Dict[str, Any]:
        """Full diagnostic check of the host system."""
        return get_quick_diagnostics()

# Tool schemas for LLM Function Calling
TOOL_DEFINITIONS = [
    {
        "name": "play_highway_to_hell",
        "description": "Blasts AC/DC Highway to Hell on Spotify at 75% volume. Use when the user requests Highway to Hell, Stark protocol, or hype music.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "spotify_control",
        "description": "Controls Spotify playback. Actions: 'play', 'pause', 'toggle', 'next', 'previous', 'status'.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["play", "pause", "toggle", "next", "previous", "status"]}
            },
            "required": ["action"]
        }
    },
    {
        "name": "get_battery",
        "description": "Retrieves the Mac's battery percentage and charging state.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "set_volume",
        "description": "Adjusts the macOS master volume (0 to 100).",
        "parameters": {
            "type": "object",
            "properties": {
                "level": {"type": "integer", "description": "Volume percentage 0 to 100"}
            },
            "required": ["level"]
        }
    },
    {
        "name": "open_app",
        "description": "Opens an application by name (e.g. Safari, Terminal, Calculator, Spotify, Slack).",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {"type": "string", "description": "Name of application to launch"}
            },
            "required": ["app_name"]
        }
    },
    {
        "name": "get_time_and_date",
        "description": "Returns current time and date.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "get_system_telemetry",
        "description": "Returns quick system diagnostics including battery, volume, and running applications.",
        "parameters": {"type": "object", "properties": {}}
    }
]
