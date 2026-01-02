"""Enums for the Dotloop API wrapper."""

from enum import Enum


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
