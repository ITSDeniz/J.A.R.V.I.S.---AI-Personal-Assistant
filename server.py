"""
J.A.R.V.I.S. HUD Web Server Launcher
Launches the holographic sci-fi dashboard on http://localhost:8000
"""
import sys
import time
import threading
import webbrowser
import uvicorn
from core.utils.logger import log_info, log_success, print_banner

def _open_browser_delayed(url: str):
    time.sleep(0.8)
    webbrowser.open(url)

def start_hud(port: int = 8000, open_browser: bool = True):
    print_banner()
    log_info(f"Initiating J.A.R.V.I.S. Tactical Holographic HUD on port {port}...")
    url = f"http://127.0.0.1:{port}"

    if open_browser:
        log_info(f"Opening HUD interface at {url}...")
        threading.Thread(target=_open_browser_delayed, args=(url,), daemon=True).start()

    log_success(f"HUD Server active. WebSocket gateway listening on {url}/ws")
    uvicorn.run("core.server.app:app", host="127.0.0.1", port=port, log_level="warning")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8000
    start_hud(port=port)
