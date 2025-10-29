"""
Social Sentiment Service

Tracks social media sentiment from Reddit (WallStreetBets) and other sources.
Uses free APIs to detect trending stocks and retail trader sentiment.
"""

import logging
import aiohttp
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SocialMention:
    """Represents social media mention data for a stock."""

    def __init__(
        self,
        symbol: str,
        mentions: int,
        mentions_24h_ago: int,
        sentiment_score: float,
        rank: int,
        source: str = "reddit"
    ):
        self.symbol = symbol
        self.mentions = mentions
        self.mentions_24h_ago = mentions_24h_ago
        self.sentiment_score = sentiment_score
        self.rank = rank
        self.source = source

        # Calculate momentum (% change in mentions)
        if mentions_24h_ago > 0:
            self.momentum = ((mentions - mentions_24h_ago) / mentions_24h_ago) * 100
        else:
            self.momentum = 100.0 if mentions > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "mentions": self.mentions,
            "mentions_24h_ago": self.mentions_24h_ago,
            "momentum": round(self.momentum, 1),
            "sentiment_score": round(self.sentiment_score, 2),
            "rank": self.rank,
            "source": self.source,
            "hype_level": self._get_hype_level()
        }

    def _get_hype_level(self) -> str:
        """Categorize hype level based on momentum and mentions."""
        if self.momentum > 100 and self.mentions > 500:
            return "EXTREME"
        elif self.momentum > 50 and self.mentions > 200:
            return "HIGH"
        elif self.momentum > 20:
            return "MODERATE"
        else:
            return "STABLE"


class SocialSentimentService:
    """
    Service for tracking social media sentiment and trending stocks.

    Primary source: ApeWisdom API (Reddit WallStreetBets + other communities)
    Fallback: Tradestie API
    """

    APEWISDOM_BASE_URL = "https://apewisdom.io/api/v1.0"
    TRADESTIE_BASE_URL = "https://tradestie.com/api/v1/apps/reddit"

    # Common crypto tickers to filter out
    CRYPTO_TICKERS = {
        "BTC", "ETH", "DOGE", "ADA", "SOL", "XRP", "DOT", "MATIC", "LINK",
        "UNI", "AVAX", "ATOM", "LTC", "BCH", "XLM", "ALGO", "VET", "FIL",
        "AAVE", "COMP", "SNX", "MKR", "SUSHI", "CRV", "YFI", "BAL", "REN",
        "BNB", "SHIB", "LUNA", "FTT", "CRO", "NEAR", "APE", "GALA", "SAND",
        "MANA", "AXS", "ENJ", "CHZ", "BAT", "ZRX", "OMG", "KNC", "GRT"
    }

    def __init__(self):
        """Initialize social sentiment service."""
        self.timeout = aiohttp.ClientTimeout(total=15)

    async def get_trending_stocks(
        self,
        limit: int = 50,
        filter_by: str = "all-crypto",  # "all-crypto" gets stocks from multiple subreddits
        exclude_crypto: bool = True
    ) -> List[SocialMention]:
        """
        Get trending stocks from Reddit communities.

        Args:
            limit: Number of trending stocks to return
            filter_by: Filter type ("all-crypto" = stocks+crypto from multiple subs)
            exclude_crypto: If True, filter out known crypto tickers

        Returns:
            List of SocialMention objects sorted by mentions (stocks only if exclude_crypto=True)
        """
        # Try ApeWisdom first (better data)
        mentions = await self._fetch_apewisdom_trending(limit * 2, filter_by)  # Fetch more to account for filtering

        if mentions:
            logger.info(f"Got {len(mentions)} trending items from ApeWisdom")

            # Filter out crypto if requested
            if exclude_crypto:
                mentions = [m for m in mentions if m.symbol not in self.CRYPTO_TICKERS]
                logger.info(f"After filtering crypto: {len(mentions)} stocks remaining")

            return mentions[:limit]  # Return only requested limit

        # Fallback to Tradestie
        mentions = await self._fetch_tradestie_trending(limit * 2)  # Fetch more to account for filtering

        if mentions:
            logger.info(f"Got {len(mentions)} trending items from Tradestie")

            # Filter out crypto if requested
            if exclude_crypto:
                mentions = [m for m in mentions if m.symbol not in self.CRYPTO_TICKERS]
                logger.info(f"After filtering crypto: {len(mentions)} stocks remaining")

            return mentions[:limit]  # Return only requested limit

        logger.warning("No social sentiment data available from any source")
        return []

    async def _fetch_apewisdom_trending(
        self,
        limit: int,
        filter_by: str
    ) -> List[SocialMention]:
        """
        Fetch trending stocks from ApeWisdom API.

        API Docs: https://apewisdom.io/api/

        Returns stocks mentioned on:
        - r/wallstreetbets
        - r/stocks
        - r/investing
        - r/stockmarket
        - 4chan /biz/
        """
        try:
            url = f"{self.APEWISDOM_BASE_URL}/filter/{filter_by}"

            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"ApeWisdom API error: {response.status}")
                        return []

                    data = await response.json()

                    # Parse results
                    results = data.get("results", [])
                    mentions = []

                    for idx, item in enumerate(results[:limit], 1):
                        try:
                            symbol = item.get("ticker", "").upper()
                            if not symbol or len(symbol) > 5:  # Skip invalid tickers
                                continue

                            mention = SocialMention(
                                symbol=symbol,
                                mentions=item.get("mentions") or 0,
                                mentions_24h_ago=item.get("mentions_24h_ago") or 0,
                                sentiment_score=item.get("sentiment") or 0.0,
                                rank=idx,
                                source="reddit_multi"
                            )
                            mentions.append(mention)

                        except Exception as e:
                            logger.warning(f"Error parsing ApeWisdom item: {e}")
                            continue

                    return mentions

        except Exception as e:
            logger.error(f"Error fetching ApeWisdom data: {e}")
            return []

    async def _fetch_tradestie_trending(self, limit: int) -> List[SocialMention]:
        """
        Fetch trending stocks from Tradestie API (r/wallstreetbets only).

        Fallback API with simpler data format.
        """
        try:
            url = f"{self.TRADESTIE_BASE_URL}"

            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"Tradestie API error: {response.status}")
                        return []

                    data = await response.json()
                    mentions = []

                    for idx, item in enumerate(data[:limit], 1):
                        try:
                            symbol = item.get("ticker", "").upper()
                            if not symbol or len(symbol) > 5:
                                continue

                            # Tradestie doesn't provide 24h ago data
                            current_mentions = item.get("no_of_comments", 0)

                            mention = SocialMention(
                                symbol=symbol,
                                mentions=current_mentions,
                                mentions_24h_ago=int(current_mentions * 0.8),  # Estimate
                                sentiment_score=item.get("sentiment") or 0.0,
                                rank=idx,
                                source="wallstreetbets"
                            )
                            mentions.append(mention)

                        except Exception as e:
                            logger.warning(f"Error parsing Tradestie item: {e}")
                            continue

                    return mentions

        except Exception as e:
            logger.error(f"Error fetching Tradestie data: {e}")
            return []

    async def get_symbol_social_data(self, symbol: str) -> Optional[SocialMention]:
        """
        Get social sentiment data for a specific stock symbol.

        Args:
            symbol: Stock ticker symbol

        Returns:
            SocialMention object if found, None otherwise
        """
        trending = await self.get_trending_stocks(limit=100)

        for mention in trending:
            if mention.symbol == symbol.upper():
                return mention

        return None

    def calculate_hype_score(
        self,
        social_mention: Optional[SocialMention],
        news_sentiment: float = 0.0
    ) -> float:
        """
        Calculate combined hype score from social + news sentiment.

        Formula:
        - Social momentum: 30%
        - Social sentiment: 20%
        - News sentiment: 50%

        Args:
            social_mention: Social media mention data
            news_sentiment: News sentiment score (-1 to 1)

        Returns:
            Hype score from 0 to 1
        """
        if not social_mention:
            # No social data, rely on news only
            return (news_sentiment + 1) / 2  # Convert -1 to 1 range to 0 to 1

        # Social momentum component (0 to 1)
        momentum_score = min(social_mention.momentum / 200, 1.0)  # Cap at 200% momentum

        # Social sentiment component (0 to 1)
        social_sentiment_score = (social_mention.sentiment_score + 1) / 2

        # News sentiment component (0 to 1)
        news_score = (news_sentiment + 1) / 2

        # Weighted combination
        hype_score = (
            momentum_score * 0.30 +
            social_sentiment_score * 0.20 +
            news_score * 0.50
        )

        return round(hype_score, 3)

    def is_trending(
        self,
        social_mention: Optional[SocialMention],
        min_mentions: int = 100,
        min_momentum: float = 20.0
    ) -> bool:
        """
        Check if a stock is trending on social media.

        Args:
            social_mention: Social mention data
            min_mentions: Minimum number of mentions
            min_momentum: Minimum momentum % required

        Returns:
            True if trending, False otherwise
        """
        if not social_mention:
            return False

        return (
            social_mention.mentions >= min_mentions and
            social_mention.momentum >= min_momentum
        )


# Global instance
social_sentiment_service = SocialSentimentService()
