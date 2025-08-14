import os
import asyncio
import requests
from typing import Dict, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class ChatService:
    def __init__(self):
        # Initialize Gemini
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Ollama configuration
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    async def general_chat(self, message: str) -> str:
        """Handle general financial chat using Gemini"""
        try:
            # Create a financial-focused prompt
            financial_prompt = f"""
You are IntelliFinance, an AI-powered financial assistant. You provide helpful, accurate, and actionable financial advice and insights.

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

User question: {message}

Please provide a helpful response in plain text format without any formatting symbols:"""

            response = self.gemini_model.generate_content(financial_prompt)
            return response.text
            
        except Exception as e:
            print(f"Error in general chat: {e}")
            return "Technical Difficulties\n\nI apologize, but I'm experiencing technical difficulties. Please try again or ask a specific financial question.\n\nSuggestions: Try asking about:\n- Investment strategies\n- Budgeting tips\n- Market analysis\n- Financial planning"
    
    async def generate_summary(self, content: str) -> str:
        """Generate short summary using IBM Granite via Ollama"""
        try:
            # Check if Ollama is running and has the model
            if not await self._check_ollama_connection():
                return await self._fallback_summary(content)
            
            # Prepare the prompt for summarization
            summary_prompt = f"""
Please provide a concise summary of the following financial analysis or content. Focus on the key points and actionable insights.

IMPORTANT: Use ONLY plain text format:
- NO markdown symbols (no #, *, **, etc.)
- NO HTML tags (no <b>, <br>, etc.)
- Use simple text headings
- Use plain bullet points with dashes
- Maximum 2-3 sentences
- Clear, actionable insights

Content to summarize:
{content}

Please provide the summary in plain text format only:"""

            # Make request to Ollama
            response = await self._call_ollama(summary_prompt)
            
            if response:
                return response
            else:
                return await self._fallback_summary(content)
                
        except Exception as e:
            print(f"Error generating summary: {e}")
            return await self._fallback_summary(content)
    
    async def _check_ollama_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    async def _call_ollama(self, prompt: str, model: str = "granite3.3:2b") -> Optional[str]:
        """Make API call to Ollama"""
        try:
            # First try with granite3.3:2b, fallback to other models if not available
            models_to_try = ["granite3.3:2b", "llama3.2:latest", "gemma3:latest"]
            
            for model_name in models_to_try:
                try:
                    payload = {
                        "model": model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "max_tokens": 200
                        }
                    }
                    
                    response = requests.post(
                        f"{self.ollama_base_url}/api/generate",
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return result.get('response', '').strip()
                        
                except Exception as e:
                    print(f"Error with model {model_name}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return None
    
    async def _fallback_summary(self, content: str) -> str:
        """Fallback summary using Gemini when Ollama is not available"""
        try:
            summary_prompt = f"""
Please provide a concise summary of the following content in plain text format:

{content[:1000]}  # Limit content length

IMPORTANT: Use ONLY plain text:
- NO formatting symbols
- Simple text heading "Summary"
- Use dashes for bullet points
- Plain text only

Provide the summary in plain text format:"""

            response = self.gemini_model.generate_content(summary_prompt)
            return response.text
            
        except Exception as e:
            print(f"Error in fallback summary: {e}")
            # Basic plain text truncation as last resort
            words = content.split()
            if len(words) > 50:
                return f"Summary\n\n{' '.join(words[:50])}...\n\nSummary truncated due to technical limitations."
            return f"Summary\n\n{content}"
    
    async def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of financial text using Gemini"""
        try:
            sentiment_prompt = f"""
Analyze the financial sentiment of the following text and provide a response in plain text format only.

Text to analyze: {text}

IMPORTANT: Use ONLY plain text format:
- NO markdown symbols (no #, *, **, etc.)
- NO HTML tags (no <b>, <br>, etc.)
- Use simple text headings
- Use plain bullet points with dashes

Format the response as:

Sentiment Analysis

Overall Sentiment: [Positive/Negative/Neutral]

Confidence Level: [High/Medium/Low]

Key Indicators:
- Indicator 1
- Indicator 2
- Indicator 3

Analysis Explanation:
[Brief explanation of the sentiment analysis]

Please provide the analysis in plain text format only:"""

            response = self.gemini_model.generate_content(sentiment_prompt)
            
            # Return the plain text formatted response directly
            return {
                "sentiment": "Formatted",
                "confidence": "Plain", 
                "indicators": ["Structured response"],
                "explanation": response.text  # This now contains the plain text formatted response
            }
                
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return {
                "sentiment": "Error",
                "confidence": "Low",
                "indicators": ["Analysis failed"],
                "explanation": f"Analysis Error\n\nError: {str(e)}\n\nPlease try again or contact support if the issue persists."
            }
    
    async def get_financial_advice(self, query: str, context: str = "") -> str:
        """Provide financial advice with optional context"""
        try:
            advice_prompt = f"""
You are a professional financial advisor. Provide helpful, practical financial advice in plain text format for the following query.

Context (if provided): {context}

Query: {query}

IMPORTANT: Use ONLY plain text format:
- NO markdown symbols (no #, *, **, etc.)
- NO HTML tags (no <b>, <br>, etc.)
- Use simple text headings
- Use plain bullet points with dashes
- Use numbered lists with simple numbers

Structure your response as:

Financial Advice

Direct Answer:
[Your direct response to the query]

Key Considerations:
- Important factor 1
- Important factor 2
- Important factor 3

Potential Risks and Limitations:
- Risk 1
- Risk 2
- Limitation to consider

Recommended Next Steps:
1. Step 1: [Action item]
2. Step 2: [Action item]
3. Step 3: [Action item]

Professional Consultation:
This is general advice and complex financial decisions should involve consultation with a qualified financial advisor.

Please provide the advice in plain text format only:"""

            response = self.gemini_model.generate_content(advice_prompt)
            return response.text
            
        except Exception as e:
            print(f"Error providing financial advice: {e}")
            return """Service Unavailable

I apologize, but I'm unable to provide advice at the moment due to technical difficulties.

Recommended Action:
Please consult with a qualified financial advisor for personalized guidance.

Alternative:
Try asking your question again in a few moments, or rephrase it for better results.

Your financial decisions are important - professional guidance is always recommended for complex situations."""
