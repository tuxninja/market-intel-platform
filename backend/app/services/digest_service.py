"""
Digest service for generating market intelligence reports.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.signal import Signal
from app.schemas.digest import DigestItemResponse, DigestResponse

# Import core modules (these will need to be adapted for async if needed)
# For now, we'll create a simplified version that works with the structure

logger = logging.getLogger(__name__)


class DigestService:
    """
    Service for generating and managing market intelligence digests.

    Coordinates news collection, sentiment analysis, and ML enhancement
    to produce actionable trading insights.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize digest service.

        Args:
            db: Database session for signal storage
        """
        self.db = db

    async def generate_daily_digest(
        self,
        max_items: int = 20,
        hours_lookback: int = 24,
        enable_ml: bool = True,
        categories: Optional[List[str]] = None,
    ) -> DigestResponse:
        """
        Generate daily market intelligence digest.

        Args:
            max_items: Maximum number of items to include
            hours_lookback: Hours to look back for news
            enable_ml: Whether to enable ML enhancement
            categories: Filter by specific categories

        Returns:
            Complete digest with trade alerts, watch list, and market context

        Example:
            digest = await service.generate_daily_digest(max_items=20, hours_lookback=24)
        """
        logger.info(f"Generating digest: max_items={max_items}, lookback={hours_lookback}h")

        # Calculate cutoff time
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_lookback)

        # Build query
        query = select(Signal).where(Signal.created_at >= cutoff_time)

        if categories:
            query = query.where(Signal.category.in_(categories))

        query = query.order_by(Signal.confidence_score.desc(), Signal.created_at.desc())
        query = query.limit(max_items)

        # Execute query
        result = await self.db.execute(query)
        signals = result.scalars().all()

        # Convert to response format
        items = [
            DigestItemResponse(
                id=signal.id,
                symbol=signal.symbol,
                title=signal.title,
                summary=signal.summary,
                explanation=signal.explanation,
                how_to_trade=signal.how_to_trade,
                sentiment_score=signal.sentiment_score,
                confidence_score=signal.confidence_score,
                priority=signal.priority,
                category=signal.category,
                source=signal.source,
                metadata=signal.metadata,
                created_at=signal.created_at,
            )
            for signal in signals
        ]

        # Generate market context (placeholder for now)
        market_context = await self._get_market_context()

        # Generate VIX regime info (placeholder for now)
        vix_regime = await self._get_vix_regime()

        return DigestResponse(
            generated_at=datetime.utcnow(),
            items=items,
            total_items=len(items),
            market_context=market_context,
            vix_regime=vix_regime,
        )

    async def save_signal(
        self,
        symbol: Optional[str],
        title: str,
        summary: str,
        explanation: Optional[str] = None,
        how_to_trade: Optional[str] = None,
        sentiment_score: Optional[float] = None,
        confidence_score: Optional[float] = None,
        priority: str = "medium",
        category: str = "market_context",
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Signal:
        """
        Save a signal to the database.

        Args:
            symbol: Stock ticker symbol
            title: Signal headline
            summary: Brief summary
            explanation: WHY THIS MATTERS explanation
            how_to_trade: HOW TO TRADE guidance
            sentiment_score: Sentiment score (-1 to 1)
            confidence_score: Confidence score (0 to 1)
            priority: Signal priority (high, medium, low)
            category: Signal category
            source: Data source
            metadata: Additional metadata

        Returns:
            Created Signal object
        """
        signal = Signal(
            symbol=symbol,
            title=title,
            summary=summary,
            explanation=explanation,
            how_to_trade=how_to_trade,
            sentiment_score=sentiment_score,
            confidence_score=confidence_score,
            priority=priority,
            category=category,
            source=source,
            metadata=metadata,
        )

        self.db.add(signal)
        await self.db.commit()
        await self.db.refresh(signal)

        logger.info(f"Saved signal: {signal.id} - {signal.title}")
        return signal

    async def _get_market_context(self) -> Dict[str, Any]:
        """
        Get overall market context information.

        Returns:
            Market context dictionary
        """
        # Placeholder - would fetch real market data
        return {
            "market_trend": "bullish",
            "major_indices": {
                "SPY": {"change": "+0.5%", "level": 450.0},
                "QQQ": {"change": "+0.8%", "level": 380.0},
            },
            "sector_rotation": "Technology leading",
        }

    async def _get_vix_regime(self) -> Dict[str, Any]:
        """
        Get VIX market regime information.

        Returns:
            VIX regime dictionary
        """
        # Placeholder - would fetch real VIX data
        return {
            "vix_level": 15.5,
            "regime": "LOW_VOL",
            "description": "Low volatility - favorable for momentum strategies",
        }
