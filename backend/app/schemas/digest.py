"""
Digest schemas for market intelligence responses.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


class DigestItemResponse(BaseModel):
    """
    Schema for a single digest item.

    Attributes:
        id: Signal ID
        symbol: Stock ticker symbol
        title: Signal headline
        summary: Brief summary
        explanation: WHY THIS MATTERS explanation
        how_to_trade: HOW TO TRADE guidance
        sentiment_score: Sentiment score (-1 to 1)
        confidence_score: Confidence score (0 to 1)
        priority: Signal priority (high, medium, low)
        category: Signal category (trade_alert, watch_list, market_context)
        source: Data source
        metadata: Additional metadata
        created_at: Creation timestamp
    """

    id: Optional[int] = None
    symbol: Optional[str] = None
    title: str
    summary: str
    explanation: Optional[str] = None
    how_to_trade: Optional[str] = None
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    priority: str = "medium"
    category: str = "market_context"
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DigestResponse(BaseModel):
    """
    Schema for complete digest response.

    Attributes:
        generated_at: Digest generation timestamp
        items: List of digest items
        total_items: Total number of items
        market_context: Overall market context information
        vix_regime: VIX market regime information
    """

    generated_at: datetime
    items: List[DigestItemResponse]
    total_items: int
    market_context: Optional[Dict[str, Any]] = None
    vix_regime: Optional[Dict[str, Any]] = None


class DigestRequest(BaseModel):
    """
    Schema for digest generation request.

    Attributes:
        max_items: Maximum number of items to return
        hours_lookback: Hours to look back for news
        enable_ml: Whether to enable ML enhancement
        categories: Filter by specific categories
    """

    max_items: int = Field(20, ge=1, le=100)
    hours_lookback: int = Field(24, ge=1, le=168)
    enable_ml: bool = True
    categories: Optional[List[str]] = None
