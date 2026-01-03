"""Enums for the Dotloop API wrapper."""

from enum import Enum
from typing import Dict, Tuple


class TransactionType(Enum):
    """Transaction type options."""

    PURCHASE_OFFER = "PURCHASE_OFFER"
    LISTING_FOR_SALE = "LISTING_FOR_SALE"
    PURCHASED = "PURCHASED"
    SOLD = "SOLD"
    LEASE = "LEASE"
    LEASED = "LEASED"


class LoopStatus(Enum):
    """Loop status options."""

    PRE_OFFER = "PRE_OFFER"
    PRE_LISTING = "PRE_LISTING"
    OFFER_SUBMITTED = "OFFER_SUBMITTED"
    UNDER_CONTRACT = "UNDER_CONTRACT"
    SOLD = "SOLD"
    ARCHIVED = "ARCHIVED"
    CANCELLED = "CANCELLED"


class ParticipantRole(Enum):
    """Participant role options."""

    BUYER = "BUYER"
    SELLER = "SELLER"
    LISTING_AGENT = "LISTING_AGENT"
    BUYING_AGENT = "BUYING_AGENT"
    AGENT = "AGENT"
    LENDER = "LENDER"
    TITLE_COMPANY = "TITLE_COMPANY"
    ATTORNEY = "ATTORNEY"
    INSPECTOR = "INSPECTOR"
    APPRAISER = "APPRAISER"
    OTHER = "OTHER"


class SortDirection(Enum):
    """Sort direction options."""

    ASC = "ASC"
    DESC = "DESC"


class ProfileType(Enum):
    """Profile type options."""

    INDIVIDUAL = "INDIVIDUAL"
    TEAM = "TEAM"
    BROKERAGE = "BROKERAGE"


class LoopSortCategory(Enum):
    """Loop sort category options."""

    DEFAULT = "default"
    ADDRESS = "address"
    CREATED = "created"
    UPDATED = "updated"
    PURCHASE_PRICE = "purchase_price"
    LISTING_DATE = "listing_date"
    EXPIRATION_DATE = "expiration_date"
    CLOSING_DATE = "closing_date"
    REVIEW_SUBMISSION_DATE = "review_submission_date"


class WebhookEventType(str, Enum):
    """Webhook event types for subscription `eventTypes`."""

    LOOP_CREATED = "LOOP_CREATED"
    LOOP_UPDATED = "LOOP_UPDATED"
    LOOP_MERGED = "LOOP_MERGED"
    LOOP_PARTICIPANT_CREATED = "LOOP_PARTICIPANT_CREATED"
    LOOP_PARTICIPANT_UPDATED = "LOOP_PARTICIPANT_UPDATED"
    LOOP_PARTICIPANT_DELETED = "LOOP_PARTICIPANT_DELETED"
    CONTACT_CREATED = "CONTACT_CREATED"
    CONTACT_UPDATED = "CONTACT_UPDATED"
    CONTACT_DELETED = "CONTACT_DELETED"
    PROFILE_UPDATED = "PROFILE_UPDATED"
    USER_PROFILE_ACTIVATED = "USER_PROFILE_ACTIVATED"
    USER_PROFILE_DEACTIVATED = "USER_PROFILE_DEACTIVATED"
    USER_ADDED_TO_PROFILE = "USER_ADDED_TO_PROFILE"
    USER_REMOVED_FROM_PROFILE = "USER_REMOVED_FROM_PROFILE"
    SUBSCRIPTION_REMOVED = "SUBSCRIPTION_REMOVED"
    SUBSCRIPTION_DISABLED = "SUBSCRIPTION_DISABLED"
    WEBHOOK_ENDPOINT_TEST_EVENT = "WEBHOOK_ENDPOINT_TEST_EVENT"


class WebhookTargetType(str, Enum):
    """Webhook subscription target types.

    Dotloop webhook subscriptions are created against a `(targetType, targetId)` pair.
    Different target types support different webhook event types.
    """

    PROFILE = "PROFILE"
    USER = "USER"


SUPPORTED_WEBHOOK_EVENT_TYPES_BY_TARGET: Dict[
    WebhookTargetType, Tuple[WebhookEventType, ...]
] = {
    WebhookTargetType.PROFILE: (
        WebhookEventType.LOOP_CREATED,
        WebhookEventType.LOOP_UPDATED,
        WebhookEventType.LOOP_MERGED,
        WebhookEventType.LOOP_PARTICIPANT_CREATED,
        WebhookEventType.LOOP_PARTICIPANT_UPDATED,
        WebhookEventType.LOOP_PARTICIPANT_DELETED,
    ),
    WebhookTargetType.USER: (
        WebhookEventType.CONTACT_CREATED,
        WebhookEventType.CONTACT_UPDATED,
        WebhookEventType.CONTACT_DELETED,
        WebhookEventType.PROFILE_UPDATED,
        WebhookEventType.USER_PROFILE_ACTIVATED,
        WebhookEventType.USER_PROFILE_DEACTIVATED,
        WebhookEventType.USER_ADDED_TO_PROFILE,
        WebhookEventType.USER_REMOVED_FROM_PROFILE,
    ),
}
