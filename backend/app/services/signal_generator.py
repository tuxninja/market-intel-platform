"""
Signal Generator Module

Combines market data and news sentiment to generate trading signals.
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from app.services.market_data_service import market_data_service
from app.services.news_service import news_service
from app.schemas.digest import DigestItemResponse

logger = logging.getLogger(__name__)


class SignalGenerator:
    """
    Generates trading signals by combining technical analysis and news sentiment.
    """

    # Default watchlist (popular stocks)
    DEFAULT_WATCHLIST = [
        "AAPL",  # Apple
        "MSFT",  # Microsoft
        "GOOGL", # Google
        "AMZN",  # Amazon
        "NVDA",  # NVIDIA
        "TSLA",  # Tesla
        "META",  # Meta
        "AMD",   # AMD
        "NFLX",  # Netflix
        "DIS",   # Disney
        "COIN",  # Coinbase
        "PLTR",  # Palantir
        "SHOP",  # Shopify
        "SQ",    # Block (Square)
        "PYPL",  # PayPal
    ]

    def __init__(self):
        """Initialize signal generator."""
        pass

    async def generate_signals(
        self,
        watchlist: Optional[List[str]] = None,
        max_signals: int = 20
    ) -> List[DigestItemResponse]:
        """
        Generate trading signals for watchlist.

        Args:
            watchlist: List of stock symbols (uses default if None)
            max_signals: Maximum number of signals to generate

        Returns:
            List of DigestItemResponse objects with signals
        """
        if watchlist is None:
            watchlist = self.DEFAULT_WATCHLIST

        signals = []

        logger.info(f"Generating signals for {len(watchlist)} symbols")

        for symbol in watchlist:
            try:
                signal = await self._analyze_symbol(symbol)
                if signal:
                    signals.append(signal)
                else:
                    logger.debug(f"No signal generated for {symbol}")
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}", exc_info=True)
                continue

        # Sort by confidence score (highest first)
        signals.sort(key=lambda x: x.confidence_score or 0, reverse=True)

        # Limit to max_signals
        signals = signals[:max_signals]

        logger.info(f"Generated {len(signals)} signals")
        return signals

    async def _analyze_symbol(self, symbol: str) -> Optional[DigestItemResponse]:
        """
        Analyze a single symbol and generate signal.

        Args:
            symbol: Stock ticker

        Returns:
            DigestItemResponse or None if no signal
        """
        try:
            # Get comprehensive technical analysis
            logger.debug(f"Fetching analysis for {symbol}...")
            analysis = await market_data_service.get_comprehensive_analysis(symbol)
            if not analysis:
                logger.warning(f"No analysis data returned for {symbol} - yfinance may have failed")
                return None
            logger.debug(f"Successfully fetched analysis for {symbol}")

            price_data = analysis.get("price", {})
            rsi = analysis.get("rsi")
            macd = analysis.get("macd", {})
            mas = analysis.get("moving_averages", {})
            volume = analysis.get("volume", {})

            # Get symbol-specific news
            news_articles = await news_service.get_symbol_specific_news(symbol, hours_lookback=24, max_articles=5)

            # Calculate technical score
            tech_score = self._calculate_technical_score(rsi, macd, mas, volume)

            # Calculate news sentiment score
            news_score = self._calculate_news_score(news_articles)

            # Combine scores
            combined_score = (tech_score * 0.6) + (news_score * 0.4)  # 60% technical, 40% news

            # Determine if signal is strong enough
            # Lower threshold to 0.15 to generate more signals even in neutral markets
            if abs(combined_score) < 0.15:  # Filter only very weak signals
                logger.info(f"Skipping {symbol}: combined_score={combined_score:.2f} below threshold")
                return None

            logger.info(f"Signal generated for {symbol}: score={combined_score:.2f}, tech={tech_score:.2f}, news={news_score:.2f}")

            # Determine signal category and priority
            category = self._determine_category(combined_score, volume)
            priority = self._determine_priority(combined_score, volume)

            # Generate title
            title = self._generate_title(symbol, combined_score, price_data, mas)

            # Generate summary
            summary = self._generate_summary(symbol, price_data, rsi, macd, mas)

            # Generate explanation (WHY THIS MATTERS)
            explanation = self._generate_explanation(
                symbol, combined_score, tech_score, news_score,
                price_data, rsi, macd, mas, volume, news_articles
            )

            # Generate trading guidance (HOW TO TRADE)
            how_to_trade = self._generate_trading_guidance(
                symbol, combined_score, price_data, mas, rsi
            )

            # Format news articles for display
            formatted_news = []
            for article in news_articles[:5]:  # Top 5 news articles
                formatted_news.append({
                    "title": article.title,
                    "summary": article.summary,
                    "url": article.url,
                    "sentiment_score": article.sentiment_score,
                    "source": article.source,
                    "published": article.published.isoformat() if isinstance(article.published, datetime) else str(article.published)
                })

            return DigestItemResponse(
                id=hash(symbol) % 100000,  # Temporary ID
                symbol=symbol,
                title=title,
                summary=summary,
                explanation=explanation,
                how_to_trade=how_to_trade,
                sentiment_score=round(combined_score, 2),
                confidence_score=round(abs(combined_score), 2),
                priority=priority,
                category=category,
                source="technical_analysis+news",
                news_articles=formatted_news if formatted_news else None,
                metadata={
                    "sector": price_data.get("sector"),
                    "current_price": price_data.get("price"),
                    "rsi": rsi,
                    "macd": macd.get("crossover") if macd else None,
                    "volume_ratio": volume.get("volume_ratio_20day") if volume else None,
                },
                created_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Error analyzing symbol {symbol}: {e}")
            return None

    def _calculate_technical_score(
        self,
        rsi: Optional[float],
        macd: Optional[Dict],
        mas: Optional[Dict],
        volume: Optional[Dict]
    ) -> float:
        """
        Calculate technical analysis score (-1 to +1).

        Returns:
            Score: -1 (very bearish) to +1 (very bullish)
        """
        score = 0.0
        factors = 0

        # RSI analysis (30% weight)
        if rsi is not None:
            if rsi < 30:
                score += 0.3  # Oversold = bullish
            elif rsi > 70:
                score -= 0.3  # Overbought = bearish
            elif 40 <= rsi <= 60:
                score += 0.0  # Neutral
            else:
                # Gradual scoring
                score += ((50 - rsi) / 100)  # Linear scale
            factors += 1

        # MACD analysis (25% weight)
        if macd:
            if macd.get("crossover") == "bullish":
                score += 0.25
            elif macd.get("crossover") == "bearish":
                score -= 0.25
            factors += 1

        # Moving Average analysis (30% weight)
        if mas:
            ma_score = 0
            if mas.get("above_ema_20"):
                ma_score += 0.1
            if mas.get("above_ema_50"):
                ma_score += 0.1
            if mas.get("above_ema_200"):
                ma_score += 0.1
            if mas.get("golden_cross"):
                ma_score += 0.15  # Very bullish
            if mas.get("death_cross"):
                ma_score -= 0.15  # Very bearish

            score += ma_score
            factors += 1

        # Volume analysis (15% weight)
        if volume:
            if volume.get("high_volume") and volume.get("volume_ratio_20day", 1) > 1.5:
                # High volume confirms trend
                score += 0.15 if score > 0 else -0.15
            factors += 1

        # Normalize if we had some factors
        if factors > 0:
            return max(-1.0, min(1.0, score))
        return 0.0

    def _calculate_news_score(self, articles: List) -> float:
        """Calculate news sentiment score."""
        if not articles:
            return 0.0

        # Average sentiment from articles
        sentiments = [a.sentiment_score for a in articles if a.sentiment_score is not None]
        if not sentiments:
            return 0.0

        avg_sentiment = sum(sentiments) / len(sentiments)
        return max(-1.0, min(1.0, avg_sentiment))

    def _determine_category(self, score: float, volume: Optional[Dict]) -> str:
        """Determine signal category."""
        if abs(score) > 0.6:
            return "trade_alert"  # High confidence
        elif abs(score) > 0.4:
            return "watch_list"   # Medium confidence
        else:
            return "market_context"  # Low confidence

    def _determine_priority(self, score: float, volume: Optional[Dict]) -> str:
        """Determine signal priority."""
        abs_score = abs(score)
        high_volume = volume.get("high_volume", False) if volume else False

        if abs_score > 0.7 and high_volume:
            return "high"
        elif abs_score > 0.5:
            return "medium"
        else:
            return "low"

    def _generate_title(
        self,
        symbol: str,
        score: float,
        price_data: Dict,
        mas: Optional[Dict]
    ) -> str:
        """Generate signal title."""
        price = price_data.get("price", 0)
        change_pct = price_data.get("change_percent", 0)

        if score > 0.6:
            if mas and mas.get("golden_cross"):
                return f"{symbol} Golden Cross Breakout Above ${price:.2f}"
            elif change_pct > 3:
                return f"{symbol} Surging {change_pct:+.1f}% - Strong Momentum"
            else:
                return f"{symbol} Shows Strong Bullish Setup at ${price:.2f}"
        elif score > 0.3:
            return f"{symbol} Building Positive Momentum Near ${price:.2f}"
        elif score < -0.6:
            if mas and mas.get("death_cross"):
                return f"{symbol} Death Cross Warning Below ${price:.2f}"
            else:
                return f"{symbol} Under Pressure at ${price:.2f} - Caution"
        elif score < -0.3:
            return f"{symbol} Showing Weakness at ${price:.2f}"
        else:
            return f"{symbol} Consolidating at ${price:.2f}"

    def _generate_summary(
        self,
        symbol: str,
        price_data: Dict,
        rsi: Optional[float],
        macd: Optional[Dict],
        mas: Optional[Dict]
    ) -> str:
        """Generate brief summary."""
        price = price_data.get("price", 0)
        change_pct = price_data.get("change_percent", 0)

        summary_parts = [f"{symbol} trading at ${price:.2f} ({change_pct:+.1f}%)"]

        if rsi and rsi < 30:
            summary_parts.append("RSI oversold")
        elif rsi and rsi > 70:
            summary_parts.append("RSI overbought")

        if macd and macd.get("crossover") == "bullish":
            summary_parts.append("MACD bullish crossover")
        elif macd and macd.get("crossover") == "bearish":
            summary_parts.append("MACD bearish crossover")

        if mas and mas.get("above_ema_200"):
            summary_parts.append("above 200 EMA")

        return ", ".join(summary_parts)

    def _generate_explanation(
        self,
        symbol: str,
        combined_score: float,
        tech_score: float,
        news_score: float,
        price_data: Dict,
        rsi: Optional[float],
        macd: Optional[Dict],
        mas: Optional[Dict],
        volume: Optional[Dict],
        news_articles: List
    ) -> str:
        """Generate WHY THIS MATTERS explanation."""
        explanation = f"**WHY THIS MATTERS**:\n\n"

        # Technical analysis insights
        explanation += "**Technical Setup**: "
        tech_insights = []

        if rsi:
            if rsi < 30:
                tech_insights.append(f"RSI at {rsi:.1f} indicates oversold conditions, suggesting potential bounce")
            elif rsi > 70:
                tech_insights.append(f"RSI at {rsi:.1f} shows overbought conditions, possible pullback ahead")
            else:
                tech_insights.append(f"RSI at {rsi:.1f} (neutral range)")

        if macd:
            if macd.get("crossover") == "bullish":
                tech_insights.append("MACD bullish crossover confirms upward momentum")
            elif macd.get("crossover") == "bearish":
                tech_insights.append("MACD bearish crossover signals weakening momentum")

        if mas:
            if mas.get("golden_cross"):
                tech_insights.append("Golden cross (50 EMA > 200 EMA) is highly bullish")
            if mas.get("above_ema_200"):
                tech_insights.append("Price above 200 EMA confirms long-term uptrend")

        if volume and volume.get("high_volume"):
            ratio = volume.get("volume_ratio_20day", 1)
            tech_insights.append(f"Volume {ratio:.1f}x average confirms strong interest")

        explanation += ". ".join(tech_insights) + ".\n\n"

        # News sentiment insights
        if news_articles:
            explanation += f"**News Sentiment**: "
            if news_score > 0.3:
                explanation += f"Recent news is bullish ({len(news_articles)} positive articles). "
            elif news_score < -0.3:
                explanation += f"Recent news is bearish ({len(news_articles)} negative articles). "
            else:
                explanation += "News sentiment is neutral. "

            # Add top news headline
            if news_articles:
                top_article = news_articles[0]
                explanation += f"Latest: '{top_article.title[:100]}...'\n\n"
        else:
            explanation += "**News Sentiment**: No recent news articles found.\n\n"

        # Overall assessment
        explanation += "**Bottom Line**: "
        if combined_score > 0.6:
            explanation += "Strong bullish setup with multiple confirmations. Consider entry on next dip."
        elif combined_score > 0.3:
            explanation += "Positive setup forming. Watch for continuation or reversal signals."
        elif combined_score < -0.6:
            explanation += "Strong bearish signals. Avoid longs or consider shorts if experienced."
        elif combined_score < -0.3:
            explanation += "Negative pressure building. Exercise caution with long positions."
        else:
            explanation += "Mixed signals. Wait for clearer direction before taking action."

        return explanation

    def _generate_trading_guidance(
        self,
        symbol: str,
        score: float,
        price_data: Dict,
        mas: Optional[Dict],
        rsi: Optional[float]
    ) -> str:
        """Generate HOW TO TRADE guidance."""
        price = price_data.get("price", 0)
        guidance = "**HOW TO TRADE**:\n\n"

        if score > 0.5:
            # Bullish signal
            entry = price * 1.01  # Entry 1% above current (on breakout)
            stop = price * 0.97   # Stop 3% below
            target1 = price * 1.05  # Target 5% above
            target2 = price * 1.10  # Target 10% above

            guidance += f"**Entry Strategy**: Consider entry around ${entry:.2f} on volume confirmation. "
            guidance += f"Watch for breakout above ${price:.2f}.\n\n"
            guidance += f"**Risk Management**: Set stop loss at ${stop:.2f} (3% risk). "
            guidance += f"Position size: 2-3% of portfolio.\n\n"
            guidance += f"**Profit Targets**: First target ${target1:.2f} (take 50% profit). "
            guidance += f"Second target ${target2:.2f} (take remaining).\n\n"
            guidance += "**Timeframe**: Swing trade (3-7 days) or day trade depending on your style."

        elif score > 0.3:
            # Mild bullish
            guidance += f"**Watch**: Monitor for entry opportunity if {symbol} breaks above ${price * 1.02:.2f} with volume.\n\n"
            guidance += f"**Entry**: ${price * 1.02:.2f} (confirmation needed)\n"
            guidance += f"**Stop Loss**: ${price * 0.98:.2f}\n"
            guidance += f"**Target**: ${price * 1.05:.2f}\n\n"
            guidance += "**Note**: Wait for confirmation before entering. This is a developing setup."

        elif score < -0.5:
            # Bearish signal
            guidance += f"**Action**: Avoid new long positions. Consider exiting longs if held.\n\n"
            guidance += f"**For Experienced Traders**: Short entry around ${price:.2f}, "
            guidance += f"stop at ${price * 1.03:.2f}, target ${price * 0.95:.2f}.\n\n"
            guidance += "**Alternative**: Buy puts with strike near current price if options-approved."

        else:
            # Neutral
            guidance += f"**Action**: No clear signal. Stay on sidelines.\n\n"
            guidance += f"**Watch**: Monitor for breakout above ${price * 1.03:.2f} (bullish) "
            guidance += f"or breakdown below ${price * 0.97:.2f} (bearish).\n\n"
            guidance += "**Patience**: Wait for clearer setup before risking capital."

        return guidance


# Global service instance
signal_generator = SignalGenerator()
