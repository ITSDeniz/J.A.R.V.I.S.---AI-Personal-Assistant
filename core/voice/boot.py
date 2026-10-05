"""
J.A.R.V.I.S. Audio Boot Sequence & Stark Protocols
"""
import time
from typing import Optional
from config import settings
from core.system.macos import get_battery_status, get_system_volume
from core.system.spotify import SpotifyController
from core.voice.tts import jarvis_voice
from core.utils.logger import log_info, log_success

def generate_boot_speech() -> str:
    """Generate dynamic greeting based on current real-time system state."""
    batt = get_battery_status()
    batt_pct = batt.get("percentage")
    charging = batt.get("is_charging")

    speech = f"At your service, {settings.owner_name}. All primary systems are online. "
    
    if batt_pct is not None:
        if charging:
            speech += f"Power cells are charging at {batt_pct} percent. "
        else:
            speech += f"Power cells at {batt_pct} percent. "
            
    if SpotifyController.is_running():
        speech += "Spotify media engine is connected and standing by. "
    else:
        speech += "All internal diagnostics report green. "

    speech += "Ready for your command."
    return speech

def run_boot_sequence(play_intro_song: bool = False):
    """
    Executes the full Stark audio boot sequence.
    Speaks diagnostic greeting, then optionally blasts Highway to Hell.
    """
    log_info("Executing J.A.R.V.I.S. vocal boot sequence...")
    greeting = generate_boot_speech()
    
    # Speak greeting through neural voice
    jarvis_voice.speak(greeting, block=True)
    
    if play_intro_song:
        time.sleep(0.5)
        log_info("Initializing Tony Stark music protocol...")
        jarvis_voice.speak("Initiating protocol: Highway to Hell.", block=True)
        SpotifyController.play_highway_to_hell(volume=settings.spotify.default_volume)
        log_success("Music protocol active.")
