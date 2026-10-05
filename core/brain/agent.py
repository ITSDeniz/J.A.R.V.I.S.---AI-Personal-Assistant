"""
J.A.R.V.I.S. Core Agent Orchestrator
Coordinates reasoning, intent parsing, tool execution, and voice output.
"""
from typing import List, Dict, Any, Optional
from config import settings
from core.brain.intents import IntentParser
from core.brain.llm import LLMEngine
from core.voice import jarvis_voice
from core.utils.logger import log_info, log_success

class JarvisAgent:
    """The central brain orchestrator for J.A.R.V.I.S."""

    def __init__(self):
        self.llm = LLMEngine()
        self.history: List[Dict[str, str]] = []
        self.max_history = 10

    def process_command(self, user_input: str, speak_output: bool = True) -> Dict[str, Any]:
        """
        Process user speech or text input:
        1. Fast-path: Check for system commands via IntentParser (0ms latency)
        2. Cognitive-path: Query LLM (Ollama or Gemini) with Tony Stark persona
        3. Vocalize response via Neural Voice Engine
        """
        user_text = user_input.strip()
        if not user_text:
            return {"text": "", "spoken": False}

        log_info(f"Processing command: '{user_text}'")

        # 1. Check direct intent parser first
        intent_result = IntentParser.match(user_text)
        if intent_result:
            reply_text, tool_data = intent_result
            log_success(f"Matched internal protocol: {reply_text}")
            if speak_output:
                jarvis_voice.speak(reply_text)
            self._append_history(user_text, reply_text)
            return {
                "text": reply_text,
                "tool_data": tool_data,
                "source": "intent_engine",
                "spoken": speak_output
            }

        # 2. Query Dual-Engine LLM
        reply_text = self.llm.generate_response(user_text, self.history)
        if speak_output:
            jarvis_voice.speak(reply_text)

        self._append_history(user_text, reply_text)
        return {
            "text": reply_text,
            "tool_data": None,
            "source": "llm_engine",
            "spoken": speak_output
        }

    def _append_history(self, user_msg: str, assistant_msg: str):
        self.history.append({"role": "user", "content": user_msg})
        self.history.append({"role": "assistant", "content": assistant_msg})
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-self.max_history * 2:]

# Global agent singleton
jarvis_agent = JarvisAgent()
