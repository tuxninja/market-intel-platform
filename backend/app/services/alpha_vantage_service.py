"""
Alpha Vantage Market Data Service

Provides real-time stock data and technical indicators using Alpha Vantage API.
Free tier: 25 API calls per day, 5 calls per minute.
"""

import logging
import os
from typing import Dict, Optional, Any
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)


class AlphaVantageService:
    """Service for fetching market data from Alpha Vantage API."""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self):
        """Initialize Alpha Vantage service."""
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if not self.api_key:
            logger.warning("ALPHA_VANTAGE_API_KEY not set - market data will be unavailable")

    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get real-time quote for a symbol.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dict with price, volume, change data or None if failed
        """
        if not self.api_key:
            logger.error("Alpha Vantage API key not configured")
            return None

        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(self.BASE_URL, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        logger.error(f"Alpha Vantage API error {response.status} for {symbol}")
                        return None

                    data = await response.json()

                    # Check for API limit message
                    if "Note" in data:
                        logger.warning(f"Alpha Vantage API limit reached: {data['Note']}")
                        return None

                    if "Error Message" in data:
                        logger.error(f"Alpha Vantage error for {symbol}: {data['Error Message']}")
                        return None

                    quote = data.get("Global Quote", {})
                    if not quote:
                        logger.warning(f"No quote data for {symbol}")
                        return None

                    # Parse the response
                    price = float(quote.get("05. price", 0))
                    previous_close = float(quote.get("08. previous close", 0))
                    change = float(quote.get("09. change", 0))
                    change_percent = quote.get("10. change percent", "0%").rstrip("%")
                    volume = int(quote.get("06. volume", 0))
                    high = float(quote.get("03. high", 0))
                    low = float(quote.get("04. low", 0))
                    open_price = float(quote.get("02. open", 0))

                    return {
                        "symbol": symbol,
                        "price": round(price, 2),
                        "change": round(change, 2),
                        "change_percent": round(float(change_percent), 2),
                        "volume": volume,
                        "day_high": round(high, 2) if high else None,
                        "day_low": round(low, 2) if low else None,
                        "open": round(open_price, 2) if open_price else None,
                        "previous_close": round(previous_close, 2),
                        "timestamp": datetime.utcnow().isoformat(),
                    }

        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None

    async def get_technical_indicators(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get technical indicators (RSI, MACD, etc.) for a symbol.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dict with technical indicators or None if failed
        """
        if not self.api_key:
            return None

        try:
            # Get RSI
            rsi_params = {
                "function": "RSI",
                "symbol": symbol,
                "interval": "daily",
                "time_period": 14,
                "series_type": "close",
                "apikey": self.api_key
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(self.BASE_URL, params=rsi_params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        return None

                    data = await response.json()

                    if "Note" in data or "Error Message" in data:
                        return None

                    # Get the most recent RSI value
                    technical_analysis = data.get("Technical Analysis: RSI", {})
                    if not technical_analysis:
                        return None

                    # Get most recent date
                    latest_date = sorted(technical_analysis.keys(), reverse=True)[0]
                    rsi_value = float(technical_analysis[latest_date]["RSI"])

                    return {
                        "rsi": round(rsi_value, 2),
                        "timestamp": latest_date
                    }

        except Exception as e:
            logger.error(f"Error fetching technical indicators for {symbol}: {e}")
            return None


# Global service instance
alpha_vantage_service = AlphaVantageService()
