"""
Signal performance tracking model for measuring signal accuracy.
"""

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class SignalPerformance(Base):
    """
    Signal performance model for tracking trading outcomes.

    Attributes:
        id: Primary key
        signal_id: Foreign key to signals table
        entry_price: Entry price for the trade
        exit_price: Exit price for the trade
        entry_time: When the trade was entered
        exit_time: When the trade was exited
        pnl: Profit/loss amount
        pnl_percentage: Profit/loss percentage
        outcome: Trade outcome (win, loss, breakeven)
        max_gain: Maximum gain achieved during trade
        max_loss: Maximum loss during trade
        notes: Additional performance notes
        created_at: Performance record creation timestamp
    """

    __tablename__ = "signal_performance"

    id = Column(Integer, primary_key=True, index=True)
    signal_id = Column(Integer, ForeignKey("signals.id"), nullable=False)
    entry_price = Column(Float, nullable=True)
    exit_price = Column(Float, nullable=True)
    entry_time = Column(DateTime(timezone=True), nullable=True)
    exit_time = Column(DateTime(timezone=True), nullable=True)
    pnl = Column(Float, nullable=True)
    pnl_percentage = Column(Float, nullable=True)
    outcome = Column(String, nullable=True)
    max_gain = Column(Float, nullable=True)
    max_loss = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    signal = relationship("Signal", back_populates="performance")

    def __repr__(self):
        return f"<SignalPerformance(id={self.id}, signal_id={self.signal_id}, outcome={self.outcome}, pnl={self.pnl})>"
