"""
J.A.R.V.I.S. System Configuration
Central configuration for all assistant subsystems.
"""
from pathlib import Path
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent

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
    spotify: SpotifyConfig = Field(default_factory=SpotifyConfig)
    voice: VoiceConfig = Field(default_factory=VoiceConfig)
    brain: BrainConfig = Field(default_factory=BrainConfig)

# Global settings instance
settings = JarvisSettings()
