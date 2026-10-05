"""
J.A.R.V.I.S. - Just A Rather Very Intelligent System
Main Application Entry Point (Part 1: macOS & Spotify Automation Engine)
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
from rich.table import Table
from rich.panel import Panel

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
    time.sleep(0.3)
    display_diagnostics()

    console.print("\n[bold cyan]─── AVAILABLE PROTOCOLS (PART 1) ───[/bold cyan]")
    console.print("  [bold green]1[/bold green] -> [bold white]Tony Stark Protocol[/bold white] (Blast 'Highway to Hell' on Spotify)")
    console.print("  [bold green]2[/bold green] -> [bold white]Spotify Toggle[/bold white] (Play / Pause)")
    console.print("  [bold green]3[/bold green] -> [bold white]Spotify Next Track[/bold white]")
    console.print("  [bold green]4[/bold green] -> [bold white]Set System Volume[/bold white]")
    console.print("  [bold green]5[/bold green] -> [bold white]Launch Application[/bold white]")
    console.print("  [bold green]6[/bold green] -> [bold white]Refresh System Telemetry[/bold white]")
    console.print("  [bold red]q[/bold red] -> [bold white]Exit[/bold white]\n")

    if len(sys.argv) > 1 and sys.argv[1] == "--test-stark":
        log_info("Triggering Stark Protocol automatically...")
        result = SpotifyController.play_highway_to_hell(volume=settings.spotify.default_volume)
        log_success(f"Protocol executed: {result['song']} playing at {result['volume']}% volume.")
        return

    while True:
        try:
            choice = console.input("[bold cyan]JARVIS > Select Protocol: [/bold cyan]").strip()
            if choice == "1":
                log_info("Initiating Tony Stark protocol: Highway to Hell...")
                res = SpotifyController.play_highway_to_hell(volume=settings.spotify.default_volume)
                log_success(f"Playing '{res['song']}' on Spotify!")
            elif choice == "2":
                SpotifyController.toggle_play()
                log_info("Toggled Spotify playback.")
            elif choice == "3":
                SpotifyController.next_track()
                log_info("Skipped to next track.")
            elif choice == "4":
                vol_str = console.input("[bold cyan]Enter volume (0-100): [/bold cyan]").strip()
                if vol_str.isdigit():
                    set_system_volume(int(vol_str))
                    log_success(f"System volume set to {vol_str}%.")
            elif choice == "5":
                app_name = console.input("[bold cyan]Enter app name (e.g. Safari, Calculator): [/bold cyan]").strip()
                if app_name:
                    if launch_application(app_name):
                        log_success(f"Launched {app_name}.")
                    else:
                        log_error(f"Could not find or launch {app_name}.")
            elif choice == "6":
                display_diagnostics()
            elif choice.lower() in ("q", "exit", "quit"):
                log_info("Standing by, Sir. Have a pleasant day.")
                break
        except KeyboardInterrupt:
            log_info("\nStanding by, Sir.")
            break

if __name__ == "__main__":
    main()
