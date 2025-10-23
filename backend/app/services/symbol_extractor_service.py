"""
Symbol Extraction Service

Extracts stock ticker symbols from news articles using multiple methods:
1. Pattern matching for explicit tickers (AAPL, $TSLA, etc.)
2. Company name to ticker mapping
3. Named Entity Recognition (NER) for company names
"""

import logging
import re
from typing import List, Set, Optional, Dict
from functools import lru_cache

logger = logging.getLogger(__name__)


class SymbolExtractor:
    """
    Extract stock ticker symbols from news text.
    """

    # Common ticker patterns
    TICKER_PATTERN = r'\b([A-Z]{1,5})\b'  # 1-5 uppercase letters
    DOLLAR_TICKER_PATTERN = r'\$([A-Z]{1,5})\b'  # $AAPL format

    # Company name to ticker mapping (most common stocks)
    COMPANY_TO_TICKER = {
        # Tech Giants
        "apple": "AAPL",
        "microsoft": "MSFT",
        "google": "GOOGL",
        "alphabet": "GOOGL",
        "amazon": "AMZN",
        "meta": "META",
        "facebook": "META",
        "tesla": "TSLA",
        "nvidia": "NVDA",
        "netflix": "NFLX",

        # Other Tech
        "amd": "AMD",
        "intel": "INTC",
        "qualcomm": "QCOM",
        "broadcom": "AVGO",
        "oracle": "ORCL",
        "salesforce": "CRM",
        "adobe": "ADBE",
        "servicenow": "NOW",
        "snowflake": "SNOW",
        "palantir": "PLTR",
        "databricks": "DATABRICKS",
        "airbnb": "ABNB",
        "uber": "UBER",
        "lyft": "LYFT",
        "doordash": "DASH",

        # Finance
        "jpmorgan": "JPM",
        "jp morgan": "JPM",
        "goldman sachs": "GS",
        "morgan stanley": "MS",
        "bank of america": "BAC",
        "wells fargo": "WFC",
        "citigroup": "C",
        "coinbase": "COIN",
        "robinhood": "HOOD",
        "square": "SQ",
        "block": "SQ",
        "paypal": "PYPL",
        "visa": "V",
        "mastercard": "MA",

        # Retail & Consumer
        "walmart": "WMT",
        "target": "TGT",
        "costco": "COST",
        "home depot": "HD",
        "lowe's": "LOW",
        "nike": "NKE",
        "starbucks": "SBUX",
        "mcdonald's": "MCD",
        "chipotle": "CMG",
        "shopify": "SHOP",

        # Healthcare & Pharma
        "pfizer": "PFE",
        "moderna": "MRNA",
        "johnson & johnson": "JNJ",
        "merck": "MRK",
        "abbvie": "ABBV",
        "eli lilly": "LLY",
        "unitedhealth": "UNH",

        # Energy
        "exxon": "XOM",
        "chevron": "CVX",
        "conocophillips": "COP",
        "schlumberger": "SLB",

        # Entertainment
        "disney": "DIS",
        "comcast": "CMCSA",
        "warner bros": "WBD",
        "paramount": "PARA",
        "spotify": "SPOT",

        # Automotive
        "ford": "F",
        "general motors": "GM",
        "gm": "GM",
        "lucid": "LCID",
        "rivian": "RIVN",
        "nio": "NIO",

        # Aerospace
        "boeing": "BA",
        "lockheed martin": "LMT",
        "raytheon": "RTX",

        # Indices (for context)
        "s&p 500": "SPY",
        "s&p": "SPY",
        "nasdaq": "QQQ",
        "dow jones": "DIA",
        "dow": "DIA",
    }

    # Common words to exclude (not tickers)
    EXCLUDED_WORDS = {
        "CEO", "CFO", "CTO", "NYSE", "NASDAQ", "USD", "USA",
        "SEC", "FDA", "FTC", "IPO", "ETF", "API", "AI", "ML",
        "Q1", "Q2", "Q3", "Q4", "YOY", "MOM", "EBITDA", "PE",
        "EPS", "GDP", "CPI", "PPI", "FOMC", "FED", "DOJ", "FBI",
        "REIT", "SPAC", "ARKK", "VIX", "DXY", "BTC", "ETH",
        "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL",
        "CAN", "HER", "WAS", "ONE", "OUR", "OUT", "DAY", "GET",
        "HAS", "HIM", "HIS", "HOW", "ITS", "MAY", "NEW", "NOW",
        "OLD", "SEE", "TWO", "WAY", "WHO", "BOY", "DID", "ITS",
        "LET", "PUT", "SAY", "SHE", "TOO", "USE", "DAD", "MOM",
        "BIG", "FUN", "SIR", "YES"
    }

    def __init__(self):
        """Initialize symbol extractor."""
        pass

    def extract_tickers_from_text(self, text: str) -> Set[str]:
        """
        Extract ticker symbols from text using pattern matching.

        Args:
            text: News article text (title + summary)

        Returns:
            Set of extracted ticker symbols
        """
        tickers = set()

        # Method 1: $TICKER format (most reliable)
        dollar_tickers = re.findall(self.DOLLAR_TICKER_PATTERN, text)
        tickers.update(dollar_tickers)

        # Method 2: Explicit ticker patterns (e.g., "AAPL stock", "TSLA shares")
        # Look for uppercase words followed by stock-related keywords
        ticker_contexts = re.finditer(
            r'\b([A-Z]{2,5})\s+(stock|shares|equity|ticker|symbol|corporation|corp|inc)\b',
            text,
            re.IGNORECASE
        )
        for match in ticker_contexts:
            ticker = match.group(1)
            if ticker not in self.EXCLUDED_WORDS:
                tickers.add(ticker)

        # Method 3: Parenthetical tickers (e.g., "Apple (AAPL)")
        paren_tickers = re.findall(r'\(([A-Z]{2,5})\)', text)
        for ticker in paren_tickers:
            if ticker not in self.EXCLUDED_WORDS:
                tickers.add(ticker)

        return tickers

    def extract_companies_from_text(self, text: str) -> Set[str]:
        """
        Extract company names and map to tickers.

        Args:
            text: News article text

        Returns:
            Set of ticker symbols from company names
        """
        tickers = set()
        text_lower = text.lower()

        # Check for each known company name
        for company_name, ticker in self.COMPANY_TO_TICKER.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(company_name) + r'\b'
            if re.search(pattern, text_lower):
                tickers.add(ticker)

        return tickers

    def extract_symbols(
        self,
        title: str,
        summary: str,
        min_confidence: float = 0.5
    ) -> List[Dict[str, any]]:
        """
        Extract stock symbols from news article with confidence scores.

        Args:
            title: Article title
            summary: Article summary/content
            min_confidence: Minimum confidence threshold (0-1)

        Returns:
            List of dicts: [{"symbol": "AAPL", "confidence": 0.95, "method": "dollar_sign"}, ...]
        """
        results = []
        text = f"{title} {summary}"

        # Extract using different methods
        ticker_symbols = self.extract_tickers_from_text(text)
        company_symbols = self.extract_companies_from_text(text)

        # Tickers found via explicit patterns (higher confidence)
        for symbol in ticker_symbols:
            # Check if ticker appears in title (very high confidence)
            if symbol in title.upper():
                confidence = 0.95
            # Check if ticker appears multiple times
            elif text.upper().count(symbol) > 2:
                confidence = 0.85
            else:
                confidence = 0.7

            if confidence >= min_confidence:
                results.append({
                    "symbol": symbol,
                    "confidence": confidence,
                    "method": "ticker_pattern"
                })

        # Companies mapped to tickers (medium-high confidence)
        for symbol in company_symbols:
            # Avoid duplicates
            if any(r["symbol"] == symbol for r in results):
                continue

            # Check if company name appears in title
            company_name = self._get_company_name(symbol)
            if company_name and company_name.lower() in title.lower():
                confidence = 0.9
            # Multiple mentions
            elif text.lower().count(company_name.lower()) > 1:
                confidence = 0.75
            else:
                confidence = 0.6

            if confidence >= min_confidence:
                results.append({
                    "symbol": symbol,
                    "confidence": confidence,
                    "method": "company_name"
                })

        # Sort by confidence (highest first)
        results.sort(key=lambda x: x["confidence"], reverse=True)

        return results

    def _get_company_name(self, ticker: str) -> Optional[str]:
        """Get company name from ticker (reverse lookup)."""
        for company, symbol in self.COMPANY_TO_TICKER.items():
            if symbol == ticker:
                return company
        return None

    def is_valid_ticker(self, symbol: str) -> bool:
        """
        Check if a symbol is likely a valid stock ticker.

        Args:
            symbol: Ticker symbol to validate

        Returns:
            True if likely valid, False otherwise
        """
        # Length check (1-5 chars)
        if not (1 <= len(symbol) <= 5):
            return False

        # Must be all uppercase letters
        if not symbol.isalpha() or not symbol.isupper():
            return False

        # Not in exclusion list
        if symbol in self.EXCLUDED_WORDS:
            return False

        # Known ticker or company mapping
        if symbol in self.COMPANY_TO_TICKER.values():
            return True

        # If 2-4 chars and not excluded, probably valid
        if 2 <= len(symbol) <= 4:
            return True

        return False


# Global service instance
symbol_extractor = SymbolExtractor()
