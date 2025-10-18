"""
Market Data Service Module

Fetches real-time stock prices, technical indicators, and market data.
Uses Alpha Vantage API as primary source, yfinance as fallback.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
from ta.trend import MACD, EMAIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volume import OnBalanceVolumeIndicator, VolumeWeightedAveragePrice
from app.services.alpha_vantage_service import alpha_vantage_service

logger = logging.getLogger(__name__)


class MarketDataService:
    """
    Service for fetching real-time market data and calculating technical indicators.

    Uses Alpha Vantage API (with rate limiting) and yfinance as fallback.
    """

    def __init__(self):
        """Initialize market data service."""
        self.use_alpha_vantage = True  # Try Alpha Vantage first

    async def get_stock_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get current stock price and basic info.

        Args:
            symbol: Stock ticker symbol (e.g., "AAPL")

        Returns:
            Dict with current price, change, volume, etc.

        Example:
            {
                "symbol": "AAPL",
                "price": 182.50,
                "change": 2.30,
                "change_percent": 1.28,
                "volume": 45234567,
                "day_high": 183.20,
                "day_low": 180.10,
                "open": 181.00,
                "previous_close": 180.20
            }
        """
        # Try Alpha Vantage first
        if self.use_alpha_vantage:
            try:
                quote = await alpha_vantage_service.get_quote(symbol)
                if quote:
                    logger.info(f"Got price for {symbol} from Alpha Vantage")
                    return quote
                else:
                    logger.debug(f"Alpha Vantage failed for {symbol}, trying yfinance")
            except Exception as e:
                logger.debug(f"Alpha Vantage error for {symbol}: {e}")

        # Fallback to yfinance (but it's rate limited)
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Get current price
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            previous_close = info.get('previousClose')

            if not current_price or not previous_close:
                logger.warning(f"Could not get price for {symbol} from yfinance")
                return None

            change = current_price - previous_close
            change_percent = (change / previous_close) * 100

            logger.info(f"Got price for {symbol} from yfinance fallback")
            return {
                "symbol": symbol,
                "price": round(current_price, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "volume": info.get('volume', 0),
                "day_high": info.get('dayHigh'),
                "day_low": info.get('dayLow'),
                "open": info.get('open'),
                "previous_close": previous_close,
                "market_cap": info.get('marketCap'),
                "sector": info.get('sector'),
                "industry": info.get('industry'),
            }

        except Exception as e:
            logger.error(f"Error fetching price for {symbol} (both APIs failed): {e}")
            return None

    async def get_historical_data(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Get historical price data.

        Args:
            symbol: Stock ticker
            period: Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            interval: Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo

        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)

            if df.empty:
                logger.warning(f"No historical data for {symbol}")
                return None

            return df

        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None

    async def calculate_rsi(
        self,
        symbol: str,
        period: int = 14,
        lookback: str = "3mo"
    ) -> Optional[float]:
        """
        Calculate RSI (Relative Strength Index).

        Args:
            symbol: Stock ticker
            period: RSI period (default 14 days)
            lookback: How far back to fetch data

        Returns:
            Current RSI value (0-100)
            - < 30: Oversold (bullish signal)
            - > 70: Overbought (bearish signal)
        """
        try:
            df = await self.get_historical_data(symbol, period=lookback)
            if df is None or df.empty:
                return None

            # Calculate RSI using ta library
            rsi_indicator = RSIIndicator(close=df['Close'], window=period)
            rsi = rsi_indicator.rsi()

            # Return most recent RSI value
            current_rsi = rsi.iloc[-1]
            return round(current_rsi, 2)

        except Exception as e:
            logger.error(f"Error calculating RSI for {symbol}: {e}")
            return None

    async def calculate_macd(
        self,
        symbol: str,
        lookback: str = "6mo"
    ) -> Optional[Dict[str, float]]:
        """
        Calculate MACD (Moving Average Convergence Divergence).

        Args:
            symbol: Stock ticker
            lookback: How far back to fetch data

        Returns:
            Dict with MACD, signal, and histogram values
        """
        try:
            df = await self.get_historical_data(symbol, period=lookback)
            if df is None or df.empty:
                return None

            # Calculate MACD (12, 26, 9)
            macd_indicator = MACD(
                close=df['Close'],
                window_slow=26,
                window_fast=12,
                window_sign=9
            )

            macd = macd_indicator.macd()
            signal = macd_indicator.macd_signal()
            histogram = macd_indicator.macd_diff()

            return {
                "macd": round(macd.iloc[-1], 4),
                "signal": round(signal.iloc[-1], 4),
                "histogram": round(histogram.iloc[-1], 4),
                "crossover": "bullish" if histogram.iloc[-1] > 0 else "bearish"
            }

        except Exception as e:
            logger.error(f"Error calculating MACD for {symbol}: {e}")
            return None

    async def calculate_moving_averages(
        self,
        symbol: str,
        lookback: str = "6mo"
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate moving averages (SMA and EMA).

        Args:
            symbol: Stock ticker
            lookback: How far back to fetch data

        Returns:
            Dict with 20, 50, 200 day MAs
        """
        try:
            df = await self.get_historical_data(symbol, period=lookback)
            if df is None or df.empty:
                return None

            current_price = df['Close'].iloc[-1]

            # Calculate EMAs
            ema_20 = EMAIndicator(close=df['Close'], window=20).ema_indicator().iloc[-1]
            ema_50 = EMAIndicator(close=df['Close'], window=50).ema_indicator().iloc[-1]
            ema_200 = EMAIndicator(close=df['Close'], window=200).ema_indicator().iloc[-1] if len(df) >= 200 else None

            return {
                "current_price": round(current_price, 2),
                "ema_20": round(ema_20, 2),
                "ema_50": round(ema_50, 2),
                "ema_200": round(ema_200, 2) if ema_200 else None,
                "above_ema_20": current_price > ema_20,
                "above_ema_50": current_price > ema_50,
                "above_ema_200": current_price > ema_200 if ema_200 else None,
                "golden_cross": ema_50 > ema_200 if ema_200 else None,  # Bullish
                "death_cross": ema_50 < ema_200 if ema_200 else None,   # Bearish
            }

        except Exception as e:
            logger.error(f"Error calculating MAs for {symbol}: {e}")
            return None

    async def analyze_volume(
        self,
        symbol: str,
        lookback: str = "3mo"
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze volume trends.

        Args:
            symbol: Stock ticker
            lookback: How far back to fetch data

        Returns:
            Dict with volume analysis
        """
        try:
            df = await self.get_historical_data(symbol, period=lookback)
            if df is None or df.empty:
                return None

            current_volume = df['Volume'].iloc[-1]
            avg_volume_20 = df['Volume'].tail(20).mean()
            avg_volume_50 = df['Volume'].tail(50).mean()

            # On-Balance Volume (OBV)
            obv_indicator = OnBalanceVolumeIndicator(
                close=df['Close'],
                volume=df['Volume']
            )
            obv = obv_indicator.on_balance_volume().iloc[-1]

            return {
                "current_volume": int(current_volume),
                "avg_volume_20day": int(avg_volume_20),
                "avg_volume_50day": int(avg_volume_50),
                "volume_ratio_20day": round(current_volume / avg_volume_20, 2),
                "volume_ratio_50day": round(current_volume / avg_volume_50, 2),
                "high_volume": current_volume > (avg_volume_20 * 1.5),  # 50% above average
                "obv": int(obv),
            }

        except Exception as e:
            logger.error(f"Error analyzing volume for {symbol}: {e}")
            return None

    async def get_comprehensive_analysis(
        self,
        symbol: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive technical analysis for a symbol.

        Combines price, indicators, volume analysis.

        Args:
            symbol: Stock ticker

        Returns:
            Complete analysis dict
        """
        try:
            # Fetch all data concurrently would be ideal, but for simplicity run sequentially
            price_data = await self.get_stock_price(symbol)
            if not price_data:
                return None

            rsi = await self.calculate_rsi(symbol)
            macd = await self.calculate_macd(symbol)
            mas = await self.calculate_moving_averages(symbol)
            volume = await self.analyze_volume(symbol)

            return {
                "symbol": symbol,
                "timestamp": datetime.utcnow().isoformat(),
                "price": price_data,
                "rsi": rsi,
                "macd": macd,
                "moving_averages": mas,
                "volume": volume,
            }

        except Exception as e:
            logger.error(f"Error getting comprehensive analysis for {symbol}: {e}")
            return None

    async def get_market_indices(self) -> Dict[str, Dict[str, Any]]:
        """
        Get current values for major market indices.

        Returns:
            Dict with SPY, DIA, QQQ, VIX data
        """
        indices = {
            "SPY": "^GSPC",  # S&P 500
            "DIA": "^DJI",   # Dow Jones
            "QQQ": "^IXIC",  # NASDAQ
            "VIX": "^VIX",   # Volatility Index
        }

        result = {}

        for name, symbol in indices.items():
            try:
                data = await self.get_stock_price(symbol)
                if data:
                    result[name] = {
                        "level": data["price"],
                        "change": f"+{data['change_percent']:.2f}%" if data['change_percent'] >= 0 else f"{data['change_percent']:.2f}%",
                        "raw_change": data['change_percent']
                    }
            except Exception as e:
                logger.error(f"Error fetching index {name}: {e}")
                result[name] = {
                    "level": 0,
                    "change": "N/A",
                    "raw_change": 0
                }

        return result

    async def get_vix_regime(self) -> Dict[str, Any]:
        """
        Get VIX regime information.

        Returns:
            VIX level and regime classification
        """
        try:
            vix_data = await self.get_stock_price("^VIX")
            if not vix_data:
                return {
                    "vix_level": 15.5,
                    "regime": "NORMAL",
                    "description": "Unable to fetch VIX data"
                }

            vix_level = vix_data["price"]

            # Classify regime
            if vix_level < 15:
                regime = "LOW_VOL"
                description = "Low volatility - favorable for momentum strategies"
            elif vix_level < 20:
                regime = "NORMAL"
                description = "Normal volatility - balanced market conditions"
            elif vix_level < 30:
                regime = "ELEVATED"
                description = "Elevated volatility - caution advised"
            else:
                regime = "HIGH_VOL"
                description = "High volatility - risk-off environment"

            return {
                "vix_level": round(vix_level, 2),
                "regime": regime,
                "description": description
            }

        except Exception as e:
            logger.error(f"Error fetching VIX regime: {e}")
            return {
                "vix_level": 15.5,
                "regime": "NORMAL",
                "description": "Unable to fetch VIX data"
            }


# Global service instance
market_data_service = MarketDataService()
