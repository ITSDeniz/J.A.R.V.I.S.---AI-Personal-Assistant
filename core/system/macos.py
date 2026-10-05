"""
macOS System Control & Automation Subsystem
Native interaction with macOS via AppleScript and system utilities.
"""
import re
import subprocess
from typing import Dict, Any, Optional

def run_applescript(script: str) -> str:
    """Execute an AppleScript snippet and return the output."""
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"

def get_battery_status() -> Dict[str, Any]:
    """Retrieve current battery percentage and charging state."""
    try:
        output = subprocess.check_output(["pmset", "-g", "batt"], text=True)
        # Example output: "Now drawing from 'Battery Power'\n -InternalBattery-0 (id=...)  85%; discharging; ..."
        pct_match = re.search(r"(\d+)%", output)
        pct = int(pct_match.group(1)) if pct_match else None
        is_charging = "charging" in output.lower() and "discharging" not in output.lower()
        ac_power = "AC Power" in output
        return {
            "percentage": pct,
            "is_charging": is_charging,
            "on_ac_power": ac_power,
            "raw": output.strip()
        }
    except Exception as e:
        return {"error": str(e), "percentage": None}

def get_system_volume() -> Optional[int]:
    """Get output volume level (0-100)."""
    res = run_applescript("output volume of (get volume settings)")
    try:
        return int(res)
    except ValueError:
        return None

def set_system_volume(volume: int) -> bool:
    """Set output volume level between 0 and 100."""
    volume = max(0, min(100, volume))
    res = run_applescript(f"set volume output volume {volume}")
    return "Error" not in res

def set_system_muted(mute: bool = True) -> bool:
    """Mute or unmute system audio."""
    res = run_applescript(f"set volume output muted {'true' if mute else 'false'}")
    return "Error" not in res

def launch_application(app_name: str) -> bool:
    """Launch an installed macOS application."""
    try:
        subprocess.run(["open", "-a", app_name], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def quit_application(app_name: str) -> bool:
    """Gracefully quit a running macOS application."""
    script = f'tell application "{app_name}" to quit'
    res = run_applescript(script)
    return "Error" not in res

def get_running_apps() -> list[str]:
    """Get list of active visible applications on macOS."""
    script = 'tell application "System Events" to get name of (processes where background only is false)'
    res = run_applescript(script)
    if "Error" in res or not res:
        return []
    return [name.strip() for name in res.split(",")]

def get_quick_diagnostics() -> Dict[str, Any]:
    """Gather quick diagnostic telemetry of the Mac."""
    battery = get_battery_status()
    volume = get_system_volume()
    return {
        "battery": battery.get("percentage"),
        "charging": battery.get("is_charging"),
        "volume": volume,
        "running_apps": len(get_running_apps())
    }
