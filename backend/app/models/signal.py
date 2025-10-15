"""
Signal model for storing trading signals and market intelligence.
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Signal(Base):
    """
    Signal model for trading signals and market intelligence items.

    Attributes:
        id: Primary key
        symbol: Stock ticker symbol
        title: Signal headline/title
        summary: Brief summary of the signal
        explanation: Detailed WHY THIS MATTERS explanation
        how_to_trade: HOW TO TRADE guidance
        sentiment_score: Sentiment analysis score (-1 to 1)
        confidence_score: Signal confidence score (0 to 1)
        priority: Signal priority (high, medium, low)
        category: Signal category (trade_alert, watch_list, market_context)
        source: Data source information
        extra_data: Additional signal metadata (JSON)
        created_at: Signal generation timestamp
        expires_at: Signal expiration timestamp
    """

    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=True)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    how_to_trade = Column(Text, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    priority = Column(String, default="medium", nullable=False)
    category = Column(String, default="market_context", nullable=False)
    source = Column(String, nullable=True)
    extra_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    performance = relationship("SignalPerformance", back_populates="signal", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Signal(id={self.id}, symbol={self.symbol}, category={self.category}, priority={self.priority})>"
