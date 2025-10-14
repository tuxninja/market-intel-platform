"""
News Collection Module

This module provides functionality to collect financial news from multiple sources
including RSS feeds and NewsAPI. It filters news relevant to specific stocks and
provides caching to minimize API usage while staying within free tier limits.

Dependencies:
    - aiohttp: For async HTTP requests to NewsAPI
    - feedparser: For parsing RSS feeds (unlimited, free)
    - newsapi: Optional API key for enhanced news coverage (100 req/day free)

Author: Market Intelligence Platform
"""

import aiohttp
import feedparser
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


class NewsCollector:
    """
    Collects and filters financial news from multiple sources.

    This class aggregates news from RSS feeds (free) and optionally from NewsAPI
    (100 requests/day free tier). It filters content for relevance to specific
    stocks and caches results to minimize API usage.

    Attributes:
        newsapi_key (Optional[str]): API key for NewsAPI (optional)
        rss_feeds (List[str]): List of RSS feed URLs to monitor
        cache (Dict): In-memory cache for news articles
        cache_expiry (Dict): Cache expiration tracking
    """

    def __init__(self, newsapi_key: Optional[str] = None):
        """
        Initialize NewsCollector with optional NewsAPI key.

        Args:
            newsapi_key (Optional[str]): NewsAPI key for enhanced coverage.
                                       If None, only RSS feeds will be used.
        """
        self.newsapi_key = newsapi_key
        # Free RSS feeds - no API limits
        self.rss_feeds = [
            "https://feeds.finance.yahoo.com/rss/2.0/headline",
            "https://www.marketwatch.com/rss/topstories",
            "https://feeds.reuters.com/reuters/businessNews",
            "https://rss.cnn.com/rss/money_latest.rss",
            "https://feeds.bloomberg.com/markets/news.rss",
            "https://feeds.feedburner.com/TheMotleyFool",
            "https://seekingalpha.com/market_currents.xml",
            "https://finance.yahoo.com/rss/",
            "https://www.cnbc.com/id/100003114/device/rss/rss.html",
            "https://feeds.feedburner.com/techcrunch/startups",
        ]
        self.cache = {}
        self.cache_expiry = {}

    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """
        Parse various date formats from news sources.

        Args:
            date_str (Optional[str]): Date string from news source

        Returns:
            datetime: Parsed datetime object, current time if parsing fails

        Handles:
            - ISO 8601 format (NewsAPI)
            - RSS date format (RFC 2822)
            - Falls back to current time for unparseable dates
        """
        if not date_str:
            return datetime.now()

        try:
            if "T" in date_str and "Z" in date_str:
                # Handle ISO format with timezone
                parsed = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                # Convert to naive datetime for consistency
                return parsed.replace(tzinfo=None)
            else:
                # Handle RSS format - try multiple common formats
                try:
                    parsed = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
                    # Convert to naive datetime for consistency
                    return parsed.replace(tzinfo=None)
                except ValueError:
                    # Try without timezone
                    return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S")
        except Exception as e:
            logger.debug(f"Date parsing failed for '{date_str}': {e}")
            return datetime.now()

    def _deduplicate_news(self, articles: List[Dict]) -> List[Dict]:
        """
        Remove duplicate articles based on normalized titles.

        Args:
            articles (List[Dict]): List of news articles

        Returns:
            List[Dict]: Deduplicated list of articles

        Method:
            Creates normalized title keys by removing punctuation and
            converting to lowercase, then filters duplicates.
        """
        seen_titles = set()
        unique_articles = []

        for article in articles:
            title_key = re.sub(r"[^\w\s]", "", article["title"].lower())
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)

        return unique_articles
