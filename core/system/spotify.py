"""
Spotify Automation Engine for macOS
Controls Spotify playback, tracks, and the iconic 'Highway to Hell' protocol.
"""
import re
from typing import Dict, Any, Optional
from config import settings
from core.system.macos import run_applescript

class SpotifyController:
    """Controls Spotify on macOS via native AppleScript."""

    @staticmethod
    def is_running() -> bool:
        """Check if Spotify is currently running."""
        script = 'tell application "System Events" to (name of processes) contains "Spotify"'
        return run_applescript(script).lower() == "true"

    @staticmethod
    def launch() -> bool:
        """Launch Spotify application."""
        script = 'tell application "Spotify" to activate'
        res = run_applescript(script)
        return "Error" not in res

    @staticmethod
    def normalize_uri(track_input: str) -> str:
        """Convert Spotify URL or URI into a clean spotify:track:URI format."""
        track_input = track_input.strip()
        # If web URL: https://open.spotify.com/track/2zYzyRzz6pRmhPzyfMEC8s?si=...
        url_match = re.search(r"spotify\.com/track/([a-zA-Z0-9]+)", track_input)
        if url_match:
            return f"spotify:track:{url_match.group(1)}"
        return track_input

    @staticmethod
    def play_track(track_uri: str) -> bool:
        """Play a specific Spotify track by URI or URL."""
        SpotifyController.launch()
        uri = SpotifyController.normalize_uri(track_uri)
        script = f'''
        tell application "Spotify"
            activate
            play track "{uri}"
        end tell
        '''
        res = run_applescript(script)
        return "Error" not in res

    @staticmethod
    def play_highway_to_hell(volume: int = 75) -> Dict[str, Any]:
        """
        Tony Stark Protocol:
        Launches Spotify, sets volume, and blasts AC/DC's Highway to Hell.
        """
        uri = settings.spotify.intro_song_uri
        SpotifyController.launch()
        SpotifyController.set_volume(volume)
        success = SpotifyController.play_track(uri)
        return {
            "status": "success" if success else "failed",
            "song": settings.spotify.intro_song_name,
            "volume": volume,
            "uri": uri
        }

    @staticmethod
    def play() -> bool:
        """Resume playback."""
        script = 'tell application "Spotify" to play'
        return "Error" not in run_applescript(script)

    @staticmethod
    def pause() -> bool:
        """Pause playback safely if Spotify is running."""
        script = '''
        tell application "System Events"
            set isRunning to (name of processes) contains "Spotify"
        end tell
        if isRunning then
            tell application "Spotify"
                try
                    if player state is playing then
                        pause
                    end if
                on error
                    pause
                end try
            end tell
        end if
        '''
        return "Error" not in run_applescript(script)

    @staticmethod
    def toggle_play() -> bool:
        """Toggle play/pause."""
        script = 'tell application "Spotify" to playpause'
        return "Error" not in run_applescript(script)

    @staticmethod
    def next_track() -> bool:
        """Skip to next track."""
        script = 'tell application "Spotify" to next track'
        return "Error" not in run_applescript(script)

    @staticmethod
    def previous_track() -> bool:
        """Return to previous track."""
        script = 'tell application "Spotify" to previous track'
        return "Error" not in run_applescript(script)

    @staticmethod
    def set_volume(volume: int) -> bool:
        """Set Spotify sound volume (0-100)."""
        volume = max(0, min(100, volume))
        script = f'tell application "Spotify" to set sound volume to {volume}'
        return "Error" not in run_applescript(script)

    @staticmethod
    def get_current_track() -> Optional[Dict[str, str]]:
        """Get details about the currently playing track safely."""
        if not SpotifyController.is_running():
            return None
        
        script = '''
        tell application "Spotify"
            try
                if player state is stopped then
                    return "stopped"
                end if
                set trackName to name of current track
                set artistName to artist of current track
                set albumName to album of current track
                set playerStatus to player state as string
                return trackName & "|||" & artistName & "|||" & albumName & "|||" & playerStatus
            on error
                return "stopped"
            end try
        end tell
        '''
        res = run_applescript(script)
        if "Error" in res or not res or res == "stopped":
            return None
        
        parts = res.split("|||")
        if len(parts) >= 4:
            return {
                "name": parts[0].strip(),
                "artist": parts[1].strip(),
                "album": parts[2].strip(),
                "state": parts[3].strip()
            }
        return None
