"""
NeMo Guardrails Service for IntelliFinance
==========================================
Replaces the custom rule-based guardrails with NVIDIA NeMo Guardrails.

Architecture:
  - Chat Service  : uses get_chat_rails() → calls rails.generate_async() directly
                    (NeMo handles full pipeline: input rails → LLM → output rails)
  - RAG Service   : calls validate_input() / validate_output() which use NeMo's
                    action-based checks with rule-based Python post-processing

Input Guardrails (via NeMo):
  1. Topic/Domain Control          — self_check_input prompt
  2. Jailbreak & Prompt Injection  — self_check_input prompt
  3. PII Detection & Masking       — check_pii_input action (rule-based)
  4. Regulatory Compliance Filter  — self_check_input prompt
  5. Sensitive Query Flagging      — self_check_input prompt

Output Guardrails (via NeMo):
  1. Hallucination / Grounding     — process_output_quality action (rule-based)
  2. Disclaimer Injection          — process_output_quality action (rule-based)
  3. PII Leakage Detection         — process_output_quality action (rule-based)
  4. Numerical Sanity Checks       — process_output_quality action (rule-based)
  5. Sentiment & Toxicity Filter   — self_check_output prompt (LLM-based)
  6. Source Citation Enforcement   — process_output_quality action (rule-based, RAG only)
"""

import os
import asyncio
from typing import Tuple, Dict, Optional
from pathlib import Path

from nemoguardrails import RailsConfig, LLMRails
from dotenv import load_dotenv

load_dotenv()

# Path to the NeMo config directory (relative to backend/)
_CONFIG_PATH = str(Path(__file__).parent.parent.parent / "nemo_config")

# Refusal message set in rails.co — used to detect blocked responses
_REFUSAL_PREFIX = "I'm sorry, I'm unable to assist with that request."


class NemoGuardrailsService:
    """
    Wraps NeMo Guardrails LLMRails with the same interface used by
    chat_service and rag_service so no call-site changes are needed.
    """

    def __init__(self):
        self._rails: Optional[LLMRails] = None
        self.enabled = True
        self.strict_mode = False
        self._config_path = _CONFIG_PATH

    # ------------------------------------------------------------------
    # Initialisation (lazy, async)
    # ------------------------------------------------------------------
    async def _ensure_rails(self) -> LLMRails:
        if self._rails is None:
            config = RailsConfig.from_path(self._config_path)
            self._rails = LLMRails(config)
            print(f"✅ [NeMo] Guardrails initialised from: {self._config_path}")
        return self._rails

    def get_chat_rails(self) -> LLMRails:
        """
        Return the LLMRails instance for direct use in chat_service.
        Initialises synchronously on first call (safe for startup).
        """
        if self._rails is None:
            config = RailsConfig.from_path(self._config_path)
            self._rails = LLMRails(config)
            print(f"✅ [NeMo] Guardrails initialised from: {self._config_path}")
        return self._rails

    # ------------------------------------------------------------------
    # Input Validation  (used by RAG service)
    # ------------------------------------------------------------------
    async def validate_input(self, query: str) -> Tuple[bool, str, Dict]:
        """
        Run NeMo input rails against the user query.

        Returns:
            (is_allowed: bool, message: str, details: dict)
            details["sanitized_query"] contains the PII-masked version.
        """
        if not self.enabled:
            return True, "Guardrails disabled", {"sanitized_query": query, "warnings": []}

        try:
            rails = await self._ensure_rails()

            # Run NeMo generate — if input rail blocks, it returns refusal message
            # without calling the main LLM (NeMo short-circuits on blocked input)
            result = await rails.generate_async(
                messages=[{"role": "user", "content": query}]
            )

            response_text = result if isinstance(result, str) else result.get("content", "")

            # Check if NeMo blocked the input
            if response_text.startswith(_REFUSAL_PREFIX) or _is_refusal(response_text):
                print(f"⛔ [NeMo] Input blocked: {response_text[:80]}...")
                return False, response_text, {
                    "sanitized_query": query,
                    "warnings": [],
                    "nemo_blocked": True,
                }

            # Input passed — extract sanitized query from context if PII was masked
            sanitized = getattr(rails, "_sanitized_input", query)
            return True, "Input validated", {
                "sanitized_query": sanitized,
                "warnings": [],
                "nemo_blocked": False,
            }

        except Exception as e:
            print(f"⚠️  [NeMo] validate_input error: {e} — allowing with warning")
            return True, "Guardrail check failed (allowing with caution)", {
                "sanitized_query": query,
                "warnings": [f"Guardrail error: {str(e)}"],
            }

    # ------------------------------------------------------------------
    # Output Validation  (used by RAG service)
    # ------------------------------------------------------------------
    async def validate_output(
        self,
        response: str,
        query: str,
        context: str = "",
        confidence_score: float = 1.0,
    ) -> Tuple[str, Dict]:
        """
        Run NeMo output rails + Python-based post-processing.

        Returns:
            (processed_response: str, details: dict)
        """
        if not self.enabled:
            return response, {"guardrails": "disabled"}

        try:
            from nemo_config.actions import process_output_quality, _mask_pii

            # Build a minimal context dict for actions
            action_context = {
                "bot_message": response,
                "user_message": query,
                "rag_context": context,
            }

            # Run the combined output quality action (rules-based guardrails 1,2,3,4,6)
            quality_result = await process_output_quality(context=action_context)
            processed = quality_result.get("processed_response", response)
            details = quality_result.get("details", {})
            details["confidence_score"] = confidence_score

            # Low-confidence warning (Rail 4 supplement)
            if confidence_score < 0.3 and "low confidence" not in processed.lower():
                processed += (
                    "\n\nLow Confidence Warning: This response is based on limited "
                    "relevant information. Results may be incomplete — please verify "
                    "with official sources."
                )
                details["low_confidence_warning"] = True

            print(f"🛡️  [NeMo] Output guardrails applied. Modified: {quality_result.get('modified', False)}")
            return processed, details

        except Exception as e:
            print(f"⚠️  [NeMo] validate_output error: {e}")
            return response, {"error": str(e), "guardrails": "partial"}

    # ------------------------------------------------------------------
    # Control methods (kept for API compatibility)
    # ------------------------------------------------------------------
    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        print(f"[NeMo] Guardrails {'enabled' if enabled else 'disabled'}")

    def set_strict_mode(self, strict: bool):
        self.strict_mode = strict
        print(f"[NeMo] Strict mode {'enabled' if strict else 'disabled'}")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _is_refusal(text: str) -> bool:
    """Heuristic to detect NeMo refusal responses."""
    lower = text.lower()
    refusal_signals = [
        "i'm sorry, i cannot",
        "i'm sorry, i'm unable",
        "i cannot assist",
        "i'm not able to help",
        "i cannot help with",
    ]
    return any(s in lower for s in refusal_signals)


# ---------------------------------------------------------------------------
# Singleton — same name as old service for drop-in compatibility
# ---------------------------------------------------------------------------
guardrails_service = NemoGuardrailsService()
