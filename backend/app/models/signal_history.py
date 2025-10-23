"""
Signal History Model

Tracks previously sent signals to avoid duplicates.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class SignalHistory(Base):
    """
    Track signal history for deduplication.

    Stores all signals sent to users to avoid sending the same
    trade idea repeatedly within a short time window.
    """

    __tablename__ = "signal_history"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    signal_type = Column(String(20), nullable=False)  # 'bullish', 'bearish', 'neutral'
    confidence_score = Column(Float, nullable=False)
    news_article_id = Column(String(255), nullable=True)  # Hash of article URL
    news_title = Column(String, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    technical_score = Column(Float, nullable=True)
    price_at_signal = Column(Float, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)  # Stale date

    def __repr__(self):
        return f"<SignalHistory(symbol={self.symbol}, type={self.signal_type}, confidence={self.confidence_score})>"
