"""
J.A.R.V.I.S. - Just A Rather Very Intelligent System
Main Application Entry Point (Part 4: Microphone, Speech-to-Text & Wake Word Detection)
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
from core.voice import (
    jarvis_voice,
    run_boot_sequence,
    generate_boot_speech,
    jarvis_stt,
    jarvis_listener,
)
from core.brain import jarvis_agent
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

    # Audio IO
    table.add_row("Audio Input (Mic)", "[green]Online[/green]", "CoreAudio 16kHz VAD")
    table.add_row("Voice Output (TTS)", "[green]Online[/green]", f"{settings.voice.voice_name}")

    # Cognitive Engine
    table.add_row("Cognitive Core", "[green]Online[/green]", f"Dual-Engine ({settings.brain.provider.upper()})")

    # Spotify
    if SpotifyController.is_running():
        track_info = f"{spotify_track['name']} - {spotify_track['artist']}" if spotify_track else "Idle / Paused"
        table.add_row("Media Engine (Spotify)", "[green]Connected[/green]", track_info)
    else:
        table.add_row("Media Engine (Spotify)", "[yellow]Standby[/yellow]", "Not running")

    console.print(table)

def conversational_console():
    """Interactive conversational agent console."""
    console.print("\n[bold cyan]─── J.A.R.V.I.S. CONVERSATIONAL TERMINAL ───[/bold cyan]")
    console.print("[dim]Talk to JARVIS naturally. Type 'menu' for quick protocols or 'exit' to quit.[/dim]\n")

    while True:
        try:
            user_input = console.input("[bold green]Sir > [/bold green]").strip()
            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit", "q"):
                jarvis_voice.speak(f"Standing down. At your service whenever needed, {settings.owner_name}.")
                break

            if user_input.lower() == "menu":
                return True

            # Process command through agent
            jarvis_agent.process_command(user_input, speak_output=True)

        except KeyboardInterrupt:
            log_info("\nStanding down, Sir.")
            break
    return False

def push_to_talk_mode():
    """Push-to-Talk voice interface."""
    console.print("\n[bold cyan]─── PUSH-TO-TALK VOICE INTERFACE ───[/bold cyan]")
    console.print("[dim]Press [Enter] to start speaking. Say your command, then pause.[/dim]")
    console.print("[dim]Type 'q' and press Enter to return to menu.[/dim]\n")

    while True:
        try:
            prompt = console.input("[bold yellow]Press [Enter] to Speak (or 'q' to return): [/bold yellow]").strip()
            if prompt.lower() in ("q", "quit", "exit"):
                break

            jarvis_listener.listen_single_turn()
        except KeyboardInterrupt:
            break

def main():
    print_banner()
    log_info(f"Initializing {settings.assistant_name} v{settings.version}...")
    time.sleep(0.2)
    display_diagnostics()

    # CLI Flags
    if "--boot" in sys.argv:
        run_boot_sequence(play_intro_song="--music" in sys.argv)
        return

    if "--listen" in sys.argv:
        jarvis_listener.run_continuous_loop()
        return

    if "--voice" in sys.argv or "--push-to-talk" in sys.argv:
        push_to_talk_mode()
        return

    if "--command" in sys.argv:
        idx = sys.argv.index("--command")
        if idx + 1 < len(sys.argv):
            cmd = " ".join(sys.argv[idx + 1:])
            jarvis_agent.process_command(cmd, speak_output=True)
            return

    console.print("\n[bold cyan]─── AVAILABLE PROTOCOLS (PART 4: FULL VOICE LOOP) ───[/bold cyan]")
    console.print("  [bold green]1[/bold green] -> [bold white]Interactive AI Chat Terminal[/bold white] (Type naturally to JARVIS)")
    console.print("  [bold green]2[/bold green] -> [bold white]Push-to-Talk Microphone Mode[/bold white] (Press Enter & talk with your voice)")
    console.print("  [bold green]3[/bold green] -> [bold white]Hands-Free Wake Word Mode[/bold white] (Always listening for 'Hey Jarvis')")
    console.print("  [bold green]4[/bold green] -> [bold white]Tony Stark Full Boot Sequence[/bold white] (Greeting + Highway to Hell)")
    console.print("  [bold green]5[/bold green] -> [bold white]Spotify Play/Pause Toggle[/bold white]")
    console.print("  [bold green]6[/bold green] -> [bold white]Refresh System Telemetry[/bold white]")
    console.print("  [bold red]q[/bold red] -> [bold white]Exit[/bold white]\n")

    while True:
        try:
            choice = console.input("[bold cyan]JARVIS > Select Mode: [/bold cyan]").strip()
            if choice == "1":
                conversational_console()
            elif choice == "2":
                push_to_talk_mode()
            elif choice == "3":
                jarvis_listener.run_continuous_loop()
            elif choice == "4":
                run_boot_sequence(play_intro_song=True)
            elif choice == "5":
                SpotifyController.toggle_play()
                log_info("Toggled Spotify playback.")
            elif choice == "6":
                display_diagnostics()
            elif choice.lower() in ("q", "exit", "quit"):
                log_info("Standing by, Sir.")
                break
        except KeyboardInterrupt:
            log_info("\nStanding by, Sir.")
            break

if __name__ == "__main__":
    main()
