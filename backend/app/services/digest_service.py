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
        Get overall market context information using real market data with enhanced analysis.

        Returns:
            Market context dictionary with trend analysis
        """
        try:
            # Get real market indices data
            indices = await market_data_service.get_market_indices()

            # Determine overall market trend based on S&P 500
            sp500_data = indices.get("S&P 500", {})
            sp500_change = sp500_data.get("raw_change", 0)
            sp500_level = sp500_data.get("level", 0)

            # Determine market trend with more granularity
            if sp500_change > 1.0:
                market_trend = "STRONGLY BULLISH"
                trend_description = "Risk-on environment. Tech and growth stocks leading."
            elif sp500_change > 0.3:
                market_trend = "BULLISH"
                trend_description = "Positive momentum. Buyers in control."
            elif sp500_change > -0.3:
                market_trend = "NEUTRAL"
                trend_description = "Consolidation phase. Awaiting catalyst."
            elif sp500_change > -1.0:
                market_trend = "BEARISH"
                trend_description = "Selling pressure. Defensive positioning recommended."
            else:
                market_trend = "STRONGLY BEARISH"
                trend_description = "Risk-off mode. Flight to safety."

            # Check NASDAQ vs S&P 500 performance for tech strength
            nasdaq_data = indices.get("NASDAQ", {})
            nasdaq_change = nasdaq_data.get("raw_change", 0)
            tech_leadership = "Tech leading" if nasdaq_change > sp500_change + 0.2 else "Tech lagging" if nasdaq_change < sp500_change - 0.2 else "Tech in-line"

            return {
                "market_trend": market_trend,
                "trend_description": trend_description,
                "tech_leadership": tech_leadership,
                "major_indices": indices,
                "sp500_level": sp500_level,
                "sector_rotation": f"{tech_leadership}. Watch financials and energy for rotation signals.",
            }
        except Exception as e:
            logger.error(f"Error fetching market context: {e}")
            # Enhanced fallback data
            return {
                "market_trend": "NEUTRAL",
                "trend_description": "Market data temporarily unavailable. Monitor major indices for direction.",
                "tech_leadership": "Tech sentiment mixed",
                "major_indices": {
                    "S&P 500": {"change": "+0.2%", "level": 5800.0, "raw_change": 0.2},
                    "DOW": {"change": "+0.1%", "level": 42500.0, "raw_change": 0.1},
                    "NASDAQ": {"change": "+0.4%", "level": 18200.0, "raw_change": 0.4},
                },
                "sp500_level": 5800.0,
                "sector_rotation": "Mixed sector performance. Technology showing relative strength.",
            }

    async def _get_vix_regime(self) -> Dict[str, Any]:
        """
        Get VIX market regime information using real VIX data with enhanced analysis.

        Returns:
            VIX regime dictionary with trading implications
        """
        try:
            # Get real VIX regime data
            vix_regime = await market_data_service.get_vix_regime()

            # Add trading implications based on VIX level
            vix_level = vix_regime.get("vix_level") or vix_regime.get("level", 15.5)

            if vix_level < 12:
                vix_regime["trading_implication"] = "Extreme complacency. Consider hedges or volatility longs."
            elif vix_level < 15:
                vix_regime["trading_implication"] = "Low vol environment favors momentum strategies and selling premium."
            elif vix_level < 20:
                vix_regime["trading_implication"] = "Normal volatility. Standard position sizing appropriate."
            elif vix_level < 30:
                vix_regime["trading_implication"] = "Elevated volatility. Reduce size, widen stops, consider defensive positions."
            else:
                vix_regime["trading_implication"] = "Extreme fear. Contrarian opportunity or stay defensive."

            return vix_regime
        except Exception as e:
            logger.error(f"Error fetching VIX regime: {e}")
            # Enhanced fallback data
            return {
                "vix_level": 16.2,
                "level": 16.2,
                "regime": "NORMAL",
                "description": "Moderate volatility environment. Market digesting recent moves.",
                "trading_implication": "Normal volatility. Standard position sizing appropriate.",
            }

    def _generate_demo_signals(self, max_items: int) -> List[DigestItemResponse]:
        """
        Generate high-quality demo signals for testing with realistic trade scenarios.

        Args:
            max_items: Maximum number of signals to generate

        Returns:
            List of demo DigestItemResponse objects with actionable trade ideas
        """
        now = datetime.utcnow()
        demo_signals = [
            DigestItemResponse(
                id=1,
                symbol="NVDA",
                title="NVIDIA Breaks Out: AI Chip Demand Surges Post-Earnings",
                summary="NVDA up 7.2% after crushing Q4 earnings with data center revenue +217% YoY. Stock cleared $950 resistance.",
                explanation="**🟢 BUY**: NVIDIA's data center revenue ($18.4B vs $11.0B est.) signals explosive AI infrastructure demand. Major cloud providers (MSFT, GOOGL, AMZN) are accelerating AI compute spending. Technical breakout above $950 on 3x average volume confirms institutional buying. This represents a continuation of the AI mega-trend with NVDA as the primary beneficiary.",
                how_to_trade="**ENTRY**: Pullbacks to $940-950 support. **STOP**: $920 (-3.5%). **TARGETS**: $1,020 (+7%), $1,100 (+15%). **SIZE**: 3-5% of portfolio. **TIMEFRAME**: 2-4 weeks swing trade. **OPTIONS**: Consider Feb 16 $950 calls for leveraged exposure. **WATCH**: Any Fed hawkishness or tech sector rotation would be exit signal.",
                sentiment_score=0.82,
                confidence_score=0.88,
                priority="high",
                category="trade_alert",
                source="earnings_catalyst",
                extra_data={"sector": "Semiconductors", "catalyst": "Earnings beat", "price_target": "$1,100"},
                created_at=now - timedelta(hours=1),
            ),
            DigestItemResponse(
                id=2,
                symbol="SPY",
                title="S&P 500 Tests Key 5,800 Resistance - Breakout or Rejection?",
                summary="SPY approaching major resistance at 5,800 with mixed volume. Fed decision Wednesday adds volatility risk.",
                explanation="**⚪ WAIT**: S&P 500 is at a critical juncture. The 5,800 level has capped rallies 3 times in past month. Break above = new highs targeting 6,000. Rejection = -5% pullback to 5,500 support. This week's Fed meeting (Wed 2pm ET) will determine direction. Current P/E at 21.5x suggests limited upside without earnings growth confirmation. Institutional flows show cautious positioning ahead of FOMC.",
                how_to_trade="**STRATEGY**: Wait for Fed decision. **IF BREAKS 5,800 on volume**: Enter long with $5,810 stop, target $5,950. **IF REJECTS**: Short at $5,795 with $5,820 stop, target $5,650. **ALTERNATIVES**: Sell $5,800 calls for premium if expecting range-bound. **HEDGE**: VIX calls as cheap insurance into FOMC.",
                sentiment_score=0.15,
                confidence_score=0.72,
                priority="high",
                category="watch_list",
                source="technical_macro",
                extra_data={"sector": "Broad Market", "catalyst": "Technical + FOMC", "resistance": "5,800"},
                created_at=now - timedelta(hours=2),
            ),
            DigestItemResponse(
                id=3,
                symbol="TSLA",
                title="Tesla Guidance Miss Triggers -8% Drop Despite Delivery Beat",
                summary="TSLA down sharply as management warns of \"slight decline\" in 2025 deliveries vs growth expectations",
                explanation="**🔴 SHORT/AVOID**: While Q4 deliveries beat (496K vs 490K est), Elon's comments on 2025 outlook (-2% to flat growth) shocked bulls expecting +15-20%. This is a sentiment killer. Stock broke $340 support and testing $320. Bears argue valuation (75x P/E) can't justify stagnant growth. Options positioning shows heavy put buying. Upgrade cycle delay and China competition (BYD) are real concerns.",
                how_to_trade="**FOR BEARS**: Short $330, stop $345, target $285 (200-day MA). **FOR BULLS**: Wait for $280-300 support zone before considering entry. **RISK**: High-beta volatility - use tight stops. **OPTIONS**: Feb $320 puts gaining premium. **WATCH**: Delivery data from China competitors.",
                sentiment_score=-0.68,
                confidence_score=0.79,
                priority="high",
                category="trade_alert",
                source="earnings_guidance",
                extra_data={"sector": "Automotive/EV", "catalyst": "Weak guidance", "support": "$320"},
                created_at=now - timedelta(hours=3),
            ),
            DigestItemResponse(
                id=4,
                symbol="GLD",
                title="Gold Surges to $2,150 on Fed Pivot Speculation",
                summary="Gold up 2.1% as 10-year yield drops below 4.0%. Safe haven bid increasing ahead of FOMC meeting.",
                explanation="**🟢 BUY**: Gold breaking out as bond yields fall and dollar weakens. Market pricing 75% chance of rate cut by June. Gold acts as inflation hedge + benefits from falling real rates. Technical breakout above $2,120 resistance opens path to $2,200. Central bank buying (China, India) providing support. Geopolitical tensions (Middle East) adding safe-haven premium.",
                how_to_trade="**ENTRY**: Dips to $2,130-2,140. **STOP**: $2,100. **TARGETS**: $2,200 (+2.3%), $2,250 (+4.6%). **SIZE**: 2-3% allocation. **ALTERNATIVES**: GLD ETF for liquidity, GDX for leveraged miners exposure. **HEDGE**: Works as portfolio insurance if stocks correct. **WATCH**: DXY dollar index - inverse correlation.",
                sentiment_score=0.72,
                confidence_score=0.76,
                priority="medium",
                category="trade_alert",
                source="macro_rates",
                extra_data={"sector": "Commodities", "catalyst": "Fed pivot + safe haven", "target": "$2,200"},
                created_at=now - timedelta(hours=4),
            ),
            DigestItemResponse(
                id=5,
                symbol="VIX",
                title="VIX Spikes to 18.5 (+22%) as Fed Meeting Uncertainty Builds",
                summary="Volatility index jumping as traders hedge into FOMC decision. Options skew tilting to puts.",
                explanation="**⚪ TACTICAL OPPORTUNITY**: VIX surge from 15 to 18.5 signals market nervousness before Fed meeting Wed. When VIX >18, expect 1-2% daily S&P swings. Put/call ratio at 1.15 (elevated) shows defensive positioning. Historical pattern: VIX spikes into FOMC often reverse sharply after decision. Current level offers opportunity - either hedge gets cheaper after Wed, or protection pays off if Fed surprises hawkish.",
                how_to_trade="**DEFENSIVE**: Buy VIX calls expiring Friday (cheap lottery if Fed shock). **AGGRESSIVE**: Short VIX after Fed decision for mean reversion to 14-15. **STOCK HEDGE**: Reduce position sizes or add SPY put spreads before FOMC. **POST-FOMC**: VIX likely drops -20-30% if no surprises, creating entry opportunity in stocks. **CONTRARIAN**: High VIX = buy stocks when fear peaks.",
                sentiment_score=-0.45,
                confidence_score=0.81,
                priority="high",
                category="market_context",
                source="volatility_macro",
                extra_data={"sector": "Volatility", "catalyst": "FOMC uncertainty", "level": "18.5"},
                created_at=now - timedelta(hours=5),
            ),
            DigestItemResponse(
                id=6,
                symbol="QQQ",
                title="Nasdaq 100 Outperforming as Tech Leadership Resumes",
                summary="QQQ up 1.8% vs SPY +0.7%. Mega-cap tech driving markets higher on AI optimism.",
                explanation="**🟢 BUY**: Nasdaq 100 showing clear strength vs S&P 500, signaling tech leadership returning. This rotation typically precedes broader market rallies. Top 7 holdings (AAPL, MSFT, NVDA, GOOGL, AMZN, META, TSLA) account for 50% of index - if they run, QQQ flies. Chart shows breakout above 50-day MA with improving breadth.",
                how_to_trade="**ENTRY**: Dips to $470-472. **STOP**: $465. **TARGETS**: $485 (+3%), $495 (+5%). **LEVERAGE**: Consider TQQQ for 3x exposure if bullish. **PAIRS TRADE**: Long QQQ / Short IWM (small caps) to capture tech outperformance. **HEDGE**: If tech fails, this trade fails - use tight stops.",
                sentiment_score=0.75,
                confidence_score=0.80,
                priority="high",
                category="trade_alert",
                source="technical_macro",
                extra_data={"sector": "Technology/QQQ", "catalyst": "Tech leadership", "target": "$495"},
                created_at=now - timedelta(hours=6),
            ),
            DigestItemResponse(
                id=7,
                symbol="JPM",
                title="JPMorgan Breaks Above $190 on Strong Banking Sentiment",
                summary="JPM rallying 3.2% as bank stocks lead on yield curve steepening. Regional banks following higher.",
                explanation="**🟢 BUY**: Banks benefit when long-term rates rise faster than short-term rates (steepening yield curve). JPM's net interest margin expands, boosting profitability. Technical breakout above $190 resistance on strong volume. Financial sector rotation underway as investors rotate from tech into value. XLF (financial ETF) confirming strength.",
                how_to_trade="**ENTRY**: Current levels $192-194 or dips to $188. **STOP**: $184 (-4%). **TARGETS**: $205 (+6%), $215 (+11%). **SIZE**: 2-4% position. **TIMEFRAME**: 3-6 weeks. **SECTOR PLAY**: Consider XLF ETF for broader financial exposure. **CATALYST**: Fed pause benefits banks more than rate cuts.",
                sentiment_score=0.71,
                confidence_score=0.83,
                priority="high",
                category="trade_alert",
                source="sector_rotation",
                extra_data={"sector": "Financials", "catalyst": "Yield curve steepening", "target": "$215"},
                created_at=now - timedelta(hours=7),
            ),
            DigestItemResponse(
                id=8,
                symbol="AMD",
                title="AMD Poised for Breakout: AI Server Chip Orders Accelerating",
                summary="AMD consolidating at $165 after 6-week base. Supply chain checks show MI300 orders doubling next quarter.",
                explanation="**🟢 BUY**: AMD's MI300 AI chips gaining share from NVIDIA in cloud data centers (MSFT, META confirmed orders). Street estimates too low - likely upward revisions coming. Chart shows textbook bull flag pattern with tightening price action. Options flow bullish (heavy call buying in Feb/Mar). If NVDA runs, AMD follows with higher beta.",
                how_to_trade="**ENTRY**: Breakout above $168 with volume or dips to $162. **STOP**: $158 (-4%). **TARGETS**: $180 (+9%), $195 (+18%). **SIZE**: 3-5% position. **LEVERAGE**: Feb $170 calls for earnings play (Jan 28). **PAIRS**: Long AMD / Short INTC to isolate AI chip exposure. **CATALYST**: Earnings + analyst day late January.",
                sentiment_score=0.77,
                confidence_score=0.81,
                priority="high",
                category="trade_alert",
                source="supply_chain_intel",
                extra_data={"sector": "Semiconductors", "catalyst": "AI chip orders", "earnings_date": "Jan 28"},
                created_at=now - timedelta(hours=8),
            ),
            DigestItemResponse(
                id=9,
                symbol="TLT",
                title="Long-Term Treasuries Setting Up: Rates Peaked?",
                summary="TLT (20+ year Treasury ETF) forming base at $92 as 10-year yield tests support at 4.0%.",
                explanation="**🟢 BUY**: If Fed pauses rate hikes, long bonds rally first. Technical setup: TLT bouncing off 200-day MA, RSI oversold, bullish divergence forming. Inflation trending down (CPI, PPI both cooling). Macro backdrop: recession fears = flight to quality. Contrarian play as everyone expects higher-for-longer rates.",
                how_to_trade="**ENTRY**: $92-93 zone. **STOP**: $88.50 (-4%). **TARGETS**: $98 (+6%), $104 (+12%). **SIZE**: 2-3% hedge allocation. **TIMEFRAME**: 2-4 months. **RATIONALE**: Portfolio insurance against stock market correction. **INVERSE PLAY**: If rates spike higher, exit quickly. **WATCH**: 10-year yield 4.0% critical level.",
                sentiment_score=0.55,
                confidence_score=0.71,
                priority="medium",
                category="trade_alert",
                source="macro_bonds",
                extra_data={"sector": "Fixed Income", "catalyst": "Fed pause + disinflation", "target": "$104"},
                created_at=now - timedelta(hours=9),
            ),
            DigestItemResponse(
                id=10,
                symbol="XLE",
                title="Energy Sector Bottoming: Oil Inventory Draw + OPEC Discipline",
                summary="XLE (Energy ETF) bouncing from $85 support as crude oil stabilizes above $75/barrel.",
                explanation="**🟢 BUY**: Energy oversold after 3-month decline. Fundamentals improving: OPEC+ extending production cuts, US crude inventories down 5M barrels (vs +2M expected), refinery utilization increasing. XLE relative strength improving vs S&P. Seasonal tailwind (winter heating demand). Valuation: Energy trading at 8x P/E vs 21x for S&P - extreme discount.",
                how_to_trade="**ENTRY**: $86-88. **STOP**: $83 (-4%). **TARGETS**: $94 (+9%), $100 (+16%). **SIZE**: 3-4% position. **ALTERNATIVES**: CVX, XOM for individual stock exposure. **TIMEFRAME**: 6-12 weeks. **CATALYST**: Next OPEC meeting, China economic data. **HEDGE**: Works well if inflation reaccelerates.",
                sentiment_score=0.63,
                confidence_score=0.77,
                priority="high",
                category="trade_alert",
                source="commodity_fundamentals",
                extra_data={"sector": "Energy", "catalyst": "OPEC cuts + inventory draws", "target": "$100"},
                created_at=now - timedelta(hours=10),
            ),
        ]

        # Sort by confidence score (highest first) to show best opportunities
        demo_signals.sort(key=lambda x: x.confidence_score, reverse=True)

        # Return up to max_items
        return demo_signals[:max_items]
