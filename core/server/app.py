"""
J.A.R.V.I.S. Sci-Fi HUD Server & WebSocket Gateway
Serves the holographic dashboard and synchronizes real-time telemetry.
"""
import asyncio
import json
from pathlib import Path
from typing import Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from config import settings
from core.system.macos import (
    get_battery_status,
    get_system_volume,
    set_system_volume,
    get_running_apps,
    get_quick_diagnostics,
)
from core.system.spotify import SpotifyController
from core.system.audio_player import StarkAudioPlayer
from core.system.weather import WeatherService
from core.brain import jarvis_agent
from core.voice import jarvis_voice, run_boot_sequence, jarvis_stt

STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="J.A.R.V.I.S. HUD Gateway", version=settings.version)

# Active WebSocket connections
active_connections: Set[WebSocket] = set()

class CommandRequest(BaseModel):
    command: str

@app.get("/")
async def get_index():
    """Serve the primary Sci-Fi HUD interface."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return JSONResponse({"status": "JARVIS Core Online", "hud": "Static assets loading"})

@app.get("/api/telemetry")
async def get_telemetry():
    """Return live system telemetry data."""
    batt = get_battery_status()
    vol = get_system_volume()
    spotify_track = SpotifyController.get_current_track()
    weather = WeatherService.get_current_weather()
    
    is_local_playing = StarkAudioPlayer._current_proc is not None and StarkAudioPlayer._current_proc.poll() is None
    
    if is_local_playing:
        media_info = {
            "is_running": True,
            "track": {
                "name": "Highway To Hell",
                "artist": "AC/DC (Stark Protocol)",
                "state": "playing"
            }
        }
    elif spotify_track:
        media_info = {
            "is_running": SpotifyController.is_running(),
            "track": spotify_track
        }
    else:
        media_info = {
            "is_running": SpotifyController.is_running(),
            "track": {
                "name": "AC/DC - Highway To Hell",
                "artist": "Stark Protocol Standby",
                "state": "ready"
            }
        }

    return {
        "assistant_name": settings.assistant_name,
        "owner": settings.owner_name,
        "battery": batt,
        "volume": vol,
        "spotify": media_info,
        "weather": weather,
        "running_apps": len(get_running_apps()),
        "voice": settings.voice.voice_name
    }

@app.on_event("startup")
async def start_telemetry_heartbeat():
    """Continuously broadcast telemetry updates to connected clients every 1.5 seconds."""
    async def heartbeat():
        while True:
            await asyncio.sleep(1.5)
            if active_connections:
                try:
                    telem = await get_telemetry()
                    await broadcast_message({"type": "telemetry", "data": telem})
                except Exception:
                    pass
    asyncio.create_task(heartbeat())

@app.post("/api/command")
async def execute_command(req: CommandRequest):
    """Execute a text command and broadcast results."""
    res = jarvis_agent.process_command(req.command, speak_output=True)
    await broadcast_message({
        "type": "conversation",
        "user": req.command,
        "jarvis": res["text"]
    })
    return res

@app.post("/api/stark")
async def trigger_stark_protocol():
    """Initiate Tony Stark Highway to Hell protocol."""
    jarvis_voice.speak("Initiating protocol: Highway to Hell, Sir.", block=False)
    res = StarkAudioPlayer.play_highway_to_hell(volume=settings.spotify.default_volume)
    await broadcast_message({
        "type": "stark_protocol",
        "status": "active",
        "song": res.get("song", "Highway to Hell")
    })
    return res

@app.post("/api/spotify/{action}")
async def control_spotify(action: str):
    """Control music playback."""
    if action == "toggle":
        SpotifyController.toggle_play()
    elif action == "pause":
        StarkAudioPlayer.stop_local_file()
        SpotifyController.pause()
    elif action == "play":
        SpotifyController.play()
    elif action == "next":
        SpotifyController.next_track()
    elif action == "previous":
        SpotifyController.previous_track()
    return {"status": "ok", "action": action}

@app.post("/api/volume/{level}")
async def set_vol(level: int):
    """Set system audio volume."""
    set_system_volume(level)
    return {"status": "ok", "volume": level}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time bi-directional telemetry and command bridge."""
    await websocket.accept()
    active_connections.add(websocket)
    try:
        # Send initial telemetry snapshot
        telemetry = await get_telemetry()
        await websocket.send_json({"type": "telemetry", "data": telemetry})

        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            action = msg.get("action")

            if action == "command":
                cmd = msg.get("text", "")
                res = jarvis_agent.process_command(cmd, speak_output=True)
                await broadcast_message({
                    "type": "conversation",
                    "user": cmd,
                    "jarvis": res["text"]
                })
            elif action == "stark":
                res = StarkAudioPlayer.play_highway_to_hell(volume=settings.spotify.default_volume)
                await broadcast_message({"type": "stark_protocol", "data": res})
            elif action == "voice_input":
                # Trigger single-turn voice transcription from server mic
                cmd = jarvis_stt.listen_and_transcribe(prompt="Listening via HUD trigger...")
                if cmd:
                    res = jarvis_agent.process_command(cmd, speak_output=True)
                    await broadcast_message({
                        "type": "conversation",
                        "user": cmd,
                        "jarvis": res["text"]
                    })
            elif action == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception:
        if websocket in active_connections:
            active_connections.remove(websocket)

async def broadcast_message(message: dict):
    """Broadcast JSON message to all connected clients."""
    for conn in list(active_connections):
        try:
            await conn.send_json(message)
        except Exception:
            pass

# Mount static assets
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
