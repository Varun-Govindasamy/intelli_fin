import os
from typing import Dict
from dotenv import load_dotenv
from app.services.guardrails_service import guardrails_service
from app.utils.response_cleaner import clean_response

load_dotenv()

# System prompt injected into every NeMo chat call
_SYSTEM_PROMPT = """You are IntelliFinance, an AI-powered financial assistant. You provide helpful, accurate, and actionable financial advice and insights.

IMPORTANT FORMATTING RULES:
- Write in plain text format only
- Do NOT use any markdown symbols (no #, *, **, <b>, <br>, etc.)
- Do NOT use HTML tags
- Use simple line breaks for spacing
- Use regular text for emphasis (NO bold or italic formatting)
- Structure with clear headings using plain text
- Use bullet points with simple dashes or dots

Key guidelines:
- Focus on financial topics like investments, budgeting, market analysis, and financial planning
- Provide clear, practical advice in natural, conversational language
- Structure responses with clear sections using plain text headings
- Mention when professional financial advice should be sought for complex decisions
- Be conversational but professional
- If the question is not finance-related, politely redirect to financial topics

Please provide a helpful response in plain text format without any formatting symbols."""


class ChatService:
    def __init__(self):
        # NeMo rails are initialised lazily on first use
        self._rails = None

    def _get_rails(self):
        """Get (or lazily initialise) the NeMo LLMRails instance."""
        if self._rails is None:
            self._rails = guardrails_service.get_chat_rails()
        return self._rails

    async def general_chat(self, message: str) -> str:
        """
        Handle general financial chat using NeMo Guardrails full pipeline.
        NeMo automatically applies:
          - Input rails: PII masking, jailbreak detection, domain control,
                         regulatory compliance, sensitive query flagging
          - LLM generation via gpt-4o-mini
          - Output rails: sentiment/toxicity filter, output quality processing
                          (disclaimer injection, PII leakage, numerical sanity)
        """
        try:
            rails = self._get_rails()

            response = await rails.generate_async(
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user",   "content": message},
                ]
            )

            # NeMo returns either a string or a dict with "content"
            if isinstance(response, dict):
                return clean_response(response.get("content", str(response)))
            return clean_response(str(response))

        except Exception as e:
            print(f"Error in general chat: {e}")
            return (
                "Technical Difficulties\n\n"
                "I apologize, but I'm experiencing technical difficulties. "
                "Please try again or ask a specific financial question.\n\n"
                "Suggestions: Try asking about:\n"
                "- Investment strategies\n"
                "- Budgeting tips\n"
                "- Market analysis\n"
                "- Financial planning"
            )

    async def generate_summary(self, content: str) -> str:
        """Generate a short summary using NeMo-guarded OpenAI call."""
        try:
            rails = self._get_rails()

            prompt = (
                "Please provide a concise 2-3 sentence summary of the following "
                "financial content. Focus on key points and actionable insights. "
                "Use plain text only — no markdown or HTML.\n\n"
                f"Content:\n{content[:2000]}"
            )

            response = await rails.generate_async(
                messages=[{"role": "user", "content": prompt}]
            )

            if isinstance(response, dict):
                return response.get("content", str(response))
            return str(response)

        except Exception as e:
            print(f"Error generating summary: {e}")
            return await self._fallback_summary(content)

    async def _fallback_summary(self, content: str) -> str:
        words = content.split()
        if len(words) > 50:
            return f"Summary\n\n{' '.join(words[:50])}...\n\nSummary truncated due to technical limitations."
        return f"Summary\n\n{content}"

    async def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of financial text using NeMo-guarded pipeline."""
        try:
            rails = self._get_rails()

            prompt = (
                "Analyze the financial sentiment of the following text. "
                "Use ONLY plain text format (no markdown or HTML).\n\n"
                f"Text: {text}\n\n"
                "Format your response as:\n\n"
                "Sentiment Analysis\n\n"
                "Overall Sentiment: [Positive/Negative/Neutral]\n\n"
                "Confidence Level: [High/Medium/Low]\n\n"
                "Key Indicators:\n"
                "- Indicator 1\n"
                "- Indicator 2\n"
                "- Indicator 3\n\n"
                "Analysis Explanation:\n"
                "[Brief explanation]\n\n"
                "Plain text only:"
            )

            response = await rails.generate_async(
                messages=[{"role": "user", "content": prompt}]
            )

            text_response = response.get("content", str(response)) if isinstance(response, dict) else str(response)

            return {
                "sentiment": "Formatted",
                "confidence": "Plain",
                "indicators": ["Structured response"],
                "explanation": clean_response(text_response),
            }

        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return {
                "sentiment": "Error",
                "confidence": "Low",
                "indicators": ["Analysis failed"],
                "explanation": f"Analysis Error\n\nError: {str(e)}\n\nPlease try again.",
            }

    async def get_financial_advice(self, query: str, context: str = "") -> str:
        """Provide financial advice with optional context through NeMo pipeline."""
        try:
            rails = self._get_rails()

            prompt = (
                "You are a professional financial advisor. Provide helpful, practical "
                "financial information in plain text format for the following query.\n\n"
                f"Context (if provided): {context}\n\n"
                f"Query: {query}\n\n"
                "IMPORTANT: Use ONLY plain text format. No markdown or HTML.\n\n"
                "Structure as:\n\n"
                "Financial Information\n\n"
                "Direct Answer:\n[Response]\n\n"
                "Key Considerations:\n- Factor 1\n- Factor 2\n\n"
                "Potential Risks:\n- Risk 1\n- Risk 2\n\n"
                "Recommended Next Steps:\n1. Step 1\n2. Step 2\n\n"
                "Professional Consultation:\n"
                "For personalized advice, consult a SEBI-registered financial advisor.\n\n"
                "Plain text only:"
            )

            response = await rails.generate_async(
                messages=[{"role": "user", "content": prompt}]
            )

            if isinstance(response, dict):
                return response.get("content", str(response))
            return str(response)

        except Exception as e:
            print(f"Error providing financial advice: {e}")
            return (
                "Service Unavailable\n\n"
                "I apologize, but I'm unable to provide advice at the moment.\n\n"
                "Recommended Action:\n"
                "Please consult with a qualified financial advisor for personalized guidance."
            )
