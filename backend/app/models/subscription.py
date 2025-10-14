"""
Subscription model for tracking user payment plans.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Subscription(Base):
    """
    Subscription model for managing user payment plans.

    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        stripe_subscription_id: Stripe subscription identifier
        stripe_customer_id: Stripe customer identifier
        status: Subscription status (active, canceled, past_due)
        plan: Plan name (free, pro_monthly, pro_yearly, premium_monthly, premium_yearly)
        current_period_start: Current billing period start
        current_period_end: Current billing period end
        cancel_at_period_end: Whether subscription cancels at period end
        created_at: Subscription creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stripe_subscription_id = Column(String, unique=True, nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    status = Column(String, default="active", nullable=False)
    plan = Column(String, default="free", nullable=False)
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end = Column(String, default="false", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan={self.plan}, status={self.status})>"
