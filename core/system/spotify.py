"""
Spotify Automation Engine for macOS
Controls Spotify playback, tracks, and the iconic 'Highway to Hell' protocol.
"""
from typing import Dict, Any, Optional
from core.system.macos import run_applescript

HIGHWAY_TO_HELL_URI = "spotify:track:2zYzyRzz6Ye8jC9ot8JWHd"

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
    def play_track(track_uri: str) -> bool:
        """Play a specific Spotify track by URI."""
        SpotifyController.launch()
        script = f'tell application "Spotify" to play track "{track_uri}"'
        res = run_applescript(script)
        return "Error" not in res

    @staticmethod
    def play_highway_to_hell(volume: int = 75) -> Dict[str, Any]:
        """
        Tony Stark Protocol:
        Launches Spotify, sets volume, and blasts AC/DC's Highway to Hell.
        """
        SpotifyController.launch()
        SpotifyController.set_volume(volume)
        success = SpotifyController.play_track(HIGHWAY_TO_HELL_URI)
        return {
            "status": "success" if success else "failed",
            "song": "Highway to Hell - AC/DC",
            "volume": volume,
            "uri": HIGHWAY_TO_HELL_URI
        }

    @staticmethod
    def play() -> bool:
        """Resume playback."""
        script = 'tell application "Spotify" to play'
        return "Error" not in run_applescript(script)

    @staticmethod
    def pause() -> bool:
        """Pause playback."""
        script = 'tell application "Spotify" to pause'
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
        """Get details about the currently playing track."""
        if not SpotifyController.is_running():
            return None
        
        script = '''
        tell application "Spotify"
            if player state is stopped then
                return "stopped"
            end if
            set trackName to name of current track
            set artistName to artist of current track
            set albumName to album of current track
            set playerStatus to player state as string
            return trackName & "|||" & artistName & "|||" & albumName & "|||" & playerStatus
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
