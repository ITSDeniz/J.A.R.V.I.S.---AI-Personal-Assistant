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
        """Synthesize text into an audio file atomically to avoid corrupt 0-byte cache entries."""
        tmp_path = output_path.with_suffix(".tmp")
        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=self.voice_name,
                rate=settings.voice.speech_rate,
                pitch=settings.voice.speech_pitch,
                volume=settings.voice.speech_volume
            )
            await communicate.save(str(tmp_path))
            if not tmp_path.exists() or tmp_path.stat().st_size == 0:
                raise RuntimeError("Synthesized audio file is empty")
            tmp_path.replace(output_path)
            return True
        except Exception as e:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
            log_error(f"TTS synthesis failure: {e}")
            return False

    def _speak_macos_fallback(self, text: str, block: bool = True) -> bool:
        """Fallback to native macOS 'say' if cloud neural TTS is unavailable."""
        try:
            cmd = ["say", "-v", "Daniel", text]
            if block:
                res = subprocess.run(cmd, capture_output=True)
                if res.returncode != 0:
                    subprocess.run(["say", text], check=True)
            else:
                self._current_process = subprocess.Popen(cmd)
            return True
        except Exception as e:
            log_error(f"Fallback speech error: {e}")
            return False

    def play_audio(self, audio_path: Path, block: bool = True) -> bool:
        """Play audio file via native macOS afplay utility."""
        if not audio_path.exists() or audio_path.stat().st_size == 0:
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

    async def _ensure_cached(self, text: str) -> Optional[Path]:
        """Return a valid cached audio path for text, synthesizing if missing or empty."""
        cache_file = self._get_cache_path(text)
        if not cache_file.exists() or cache_file.stat().st_size == 0:
            if cache_file.exists():
                cache_file.unlink(missing_ok=True)
            if not await self.synthesize(text, cache_file):
                return None
        return cache_file

    def prepare(self, text: str) -> bool:
        """Pre-synthesize and cache audio without playing it yet."""
        text = text.strip()
        if not text:
            return False
        return asyncio.run(self._ensure_cached(text)) is not None

    async def speak_async(self, text: str, block: bool = True) -> bool:
        """
        Synthesizes (or loads from cache) and speaks the given text out loud.
        """
        text = text.strip()
        if not text:
            return False

        log_jarvis_speak(text)
        loop = asyncio.get_running_loop()
        cache_file = await self._ensure_cached(text)
        if cache_file is None:
            return await loop.run_in_executor(None, self._speak_macos_fallback, text, block)

        # Play audio via macOS CoreAudio afplay
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
