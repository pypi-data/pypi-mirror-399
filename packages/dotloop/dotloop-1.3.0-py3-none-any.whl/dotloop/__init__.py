"""Dotloop API Python wrapper."""

__version__ = "1.3.0"
__author__ = "The Perry Group"
__email__ = "dev@theperry.group"
__description__ = (
    "Python wrapper for Dotloop API - Real estate transaction management and "
    "document handling"
)

from .account import AccountClient
from .activity import ActivityClient
from .auth import AuthClient

# Import main classes
from .client import DotloopClient
from .contact import ContactClient
from .document import DocumentClient
from .enums import (
    SUPPORTED_WEBHOOK_EVENT_TYPES_BY_TARGET,
    LoopSortCategory,
    LoopStatus,
    ParticipantRole,
    ProfileType,
    SortDirection,
    TransactionType,
    WebhookEventType,
    WebhookTargetType,
)
from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    DotloopError,
    NotFoundError,
    RateLimitError,
    RedirectError,
    ServerError,
    ValidationError,
)
from .folder import FolderClient
from .loop import LoopClient
from .loop_detail import LoopDetailClient
from .loop_it import LoopItClient
from .participant import ParticipantClient
from .profile import ProfileClient
from .task import TaskClient
from .template import TemplateClient
from .webhook import (
    EnsureWebhookSubscriptionAction,
    EnsureWebhookSubscriptionResult,
    WebhookClient,
    WebhookSubscription,
)

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    # Main client
    "DotloopClient",
    # Individual clients
    "AccountClient",
    "ActivityClient",
    "ContactClient",
    "DocumentClient",
    "FolderClient",
    "LoopClient",
    "LoopDetailClient",
    "LoopItClient",
    "ParticipantClient",
    "ProfileClient",
    "TaskClient",
    "TemplateClient",
    "WebhookClient",
    "WebhookSubscription",
    "EnsureWebhookSubscriptionAction",
    "EnsureWebhookSubscriptionResult",
    "AuthClient",
    # Exceptions
    "DotloopError",
    "AuthenticationError",
    "AuthorizationError",
    "ValidationError",
    "NotFoundError",
    "RateLimitError",
    "RedirectError",
    "ServerError",
    # Enums
    "TransactionType",
    "LoopStatus",
    "ParticipantRole",
    "SortDirection",
    "ProfileType",
    "LoopSortCategory",
    "WebhookEventType",
    "WebhookTargetType",
    "SUPPORTED_WEBHOOK_EVENT_TYPES_BY_TARGET",
]
