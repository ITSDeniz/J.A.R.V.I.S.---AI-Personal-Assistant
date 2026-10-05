"""
J.A.R.V.I.S. Neural Voice Engine (Text-to-Speech)
Produces high-fidelity British assistant voice using Edge Neural TTS.
Features audio caching for near-zero latency on common phrases.
"""
import asyncio
import hashlib
import os
import subprocess
from pathlib import Path
from typing import Optional
import edge_tts
from config import settings
from core.utils.logger import log_jarvis_speak, log_info, log_error

class VoiceEngine:
    """Neural Text-to-Speech engine tailored for JARVIS."""

    def __init__(self, voice_name: Optional[str] = None):
        self.voice_name = voice_name or settings.voice.voice_name
        self.cache_dir = settings.voice.cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._current_process: Optional[subprocess.Popen] = None

    def _get_cache_path(self, text: str) -> Path:
        """Generate a deterministic file path based on voice and text hash."""
        text_hash = hashlib.md5(f"{self.voice_name}:{text.strip()}".encode("utf-8")).hexdigest()
        return self.cache_dir / f"{text_hash}.mp3"

    async def synthesize(self, text: str, output_path: Path) -> bool:
        """Synthesize text into an audio file asynchronously."""
        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=self.voice_name,
                rate=settings.voice.speech_rate,
                pitch=settings.voice.speech_pitch,
                volume=settings.voice.speech_volume
            )
            await communicate.save(str(output_path))
            return True
        except Exception as e:
            log_error(f"TTS synthesis failure: {e}")
            return False

    def play_audio(self, audio_path: Path, block: bool = True) -> bool:
        """Play audio file via native macOS afplay utility."""
        if not audio_path.exists():
            return False
        try:
            if block:
                subprocess.run(["afplay", str(audio_path)], check=True)
            else:
                self._current_process = subprocess.Popen(["afplay", str(audio_path)])
            return True
        except Exception as e:
            log_error(f"Audio playback error: {e}")
            return False

    def stop_audio(self):
        """Immediately interrupt current speech playback."""
        if self._current_process and self._current_process.poll() is None:
            self._current_process.terminate()
            self._current_process = None

    async def speak_async(self, text: str, block: bool = True) -> bool:
        """
        Synthesizes (or loads from cache) and speaks the given text out loud.
        """
        text = text.strip()
        if not text:
            return False

        log_jarvis_speak(text)
        cache_file = self._get_cache_path(text)

        # Use cached audio if available, otherwise synthesize
        if not cache_file.exists():
            success = await self.synthesize(text, cache_file)
            if not success:
                return False

        # Play audio via macOS CoreAudio afplay
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.play_audio, cache_file, block)

    def speak(self, text: str, block: bool = True) -> bool:
        """Synchronous wrapper for speech synthesis and playback."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already running inside an active async event loop
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(asyncio.run, self.speak_async(text, block)).result()
            else:
                return loop.run_until_complete(self.speak_async(text, block))
        except RuntimeError:
            return asyncio.run(self.speak_async(text, block))

# Global voice engine instance
jarvis_voice = VoiceEngine()
