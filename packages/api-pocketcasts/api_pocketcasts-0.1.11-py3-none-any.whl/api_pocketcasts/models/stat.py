# Subscription status models for Pocket Casts API
from typing import Optional, List
import attr


@attr.s(auto_attribs=True, frozen=True)
class SubscriptionFeatures:
    remove_banner_ads: Optional[bool] = None
    remove_discover_ads: Optional[bool] = None


@attr.s(auto_attribs=True, frozen=True)
class SubscriptionTier:
    monthly: Optional[int] = None
    yearly: Optional[int] = None
    trial_days: Optional[int] = None


@attr.s(auto_attribs=True, frozen=True)
class SubscriptionWeb:
    monthly: Optional[int] = None
    yearly: Optional[int] = None
    trial: Optional[int] = None
    web_status: Optional[int] = None
    plus: Optional[SubscriptionTier] = None
    patron: Optional[SubscriptionTier] = None


@attr.s(auto_attribs=True, frozen=True)
class SubscriptionStatus:
    paid: Optional[int] = None
    platform: Optional[int] = None
    auto_renewing: Optional[bool] = None
    gift_days: Optional[int] = None
    cancel_url: Optional[str] = None
    update_url: Optional[str] = None
    frequency: Optional[int] = None
    web: Optional[SubscriptionWeb] = None
    subscriptions: Optional[List[dict]] = None
    type: Optional[int] = None
    index: Optional[int] = None
    web_status: Optional[int] = None
    tier: Optional[str] = None
    features: Optional[SubscriptionFeatures] = None
    created_at: Optional[str] = None
