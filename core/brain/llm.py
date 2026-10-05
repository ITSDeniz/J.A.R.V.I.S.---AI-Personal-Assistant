"""
J.A.R.V.I.S. Dual-Engine LLM Core
Supports both local Ollama (Apple Silicon / offline) and Cloud Gemini APIs.
"""
import os
import json
import requests
from typing import List, Dict, Any, Optional
from config import settings
from core.brain.tools import TOOL_DEFINITIONS, ToolRegistry
from core.utils.logger import log_info, log_warning, log_error

class LLMEngine:
    """Unified AI interface with tool-calling capabilities."""

    def __init__(self):
        self.provider = settings.brain.provider
        self.ollama_model = settings.brain.ollama_model
        self.ollama_url = settings.brain.ollama_url
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")

    def query_ollama(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Query local Ollama instance."""
        try:
            url = f"{self.ollama_url}/api/chat"
            payload = {
                "model": self.ollama_model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.7}
            }
            res = requests.post(url, json=payload, timeout=20)
            if res.status_code == 200:
                data = res.json()
                return data.get("message", {}).get("content", "").strip()
            return None
        except Exception as e:
            return None

    def query_gemini(self, prompt: str, system_prompt: str) -> Optional[str]:
        """Query Google Gemini API if GEMINI_API_KEY is configured."""
        if not self.gemini_key:
            return None
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
            payload = {
                "system_instruction": {"parts": [{"text": system_prompt}]},
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 300}
            }
            res = requests.post(url, json=payload, timeout=15)
            if res.status_code == 200:
                data = res.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
            return None
        except Exception as e:
            log_error(f"Gemini API query error: {e}")
            return None

    def generate_response(self, user_text: str, history: List[Dict[str, str]]) -> str:
        """Route query to available LLM or fallback smoothly."""
        system_prompt = settings.brain.system_prompt

        # Attempt Gemini if key is provided
        if self.gemini_key or self.provider == "gemini":
            ans = self.query_gemini(user_text, system_prompt)
            if ans:
                return ans

        # Attempt Ollama if running
        ollama_messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_text}]
        ans = self.query_ollama(ollama_messages)
        if ans:
            return ans

        # Fallback persona answer when offline
        return (
            f"I have received your request, {settings.owner_name}. "
            "Internal neural core is currently operating in offline autonomy mode."
        )
