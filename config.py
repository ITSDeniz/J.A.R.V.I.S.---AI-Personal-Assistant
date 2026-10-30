"""
J.A.R.V.I.S. System Configuration
Central configuration for all assistant subsystems.
"""
import json
from pathlib import Path
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
USER_SETTINGS_PATH = BASE_DIR / "assets" / "user_settings.json"

class SpotifyConfig(BaseModel):
    enabled: bool = True
    intro_song_name: str = "Highway to Hell - AC/DC"
    # Spotify Track URI for AC/DC - Highway to Hell (User's region-verified track)
    intro_song_uri: str = "spotify:track:2zYzyRzz6pRmhPzyfMEC8s"
    default_volume: int = 75

class VoiceConfig(BaseModel):
    # Microsoft Edge Neural British Voices:
    # "en-GB-RyanNeural" (Polite, crisp British male - authentic Jarvis style)
    # "en-GB-ThomasNeural" (Alternative British male)
    voice_name: str = "en-GB-RyanNeural"
    speech_rate: str = "+0%"
    speech_pitch: str = "+0Hz"
    speech_volume: str = "+0%"
    cache_dir: Path = BASE_DIR / "assets" / "cache"

class BrainConfig(BaseModel):
    provider: str = "ollama"  # "ollama" or "gemini"
    ollama_model: str = "llama3.2"
    ollama_url: str = "http://localhost:11434"
    system_prompt: str = (
        "You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), the iconic, sophisticated, "
        "and witty AI personal assistant originally created by Tony Stark. "
        "You address the user respectfully as 'Sir' or 'Boss'. "
        "Your responses are concise, cultured, exceptionally sharp, slightly sarcastic when appropriate, "
        "and always focused on efficiency. Never give generic long chatbot disclaimers."
    )

class JarvisSettings(BaseModel):
    assistant_name: str = "J.A.R.V.I.S."
    owner_name: str = "Sir"
    version: str = "1.0.0"
    play_boot_music: bool = True
    spotify: SpotifyConfig = Field(default_factory=SpotifyConfig)
    voice: VoiceConfig = Field(default_factory=VoiceConfig)
    brain: BrainConfig = Field(default_factory=BrainConfig)

    def load_user_overrides(self):
        """Load persistent user preferences from disk if present."""
        if USER_SETTINGS_PATH.exists():
            try:
                with open(USER_SETTINGS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if "play_boot_music" in data:
                    self.play_boot_music = bool(data["play_boot_music"])
            except Exception:
                pass

    def set_play_boot_music(self, enabled: bool):
        """Update and persist the boot music preference."""
        self.play_boot_music = enabled
        try:
            USER_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
            data = {}
            if USER_SETTINGS_PATH.exists():
                try:
                    with open(USER_SETTINGS_PATH, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    data = {}
            data["play_boot_music"] = enabled
            with open(USER_SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

# Global settings instance
settings = JarvisSettings()
settings.load_user_overrides()
