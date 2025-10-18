"""
News Service Module

Fetches financial news and performs sentiment analysis.
Uses NewsAPI as primary source, RSS feeds as fallback.
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import feedparser
import aiohttp
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from app.services.newsapi_service import newsapi_service, NewsAPIArticle

logger = logging.getLogger(__name__)


class NewsArticle:
    """Represents a financial news article."""

    def __init__(
        self,
        title: str,
        summary: str,
        url: str,
        published: datetime,
        source: str,
        sentiment_score: Optional[float] = None
    ):
        self.title = title
        self.summary = summary
        self.url = url
        self.published = published
        self.source = source
        self.sentiment_score = sentiment_score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "summary": self.summary,
            "url": self.url,
            "published": self.published.isoformat() if isinstance(self.published, datetime) else self.published,
            "source": self.source,
            "sentiment_score": self.sentiment_score
        }


class NewsService:
    """
    Service for fetching financial news and analyzing sentiment.

    Uses free RSS feeds from major financial news sources.
    """

    # Free RSS feeds (no API key required)
    RSS_FEEDS = {
        "reuters": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
        "marketwatch": "https://www.marketwatch.com/rss/topstories",
        "cnbc": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664",
        "yahoo": "https://finance.yahoo.com/news/rssindex",
        "seeking_alpha": "https://seekingalpha.com/feed.xml",
    }

    def __init__(self):
        """Initialize news service."""
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    async def fetch_rss_feed(
        self,
        feed_url: str,
        source: str,
        hours_lookback: int = 24
    ) -> List[NewsArticle]:
        """
        Fetch articles from RSS feed.

        Args:
            feed_url: URL of RSS feed
            source: Source name
            hours_lookback: Only return articles from last N hours

        Returns:
            List of NewsArticle objects
        """
        try:
            # Parse RSS feed
            feed = feedparser.parse(feed_url)

            articles = []
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_lookback)

            for entry in feed.entries[:20]:  # Limit to 20 most recent
                try:
                    # Parse published date
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])
                    else:
                        published = datetime.utcnow()

                    # Filter by time
                    if published < cutoff_time:
                        continue

                    # Extract content
                    title = entry.get('title', '').strip()
                    summary = entry.get('summary', entry.get('description', '')).strip()
                    url = entry.get('link', '')

                    if not title or not summary:
                        continue

                    # Clean HTML tags from summary
                    summary = self._clean_html(summary)

                    article = NewsArticle(
                        title=title,
                        summary=summary,
                        url=url,
                        published=published,
                        source=source
                    )

                    articles.append(article)

                except Exception as e:
                    logger.warning(f"Error parsing RSS entry from {source}: {e}")
                    continue

            logger.info(f"Fetched {len(articles)} articles from {source}")
            return articles

        except Exception as e:
            logger.error(f"Error fetching RSS feed {source}: {e}")
            return []

    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from text."""
        import re
        # Remove HTML tags
        clean = re.sub('<.*?>', '', text)
        # Remove extra whitespace
        clean = ' '.join(clean.split())
        return clean

    async def fetch_all_news(
        self,
        hours_lookback: int = 24,
        max_articles: int = 50
    ) -> List[NewsArticle]:
        """
        Fetch news from all RSS feeds.

        Args:
            hours_lookback: Only return articles from last N hours
            max_articles: Maximum total articles to return

        Returns:
            List of NewsArticle objects sorted by published date
        """
        all_articles = []

        # Fetch from each feed
        for source, feed_url in self.RSS_FEEDS.items():
            articles = await self.fetch_rss_feed(feed_url, source, hours_lookback)
            all_articles.extend(articles)

        # Sort by published date (newest first)
        all_articles.sort(key=lambda x: x.published, reverse=True)

        # Limit total articles
        all_articles = all_articles[:max_articles]

        logger.info(f"Fetched {len(all_articles)} total articles from all sources")
        return all_articles

    def analyze_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of text using VADER.

        Args:
            text: Text to analyze

        Returns:
            Sentiment score from -1 (bearish) to +1 (bullish)
        """
        try:
            # VADER sentiment analysis
            vader_scores = self.sentiment_analyzer.polarity_scores(text)
            vader_compound = vader_scores['compound']

            # TextBlob sentiment analysis (for comparison)
            blob = TextBlob(text)
            textblob_polarity = blob.sentiment.polarity

            # Average the two methods
            sentiment = (vader_compound + textblob_polarity) / 2

            return round(sentiment, 3)

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return 0.0

    async def enrich_articles_with_sentiment(
        self,
        articles: List[NewsArticle]
    ) -> List[NewsArticle]:
        """
        Add sentiment scores to articles.

        Args:
            articles: List of NewsArticle objects

        Returns:
            Same list with sentiment_score populated
        """
        for article in articles:
            # Combine title and summary for sentiment analysis
            text = f"{article.title}. {article.summary}"
            article.sentiment_score = self.analyze_sentiment(text)

        return articles

    async def filter_relevant_news(
        self,
        articles: List[NewsArticle],
        symbols: Optional[List[str]] = None,
        min_sentiment_magnitude: float = 0.2
    ) -> List[NewsArticle]:
        """
        Filter news for relevance.

        Args:
            articles: List of NewsArticle objects
            symbols: Optional list of stock symbols to filter by
            min_sentiment_magnitude: Minimum absolute sentiment score

        Returns:
            Filtered list of articles
        """
        filtered = []

        for article in articles:
            # Filter by sentiment magnitude (ignore neutral articles)
            if article.sentiment_score is not None:
                if abs(article.sentiment_score) < min_sentiment_magnitude:
                    continue

            # Filter by symbols if provided
            if symbols:
                # Check if any symbol appears in title or summary
                text = f"{article.title} {article.summary}".upper()
                if not any(symbol.upper() in text for symbol in symbols):
                    continue

            filtered.append(article)

        logger.info(f"Filtered to {len(filtered)} relevant articles")
        return filtered

    async def get_market_news_summary(
        self,
        hours_lookback: int = 24,
        max_articles: int = 20
    ) -> Dict[str, Any]:
        """
        Get summarized market news with sentiment analysis.

        Args:
            hours_lookback: Only return articles from last N hours
            max_articles: Maximum articles to return

        Returns:
            Dict with news summary and sentiment breakdown
        """
        try:
            # Fetch all news
            articles = await self.fetch_all_news(hours_lookback, max_articles)

            # Enrich with sentiment
            articles = await self.enrich_articles_with_sentiment(articles)

            # Filter for relevant news (significant sentiment)
            relevant_articles = await self.filter_relevant_news(
                articles,
                min_sentiment_magnitude=0.15
            )

            # Calculate overall market sentiment
            if relevant_articles:
                avg_sentiment = sum(a.sentiment_score or 0 for a in relevant_articles) / len(relevant_articles)
            else:
                avg_sentiment = 0.0

            # Categorize by sentiment
            bullish = [a for a in relevant_articles if (a.sentiment_score or 0) > 0.2]
            bearish = [a for a in relevant_articles if (a.sentiment_score or 0) < -0.2]
            neutral = [a for a in relevant_articles if -0.2 <= (a.sentiment_score or 0) <= 0.2]

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "total_articles": len(articles),
                "relevant_articles": len(relevant_articles),
                "average_sentiment": round(avg_sentiment, 3),
                "bullish_count": len(bullish),
                "bearish_count": len(bearish),
                "neutral_count": len(neutral),
                "top_bullish": [a.to_dict() for a in bullish[:5]],
                "top_bearish": [a.to_dict() for a in bearish[:5]],
                "market_tone": self._classify_market_tone(avg_sentiment)
            }

        except Exception as e:
            logger.error(f"Error getting market news summary: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "total_articles": 0,
                "relevant_articles": 0,
                "average_sentiment": 0.0,
                "market_tone": "neutral"
            }

    def _classify_market_tone(self, sentiment: float) -> str:
        """Classify overall market tone based on sentiment."""
        if sentiment > 0.3:
            return "very_bullish"
        elif sentiment > 0.1:
            return "bullish"
        elif sentiment < -0.3:
            return "very_bearish"
        elif sentiment < -0.1:
            return "bearish"
        else:
            return "neutral"

    async def get_symbol_specific_news(
        self,
        symbol: str,
        hours_lookback: int = 24,
        max_articles: int = 10
    ) -> List[NewsArticle]:
        """
        Get news articles specific to a stock symbol.

        Args:
            symbol: Stock ticker symbol
            hours_lookback: Hours to look back
            max_articles: Max articles to return

        Returns:
            List of articles mentioning the symbol
        """
        try:
            # Try NewsAPI first
            newsapi_articles = await newsapi_service.get_symbol_news(symbol, hours_lookback, max_articles)

            if newsapi_articles:
                logger.info(f"Got {len(newsapi_articles)} articles for {symbol} from NewsAPI")
                # Convert NewsAPIArticle to NewsArticle and enrich with sentiment
                articles = []
                for api_article in newsapi_articles:
                    article = NewsArticle(
                        title=api_article.title,
                        summary=api_article.description or api_article.content,
                        url=api_article.url,
                        published=api_article.published,
                        source=api_article.source
                    )
                    # Add sentiment
                    text = f"{article.title}. {article.summary}"
                    article.sentiment_score = self.analyze_sentiment(text)
                    articles.append(article)

                return articles[:max_articles]

            # Fallback to RSS feeds
            logger.debug(f"NewsAPI failed for {symbol}, using RSS fallback")
            articles = await self.fetch_all_news(hours_lookback, max_articles * 3)

            # Enrich with sentiment
            articles = await self.enrich_articles_with_sentiment(articles)

            # Filter for symbol
            symbol_articles = await self.filter_relevant_news(
                articles,
                symbols=[symbol],
                min_sentiment_magnitude=0.0  # Include all sentiment levels
            )

            return symbol_articles[:max_articles]

        except Exception as e:
            logger.error(f"Error getting news for {symbol}: {e}")
            return []


# Global service instance
news_service = NewsService()
