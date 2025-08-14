import os
import re
import asyncio
import aiohttp
import feedparser
from typing import List, Dict
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from dotenv import load_dotenv

load_dotenv()

class NewsService:
    def __init__(self):
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        self.news_sources = [
            "https://feeds.finance.yahoo.com/rss/2.0/headline",
            "https://www.reuters.com/business/finance",
            "https://feeds.bloomberg.com/markets/news.rss"
        ]
    
    async def get_company_news(self, symbols: List[str]) -> List[Dict]:
        """Get news for specific company symbols"""
        try:
            all_news = []
            
            for symbol in symbols:
                # Use Serper API to search for company news
                news_items = await self._search_company_news(symbol)
                all_news.extend(news_items)
            
            # Sort by date and return recent news
            sorted_news = sorted(all_news, key=lambda x: x.get('date', ''), reverse=True)
            return sorted_news[:20]  # Return top 20 news items
            
        except Exception as e:
            print(f"Error fetching company news: {e}")
            return self._get_sample_news("company")
    
    async def get_general_financial_news(self) -> List[Dict]:
        """Get general financial news from RSS feeds"""
        try:
            all_news = []
            
            # Fetch from RSS feeds
            for feed_url in self.news_sources:
                try:
                    news_items = await self._fetch_rss_news(feed_url)
                    all_news.extend(news_items)
                except Exception as e:
                    print(f"Error fetching from {feed_url}: {e}")
                    continue
            
            # Also search for general financial news using Serper
            serper_news = await self._search_financial_news()
            all_news.extend(serper_news)
            
            # Remove duplicates and sort
            unique_news = self._deduplicate_news(all_news)
            sorted_news = sorted(unique_news, key=lambda x: x.get('date', ''), reverse=True)
            
            return sorted_news[:15]  # Return top 15 news items
            
        except Exception as e:
            print(f"Error fetching general news: {e}")
            return self._get_sample_news("general")
    
    async def _search_company_news(self, symbol: str) -> List[Dict]:
        """Search for company-specific news using Serper API"""
        try:
            if not self.serper_api_key:
                return []
            
            async with aiohttp.ClientSession() as session:
                url = "https://google.serper.dev/news"
                headers = {
                    "X-API-KEY": self.serper_api_key,
                    "Content-Type": "application/json"
                }
                payload = {
                    "q": f"{symbol} stock financial news",
                    "num": 5
                }
                
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_serper_news(data, symbol)
                    else:
                        print(f"Serper API error: {response.status}")
                        return []
        except Exception as e:
            print(f"Error searching company news for {symbol}: {e}")
            return []
    
    async def _search_financial_news(self) -> List[Dict]:
        """Search for general financial news using Serper API"""
        try:
            if not self.serper_api_key:
                return []
            
            async with aiohttp.ClientSession() as session:
                url = "https://google.serper.dev/news"
                headers = {
                    "X-API-KEY": self.serper_api_key,
                    "Content-Type": "application/json"
                }
                payload = {
                    "q": "financial markets stock market news today",
                    "num": 10
                }
                
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_serper_news(data)
                    else:
                        print(f"Serper API error: {response.status}")
                        return []
        except Exception as e:
            print(f"Error searching financial news: {e}")
            return []
    
    async def _fetch_rss_news(self, feed_url: str) -> List[Dict]:
        """Fetch news from RSS feeds"""
        try:
            # Note: In a real implementation, you'd want to use aiohttp for async RSS parsing
            # For now, we'll use feedparser (which is synchronous)
            feed = feedparser.parse(feed_url)
            
            news_items = []
            for entry in feed.entries[:5]:  # Limit to 5 items per feed
                news_item = {
                    "title": entry.get('title', 'No title'),
                    "description": entry.get('summary', entry.get('description', 'No description')),
                    "url": entry.get('link', ''),
                    "date": self._parse_date(entry.get('published', '')),
                    "source": feed.feed.get('title', 'RSS Feed'),
                    "type": "rss"
                }
                news_items.append(news_item)
            
            return news_items
        except Exception as e:
            print(f"Error parsing RSS feed {feed_url}: {e}")
            return []
    
    def _parse_serper_news(self, data: Dict, symbol: str = None) -> List[Dict]:
        """Parse news data from Serper API response"""
        news_items = []
        
        if 'news' in data:
            for item in data['news']:
                # Parse the date properly
                raw_date = item.get('date', '')
                formatted_date = self._parse_date(raw_date) if raw_date else datetime.now().isoformat()
                
                news_item = {
                    "title": item.get('title', 'No title'),
                    "description": item.get('snippet', 'No description'),
                    "url": item.get('link', ''),
                    "date": formatted_date,
                    "source": item.get('source', 'Unknown'),
                    "type": "serper",
                    "symbol": symbol if symbol else None
                }
                news_items.append(news_item)
        
        return news_items
    
    def _parse_date(self, date_string: str) -> str:
        """Parse and normalize date string"""
        try:
            if not date_string or date_string.strip() == "":
                return datetime.now().isoformat()
            
            date_string = date_string.strip()
            
            # Handle relative time formats like "4 days ago", "1 week ago", etc.
            if "ago" in date_string.lower():
                return self._parse_relative_date(date_string)
            
            # Try to parse standard date formats
            parsed_date = date_parser.parse(date_string)
            
            # Convert timezone-aware datetime to timezone-naive for comparison
            if parsed_date.tzinfo is not None:
                parsed_date = parsed_date.replace(tzinfo=None)
                
            # Validate that the date is reasonable (not too far in past/future)
            now = datetime.now()
            time_diff = abs((now - parsed_date).days)
            
            if time_diff > 365:  # More than a year difference
                return datetime.now().isoformat()
                
            return parsed_date.isoformat()
        except Exception as e:
            print(f"Date parsing error for '{date_string}': {e}")
            return datetime.now().isoformat()
    
    def _parse_relative_date(self, relative_string: str) -> str:
        """Parse relative date strings like '4 days ago', '1 week ago'"""
        try:
            relative_string = relative_string.lower().strip()
            now = datetime.now()
            
            # Extract number and unit
            match = re.match(r'(\d+)\s+(minute|hour|day|week|month|year)s?\s+ago', relative_string)
            if not match:
                return now.isoformat()
            
            number = int(match.group(1))
            unit = match.group(2)
            
            if unit == 'minute':
                target_date = now - timedelta(minutes=number)
            elif unit == 'hour':
                target_date = now - timedelta(hours=number)
            elif unit == 'day':
                target_date = now - timedelta(days=number)
            elif unit == 'week':
                target_date = now - timedelta(weeks=number)
            elif unit == 'month':
                target_date = now - timedelta(days=number * 30)  # Approximate
            elif unit == 'year':
                target_date = now - timedelta(days=number * 365)  # Approximate
            else:
                return now.isoformat()
            
            return target_date.isoformat()
            
        except Exception as e:
            print(f"Relative date parsing error for '{relative_string}': {e}")
            return datetime.now().isoformat()
    
    def _deduplicate_news(self, news_items: List[Dict]) -> List[Dict]:
        """Remove duplicate news items based on title similarity"""
        unique_news = []
        seen_titles = set()
        
        for item in news_items:
            title_lower = item.get('title', '').lower()
            # Simple deduplication based on first few words
            title_key = ' '.join(title_lower.split()[:5])
            
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_news.append(item)
        
        return unique_news
    
    def _get_sample_news(self, news_type: str) -> List[Dict]:
        """Return sample news data as fallback"""
        sample_news = [
            {
                "title": "Market Analysis: Tech Stocks Show Strong Performance",
                "description": "Technology sector continues to outperform broader market indices amid strong earnings reports.",
                "url": "https://example.com/news1",
                "date": datetime.now().isoformat(),
                "source": "Financial Times",
                "type": "sample"
            },
            {
                "title": "Federal Reserve Maintains Interest Rate Policy",
                "description": "Central bank keeps rates steady as inflation shows signs of stabilizing.",
                "url": "https://example.com/news2",
                "date": (datetime.now() - timedelta(hours=2)).isoformat(),
                "source": "Reuters",
                "type": "sample"
            },
            {
                "title": "Quarterly Earnings Season Kicks Off",
                "description": "Major corporations begin reporting Q4 earnings with mixed expectations.",
                "url": "https://example.com/news3",
                "date": (datetime.now() - timedelta(hours=4)).isoformat(),
                "source": "Bloomberg",
                "type": "sample"
            }
        ]
        
        if news_type == "company":
            sample_news[0]["title"] = "Company-Specific Financial Update"
            sample_news[0]["description"] = "Latest developments in corporate financial performance."
        
        return sample_news
