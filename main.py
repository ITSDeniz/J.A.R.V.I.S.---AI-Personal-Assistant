"""
J.A.R.V.I.S. - Just A Rather Very Intelligent System
Main Application Entry Point (Part 2: Vocal Diagnostics & Stark Protocol)
"""
import sys
import time
from config import settings
from core.utils.logger import (
    console,
    print_banner,
    log_info,
    log_success,
    log_warning,
    log_error,
)
from core.system.macos import (
    get_battery_status,
    get_system_volume,
    set_system_volume,
    launch_application,
    get_running_apps,
    get_quick_diagnostics,
)
from core.system.spotify import SpotifyController
from core.voice import jarvis_voice, run_boot_sequence, generate_boot_speech
from rich.table import Table

def display_diagnostics():
    """Display real-time system diagnostics in a sci-fi table."""
    diag = get_quick_diagnostics()
    batt = get_battery_status()
    spotify_track = SpotifyController.get_current_track()

    table = Table(title="[bold cyan]SYSTEM TELEMETRY[/bold cyan]", border_style="cyan")
    table.add_column("Subsystem", style="bold white")
    table.add_column("Status", style="green")
    table.add_column("Details", style="dim white")

    # Battery
    batt_pct = batt.get("percentage")
    charging = "⚡ Charging" if batt.get("is_charging") else "🔋 On Battery"
    table.add_row(
        "Power Core",
        f"{batt_pct}%" if batt_pct is not None else "N/A",
        charging
    )

    # Master Volume
    vol = diag.get("volume")
    table.add_row("Acoustic Levels", f"{vol}%" if vol is not None else "Muted", "macOS CoreAudio")

    # Active Apps
    app_count = diag.get("running_apps", 0)
    table.add_row("Process Matrix", f"{app_count} apps active", "WindowServer OK")

    # Voice Engine
    table.add_row("Neural Voice", "[green]Online[/green]", f"{settings.voice.voice_name} (British)")

    # Spotify
    if SpotifyController.is_running():
        track_info = f"{spotify_track['name']} - {spotify_track['artist']}" if spotify_track else "Idle / Paused"
        table.add_row("Media Engine (Spotify)", "[green]Connected[/green]", track_info)
    else:
        table.add_row("Media Engine (Spotify)", "[yellow]Standby[/yellow]", "Not running")

    console.print(table)

def main():
    print_banner()
    log_info(f"Initializing {settings.assistant_name} v{settings.version}...")
    time.sleep(0.2)
    display_diagnostics()

    # CLI argument flags
    if "--boot" in sys.argv:
        play_music = "--music" in sys.argv
        run_boot_sequence(play_intro_song=play_music)
        return

    if "--test-stark" in sys.argv:
        jarvis_voice.speak("Initiating protocol: Highway to Hell.", block=True)
        SpotifyController.play_highway_to_hell(volume=settings.spotify.default_volume)
        log_success("Highway to Hell protocol triggered on Spotify.")
        return

    console.print("\n[bold cyan]─── AVAILABLE PROTOCOLS (PART 2: AUDIO ENABLED) ───[/bold cyan]")
    console.print("  [bold green]1[/bold green] -> [bold white]Tony Stark Full Boot Sequence[/bold white] (Vocal greeting + Highway to Hell)")
    console.print("  [bold green]2[/bold green] -> [bold white]Vocal Diagnostics Only[/bold white] (JARVIS speaks system report)")
    console.print("  [bold green]3[/bold green] -> [bold white]Custom Voice Test[/bold white] (Type text for JARVIS to speak)")
    console.print("  [bold green]4[/bold green] -> [bold white]Spotify Highway to Hell[/bold white] (Direct music launch)")
    console.print("  [bold green]5[/bold green] -> [bold white]Spotify Play/Pause Toggle[/bold white]")
    console.print("  [bold green]6[/bold green] -> [bold white]Spotify Next Track[/bold white]")
    console.print("  [bold green]7[/bold green] -> [bold white]Set Master Volume[/bold white]")
    console.print("  [bold green]8[/bold green] -> [bold white]Launch Application[/bold white]")
    console.print("  [bold green]9[/bold green] -> [bold white]Refresh Telemetry[/bold white]")
    console.print("  [bold red]q[/bold red] -> [bold white]Exit[/bold white]\n")

    while True:
        try:
            choice = console.input("[bold cyan]JARVIS > Select Protocol: [/bold cyan]").strip()
            if choice == "1":
                run_boot_sequence(play_intro_song=True)
            elif choice == "2":
                report = generate_boot_speech()
                jarvis_voice.speak(report)
            elif choice == "3":
                phrase = console.input("[bold cyan]Enter phrase to speak: [/bold cyan]").strip()
                if phrase:
                    jarvis_voice.speak(phrase)
            elif choice == "4":
                jarvis_voice.speak("Commencing audio playback, Sir.")
                res = SpotifyController.play_highway_to_hell(volume=settings.spotify.default_volume)
                log_success(f"Playing '{res['song']}' on Spotify!")
            elif choice == "5":
                SpotifyController.toggle_play()
                log_info("Toggled Spotify playback.")
            elif choice == "6":
                SpotifyController.next_track()
                log_info("Skipped to next track.")
            elif choice == "7":
                vol_str = console.input("[bold cyan]Enter volume (0-100): [/bold cyan]").strip()
                if vol_str.isdigit():
                    set_system_volume(int(vol_str))
                    jarvis_voice.speak(f"Master volume adjusted to {vol_str} percent, Sir.")
            elif choice == "8":
                app_name = console.input("[bold cyan]Enter app name: [/bold cyan]").strip()
                if app_name:
                    if launch_application(app_name):
                        jarvis_voice.speak(f"Opening {app_name}, Sir.")
                    else:
                        jarvis_voice.speak(f"I was unable to locate {app_name}, Sir.")
            elif choice == "9":
                display_diagnostics()
            elif choice.lower() in ("q", "exit", "quit"):
                jarvis_voice.speak(f"Standing down. Have a pleasant day, {settings.owner_name}.")
                break
        except KeyboardInterrupt:
            log_info("\nStanding down, Sir.")
            break

if __name__ == "__main__":
    main()
