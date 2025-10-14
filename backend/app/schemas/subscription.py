"""
Subscription schemas for payment plan management.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SubscriptionBase(BaseModel):
    """Base subscription schema with common fields."""

    plan: str


class SubscriptionCreate(SubscriptionBase):
    """
    Schema for creating a subscription.

    Attributes:
        plan: Subscription plan name
        stripe_payment_method_id: Stripe payment method ID
    """

    stripe_payment_method_id: Optional[str] = None


class SubscriptionResponse(SubscriptionBase):
    """
    Schema for subscription response.

    Attributes:
        id: Subscription ID
        user_id: User ID
        plan: Subscription plan
        status: Subscription status
        current_period_start: Billing period start
        current_period_end: Billing period end
        cancel_at_period_end: Whether subscription cancels at period end
        created_at: Subscription creation timestamp
    """

    id: int
    user_id: int
    status: str
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: str
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionUpdate(BaseModel):
    """
    Schema for updating a subscription.

    Attributes:
        plan: New plan name
        cancel_at_period_end: Whether to cancel at period end
    """

    plan: Optional[str] = None
    cancel_at_period_end: Optional[str] = None
