"""
News Digest Analyzer Module

This module provides functionality to analyze financial news and generate
TLDR summaries with trading advice. It processes daily news from multiple
sources and categorizes them into actionable trading insights.

Dependencies:
    - textblob: For sentiment analysis and text processing
    - re: For pattern matching and text cleaning
    - datetime: For time-based filtering and caching

Author: Trade Ideas Analyzer
"""

import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None

logger = logging.getLogger(__name__)


class TradingAdvice(Enum):
    """Trading advice categories for news items."""

    TRADE_ALERT = "TRADE_ALERT"  # Strong buy/sell signal
    WATCH = "WATCH"              # Monitor closely
    INFO = "INFO"                # Background information


@dataclass
class NewsDigestItem:
    """Single news item in the digest."""

    title: str
    summary: str
    trading_advice: TradingAdvice
    advice_reason: str
    sentiment_score: float
    url: str
    published: datetime
    source: str
    affected_symbols: List[str]


class NewsDigestAnalyzer:
    """
    Analyzes financial news to generate TLDR summaries with trading advice.

    This class processes news articles and categorizes them into actionable
    trading insights using sentiment analysis, keyword detection, and
    market impact assessment.

    Attributes:
        cache (Dict): In-memory cache for processed news items
        cache_expiry (Dict): Cache expiration tracking
        market_keywords (Dict): Keywords for market impact detection
        trading_signals (Dict): Signal patterns for trading advice
    """

    def __init__(self):
        """Initialize the news digest analyzer."""
        self.cache = {}
        self.cache_expiry = {}

        # Market impact keywords - categorized by significance
        self.market_keywords = {
            'high_impact': [
                'earnings', 'revenue', 'guidance', 'forecast', 'outlook',
                'merger', 'acquisition', 'deal', 'partnership', 'contract',
                'fda approval', 'drug approval', 'clinical trial',
                'upgrade', 'downgrade', 'price target', 'analyst',
                'bankruptcy', 'lawsuit', 'investigation', 'regulation',
                'ceo', 'executive', 'management change', 'resignation',
                'ipo', 'spinoff', 'dividend', 'split', 'buyback'
            ],
            'medium_impact': [
                'sales', 'growth', 'decline', 'profit', 'loss',
                'competition', 'market share', 'product launch',
                'expansion', 'investment', 'funding', 'valuation',
                'trading volume', 'volatility', 'momentum'
            ],
            'sector_impact': [
                'tech sector', 'healthcare', 'financial', 'energy',
                'semiconductor', 'cloud', 'ai', 'electric vehicle',
                'streaming', 'e-commerce', 'biotech', 'crypto'
            ]
        }

        # Trading signal patterns
        self.trading_signals = {
            'strong_buy': [
                'beats expectations', 'exceeds forecast', 'strong growth',
                'record revenue', 'upgrade to buy', 'raised guidance',
                'positive surprise', 'breakthrough', 'milestone'
            ],
            'strong_sell': [
                'misses expectations', 'below forecast', 'disappointing',
                'cuts guidance', 'downgrade to sell', 'investigation',
                'lawsuit', 'scandal', 'bankruptcy', 'warning'
            ],
            'watch_positive': [
                'potential', 'exploring', 'considering', 'rumored',
                'may announce', 'preparing', 'upcoming', 'expected'
            ],
            'watch_negative': [
                'concerns', 'risks', 'challenges', 'uncertainty',
                'volatility', 'pressure', 'headwinds', 'caution'
            ]
        }

    async def generate_daily_digest(
        self,
        news_collector,
        max_items: int = 20,
        hours_lookback: int = 24
    ) -> List[NewsDigestItem]:
        """
        Generate daily news digest with trading insights.

        Args:
            news_collector: NewsCollector instance for fetching news
            max_items (int): Maximum number of digest items to return
            hours_lookback (int): Hours to look back for news

        Returns:
            List[NewsDigestItem]: Sorted list of digest items by priority

        Note:
            Results are cached for 2 hours to minimize processing overhead.
            Items are sorted by trading significance and recency.
        """
        cache_key = f"digest_{max_items}_{hours_lookback}"
        now = datetime.now()

        # Check cache first
        if (cache_key in self.cache and
            cache_key in self.cache_expiry and
            now < self.cache_expiry[cache_key]):
            return self.cache[cache_key]

        try:
            # Collect general financial news (not stock-specific)
            all_news = await self._collect_general_news(news_collector)

            # Filter by time
            cutoff_time = now - timedelta(hours=hours_lookback)
            recent_news = [
                article for article in all_news
                if article.get('published', now) > cutoff_time
            ]

            # Process each news item
            digest_items = []
            for article in recent_news[:max_items * 2]:  # Process more, filter later
                digest_item = self._analyze_news_item(article)
                if digest_item:
                    digest_items.append(digest_item)

            # Sort by priority and limit results
            digest_items = self._prioritize_digest_items(digest_items)
            digest_items = digest_items[:max_items]

            # Cache results
            self.cache[cache_key] = digest_items
            self.cache_expiry[cache_key] = now + timedelta(hours=2)

            logger.info(f"Generated digest with {len(digest_items)} items")
            return digest_items

        except Exception as e:
            logger.error(f"Error generating news digest: {e}")
            return []

    async def _collect_general_news(self, news_collector) -> List[Dict]:
        """
        Collect general financial news from all RSS sources.

        Args:
            news_collector: NewsCollector instance

        Returns:
            List[Dict]: Raw news articles from all sources
        """
        all_articles = []

        # Use RSS feeds directly for general news
        for feed_url in news_collector.rss_feeds:
            try:
                import feedparser
                feed = feedparser.parse(feed_url)

                for entry in feed.entries[:15]:  # Limit per source
                    title = entry.get('title', '')
                    summary = entry.get('summary', entry.get('description', ''))

                    article = {
                        'title': title,
                        'content': summary,
                        'url': entry.get('link', ''),
                        'published': news_collector._parse_date(entry.get('published')),
                        'source': self._get_source_name(feed_url)
                    }
                    all_articles.append(article)

            except Exception as e:
                logger.warning(f"Error parsing RSS feed {feed_url}: {e}")

        # Deduplicate
        return news_collector._deduplicate_news(all_articles)

    def _analyze_news_item(self, article: Dict) -> Optional[NewsDigestItem]:
        """
        Analyze a single news article and create digest item.

        Args:
            article (Dict): Raw news article data

        Returns:
            Optional[NewsDigestItem]: Processed digest item or None if not relevant
        """
        try:
            title = article.get('title', '')
            content = article.get('content', '')
            full_text = f"{title} {content}"

            # Skip if not financial news
            if not self._is_financial_news(full_text):
                return None

            # Generate TLDR summary
            summary = self._generate_tldr(title, content)

            # Analyze sentiment
            sentiment_score = self._analyze_sentiment(full_text)

            # Determine trading advice
            trading_advice, advice_reason = self._classify_trading_advice(
                full_text, sentiment_score
            )

            # Extract affected symbols
            affected_symbols = self._extract_symbols(full_text)

            return NewsDigestItem(
                title=title,
                summary=summary,
                trading_advice=trading_advice,
                advice_reason=advice_reason,
                sentiment_score=sentiment_score,
                url=article.get('url', ''),
                published=article.get('published', datetime.now()),
                source=article.get('source', 'Unknown'),
                affected_symbols=affected_symbols
            )

        except Exception as e:
            logger.error(f"Error analyzing news item: {e}")
            return None

    def _is_financial_news(self, content: str) -> bool:
        """
        Determine if content is relevant financial/trading news.

        Args:
            content (str): Full article text

        Returns:
            bool: True if content is financial news
        """
        content_lower = content.lower()

        # Financial keywords that indicate trading relevance
        financial_terms = [
            'stock', 'shares', 'market', 'trading', 'earnings', 'revenue',
            'profit', 'loss', 'analyst', 'investor', 'wall street',
            'nasdaq', 'nyse', 's&p', 'dow jones', 'portfolio',
            'bull market', 'bear market', 'volatility', 'ipo'
        ]

        # Must have at least 2 financial terms to be relevant
        financial_count = sum(1 for term in financial_terms if term in content_lower)
        return financial_count >= 2

    def _generate_tldr(self, title: str, content: str) -> str:
        """
        Generate TLDR summary from title and content.

        Args:
            title (str): Article title
            content (str): Article content

        Returns:
            str: Concise TLDR summary (1 sentence)
        """
        # Use title as base, enhance with key content points
        if not content or len(content.strip()) < 50:
            return title

        # Extract key information from content
        content_clean = re.sub(r'<[^>]+>', '', content)  # Remove HTML
        content_clean = re.sub(r'\s+', ' ', content_clean).strip()  # Normalize whitespace

        # Look for key financial metrics or events
        key_patterns = [
            r'(\$[\d,]+(?:\.\d+)?\s*(?:million|billion|trillion))',
            r'(\d+(?:\.\d+)?%)',
            r'(Q[1-4]\s+\d{4})',
            r'(earnings per share|EPS)',
            r'(revenue|sales|profit|loss)\s+(?:of|was|is)\s+(\$[\d,]+(?:\.\d+)?)',
        ]

        key_info = []
        for pattern in key_patterns:
            matches = re.findall(pattern, content_clean, re.IGNORECASE)
            key_info.extend([match if isinstance(match, str) else ' '.join(match) for match in matches])

        # Create TLDR
        if key_info:
            # Include most relevant key info
            key_detail = key_info[0] if key_info else ""
            summary = f"{title.rstrip('.')} ({key_detail})" if key_detail else title
        else:
            summary = title

        # Ensure it's not too long
        if len(summary) > 100:
            summary = summary[:97] + "..."

        return summary

    def _analyze_sentiment(self, content: str) -> float:
        """
        Analyze sentiment of news content.

        Args:
            content (str): News article text

        Returns:
            float: Sentiment score (-1 to 1, negative to positive)
        """
        if not TextBlob:
            # Fallback simple sentiment if TextBlob not available
            return self._simple_sentiment(content)

        try:
            blob = TextBlob(content)
            # TextBlob polarity ranges from -1 to 1
            return blob.sentiment.polarity
        except Exception:
            return self._simple_sentiment(content)

    def _simple_sentiment(self, content: str) -> float:
        """
        Simple sentiment analysis using keyword lists.

        Args:
            content (str): Text to analyze

        Returns:
            float: Sentiment score (-1 to 1)
        """
        content_lower = content.lower()

        positive_words = [
            'gain', 'rise', 'up', 'growth', 'increase', 'strong', 'beat',
            'exceed', 'positive', 'bull', 'rally', 'surge', 'breakthrough',
            'record', 'milestone', 'success', 'profit', 'boost'
        ]

        negative_words = [
            'fall', 'drop', 'down', 'decline', 'decrease', 'weak', 'miss',
            'disappoint', 'negative', 'bear', 'crash', 'plunge', 'concern',
            'risk', 'loss', 'warning', 'cut', 'reduce', 'pressure'
        ]

        pos_count = sum(1 for word in positive_words if word in content_lower)
        neg_count = sum(1 for word in negative_words if word in content_lower)

        total = pos_count + neg_count
        if total == 0:
            return 0.0

        return (pos_count - neg_count) / total

    def _classify_trading_advice(
        self,
        content: str,
        sentiment_score: float
    ) -> Tuple[TradingAdvice, str]:
        """
        Classify news into trading advice category.

        Args:
            content (str): News article content
            sentiment_score (float): Sentiment score (-1 to 1)

        Returns:
            Tuple[TradingAdvice, str]: Trading advice category and reason
        """
        content_lower = content.lower()

        # Check for strong trading signals
        for signal_type, keywords in self.trading_signals.items():
            matches = [kw for kw in keywords if kw in content_lower]
            if matches:
                if signal_type in ['strong_buy', 'strong_sell']:
                    reason = f"Strong signal: {matches[0]}"
                    return TradingAdvice.TRADE_ALERT, reason
                elif signal_type in ['watch_positive', 'watch_negative']:
                    reason = f"Watch signal: {matches[0]}"
                    return TradingAdvice.WATCH, reason

        # Check for high-impact events
        high_impact_matches = [
            kw for kw in self.market_keywords['high_impact']
            if kw in content_lower
        ]
        if high_impact_matches:
            if abs(sentiment_score) > 0.3:  # Strong sentiment
                reason = f"High impact event: {high_impact_matches[0]}"
                return TradingAdvice.TRADE_ALERT, reason
            else:
                reason = f"Monitor impact: {high_impact_matches[0]}"
                return TradingAdvice.WATCH, reason

        # Medium impact with strong sentiment
        medium_impact_matches = [
            kw for kw in self.market_keywords['medium_impact']
            if kw in content_lower
        ]
        if medium_impact_matches and abs(sentiment_score) > 0.4:
            reason = f"Notable development: {medium_impact_matches[0]}"
            return TradingAdvice.WATCH, reason

        # Default to INFO
        reason = "Market context"
        return TradingAdvice.INFO, reason

    def _extract_symbols(self, content: str) -> List[str]:
        """
        Extract stock symbols mentioned in the content.

        Args:
            content (str): News article content

        Returns:
            List[str]: List of stock symbols found
        """
        # Pattern to match stock symbols (3-5 capital letters)
        symbol_pattern = r'\b([A-Z]{3,5})\b'
        potential_symbols = re.findall(symbol_pattern, content)

        # Expanded company names to symbols (50+ major companies)
        company_to_symbol = {
            # FAANG + Big Tech
            'apple': 'AAPL', 'microsoft': 'MSFT', 'google': 'GOOGL', 'alphabet': 'GOOGL',
            'amazon': 'AMZN', 'tesla': 'TSLA', 'meta': 'META', 'facebook': 'META',
            'nvidia': 'NVDA', 'netflix': 'NFLX', 'oracle': 'ORCL',
            # Retail
            'walmart': 'WMT', 'target': 'TGT', 'costco': 'COST', 'home depot': 'HD',
            "lowe's": 'LOW', 'best buy': 'BBY', 'dollar general': 'DG',
            # Finance
            'jpmorgan': 'JPM', 'jp morgan': 'JPM', 'bank of america': 'BAC',
            'goldman sachs': 'GS', 'morgan stanley': 'MS', 'wells fargo': 'WFC',
            'citigroup': 'C', 'american express': 'AXP',
            # Tech/Software
            'salesforce': 'CRM', 'adobe': 'ADBE', 'intel': 'INTC', 'amd': 'AMD',
            'qualcomm': 'QCOM', 'broadcom': 'AVGO', 'cisco': 'CSCO',
            'ibm': 'IBM', 'servicenow': 'NOW', 'workday': 'WDAY',
            # Consumer
            'coca-cola': 'KO', 'coca cola': 'KO', 'pepsi': 'PEP', 'pepsico': 'PEP',
            'mcdonalds': 'MCD', "mcdonald's": 'MCD', 'starbucks': 'SBUX',
            'nike': 'NKE', 'procter & gamble': 'PG', 'johnson & johnson': 'JNJ',
            # Healthcare/Pharma
            'pfizer': 'PFE', 'moderna': 'MRNA', 'abbvie': 'ABBV',
            'merck': 'MRK', 'eli lilly': 'LLY', 'unitedhealth': 'UNH',
            # Automotive
            'ford': 'F', 'general motors': 'GM', 'gm': 'GM', 'rivian': 'RIVN',
            'lucid': 'LCID', 'nio': 'NIO',
            # Energy
            'exxon': 'XOM', 'chevron': 'CVX', 'conocophillips': 'COP',
            # Other
            'boeing': 'BA', 'disney': 'DIS', 'visa': 'V', 'mastercard': 'MA',
            'paypal': 'PYPL', 'square': 'SQ', 'uber': 'UBER', 'lyft': 'LYFT',
            'airbnb': 'ABNB', 'doordash': 'DASH', 'coinbase': 'COIN'
        }

        content_lower = content.lower()
        symbols_from_names = [
            symbol for company, symbol in company_to_symbol.items()
            if company in content_lower
        ]

        # Combine and deduplicate
        all_symbols = list(set(potential_symbols + symbols_from_names))

        # Filter out common false positives
        false_positives = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'NEW', 'GET', 'ITS', 'USA', 'CEO', 'IPO', 'ETF', 'ESG']
        symbols = [s for s in all_symbols if s not in false_positives]

        return symbols[:5]  # Limit to 5 symbols

    def _prioritize_digest_items(self, items: List[NewsDigestItem]) -> List[NewsDigestItem]:
        """
        Sort digest items by trading priority and recency.

        Args:
            items (List[NewsDigestItem]): Unordered digest items

        Returns:
            List[NewsDigestItem]: Sorted items by priority
        """
        def priority_score(item: NewsDigestItem) -> float:
            # Base score by advice type
            advice_scores = {
                TradingAdvice.TRADE_ALERT: 10.0,
                TradingAdvice.WATCH: 5.0,
                TradingAdvice.INFO: 1.0
            }
            score = advice_scores.get(item.trading_advice, 1.0)

            # Boost for strong sentiment
            score += abs(item.sentiment_score) * 3.0

            # Boost for having symbols
            score += len(item.affected_symbols) * 0.5

            # Recency boost (more recent = higher score)
            hours_ago = (datetime.now() - item.published).total_seconds() / 3600
            recency_boost = max(0, 24 - hours_ago) / 24  # 0 to 1
            score += recency_boost * 2.0

            return score

        return sorted(items, key=priority_score, reverse=True)

    def _get_source_name(self, feed_url: str) -> str:
        """
        Extract readable source name from RSS feed URL.

        Args:
            feed_url (str): RSS feed URL

        Returns:
            str: Human-readable source name
        """
        source_map = {
            'yahoo.com': 'Yahoo Finance',
            'marketwatch.com': 'MarketWatch',
            'reuters.com': 'Reuters',
            'cnn.com': 'CNN Business',
            'bloomberg.com': 'Bloomberg',
            'fool.com': 'Motley Fool',
            'seekingalpha.com': 'Seeking Alpha',
            'cnbc.com': 'CNBC',
            'techcrunch.com': 'TechCrunch'
        }

        for domain, name in source_map.items():
            if domain in feed_url:
                return name

        return 'Financial News'