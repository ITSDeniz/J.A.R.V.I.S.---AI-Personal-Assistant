"""
J.A.R.V.I.S. Audio Boot Sequence & Stark Protocols
"""
import time
from datetime import datetime
from typing import Optional
from config import settings
from core.system.macos import get_battery_status, get_system_volume, get_running_apps
from core.system.weather import WeatherService
from core.system.spotify import SpotifyController
from core.system.audio_player import StarkAudioPlayer
from core.voice.tts import jarvis_voice
from core.utils.logger import log_info, log_success

def generate_boot_speech() -> str:
    """Generate comprehensive general status report based on real-time system state."""
    now = datetime.now()
    hour = now.hour

    if hour < 12:
        greeting = "Good morning"
    elif hour < 18:
        greeting = "Good afternoon"
    elif hour < 22:
        greeting = "Good evening"
    else:
        greeting = "Working late"

    time_str = now.strftime("%I:%M %p").lstrip("0")
    speech_parts = [f"{greeting}, {settings.owner_name}. The time is {time_str}."]

    # Real-time weather telemetry
    try:
        weather = WeatherService.get_current_weather()
        if weather and weather.get("temp_c") and weather.get("condition"):
            cond = weather["condition"].lower().replace("in area", "").strip()
            temp = weather["temp_c"]
            speech_parts.append(f"Atmospheric forecast reports {cond} at {temp} degrees Celsius.")
    except Exception:
        pass

    # Power core telemetry
    batt = get_battery_status()
    batt_pct = batt.get("percentage")
    charging = batt.get("is_charging")
    if batt_pct is not None:
        state = "charging" if charging else "on battery power"
        speech_parts.append(f"Power core is at {batt_pct} percent, {state}.")

    # Host process matrix
    try:
        apps = get_running_apps()
        if apps:
            speech_parts.append(f"{len(apps)} active applications detected.")
    except Exception:
        pass

    # Subsystems report
    speech_parts.append("All primary cognitive, acoustic, and tactical subsystems are fully operational. Ready for your instructions.")
    return " ".join(speech_parts)

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
        time.sleep(0.4)
        log_info("Initializing startup audio theme...")
        jarvis_voice.speak("Initiating startup theme: Highway to Hell.", block=True)
        StarkAudioPlayer.play_highway_to_hell(volume=settings.spotify.default_volume)
        log_success("Startup theme active.")
