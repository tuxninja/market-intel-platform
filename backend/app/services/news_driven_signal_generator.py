"""
News-Driven Signal Generator

Event-driven signal generation based on breaking news with ML sentiment analysis.
Only generates signals when significant news breaks, avoiding stale repeated recommendations.
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import hashlib
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ml_sentiment_service import ml_sentiment_analyzer
from app.services.symbol_extractor_service import symbol_extractor
from app.services.news_service import news_service
from app.services.market_data_service import market_data_service
from app.models.signal_history import SignalHistory
from app.schemas.digest import DigestItemResponse

logger = logging.getLogger(__name__)


class NewsDrivenSignalGenerator:
    """
    Generate trading signals based on breaking news events.

    Key Features:
    1. Event-driven: Only triggers on fresh news (last 3-6 hours)
    2. ML-powered: Uses FinBERT for accurate sentiment analysis
    3. Smart deduplication: Avoids repeating same signal within 7 days
    4. Real-time validation: Confirms current price before recommending
    5. Multi-source: Combines news sentiment with technical confirmation
    """

    # Configuration
    NEWS_LOOKBACK_HOURS = 6  # Only consider very recent news
    MIN_SENTIMENT_CONFIDENCE = 0.6  # FinBERT confidence threshold
    MIN_COMBINED_SCORE = 0.3  # Minimum score to generate signal
    SIGNAL_EXPIRY_DAYS = 7  # Don't repeat signal for 7 days
    MAX_SIGNALS_PER_RUN = 10  # Limit signals per digest

    def __init__(self, db: AsyncSession):
        """Initialize the generator with async database session."""
        self.db = db

    async def generate_signals(self, max_signals: int = 10) -> List[DigestItemResponse]:
        """
        Generate trading signals from breaking news.

        Args:
            max_signals: Maximum number of signals to return

        Returns:
            List of high-quality, time-relevant trade signals
        """
        logger.info("Starting news-driven signal generation...")

        # Step 1: Fetch recent breaking news (last 6 hours)
        logger.info(f"Fetching news from last {self.NEWS_LOOKBACK_HOURS} hours...")
        news_articles = await news_service.fetch_all_news(
            hours_lookback=self.NEWS_LOOKBACK_HOURS,
            max_articles=100
        )

        if not news_articles:
            logger.warning("No recent news found")
            return []

        logger.info(f"Found {len(news_articles)} recent articles")

        # Step 2: Analyze sentiment with FinBERT (batch processing)
        logger.info("Analyzing sentiment with FinBERT ML model...")
        texts = [f"{article.title}. {article.summary}" for article in news_articles]
        sentiments = ml_sentiment_analyzer.batch_analyze_sentiment(texts)

        # Attach sentiment to articles
        for article, sentiment in zip(news_articles, sentiments):
            article.sentiment_score = sentiment["score"]
            article.ml_confidence = sentiment["confidence"]
            article.sentiment_label = sentiment["label"]

        # Step 3: Filter for high-confidence sentiment
        significant_news = [
            article for article in news_articles
            if hasattr(article, 'ml_confidence') and article.ml_confidence >= self.MIN_SENTIMENT_CONFIDENCE
            and abs(article.sentiment_score) >= 0.3  # Must be clearly positive or negative
        ]

        logger.info(f"Filtered to {len(significant_news)} high-confidence articles")

        if not significant_news:
            logger.warning("No significant news found after filtering")
            return []

        # Step 4: Extract stock symbols from news
        logger.info("Extracting stock symbols from news articles...")
        symbol_opportunities = []

        for article in significant_news:
            # Extract symbols mentioned in article
            extracted = symbol_extractor.extract_symbols(
                article.title,
                article.summary,
                min_confidence=0.6
            )

            for symbol_data in extracted:
                symbol = symbol_data["symbol"]

                # Check if we already sent this signal recently
                if await self._is_duplicate_signal(symbol, article.sentiment_label):
                    logger.debug(f"Skipping {symbol} - signal sent recently")
                    continue

                symbol_opportunities.append({
                    "symbol": symbol,
                    "symbol_confidence": symbol_data["confidence"],
                    "article": article,
                    "news_sentiment": article.sentiment_score,
                    "ml_confidence": article.ml_confidence,
                    "sentiment_label": article.sentiment_label
                })

        logger.info(f"Found {len(symbol_opportunities)} unique symbol opportunities")

        if not symbol_opportunities:
            logger.warning("No new symbol opportunities (all filtered as duplicates)")
            return []

        # Step 5: Validate with real-time market data and technical analysis
        logger.info("Validating opportunities with real-time market data...")
        signals = []

        for opportunity in symbol_opportunities:
            try:
                signal = await self._create_signal_from_opportunity(opportunity)
                if signal:
                    signals.append(signal)

                    # Record in history to prevent duplicates
                    await self._record_signal_history(opportunity, signal)

            except Exception as e:
                logger.error(f"Error processing {opportunity['symbol']}: {e}", exc_info=True)
                continue

        # Step 6: Sort by combined score and limit
        signals.sort(key=lambda x: x.confidence_score or 0, reverse=True)
        signals = signals[:max_signals]

        logger.info(f"Generated {len(signals)} final signals")
        return signals

    async def _create_signal_from_opportunity(
        self,
        opportunity: Dict[str, Any]
    ) -> Optional[DigestItemResponse]:
        """
        Create a signal from a news opportunity with technical confirmation.

        Args:
            opportunity: Dict with symbol, article, sentiment data

        Returns:
            DigestItemResponse or None if signal doesn't meet criteria
        """
        symbol = opportunity["symbol"]
        article = opportunity["article"]
        news_sentiment = opportunity["news_sentiment"]

        # Get real-time market data and technical analysis
        logger.debug(f"Fetching technical analysis for {symbol}...")
        analysis = await market_data_service.get_comprehensive_analysis(symbol)

        if not analysis:
            logger.warning(f"No market data available for {symbol}")
            return None

        price_data = analysis.get("price", {})
        current_price = price_data.get("price")

        if not current_price:
            logger.warning(f"No current price for {symbol}")
            return None

        # Calculate technical score
        tech_score = self._calculate_technical_score(
            analysis.get("rsi"),
            analysis.get("macd", {}),
            analysis.get("moving_averages", {}),
            analysis.get("volume", {})
        )

        # Combine news sentiment (70%) with technical (30%)
        # News is primary driver in news-driven system
        combined_score = (news_sentiment * 0.7) + (tech_score * 0.3)

        # Check if signal is strong enough
        if abs(combined_score) < self.MIN_COMBINED_SCORE:
            logger.debug(f"Skipping {symbol}: combined_score={combined_score:.2f} below threshold")
            return None

        logger.info(f"Creating signal for {symbol}: combined={combined_score:.2f}, news={news_sentiment:.2f}, tech={tech_score:.2f}")

        # Determine signal category and priority
        category = self._determine_category(combined_score)
        priority = self._determine_priority(combined_score, opportunity["ml_confidence"])

        # Generate title based on news and current price
        title = self._generate_news_driven_title(symbol, article, current_price, combined_score)

        # Generate summary
        summary = f"{symbol} at ${current_price:.2f} - Breaking: {article.title[:80]}..."

        # Generate explanation
        explanation = self._generate_explanation(
            symbol, article, news_sentiment, tech_score, combined_score,
            price_data, analysis
        )

        # Generate trading guidance
        how_to_trade = self._generate_trading_guidance(
            symbol, combined_score, current_price, analysis
        )

        # Format news articles (just this one breaking article)
        formatted_news = [{
            "title": article.title,
            "summary": article.summary,
            "url": article.url,
            "sentiment_score": article.sentiment_score,
            "source": article.source,
            "published": article.published.isoformat() if isinstance(article.published, datetime) else str(article.published)
        }]

        return DigestItemResponse(
            id=hash(f"{symbol}{article.url}") % 100000,
            symbol=symbol,
            title=title,
            summary=summary,
            explanation=explanation,
            how_to_trade=how_to_trade,
            sentiment_score=round(combined_score, 2),
            confidence_score=round(abs(combined_score), 2),
            priority=priority,
            category=category,
            source="news_driven_ml",
            news_articles=formatted_news,
            metadata={
                "sector": price_data.get("sector"),
                "current_price": current_price,
                "ml_confidence": opportunity["ml_confidence"],
                "news_age_hours": (datetime.utcnow() - article.published).total_seconds() / 3600,
                "rsi": analysis.get("rsi"),
                "technical_score": tech_score,
                "news_sentiment": news_sentiment,
            },
            created_at=datetime.utcnow(),
        )

    def _calculate_technical_score(
        self,
        rsi: Optional[float],
        macd: Optional[Dict],
        mas: Optional[Dict],
        volume: Optional[Dict]
    ) -> float:
        """Calculate technical score (used for confirmation only)."""
        score = 0.0

        # RSI
        if rsi:
            if rsi < 30:
                score += 0.3  # Oversold
            elif rsi > 70:
                score -= 0.3  # Overbought
            elif 40 <= rsi <= 60:
                score += 0.0
            else:
                score += ((50 - rsi) / 100)

        # MACD
        if macd and macd.get("crossover"):
            score += 0.2 if macd["crossover"] == "bullish" else -0.2

        # Moving averages
        if mas:
            if mas.get("above_ema_200"):
                score += 0.15
            if mas.get("golden_cross"):
                score += 0.2
            if mas.get("death_cross"):
                score -= 0.2

        # Volume (confirmation)
        if volume and volume.get("high_volume"):
            score += 0.1 if score > 0 else -0.1

        return max(-1.0, min(1.0, score))

    def _determine_category(self, score: float) -> str:
        """Determine signal category based on score."""
        if abs(score) > 0.6:
            return "trade_alert"
        elif abs(score) > 0.4:
            return "watch_list"
        else:
            return "market_context"

    def _determine_priority(self, score: float, ml_confidence: float) -> str:
        """Determine priority based on score and ML confidence."""
        abs_score = abs(score)

        if abs_score > 0.7 and ml_confidence > 0.8:
            return "high"
        elif abs_score > 0.5:
            return "medium"
        else:
            return "low"

    def _generate_news_driven_title(
        self,
        symbol: str,
        article: Any,
        current_price: float,
        score: float
    ) -> str:
        """Generate title focused on the news event."""
        # Extract key phrase from article title
        title_snippet = article.title[:60]

        if score > 0.5:
            return f"{symbol}: {title_snippet}"
        elif score < -0.5:
            return f"{symbol} Alert: {title_snippet}"
        else:
            return f"{symbol} News: {title_snippet}"

    def _generate_explanation(
        self,
        symbol: str,
        article: Any,
        news_sentiment: float,
        tech_score: float,
        combined_score: float,
        price_data: Dict,
        analysis: Dict
    ) -> str:
        """Generate WHY THIS MATTERS explanation."""
        explanation = "**WHY THIS MATTERS**:\n\n"

        # Breaking news context
        hours_ago = (datetime.utcnow() - article.published).total_seconds() / 3600
        explanation += f"**Breaking News ({hours_ago:.1f}h ago)**: {article.title}\n\n"

        # News sentiment
        sentiment_label = "strongly bullish" if news_sentiment > 0.6 else \
                         "bullish" if news_sentiment > 0.3 else \
                         "strongly bearish" if news_sentiment < -0.6 else \
                         "bearish" if news_sentiment < -0.3 else "neutral"

        explanation += f"**ML Sentiment Analysis**: {sentiment_label} (confidence: {article.ml_confidence:.0%}). "
        explanation += f"FinBERT analysis indicates {sentiment_label} market reaction likely.\n\n"

        # Technical confirmation
        explanation += "**Technical Confirmation**: "
        rsi = analysis.get("rsi")
        if rsi:
            if combined_score > 0 and rsi < 50:
                explanation += f"RSI at {rsi:.0f} suggests room for upside. "
            elif combined_score < 0 and rsi > 50:
                explanation += f"RSI at {rsi:.0f} confirms weakness. "

        macd = analysis.get("macd", {})
        if macd.get("crossover") == "bullish" and combined_score > 0:
            explanation += "MACD bullish crossover confirms momentum. "
        elif macd.get("crossover") == "bearish" and combined_score < 0:
            explanation += "MACD bearish crossover confirms downtrend. "

        explanation += "\n\n"

        # Bottom line
        explanation += "**Bottom Line**: "
        if combined_score > 0.5:
            explanation += f"Strong {sentiment_label} catalyst with technical support. High-probability setup."
        elif combined_score < -0.5:
            explanation += f"Significant {sentiment_label} news with technical weakness. Caution advised."
        else:
            explanation += "News developing. Monitor for clearer technical setup."

        return explanation

    def _generate_trading_guidance(
        self,
        symbol: str,
        score: float,
        current_price: float,
        analysis: Dict
    ) -> str:
        """Generate actionable trading guidance."""
        guidance = "**HOW TO TRADE**:\n\n"

        if score > 0.5:
            # Bullish news-driven setup
            entry = current_price * 1.005  # Enter near current price (news driven)
            stop = current_price * 0.97    # 3% stop
            target1 = current_price * 1.05  # 5% target
            target2 = current_price * 1.10  # 10% target

            guidance += f"**Entry**: ${entry:.2f} (current price ${current_price:.2f}) - News-driven setup, enter quickly\n"
            guidance += f"**Stop Loss**: ${stop:.2f} (3% risk)\n"
            guidance += f"**Targets**: ${target1:.2f} (50% position), ${target2:.2f} (remaining)\n"
            guidance += f"**Size**: 2-3% of portfolio max\n"
            guidance += f"**Timeframe**: 1-5 days (news catalyst trade)\n\n"
            guidance += "**Note**: This is a news-driven momentum trade. Monitor closely and take profits on strength."

        elif score < -0.5:
            # Bearish news-driven
            guidance += f"**Action**: AVOID new long positions\n"
            guidance += f"**If Long**: Consider trimming or exiting positions in {symbol}\n"
            guidance += f"**For Short Sellers**: Entry ${current_price:.2f}, stop ${current_price * 1.03:.2f}, target ${current_price * 0.95:.2f}\n\n"
            guidance += "**Note**: Negative news catalyst. Wait for stabilization before considering long entries."

        else:
            # Developing story
            guidance += f"**Action**: Watch list only - developing news\n"
            guidance += f"**Monitor**: {symbol} for price action around ${current_price:.2f}\n"
            guidance += f"**Entry Trigger**: Break above ${current_price * 1.02:.2f} (bullish) or below ${current_price * 0.98:.2f} (bearish)\n\n"
            guidance += "**Note**: News is fresh but technical setup not confirmed. Wait for clearer signals."

        return guidance

    async def _is_duplicate_signal(self, symbol: str, signal_type: str) -> bool:
        """
        Check if we've sent this signal recently.

        Args:
            symbol: Stock ticker
            signal_type: 'positive', 'negative', or 'neutral'

        Returns:
            True if duplicate, False if new signal
        """
        cutoff_date = datetime.utcnow() - timedelta(days=self.SIGNAL_EXPIRY_DAYS)

        stmt = select(SignalHistory).where(
            and_(
                SignalHistory.symbol == symbol,
                SignalHistory.signal_type == signal_type,
                SignalHistory.created_at >= cutoff_date
            )
        )

        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        return existing is not None

    async def _record_signal_history(
        self,
        opportunity: Dict[str, Any],
        signal: DigestItemResponse
    ):
        """Record signal in history for deduplication."""
        article = opportunity["article"]

        # Create hash of article URL for deduplication
        article_hash = hashlib.md5(article.url.encode()).hexdigest()

        history = SignalHistory(
            symbol=opportunity["symbol"],
            signal_type=opportunity["sentiment_label"],  # 'positive', 'negative', 'neutral'
            confidence_score=signal.confidence_score,
            news_article_id=article_hash,
            news_title=article.title,
            sentiment_score=opportunity["news_sentiment"],
            technical_score=signal.metadata.get("technical_score"),
            price_at_signal=signal.metadata.get("current_price"),
            metadata=signal.metadata,
            expires_at=datetime.utcnow() + timedelta(days=self.SIGNAL_EXPIRY_DAYS)
        )

        self.db.add(history)
        await self.db.commit()

        logger.debug(f"Recorded signal history for {opportunity['symbol']}")


def create_news_driven_generator(db: AsyncSession) -> NewsDrivenSignalGenerator:
    """Factory function to create signal generator with async DB session."""
    return NewsDrivenSignalGenerator(db)
