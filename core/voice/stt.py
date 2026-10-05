"""
J.A.R.V.I.S. Speech-to-Text (The Ears)
Records microphone audio via sounddevice and transcribes using neural speech recognition.
"""
import io
import time
import wave
from typing import Optional
import numpy as np
import sounddevice as sd
import speech_recognition as sr
from core.utils.logger import log_info, log_error, log_warning, console

class SpeechToText:
    """Microphone recording and Speech-to-Text transcriber."""

    def __init__(self, samplerate: int = 16000):
        self.samplerate = samplerate
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True

    def record_until_silence(self, max_duration: float = 8.0, silence_timeout: float = 1.2) -> Optional[np.ndarray]:
        """
        Record audio from the default microphone, stopping when user pauses or after max_duration.
        """
        chunk_duration = 0.2  # 200ms chunks
        chunk_samples = int(self.samplerate * chunk_duration)
        silence_threshold = 400  # RMS energy threshold for speech

        chunks = []
        silence_start = None
        has_spoken = False
        start_time = time.time()

        with sd.InputStream(samplerate=self.samplerate, channels=1, dtype='int16') as stream:
            while time.time() - start_time < max_duration:
                chunk, _ = stream.read(chunk_samples)
                chunks.append(chunk)

                # Compute Root Mean Square (RMS) energy to detect speech vs silence
                rms = np.sqrt(np.mean(chunk.astype(float)**2))

                if rms > silence_threshold:
                    has_spoken = True
                    silence_start = None
                elif has_spoken:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > silence_timeout:
                        # User stopped speaking
                        break

        if not chunks:
            return None

        audio_data = np.concatenate(chunks, axis=0)
        return audio_data

    def transcribe(self, audio_data: np.ndarray) -> Optional[str]:
        """Transcribe in-memory PCM audio using neural speech recognition."""
        try:
            byte_io = io.BytesIO()
            with wave.open(byte_io, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.samplerate)
                wf.writeframes(audio_data.tobytes())
            byte_io.seek(0)

            with sr.AudioFile(byte_io) as source:
                audio = self.recognizer.record(source)

            # Transcribe via Google Speech Recognition (free, fast, highly accurate)
            text = self.recognizer.recognize_google(audio)
            return text.strip()
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            log_error(f"Speech recognition network error: {e}")
            return None
        except Exception as e:
            log_error(f"Audio transcription error: {e}")
            return None

    def listen_and_transcribe(self, prompt: str = "Listening, Sir...") -> Optional[str]:
        """Record a single command from the user and transcribe it."""
        console.print(f"[bold cyan]🎤 [MICROPHONE][/bold cyan] {prompt}")
        audio = self.record_until_silence()
        if audio is None or len(audio) < self.samplerate * 0.5:
            return None

        console.print("[dim cyan]⚡ Processing speech...[/dim cyan]")
        text = self.transcribe(audio)
        if text:
            console.print(f"[bold green]✔ User Spoke:[/bold green] \"{text}\"")
        return text

# Global STT instance
jarvis_stt = SpeechToText()
