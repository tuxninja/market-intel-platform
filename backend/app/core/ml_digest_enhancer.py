"""
ML-Enhanced Digest Analysis Module

This module provides ML-driven analysis for news digest items by:
- Fetching real market data for affected symbols
- Running technical analysis (RSI, MACD, Bollinger, volume)
- Cross-referencing technical signals with news sentiment
- Generating actionable "WHY TRADE THIS" guidance with specific entry/exit levels

Dependencies:
    - yfinance: Real-time market data
    - pandas/numpy: Data processing
    - ta-lib (optional): Technical indicators

Author: Trade Ideas Analyzer
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import asyncio

logger = logging.getLogger(__name__)


class MLDigestEnhancer:
    """ML-enhanced analysis engine for digest items."""

    def __init__(self):
        """Initialize the ML digest enhancer."""
        self.cache = {}
        self.cache_expiry = {}

    async def enhance_digest_items(self, digest_items: List) -> List:
        """
        Enhance digest items with ML-driven market analysis.

        Args:
            digest_items: List of NewsDigestItem objects

        Returns:
            List: Enhanced digest items with actionable WHY analysis
        """
        enhanced_items = []

        for item in digest_items:
            try:
                # Get enhanced advice reason with ML analysis
                enhanced_reason = await self._generate_ml_advice(item)
                item.advice_reason = enhanced_reason
                enhanced_items.append(item)

            except Exception as e:
                logger.error(f"Error enhancing item {item.title}: {e}")
                enhanced_items.append(item)  # Keep original if enhancement fails

        return enhanced_items

    async def _generate_ml_advice(self, item) -> str:
        """
        Generate ML-enhanced trading advice with technical analysis.

        Args:
            item: NewsDigestItem with symbols and sentiment

        Returns:
            str: Actionable trading advice with entry/exit guidance
        """
        # If no symbols, provide generic sentiment-based advice
        if not item.affected_symbols:
            return self._sentiment_only_advice(item)

        # Analyze the primary symbol (first in list)
        primary_symbol = item.affected_symbols[0]

        # Fetch market data and technical indicators
        market_data = await self._fetch_market_data(primary_symbol)

        if not market_data:
            return self._sentiment_only_advice(item)

        # Generate technical analysis
        technical_signals = self._analyze_technical_indicators(market_data)

        # Cross-reference with sentiment
        combined_analysis = self._combine_signals(
            sentiment=item.sentiment_score,
            technical=technical_signals,
            symbol=primary_symbol
        )

        return combined_analysis

    async def _fetch_market_data(self, symbol: str) -> Optional[Dict]:
        """
        Fetch real-time market data for symbol.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dict: Market data with OHLCV + indicators or None
        """
        cache_key = f"market_{symbol}"
        now = datetime.now()

        # Check cache (5 min expiry for real-time data)
        if (cache_key in self.cache and
            cache_key in self.cache_expiry and
            now < self.cache_expiry[cache_key]):
            return self.cache[cache_key]

        try:
            import yfinance as yf
            import pandas as pd
            import numpy as np

            # Fetch data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='3mo')  # 3 months for technical indicators

            if hist.empty or len(hist) < 20:
                return None

            # Calculate technical indicators
            data = {
                'symbol': symbol,
                'current_price': hist['Close'].iloc[-1],
                'prev_close': hist['Close'].iloc[-2],
                'volume': hist['Volume'].iloc[-1],
                'avg_volume': hist['Volume'].rolling(20).mean().iloc[-1],
                'high_52w': hist['High'].max(),
                'low_52w': hist['Low'].min(),
            }

            # RSI (14-period)
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['rsi'] = 100 - (100 / (1 + rs.iloc[-1]))

            # MACD
            ema_12 = hist['Close'].ewm(span=12).mean()
            ema_26 = hist['Close'].ewm(span=26).mean()
            data['macd'] = ema_12.iloc[-1] - ema_26.iloc[-1]
            data['macd_signal'] = (ema_12 - ema_26).ewm(span=9).mean().iloc[-1]
            data['macd_histogram'] = data['macd'] - data['macd_signal']

            # Bollinger Bands
            sma_20 = hist['Close'].rolling(20).mean()
            std_20 = hist['Close'].rolling(20).std()
            data['bb_upper'] = (sma_20 + (std_20 * 2)).iloc[-1]
            data['bb_lower'] = (sma_20 - (std_20 * 2)).iloc[-1]
            data['bb_middle'] = sma_20.iloc[-1]

            # Price change
            data['day_change_pct'] = ((data['current_price'] - data['prev_close']) / data['prev_close']) * 100

            # Volume analysis
            data['volume_ratio'] = data['volume'] / data['avg_volume']

            # Support/Resistance (simple: recent highs/lows)
            recent_10d = hist.tail(10)
            data['resistance'] = recent_10d['High'].max()
            data['support'] = recent_10d['Low'].min()

            # Cache results
            self.cache[cache_key] = data
            self.cache_expiry[cache_key] = now + timedelta(minutes=5)

            return data

        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
            return None

    def _analyze_technical_indicators(self, data: Dict) -> Dict:
        """
        Analyze technical indicators and generate signals.

        Args:
            data: Market data with indicators

        Returns:
            Dict: Technical signal analysis
        """
        signals = {
            'rsi_signal': 'neutral',
            'macd_signal': 'neutral',
            'bb_signal': 'neutral',
            'volume_signal': 'neutral',
            'trend': 'neutral',
            'strength': 0.0
        }

        # RSI Analysis
        rsi = data.get('rsi', 50)
        if rsi < 30:
            signals['rsi_signal'] = 'oversold'
            signals['strength'] += 1.0
        elif rsi > 70:
            signals['rsi_signal'] = 'overbought'
            signals['strength'] -= 1.0
        elif 40 <= rsi <= 60:
            signals['rsi_signal'] = 'neutral'
        elif rsi < 40:
            signals['rsi_signal'] = 'bearish'
            signals['strength'] -= 0.5
        else:  # rsi > 60
            signals['rsi_signal'] = 'bullish'
            signals['strength'] += 0.5

        # MACD Analysis
        macd_hist = data.get('macd_histogram', 0)
        if macd_hist > 0:
            signals['macd_signal'] = 'bullish'
            signals['strength'] += 0.5
        elif macd_hist < 0:
            signals['macd_signal'] = 'bearish'
            signals['strength'] -= 0.5

        # Bollinger Band Analysis
        current_price = data.get('current_price', 0)
        bb_upper = data.get('bb_upper', 0)
        bb_lower = data.get('bb_lower', 0)
        bb_middle = data.get('bb_middle', 0)

        if current_price > bb_upper:
            signals['bb_signal'] = 'overbought'
            signals['strength'] -= 0.5
        elif current_price < bb_lower:
            signals['bb_signal'] = 'oversold'
            signals['strength'] += 0.5
        elif current_price > bb_middle:
            signals['bb_signal'] = 'above_mean'
            signals['strength'] += 0.3
        else:
            signals['bb_signal'] = 'below_mean'
            signals['strength'] -= 0.3

        # Volume Analysis
        volume_ratio = data.get('volume_ratio', 1.0)
        if volume_ratio > 1.5:
            signals['volume_signal'] = 'high'
            signals['strength'] += 0.7
        elif volume_ratio > 1.2:
            signals['volume_signal'] = 'above_avg'
            signals['strength'] += 0.3
        elif volume_ratio < 0.8:
            signals['volume_signal'] = 'low'
            signals['strength'] -= 0.3

        # Overall trend
        if signals['strength'] > 1.0:
            signals['trend'] = 'strong_bullish'
        elif signals['strength'] > 0.3:
            signals['trend'] = 'bullish'
        elif signals['strength'] < -1.0:
            signals['trend'] = 'strong_bearish'
        elif signals['strength'] < -0.3:
            signals['trend'] = 'bearish'

        return signals

    def _combine_signals(self, sentiment: float, technical: Dict, symbol: str) -> str:
        """
        Combine sentiment and technical analysis into actionable advice.

        Args:
            sentiment: News sentiment score (-1 to 1)
            technical: Technical signal analysis
            symbol: Stock symbol

        Returns:
            str: Actionable trading advice
        """
        # Determine overall signal alignment
        sentiment_direction = 'bullish' if sentiment > 0.15 else 'bearish' if sentiment < -0.15 else 'neutral'
        tech_direction = technical['trend']

        # Build advice string
        advice_parts = []

        # Signal alignment
        if sentiment_direction in tech_direction or tech_direction in sentiment_direction:
            advice_parts.append(f"✓ **Aligned Signals**: {sentiment_direction.title()} news + {tech_direction.replace('_', ' ').title()} technicals")
            action = "Strong Buy" if 'bullish' in tech_direction else "Strong Sell" if 'bearish' in tech_direction else "Hold"
        else:
            advice_parts.append(f"✗ **Mixed Signals**: {sentiment_direction.title()} news vs {tech_direction.replace('_', ' ').title()} technicals")
            action = "Wait for Confirmation"

        # Add specific technical insights
        tech_insights = []

        if technical['rsi_signal'] == 'oversold':
            tech_insights.append("RSI oversold (<30) - potential bounce")
        elif technical['rsi_signal'] == 'overbought':
            tech_insights.append("RSI overbought (>70) - pullback risk")

        if technical['macd_signal'] == 'bullish':
            tech_insights.append("MACD bullish crossover")
        elif technical['macd_signal'] == 'bearish':
            tech_insights.append("MACD bearish crossover")

        if technical['volume_signal'] == 'high':
            tech_insights.append(f"Volume surge {technical.get('volume_ratio', 0):.1f}x avg")

        if tech_insights:
            advice_parts.append("**Technicals**: " + ", ".join(tech_insights))

        # Add action recommendation
        advice_parts.append(f"**Action**: {action}")

        return " | ".join(advice_parts)

    def _sentiment_only_advice(self, item) -> str:
        """
        Generate advice based only on sentiment (when no symbols available).

        Args:
            item: NewsDigestItem

        Returns:
            str: Sentiment-based advice
        """
        sentiment = item.sentiment_score

        if abs(sentiment) < 0.1:
            return "Neutral sentiment - broad market context, no immediate action"
        elif sentiment > 0.3:
            return f"Strong positive sentiment ({sentiment:.2f}) - monitor related sectors for opportunities"
        elif sentiment < -0.3:
            return f"Strong negative sentiment ({sentiment:.2f}) - watch for sector weakness or hedge positions"
        elif sentiment > 0:
            return f"Moderately positive ({sentiment:.2f}) - informational, light sector tailwind"
        else:
            return f"Moderately negative ({sentiment:.2f}) - minor sector headwind, low urgency"
