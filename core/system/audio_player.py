"""
J.A.R.V.I.S. Audio Player & Media Subsystem
Plays local startup sounds or delegates to Spotify.
Enables zero-skip, zero-ad playback for the Tony Stark protocol.
"""
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from config import BASE_DIR, settings
from core.system.spotify import SpotifyController
from core.utils.logger import log_info, log_success

SOUNDS_DIR = BASE_DIR / "assets" / "sounds"
DEFAULT_INTRO_FILE = SOUNDS_DIR / "intro.mp3"

class StarkAudioPlayer:
    """Manages audio playback for Stark protocols and music."""

    _current_proc: Optional[subprocess.Popen] = None

    @classmethod
    def get_local_intro_path(cls) -> Optional[Path]:
        """Return path to existing local sound file in assets/sounds/."""
        if not SOUNDS_DIR.exists():
            return None
        # First priority: files matching highway or intro
        for ext in ("*.mp3", "*.wav", "*.m4a"):
            for f in SOUNDS_DIR.glob(ext):
                if any(k in f.name.lower() for k in ["highway", "hell", "intro", "stark"]):
                    return f
        # Second priority: any audio file found
        for ext in ("*.mp3", "*.wav", "*.m4a"):
            files = list(SOUNDS_DIR.glob(ext))
            if files:
                return files[0]
        return None

    @classmethod
    def has_local_intro(cls) -> bool:
        """Check if any local audio file exists."""
        return cls.get_local_intro_path() is not None

    @classmethod
    def play_local_file(cls, file_path: Path, volume: int = 75) -> bool:
        """Play local audio file non-blocking via native macOS CoreAudio afplay."""
        try:
            # Stop existing playback if any
            cls.stop_local_file()
            # afplay volume range: -v from 0 to 1 (or 0 to 2)
            vol_float = max(0.1, min(2.0, volume / 100.0 * 1.5))
            cls._current_proc = subprocess.Popen(["afplay", "-v", str(vol_float), str(file_path)])
            return True
        except Exception:
            return False

    @classmethod
    def stop_local_file(cls):
        """Stop local audio playback."""
        if cls._current_proc and cls._current_proc.poll() is None:
            cls._current_proc.terminate()
            cls._current_proc = None

    @classmethod
    def play_highway_to_hell(cls, volume: int = 75) -> Dict[str, Any]:
        """
        Executes Tony Stark Highway to Hell protocol:
        1. If local intro.mp3 is found, plays it directly (no ads, no skips).
        2. Otherwise, triggers Spotify playback.
        """
        local_file = cls.get_local_intro_path()
        if local_file:
            log_info(f"Playing local audio: {local_file.name}")
            success = cls.play_local_file(local_file, volume=volume)
            return {
                "status": "success" if success else "failed",
                "source": "local_file",
                "song": local_file.name,
                "volume": volume
            }
        else:
            log_info("Local intro.mp3 not found. Delegating to Spotify...")
            res = SpotifyController.play_highway_to_hell(volume=volume)
            res["source"] = "spotify"
            return res
