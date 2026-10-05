"""
J.A.R.V.I.S. Wake Word & Hands-Free Audio Listener
Continuously monitors microphone for 'Hey Jarvis' or runs push-to-talk.
"""
import re
import time
import threading
from typing import Optional, Callable
from config import settings
from core.voice.stt import jarvis_stt
from core.voice.tts import jarvis_voice
from core.brain import jarvis_agent
from core.utils.logger import log_info, log_success, log_warning, console

WAKE_WORDS = ["hey jarvis", "jarvis", "ok jarvis", "okay jarvis", "hi jarvis"]

class WakeWordListener:
    """Hands-free wake word detector and continuous voice loop."""

    def __init__(self):
        self.is_running = False
        self._thread: Optional[threading.Thread] = None

    @staticmethod
    def extract_wake_command(text: str) -> Optional[str]:
        """
        Check if speech contains a wake phrase.
        If it contains a command after the wake word (e.g. 'Jarvis play Highway to Hell'),
        returns the command ('play Highway to Hell').
        If it's just 'Hey Jarvis', returns empty string '' indicating wake-up.
        If not addressed to Jarvis, returns None.
        """
        t = text.lower().strip()
        for wake in WAKE_WORDS:
            if t.startswith(wake):
                cmd = t[len(wake):].strip(" ,.:;!")
                return cmd
            elif wake in t:
                idx = t.find(wake)
                cmd = t[idx + len(wake):].strip(" ,.:;!")
                return cmd
        return None

    def listen_single_turn(self):
        """Prompt user, record voice, and process through JarvisAgent."""
        cmd = jarvis_stt.listen_and_transcribe(prompt="Listening, Sir...")
        if not cmd:
            log_warning("No speech detected.")
            return

        # Execute through Jarvis agent
        jarvis_agent.process_command(cmd, speak_output=True)

    def run_continuous_loop(self):
        """Continuous background listening loop for wake word."""
        self.is_running = True
        log_success(f"Wake word listener online. Say [bold green]'Hey Jarvis'[/bold green] anytime.")

        while self.is_running:
            try:
                # Listen for speech
                speech = jarvis_stt.listen_and_transcribe(prompt="Awaiting 'Hey Jarvis'...")
                if not speech:
                    continue

                wake_cmd = self.extract_wake_command(speech)
                if wake_cmd is not None:
                    console.print(f"[bold cyan]⚡ [WAKE DETECTED][/bold cyan] Heard: \"{speech}\"")

                    if wake_cmd:
                        # User said command together with wake word
                        jarvis_agent.process_command(wake_cmd, speak_output=True)
                    else:
                        # User only said 'Hey Jarvis'
                        jarvis_voice.speak(f"Yes, {settings.owner_name}?")
                        time.sleep(0.2)
                        next_cmd = jarvis_stt.listen_and_transcribe(prompt="Ready for your command, Sir...")
                        if next_cmd:
                            jarvis_agent.process_command(next_cmd, speak_output=True)
                        else:
                            jarvis_voice.speak("Standing by, Sir.")

            except Exception as e:
                time.sleep(0.5)

    def start_background(self):
        """Start listener in a dedicated background daemon thread."""
        if not self.is_running:
            self._thread = threading.Thread(target=self.run_continuous_loop, daemon=True)
            self._thread.start()

    def stop(self):
        """Stop background listening."""
        self.is_running = False

# Global listener instance
jarvis_listener = WakeWordListener()
