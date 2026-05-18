"""
Custom NeMo Guardrails Actions for IntelliFinance

Implements rule-based guardrails as NeMo actions:
  Input:  PII Detection & Masking (Rail 3)
  Output: Disclaimer Injection (Rail 2), PII Leakage (Rail 3),
          Numerical Sanity (Rail 4), Grounding/Hallucination (Rail 1),
          Source Citation (Rail 6)
"""

import re
import os
from typing import Optional, Dict, Any
from nemoguardrails.actions import action


# ---------------------------------------------------------------------------
# PII Patterns
# ---------------------------------------------------------------------------
PII_PATTERNS = {
    "Aadhaar":      r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "PAN":          r"\b[A-Z]{5}\d{4}[A-Z]\b",
    "SSN":          r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
    "Credit Card":  r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    "Bank Account": r"\b\d{9,18}\b",
    "Phone":        r"\b(?:\+91[-\s]?)?(?:\+1[-\s]?)?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}\b",
    "Email":        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "Passport":     r"\b[A-Z]{1,2}\d{6,9}\b",
    "IFSC":         r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
}

# ---------------------------------------------------------------------------
# Disclaimer keywords
# ---------------------------------------------------------------------------
DISCLAIMER_KEYWORDS = [
    "buy", "sell", "invest", "should you", "recommend", "suggest",
    "consider buying", "consider selling", "hold", "bullish", "bearish",
    "price target", "stock pick", "trade", "position", "portfolio",
    "allocate", "put your money", "returns", "profit", "yield",
]

FINANCIAL_DISCLAIMER = (
    "\n\nDisclaimer: This information is for educational purposes only and does not "
    "constitute regulated financial advice. Please consult a SEBI-registered investment "
    "advisor or licensed financial planner before making any investment decisions."
)

# ---------------------------------------------------------------------------
# Numerical sanity thresholds
# ---------------------------------------------------------------------------
MAX_REALISTIC_RETURN_PCT = 500.0    # Flag returns > 500% as suspicious
MAX_REALISTIC_PRICE = 1_000_000.0   # ₹10 lakh / $1M per unit — flag if higher
MIN_REALISTIC_PRICE = 0.0001        # Flag near-zero prices


# ---------------------------------------------------------------------------
# Helper: PII mask text
# ---------------------------------------------------------------------------
def _mask_pii(text: str):
    detected = {}
    sanitized = text
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            detected[pii_type] = len(matches)
            sanitized = re.sub(
                pattern,
                f"[{pii_type.upper().replace(' ', '_')}_REDACTED]",
                sanitized,
                flags=re.IGNORECASE,
            )
    return sanitized, detected


# ===========================================================================
# INPUT ACTION — Rail 3: PII Detection & Masking
# ===========================================================================
@action(is_system_action=True)
async def check_pii_input(context: Optional[dict] = None) -> Dict[str, Any]:
    """Detect and mask PII in the user message before it reaches the LLM."""
    user_message = (context or {}).get("user_message", "")
    sanitized, detected = _mask_pii(user_message)
    has_pii = bool(detected)
    if has_pii:
        print(f"🔒 [NeMo] PII detected and masked: {list(detected.keys())}")
    return {
        "has_pii": has_pii,
        "sanitized_message": sanitized,
        "detected_types": list(detected.keys()),
    }


# ===========================================================================
# OUTPUT ACTION — Combined post-processing
# Covers: Rail 1 (Hallucination), Rail 2 (Disclaimer), Rail 3 (PII leakage),
#         Rail 4 (Numerical Sanity), Rail 6 (Source Citation)
# ===========================================================================
@action(is_system_action=True)
async def process_output_quality(context: Optional[dict] = None) -> Dict[str, Any]:
    """
    Run all rule-based output guardrails and return the processed response.
    Called by the 'check output quality' Colang flow.
    """
    ctx = context or {}
    bot_response = ctx.get("bot_message", "")
    user_message = ctx.get("user_message", "")
    rag_context = ctx.get("rag_context", "")   # injected by rag_service if available

    modified = False
    processed = bot_response
    details = {}

    # ------------------------------------------------------------------
    # Rail 3 (Output): PII Leakage Detection
    # ------------------------------------------------------------------
    _, leaked_pii = _mask_pii(processed)
    if leaked_pii:
        print(f"⚠️  [NeMo] PII leakage detected in output: {list(leaked_pii.keys())}")
        processed, _ = _mask_pii(processed)
        modified = True
        details["pii_leakage"] = {"detected": list(leaked_pii.keys()), "action": "masked"}
    else:
        details["pii_leakage"] = {"detected": [], "action": "none"}

    # ------------------------------------------------------------------
    # Rail 4: Numerical Sanity Check
    # ------------------------------------------------------------------
    sanity_warnings = _check_numerical_sanity(processed)
    if sanity_warnings:
        print(f"⚠️  [NeMo] Numerical sanity issues: {sanity_warnings}")
        processed += (
            "\n\nNote: Some figures in this response appear unusually high or low. "
            "Please verify all specific numbers with official sources before making "
            "any financial decisions."
        )
        modified = True
        details["numerical_sanity"] = {"warnings": sanity_warnings, "action": "warning_appended"}
    else:
        details["numerical_sanity"] = {"warnings": [], "action": "none"}

    # ------------------------------------------------------------------
    # Rail 1: Hallucination / Grounding Check (RAG-specific)
    # ------------------------------------------------------------------
    if rag_context:
        grounding = _check_grounding(processed, rag_context)
        details["grounding"] = grounding
        if not grounding["is_grounded"]:
            print(f"⚠️  [NeMo] Grounding issue: {grounding['reason']}")
            processed += (
                "\n\nNote: Some information in this response could not be directly "
                "verified against the uploaded documents. Please cross-check with "
                "the source documents before relying on specific figures."
            )
            modified = True
    else:
        details["grounding"] = {"is_grounded": True, "reason": "no RAG context provided"}

    # ------------------------------------------------------------------
    # Rail 6: Source Citation Enforcement (RAG-specific)
    # ------------------------------------------------------------------
    if rag_context and not _has_source_citation(processed):
        print("⚠️  [NeMo] No source citation found in RAG response.")
        processed += "\n\nSource: Based on the uploaded financial documents provided."
        modified = True
        details["citation"] = {"action": "citation_appended"}
    else:
        details["citation"] = {"action": "none"}

    # ------------------------------------------------------------------
    # Rail 2: Disclaimer Injection
    # ------------------------------------------------------------------
    needs_disclaimer = any(kw in (processed + user_message).lower() for kw in DISCLAIMER_KEYWORDS)
    if needs_disclaimer and "disclaimer" not in processed.lower():
        processed += FINANCIAL_DISCLAIMER
        modified = True
        details["disclaimer"] = {"action": "disclaimer_appended"}
    else:
        details["disclaimer"] = {"action": "none"}

    return {
        "modified": modified,
        "processed_response": processed,
        "details": details,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _check_numerical_sanity(response: str):
    """Flag unrealistic financial figures."""
    warnings = []

    # Check for return percentages > MAX_REALISTIC_RETURN_PCT
    pct_matches = re.findall(r"(\d[\d,]*(?:\.\d+)?)\s*%", response)
    for match in pct_matches:
        try:
            val = float(match.replace(",", ""))
            if val > MAX_REALISTIC_RETURN_PCT:
                warnings.append(f"Unusually high return percentage: {val}%")
        except ValueError:
            continue

    # Check for suspiciously small prices (near-zero NAVs etc.)
    price_matches = re.findall(r"(?:₹|\$|Rs\.?)\s*(\d[\d,]*(?:\.\d+)?)", response)
    for match in price_matches:
        try:
            val = float(match.replace(",", ""))
            if val < MIN_REALISTIC_PRICE and val > 0:
                warnings.append(f"Suspiciously low price detected: {val}")
            if val > MAX_REALISTIC_PRICE:
                warnings.append(f"Unusually high price detected: {val}")
        except ValueError:
            continue

    return warnings


def _check_grounding(response: str, context: str) -> dict:
    """
    Verify that numbers cited in the response appear in the retrieved context.
    Returns a dict with is_grounded flag and reason.
    """
    # Extract numbers from response
    response_numbers = set(re.findall(r"\d[\d,]*(?:\.\d+)?", response))
    context_numbers = set(re.findall(r"\d[\d,]*(?:\.\d+)?", context))

    if not response_numbers:
        return {"is_grounded": True, "reason": "no specific numbers to verify"}

    ungrounded = response_numbers - context_numbers
    # Allow up to 30% ungrounded numbers (e.g., calculations, percentages derived from data)
    ungrounded_ratio = len(ungrounded) / len(response_numbers)

    if ungrounded_ratio > 0.5:
        return {
            "is_grounded": False,
            "reason": f"{len(ungrounded)} of {len(response_numbers)} numbers not found in context",
            "ungrounded_sample": list(ungrounded)[:5],
        }

    return {
        "is_grounded": True,
        "reason": f"grounding ratio: {1 - ungrounded_ratio:.0%}",
    }


def _has_source_citation(response: str) -> bool:
    """Check if the response already has a source attribution."""
    citation_patterns = [
        r"according to",
        r"based on",
        r"source:",
        r"from the document",
        r"as stated in",
        r"per the",
        r"the document (shows|states|indicates)",
    ]
    response_lower = response.lower()
    return any(re.search(p, response_lower) for p in citation_patterns)
