"""
J.A.R.V.I.S. HUD Web Server Launcher
Launches the holographic sci-fi dashboard on http://localhost:8000
"""
import sys
import webbrowser
import uvicorn
from core.utils.logger import log_info, log_success, print_banner

def start_hud(port: int = 8000, open_browser: bool = True):
    print_banner()
    log_info(f"Initiating J.A.R.V.I.S. Tactical Holographic HUD on port {port}...")
    url = f"http://localhost:{port}"

    if open_browser:
        log_info(f"Opening HUD interface at {url}...")
        webbrowser.open(url)

    log_success(f"HUD Server active. WebSocket gateway listening on {url}/ws")
    uvicorn.run("core.server.app:app", host="0.0.0.0", port=port, log_level="warning")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8000
    start_hud(port=port)
