import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from crewai import Agent, Task, Crew, Process
import openai
from dotenv import load_dotenv
import requests
import yfinance as yf
import numpy as np
from dataclasses import dataclass
import aiohttp

load_dotenv()

@dataclass
class UserProfile:
    budget: float
    risk_level: str  # 'low', 'medium', 'high'
    time_horizon: str  # 'short', 'medium', 'long'
    sector_preferences: List[str]
    
@dataclass
class StockAnalysis:
    symbol: str
    current_price: float
    historical_volatility: float
    growth_potential_score: float
    sentiment_score: float
    risk_score: float
    recommended_allocation: float
    allocation_amount: float

class TradeAgentService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.ollama_base_url = "http://localhost:11434"  # Default Ollama URL
        self.granite_model = "granite3.3:2b"
        self.decision_history = []
        self.memory_file = "./data/trade_decisions.json"
        self._load_memory()
    
    def _load_memory(self):
        """Load previous decisions from memory"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    self.decision_history = json.load(f)
        except Exception as e:
            print(f"Error loading memory: {e}")
            self.decision_history = []
    
    def _save_memory(self):
        """Save decisions to memory"""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            with open(self.memory_file, 'w') as f:
                json.dump(self.decision_history, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    async def _call_granite_model(self, prompt: str, system_message: str = None) -> str:
        """Call Granite model via Ollama API"""
        try:
            url = f"{self.ollama_base_url}/api/generate"
            
            # Construct the full prompt with system message if provided
            full_prompt = prompt
            if system_message:
                full_prompt = f"System: {system_message}\n\nUser: {prompt}"
            
            payload = {
                "model": self.granite_model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for more focused financial analysis
                    "top_p": 0.9,
                    "max_tokens": 200
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('response', '').strip()
                    else:
                        error_text = await response.text()
                        print(f"Ollama API error {response.status}: {error_text}")
                        return f"Granite model error: {response.status}"
                        
        except Exception as e:
            print(f"Error calling Granite model: {e}")
            return f"Error connecting to Granite model: {str(e)}"
    
    def get_stock_price(self, symbol: str) -> str:
        """Get current stock price for a given symbol"""
        try:
            # Using yfinance for real data
            stock = yf.Ticker(symbol)
            info = stock.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            return f"Current price for {symbol}: ${current_price:.2f}"
        except Exception as e:
            return f"Error fetching price for {symbol}: {str(e)}"
    
    def get_live_stock_data(self, symbol: str) -> Dict:
        """Get comprehensive live stock data"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            hist = stock.history(period="1y")
            
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            if current_price == 0 and not hist.empty:
                current_price = hist['Close'].iloc[-1]
                
            return {
                'symbol': symbol,
                'current_price': float(current_price),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'beta': info.get('beta', 1.0),
                'volume': info.get('regularMarketVolume', 0),
                'day_change': info.get('regularMarketChangePercent', 0),
                'year_high': info.get('fiftyTwoWeekHigh', 0),
                'year_low': info.get('fiftyTwoWeekLow', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'historical_data': hist.to_dict('records') if not hist.empty else []
            }
        except Exception as e:
            return {'error': str(e), 'symbol': symbol}
    
    def calculate_historical_volatility(self, symbol: str, days: int = 252) -> float:
        """Calculate historical volatility (annualized)"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1y")
            if hist.empty:
                return 0.25  # Default volatility
            
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)  # Annualized
            return float(volatility)
        except Exception:
            return 0.25
    
    def calculate_growth_potential(self, symbol: str) -> float:
        """Calculate growth potential score (0-1)"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            hist = stock.history(period="1y")
            
            if hist.empty:
                return 0.5
            
            # Price momentum (recent performance)
            recent_return = (hist['Close'].iloc[-1] - hist['Close'].iloc[-22]) / hist['Close'].iloc[-22]
            momentum_score = min(max((recent_return + 0.1) / 0.3, 0), 1)  # Normalize to 0-1
            
            # Volume trend
            recent_volume = hist['Volume'].iloc[-10:].mean()
            older_volume = hist['Volume'].iloc[-30:-20].mean()
            volume_score = min(max((recent_volume / older_volume - 0.8) / 0.4, 0), 1) if older_volume > 0 else 0.5
            
            # Fundamental score
            pe_ratio = info.get('trailingPE', 20)
            pe_score = min(max((25 - pe_ratio) / 20, 0), 1) if pe_ratio > 0 else 0.5
            
            # Combined score
            growth_score = (momentum_score * 0.4 + volume_score * 0.3 + pe_score * 0.3)
            return float(growth_score)
        except Exception:
            return 0.5
    
    def get_financial_metrics(self, symbol: str) -> str:
        """Get key financial metrics for a company"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            return f"""
            Financial Metrics for {symbol}:
            - P/E Ratio: {info.get('trailingPE', 'N/A')}
            - Market Cap: ${info.get('marketCap', 0):,.0f}
            - Beta: {info.get('beta', 'N/A')}
            - EPS: ${info.get('trailingEps', 'N/A')}
            - Revenue Growth: {info.get('revenueGrowth', 'N/A')}
            - Profit Margins: {info.get('profitMargins', 'N/A')}
            - ROE: {info.get('returnOnEquity', 'N/A')}
            - Debt to Equity: {info.get('debtToEquity', 'N/A')}
            - Current Ratio: {info.get('currentRatio', 'N/A')}
            - Operating Margin: {info.get('operatingMargins', 'N/A')}
            """
        except Exception as e:
            return f"Error fetching metrics for {symbol}: {str(e)}"
    
    def analyze_market_sentiment(self, symbol: str, news_data: List[Dict]) -> float:
        """Analyze market sentiment from news (returns score 0-1)"""
        try:
            if not news_data:
                return 0.5  # Neutral sentiment
            
            # Use OpenAI to analyze sentiment
            news_text = " ".join([item.get('title', '') + ' ' + item.get('snippet', '') for item in news_data[:5]])
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze the sentiment of financial news. Return only a number between 0 and 1, where 0 is very negative, 0.5 is neutral, and 1 is very positive."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze sentiment for {symbol}: {news_text}"
                    }
                ],
                max_tokens=10
            )
            
            sentiment_text = response.choices[0].message.content.strip()
            try:
                sentiment_score = float(sentiment_text)
                return max(0, min(1, sentiment_score))  # Ensure 0-1 range
            except ValueError:
                return 0.5
                
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return 0.5
    
    def calculate_risk_score(self, symbol: str, volatility: float, beta: float) -> float:
        """Calculate risk score for a stock (0-1, higher = riskier)"""
        try:
            # Volatility component (0-1)
            vol_score = min(volatility / 0.5, 1)  # Normalize by 50% volatility
            
            # Beta component (0-1)
            beta_score = min(abs(beta - 1) / 1, 1)  # Distance from market beta
            
            # Combined risk score
            risk_score = (vol_score * 0.7 + beta_score * 0.3)
            return float(risk_score)
        except Exception:
            return 0.5
    
    def serper_tool(self, query: str) -> str:
        """Search for market news and information using web search"""
        try:
            serper_api_key = os.getenv("SERPER_API_KEY")
            if not serper_api_key:
                return "Serper API key not configured. Unable to fetch recent news."
            
            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": serper_api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "q": f"{query} financial news market analysis",
                "num": 5
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Process organic search results
                if "organic" in data:
                    for item in data["organic"][:3]:
                        results.append(f"Title: {item.get('title', 'N/A')}\nSnippet: {item.get('snippet', 'N/A')}\n")
                
                # Process news results
                if "news" in data:
                    for item in data["news"][:2]:
                        results.append(f"News: {item.get('title', 'N/A')}\nSummary: {item.get('snippet', 'N/A')}\n")
                
                return "\n".join(results) if results else "No relevant information found."
            else:
                return f"Search API error: {response.status_code}"
                
        except Exception as e:
            return f"Error searching for information: {str(e)}"
    
    def calculate_position_sizing(self, user_profile: UserProfile, stocks_analysis: List[StockAnalysis]) -> List[StockAnalysis]:
        """Calculate position sizing based on risk tolerance and portfolio theory"""
        try:
            total_budget = user_profile.budget
            risk_multiplier = {'low': 0.5, 'medium': 1.0, 'high': 1.5}.get(user_profile.risk_level, 1.0)
            
            # Sort stocks by growth potential
            sorted_stocks = sorted(stocks_analysis, key=lambda x: x.growth_potential_score, reverse=True)
            
            # Calculate base allocations
            total_scores = sum(stock.growth_potential_score for stock in sorted_stocks)
            
            for i, stock in enumerate(sorted_stocks):
                if total_scores > 0:
                    # Base allocation based on growth potential
                    base_allocation = stock.growth_potential_score / total_scores
                    
                    # Adjust for risk
                    risk_adjustment = (1 - stock.risk_score) * risk_multiplier
                    adjusted_allocation = base_allocation * risk_adjustment
                    
                    # Apply position limits (max 25% in single stock for diversification)
                    max_position = 0.25 if user_profile.risk_level == 'high' else 0.15 if user_profile.risk_level == 'medium' else 0.10
                    stock.recommended_allocation = min(adjusted_allocation, max_position)
                else:
                    stock.recommended_allocation = 0
            
            # Normalize allocations to sum to 1
            total_allocation = sum(stock.recommended_allocation for stock in sorted_stocks)
            if total_allocation > 0:
                for stock in sorted_stocks:
                    stock.recommended_allocation /= total_allocation
                    stock.allocation_amount = stock.recommended_allocation * total_budget
            
            return sorted_stocks
            
        except Exception as e:
            print(f"Position sizing error: {e}")
            return stocks_analysis
    
    def get_sector_diversification_bonus(self, stocks: List[StockAnalysis], user_preferences: List[str]) -> Dict[str, float]:
        """Calculate diversification bonuses based on sector spread"""
        sector_count = {}
        for stock in stocks:
            # This would normally come from stock data, for now we'll simulate
            sector = "Technology"  # Would get from yfinance
            sector_count[sector] = sector_count.get(sector, 0) + 1
        
        # Bonus for diversification
        diversification_bonus = {}
        for sector in sector_count:
            if sector in user_preferences:
                diversification_bonus[sector] = 1.1  # 10% bonus for preferred sectors
            else:
                diversification_bonus[sector] = 1.0
        
        return diversification_bonus
    
    def create_research_agent(self) -> Agent:
        """Create the research agent"""
        return Agent(
            role='Financial Research Specialist',
            goal='Research and gather comprehensive market data and news about specified companies',
            backstory="""You are an expert financial researcher with access to real-time market data 
            and news sources. Your job is to gather all relevant information about companies including 
            recent news, market trends, and financial performance indicators.""",
            verbose=True,
            allow_delegation=False
        )
    
    def create_analysis_agent(self) -> Agent:
        """Create the analysis agent"""
        return Agent(
            role='Financial Analysis Expert',
            goal='Analyze market data and perform sentiment analysis to understand market conditions',
            backstory="""You are a seasoned financial analyst with expertise in technical analysis, 
            fundamental analysis, and market sentiment evaluation. You excel at interpreting complex 
            financial data and identifying market trends and patterns.""",
            verbose=True,
            allow_delegation=False
        )
    
    def create_decision_agent(self) -> Agent:
        """Create the decision agent"""
        return Agent(
            role='Investment Decision Maker',
            goal='Make informed buy/sell/hold recommendations based on comprehensive analysis',
            backstory="""You are an experienced investment advisor who makes strategic investment 
            decisions based on thorough research and analysis. You consider risk factors, market 
            conditions, and investment objectives to provide actionable recommendations.""",
            verbose=True,
            allow_delegation=False
        )
    
    async def comprehensive_trade_analysis(self, 
                                         symbols: List[str], 
                                         user_profile: UserProfile) -> Dict:
        """Comprehensive trade analysis with user preferences and position sizing"""
        try:
            stock_analyses = []
            
            # Analyze each stock
            for symbol in symbols:
                # Get live data
                live_data = self.get_live_stock_data(symbol)
                if 'error' in live_data:
                    continue
                
                # Calculate metrics
                volatility = self.calculate_historical_volatility(symbol)
                growth_potential = self.calculate_growth_potential(symbol)
                
                # Get news and sentiment
                news_query = f"{symbol} stock news analysis"
                news_text = self.serper_tool(news_query)
                news_data = [{'title': news_text[:100], 'snippet': news_text[100:200]}]  # Simplified
                sentiment_score = self.analyze_market_sentiment(symbol, news_data)
                
                # Calculate risk score
                beta = live_data.get('beta', 1.0)
                risk_score = self.calculate_risk_score(symbol, volatility, beta)
                
                # Create stock analysis
                analysis = StockAnalysis(
                    symbol=symbol,
                    current_price=live_data['current_price'],
                    historical_volatility=volatility,
                    growth_potential_score=growth_potential,
                    sentiment_score=sentiment_score,
                    risk_score=risk_score,
                    recommended_allocation=0,  # Will be calculated later
                    allocation_amount=0
                )
                
                stock_analyses.append(analysis)
            
            # Calculate position sizing
            optimized_stocks = self.calculate_position_sizing(user_profile, stock_analyses)
            
            # Generate comprehensive summary
            total_risk = np.mean([stock.risk_score for stock in optimized_stocks])
            total_growth_potential = np.mean([stock.growth_potential_score for stock in optimized_stocks])
            portfolio_sentiment = np.mean([stock.sentiment_score for stock in optimized_stocks])
            
            # Risk assessment
            risk_level = "High" if total_risk > 0.7 else "Medium" if total_risk > 0.4 else "Low"
            
            # Investment recommendations
            recommendations = []
            for stock in optimized_stocks[:5]:  # Top 5 recommendations
                recommendations.append({
                    'symbol': stock.symbol,
                    'current_price': stock.current_price,
                    'allocation_percentage': round(stock.recommended_allocation * 100, 2),
                    'investment_amount': round(stock.allocation_amount, 2),
                    'growth_score': round(stock.growth_potential_score, 3),
                    'risk_score': round(stock.risk_score, 3),
                    'sentiment_score': round(stock.sentiment_score, 3),
                    'reasoning': f"Growth potential: {stock.growth_potential_score:.1%}, Risk: {risk_level}, Sentiment: {'Positive' if stock.sentiment_score > 0.6 else 'Neutral' if stock.sentiment_score > 0.4 else 'Negative'}"
                })
            
            return {
                'user_profile': {
                    'budget': user_profile.budget,
                    'risk_level': user_profile.risk_level,
                    'time_horizon': user_profile.time_horizon,
                    'sector_preferences': user_profile.sector_preferences
                },
                'portfolio_analysis': {
                    'total_risk_score': round(total_risk, 3),
                    'growth_potential': round(total_growth_potential, 3),
                    'market_sentiment': round(portfolio_sentiment, 3),
                    'risk_level': risk_level,
                    'diversification': len(set(stock.symbol for stock in optimized_stocks))
                },
                'recommendations': recommendations,
                'risk_factors': [
                    f"Portfolio volatility: {total_risk:.1%}",
                    f"Market sentiment: {'Positive' if portfolio_sentiment > 0.6 else 'Mixed' if portfolio_sentiment > 0.4 else 'Negative'}",
                    f"Concentration risk: {'Low' if len(recommendations) >= 5 else 'Medium' if len(recommendations) >= 3 else 'High'}",
                    f"Time horizon compatibility: {'Good' if user_profile.time_horizon == 'long' else 'Moderate' if user_profile.time_horizon == 'medium' else 'Consider longer horizon'}"
                ],
                'summary': f"Based on your ${user_profile.budget:,.0f} budget and {user_profile.risk_level} risk tolerance, we recommend a diversified portfolio with {len(recommendations)} stocks. Expected growth potential: {total_growth_potential:.1%}, Portfolio risk: {risk_level}.",
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def analyze_trade_decision(self, company_symbol: str, analysis_type: str = "comprehensive") -> Dict:
        """Run the trade decision analysis workflow"""
        try:
            # Create agents
            research_agent = self.create_research_agent()
            analysis_agent = self.create_analysis_agent()
            decision_agent = self.create_decision_agent()
            
            # Create tasks
            research_task = Task(
                description=f"""
                Research comprehensive information about {company_symbol} including:
                1. Recent news and developments
                2. Current stock price and trading volume
                3. Financial metrics and performance indicators
                4. Market sentiment and analyst opinions
                5. Industry trends affecting the company
                
                Provide a detailed research report with all findings.
                """,
                agent=research_agent,
                expected_output="A comprehensive research report with current market data and news"
            )
            
            analysis_task = Task(
                description=f"""
                Based on the research data for {company_symbol}, perform:
                1. Technical analysis of price trends and patterns
                2. Fundamental analysis of financial health
                3. Sentiment analysis of market and news sentiment
                4. Risk assessment and market condition evaluation
                5. Comparative analysis with industry peers
                
                Provide detailed analysis with key insights and risk factors.
                """,
                agent=analysis_agent,
                expected_output="Detailed financial analysis with insights and risk assessment"
            )
            
            decision_task = Task(
                description=f"""
                Based on the research and analysis for {company_symbol}, provide:
                1. Clear investment recommendation (BUY/SELL/HOLD)
                2. Confidence level (High/Medium/Low)
                3. Target price range and timeline
                4. Key risk factors to monitor
                5. Rationale for the recommendation
                
                Consider the analysis type: {analysis_type}
                """,
                agent=decision_agent,
                expected_output="Investment recommendation with rationale and risk assessment"
            )
            
            # Create and run crew
            crew = Crew(
                agents=[research_agent, analysis_agent, decision_agent],
                tasks=[research_task, analysis_task, decision_task],
                process=Process.sequential,
                verbose=True
            )
            
            # Execute the workflow
            result = crew.kickoff()
            
            # Process and structure the result
            decision_data = {
                "symbol": company_symbol,
                "timestamp": datetime.now().isoformat(),
                "analysis_type": analysis_type,
                "recommendation": self._extract_recommendation(str(result)),
                "full_analysis": str(result),
                "confidence": "Medium"  # Default, could be extracted from result
            }
            
            # Save to memory
            self.decision_history.append(decision_data)
            self._save_memory()
            
            # Generate summary using OpenAI
            summary = await self._generate_summary(decision_data["full_analysis"])
            decision_data["summary"] = summary
            
            return decision_data
            
        except Exception as e:
            print(f"Error in trade analysis: {e}")
            return {
                "symbol": company_symbol,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "recommendation": "HOLD",
                "summary": f"Analysis failed due to error: {str(e)}"
            }
    
    def _extract_recommendation(self, analysis_text: str) -> str:
        """Extract recommendation from analysis text"""
        text_upper = analysis_text.upper()
        if "BUY" in text_upper and "SELL" not in text_upper:
            return "BUY"
        elif "SELL" in text_upper:
            return "SELL"
        else:
            return "HOLD"
    
    async def _generate_summary(self, full_analysis: str) -> str:
        """Generate a concise summary using Granite model via Ollama"""
        try:
            system_message = "You are a financial analyst. Summarize the following investment analysis in 2-3 sentences, highlighting the key recommendation and main reasoning. Be concise and focus on actionable insights."
            
            prompt = f"Summarize this investment analysis:\n\n{full_analysis[:2000]}..."  # Limit input length
            
            # Call Granite model
            summary = await self._call_granite_model(prompt, system_message)
            
            # Fallback to OpenAI if Granite fails
            if summary.startswith("Error") or summary.startswith("Granite model error"):
                print("Granite model failed, falling back to OpenAI...")
                return await self._generate_summary_openai(full_analysis)
            
            return summary
            
        except Exception as e:
            print(f"Granite summary generation failed: {e}")
            # Fallback to OpenAI
            return await self._generate_summary_openai(full_analysis)
    
    async def _generate_summary_openai(self, full_analysis: str) -> str:
        """Fallback summary generation using OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial analyst. Summarize the following investment analysis in 2-3 sentences, highlighting the key recommendation and main reasoning."
                    },
                    {
                        "role": "user",
                        "content": f"Summarize this investment analysis: {full_analysis}"
                    }
                ],
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Summary generation failed: {str(e)}"
    
    async def get_decision_history(self) -> List[Dict]:
        """Get the history of trade decisions"""
        return self.decision_history[-10:]  # Return last 10 decisions
