"""
NewsAPI Service

Provides real news articles using NewsAPI.org.
Free tier: 100 requests per day.
"""

import logging
import os
from typing import List, Optional
from datetime import datetime, timedelta
import aiohttp

logger = logging.getLogger(__name__)


class NewsAPIArticle:
    """News article from NewsAPI."""

    def __init__(self, data: dict):
        self.title = data.get("title", "")
        self.description = data.get("description", "")
        self.url = data.get("url", "")
        self.source = data.get("source", {}).get("name", "Unknown")
        self.published = self._parse_date(data.get("publishedAt"))
        self.content = data.get("content", "")
        self.sentiment_score = 0.0  # Will be calculated separately

    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse ISO date string."""
        if not date_str:
            return datetime.utcnow()
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except:
            return datetime.utcnow()


class NewsAPIService:
    """Service for fetching news from NewsAPI.org."""

    BASE_URL = "https://newsapi.org/v2"

    def __init__(self):
        """Initialize NewsAPI service."""
        self.api_key = os.getenv("NEWSAPI_KEY")
        if not self.api_key:
            logger.warning("NEWSAPI_KEY not set - news data will be unavailable")

    async def get_symbol_news(
        self,
        symbol: str,
        hours_lookback: int = 24,
        max_articles: int = 10
    ) -> List[NewsAPIArticle]:
        """
        Get recent news articles for a stock symbol.

        Args:
            symbol: Stock ticker symbol
            hours_lookback: Hours to look back
            max_articles: Maximum number of articles to return

        Returns:
            List of NewsAPIArticle objects
        """
        if not self.api_key:
            logger.warning("NewsAPI key not configured")
            return []

        try:
            # Calculate date range
            to_date = datetime.utcnow()
            from_date = to_date - timedelta(hours=hours_lookback)

            # Search for company name or symbol
            query = f"{symbol} OR stock OR shares"

            params = {
                "q": query,
                "from": from_date.isoformat(),
                "to": to_date.isoformat(),
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": max_articles,
                "apiKey": self.api_key
            }

            async with aiohttp.ClientSession() as session:
                url = f"{self.BASE_URL}/everything"
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        logger.error(f"NewsAPI error {response.status} for {symbol}")
                        return []

                    data = await response.json()

                    if data.get("status") != "ok":
                        logger.error(f"NewsAPI returned error: {data.get('message')}")
                        return []

                    articles = data.get("articles", [])
                    return [NewsAPIArticle(article) for article in articles]

        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []

    async def get_market_news(
        self,
        hours_lookback: int = 24,
        max_articles: int = 20
    ) -> List[NewsAPIArticle]:
        """
        Get general market/business news.

        Args:
            hours_lookback: Hours to look back
            max_articles: Maximum number of articles

        Returns:
            List of NewsAPIArticle objects
        """
        if not self.api_key:
            return []

        try:
            to_date = datetime.utcnow()
            from_date = to_date - timedelta(hours=hours_lookback)

            params = {
                "category": "business",
                "country": "us",
                "from": from_date.isoformat(),
                "pageSize": max_articles,
                "apiKey": self.api_key
            }

            async with aiohttp.ClientSession() as session:
                url = f"{self.BASE_URL}/top-headlines"
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        logger.error(f"NewsAPI error {response.status}")
                        return []

                    data = await response.json()

                    if data.get("status") != "ok":
                        logger.error(f"NewsAPI error: {data.get('message')}")
                        return []

                    articles = data.get("articles", [])
                    return [NewsAPIArticle(article) for article in articles]

        except Exception as e:
            logger.error(f"Error fetching market news: {e}")
            return []


# Global service instance
newsapi_service = NewsAPIService()
