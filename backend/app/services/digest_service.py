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
from app.services.signal_generator import signal_generator
from app.services.news_driven_signal_generator import create_news_driven_generator
from app.services.market_data_service import market_data_service

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

        # Generate real trading signals using NEWS-DRIVEN signal generator
        try:
            logger.info("🚀 Generating NEWS-DRIVEN trading signals (ML-powered with FinBERT)")

            # Use new ML-powered news-driven generator
            news_generator = create_news_driven_generator(self.db)
            items = await news_generator.generate_signals(max_signals=max_items)
            logger.info(f"✅ Generated {len(items)} news-driven signals")

            # If no news-driven signals, fall back to technical-only generator
            if not items:
                logger.warning("⚠️ No news-driven signals found, trying technical-only generator")
                items = await signal_generator.generate_signals(max_signals=max_items)
                logger.info(f"Generated {len(items)} technical signals as fallback")

            # If still no signals, use demo
            if not items:
                logger.warning("⚠️ No signals generated, falling back to demo signals")
                items = self._generate_demo_signals(max_items)
        except Exception as gen_error:
            logger.error(f"❌ Error generating signals: {gen_error}", exc_info=True)
            logger.warning("⚠️ Falling back to demo signals due to error")
            items = self._generate_demo_signals(max_items)

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
        Get overall market context information using real market data.

        Returns:
            Market context dictionary
        """
        try:
            # Get real market indices data
            indices = await market_data_service.get_market_indices()

            # Determine overall market trend based on SPY
            spy_data = indices.get("SPY", {})
            spy_change = spy_data.get("raw_change", 0)

            if spy_change > 0.5:
                market_trend = "bullish"
            elif spy_change < -0.5:
                market_trend = "bearish"
            else:
                market_trend = "neutral"

            return {
                "market_trend": market_trend,
                "major_indices": indices,
                "sector_rotation": "Data-driven analysis",  # Could enhance this later
            }
        except Exception as e:
            logger.error(f"Error fetching market context: {e}")
            # Fallback to placeholder data
            return {
                "market_trend": "neutral",
                "major_indices": {
                    "SPY": {"change": "N/A", "level": 0},
                    "DIA": {"change": "N/A", "level": 0},
                    "QQQ": {"change": "N/A", "level": 0},
                },
                "sector_rotation": "Unable to fetch data",
            }

    async def _get_vix_regime(self) -> Dict[str, Any]:
        """
        Get VIX market regime information using real VIX data.

        Returns:
            VIX regime dictionary
        """
        try:
            # Get real VIX regime data
            vix_regime = await market_data_service.get_vix_regime()
            return vix_regime
        except Exception as e:
            logger.error(f"Error fetching VIX regime: {e}")
            # Fallback to placeholder data
            return {
                "vix_level": 15.5,
                "regime": "NORMAL",
                "description": "Unable to fetch VIX data",
            }

    def _generate_demo_signals(self, max_items: int) -> List[DigestItemResponse]:
        """
        Generate demo signals for MVP/testing when database is not available.

        Args:
            max_items: Maximum number of signals to generate

        Returns:
            List of demo DigestItemResponse objects
        """
        now = datetime.utcnow()
        demo_signals = [
            DigestItemResponse(
                id=1,
                symbol="AAPL",
                title="Apple Shows Strong Momentum Above $180",
                summary="AAPL broke above key resistance with strong volume",
                explanation="**WHY THIS MATTERS**: Apple's breakout above $180 on increased volume suggests institutional accumulation. The stock has formed a bullish flag pattern after recent consolidation, indicating potential continuation of the uptrend.",
                how_to_trade="**HOW TO TRADE**: Consider entry around $182 with stop loss at $178. Target $190 for first take-profit. Position size 2-3% of portfolio.",
                sentiment_score=0.75,
                confidence_score=0.85,
                priority="high",
                category="trade_alert",
                source="technical_analysis",
                extra_data={"sector": "Technology"},
                created_at=now - timedelta(hours=2),
            ),
            DigestItemResponse(
                id=2,
                symbol="TSLA",
                title="Tesla Approaching Key Support Level",
                summary="TSLA testing $240 support, watch for bounce",
                explanation="**WHY THIS MATTERS**: Tesla is testing a critical support level at $240 that has held multiple times. A bounce here could signal a reversal, while a break could lead to further downside to $220.",
                how_to_trade="**HOW TO TRADE**: Wait for confirmation above $245 before entering long. If breaks $238, consider taking profits or exiting longs. Risk/reward favors waiting.",
                sentiment_score=-0.30,
                confidence_score=0.70,
                priority="medium",
                category="watch_list",
                source="technical_analysis",
                extra_data={"sector": "Automotive"},
                created_at=now - timedelta(hours=4),
            ),
            DigestItemResponse(
                id=3,
                symbol="NVDA",
                title="NVIDIA Earnings Beat Expectations",
                summary="Strong Q4 results drive after-hours rally",
                explanation="**WHY THIS MATTERS**: NVIDIA's data center revenue grew 40% YoY, exceeding analyst estimates. AI chip demand remains robust, supporting premium valuation. Management guidance suggests sustained growth.",
                how_to_trade="**HOW TO TRADE**: Expect gap up at open. Wait for initial volatility to settle, then look for entry on pullback to VWAP. Target new highs above $500.",
                sentiment_score=0.90,
                confidence_score=0.92,
                priority="high",
                category="trade_alert",
                source="earnings_analysis",
                extra_data={"sector": "Semiconductors"},
                created_at=now - timedelta(hours=1),
            ),
            DigestItemResponse(
                id=4,
                symbol="SPY",
                title="S&P 500 Consolidating Near All-Time Highs",
                summary="Market digesting recent gains, awaiting catalyst",
                explanation="**WHY THIS MATTERS**: The S&P 500 is trading in a tight range near record highs. Low volatility environment (VIX ~15) suggests complacency. Watch for breakout or breakdown on upcoming economic data.",
                how_to_trade="**HOW TO TRADE**: For swing traders, wait for direction. Day traders can trade the range: buy support at $452, sell resistance at $458. Use tight stops.",
                sentiment_score=0.10,
                confidence_score=0.60,
                priority="medium",
                category="market_context",
                source="market_analysis",
                extra_data={"sector": "Market"},
                created_at=now - timedelta(hours=3),
            ),
            DigestItemResponse(
                id=5,
                symbol="AMD",
                title="AMD Breaking Out of 3-Month Consolidation",
                summary="Technical setup improves as volume increases",
                explanation="**WHY THIS MATTERS**: AMD has been consolidating between $140-$160 for 3 months, building energy for next move. Recent volume pickup and relative strength suggest bullish resolution imminent.",
                how_to_trade="**HOW TO TRADE**: Buy breakout above $162 with volume confirmation. Initial target $175. Stop loss below $157. This is a momentum play with strong risk/reward.",
                sentiment_score=0.65,
                confidence_score=0.78,
                priority="high",
                category="trade_alert",
                source="technical_analysis",
                extra_data={"sector": "Semiconductors"},
                created_at=now - timedelta(hours=5),
            ),
        ]

        # Return up to max_items
        return demo_signals[:max_items]
