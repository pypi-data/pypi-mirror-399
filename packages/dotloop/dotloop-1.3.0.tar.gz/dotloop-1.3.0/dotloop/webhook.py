"""Webhook client for the Dotloop API wrapper."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union

from .account import AccountClient
from .base_client import BaseClient
from .enums import (
    SUPPORTED_WEBHOOK_EVENT_TYPES_BY_TARGET,
    WebhookEventType,
    WebhookTargetType,
)

WebhookEventTypeInput = Union[WebhookEventType, str]
WebhookTargetTypeInput = Union[WebhookTargetType, str]


@dataclass(frozen=True)
class WebhookSubscription:
    """Typed webhook subscription model.

    Attributes:
        id: Subscription UUID.
        target_type: Dotloop subscription target type (PROFILE or USER).
        target_id: Numeric target ID (profile id or user id depending on target type).
        url: Webhook endpoint URL.
        enabled: Whether the subscription is enabled.
        event_types: Event types configured on the subscription.
        signing_key: Optional secret key used to sign webhook requests.
        external_id: Optional identifier included in every webhook event.
        raw: Raw API payload used to create this model (for forward compatibility).
    """

    id: str
    target_type: WebhookTargetType
    target_id: int
    url: str
    enabled: bool
    event_types: Tuple[WebhookEventTypeInput, ...]
    signing_key: Optional[str] = None
    external_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, subscription: Dict[str, Any]) -> "WebhookSubscription":
        """Parse a webhook subscription returned by the Dotloop API.

        Args:
            subscription: Raw subscription payload (single object, not wrapped in
                {"data": ...}).

        Returns:
            Parsed `WebhookSubscription`.

        Raises:
            ValueError: If required fields are missing or invalid.
        """
        if "id" not in subscription:
            raise ValueError("Subscription payload missing required field: id")

        target_type_raw = subscription.get("targetType")
        if target_type_raw is None:
            raise ValueError("Subscription payload missing required field: targetType")
        target_type = WebhookTargetType(str(target_type_raw))

        target_id_raw = subscription.get("targetId")
        if target_id_raw is None:
            raise ValueError("Subscription payload missing required field: targetId")
        target_id = cls._normalize_target_id(target_id_raw)

        url_raw = subscription.get("url")
        if url_raw is None:
            raise ValueError("Subscription payload missing required field: url")

        enabled_value = subscription.get("enabled")
        if enabled_value is None:
            enabled_value = subscription.get("active")
        if enabled_value is None:
            enabled_value = subscription.get("isActive")
        enabled = bool(enabled_value) if enabled_value is not None else True

        event_types_raw = (
            subscription.get("eventTypes")
            or subscription.get("events")
            or subscription.get("event_types")
        )
        if not isinstance(event_types_raw, list):
            raise ValueError(
                "Subscription payload missing required field: eventTypes (list)"
            )

        event_types: Tuple[WebhookEventTypeInput, ...] = tuple(
            cls._parse_event_type(value) for value in event_types_raw
        )

        return cls(
            id=str(subscription["id"]),
            target_type=target_type,
            target_id=target_id,
            url=str(url_raw),
            enabled=enabled,
            event_types=event_types,
            signing_key=(
                str(subscription["signingKey"])
                if subscription.get("signingKey") is not None
                else None
            ),
            external_id=(
                str(subscription["externalId"])
                if subscription.get("externalId") is not None
                else None
            ),
            raw=dict(subscription),
        )

    @staticmethod
    def _normalize_target_id(target_id: Any) -> int:
        """Normalize a subscription target ID to an integer.

        Args:
            target_id: Target id value. The API commonly returns this as a number,
                but it may appear as a numeric string.

        Returns:
            Normalized numeric target id.

        Raises:
            ValueError: If the target id cannot be parsed as an integer.
        """
        if isinstance(target_id, bool):
            raise ValueError("target_id must be an integer or numeric string.")
        if isinstance(target_id, int):
            return target_id

        target_id_str = str(target_id).strip()
        if not target_id_str.isdigit():
            raise ValueError(
                "target_id must be an integer or numeric string; got " f"{target_id!r}."
            )
        return int(target_id_str)

    @staticmethod
    def _parse_event_type(value: Any) -> WebhookEventTypeInput:
        """Parse a webhook event type value into an enum where possible."""
        try:
            return WebhookEventType(str(value))
        except ValueError:
            return str(value)

    def event_type_values(self) -> Tuple[str, ...]:
        """Get event types as raw API strings."""
        return tuple(
            (
                event_type.value
                if isinstance(event_type, WebhookEventType)
                else str(event_type)
            )
            for event_type in self.event_types
        )


class EnsureWebhookSubscriptionAction(str, Enum):
    """Action taken by `WebhookClient.ensure_subscription()`."""

    CREATED = "created"
    UPDATED = "updated"
    NOOP = "noop"


@dataclass(frozen=True)
class EnsureWebhookSubscriptionResult:
    """Result for an idempotent webhook subscription ensure operation."""

    action: EnsureWebhookSubscriptionAction
    target_type: WebhookTargetType
    target_id: int
    url: str
    subscription_id: Optional[str]
    enabled_event_types: Tuple[str, ...]
    changes: Dict[str, Dict[str, Any]]
    dry_run: bool = False


class WebhookClient(BaseClient):
    """Client for webhook subscription and event API endpoints."""

    @staticmethod
    def _normalize_target_type(
        target_type: WebhookTargetTypeInput,
    ) -> WebhookTargetType:
        """Normalize a webhook target type into a `WebhookTargetType` enum.

        Args:
            target_type: Target type as enum or raw string (e.g. "PROFILE").

        Returns:
            Normalized `WebhookTargetType`.

        Raises:
            ValueError: If the target type is not recognized.
        """
        if isinstance(target_type, WebhookTargetType):
            return target_type
        return WebhookTargetType(str(target_type))

    @staticmethod
    def _normalize_target_id(target_id: Union[int, str]) -> int:
        """Normalize a webhook target id into an integer.

        Args:
            target_id: Target id as int or numeric string.

        Returns:
            Target id as an integer.

        Raises:
            ValueError: If the target id is not an integer or numeric string.
        """
        return WebhookSubscription._normalize_target_id(target_id)

    @classmethod
    def validate_event_types(
        cls,
        *,
        target_type: WebhookTargetTypeInput,
        event_types: Iterable[WebhookEventTypeInput],
    ) -> None:
        """Validate that the given event types are compatible with a target type.

        Args:
            target_type: Subscription target type (PROFILE or USER).
            event_types: Event types for the subscription.

        Raises:
            ValueError: If any event type is invalid for the given target type.
        """
        normalized_target_type = cls._normalize_target_type(target_type)
        normalized_event_types = WebhookClient._normalize_event_types(event_types)

        allowed = SUPPORTED_WEBHOOK_EVENT_TYPES_BY_TARGET[normalized_target_type]
        allowed_values = {event.value for event in allowed}

        invalid = sorted(
            {
                event_type
                for event_type in normalized_event_types
                if event_type not in allowed_values
            }
        )
        if invalid:
            valid_sorted = sorted(allowed_values)
            raise ValueError(
                "Invalid event_types for target_type "
                f"{normalized_target_type.value}: {invalid}. "
                f"Valid event types: {valid_sorted}."
            )

    @staticmethod
    def _normalize_event_types(
        event_types: Iterable[WebhookEventTypeInput],
    ) -> List[str]:
        """Normalize event type values to Dotloop API strings.

        Args:
            event_types: Event types as `WebhookEventType` enum values or raw strings.

        Returns:
            List of event type strings accepted by Dotloop (e.g. "LOOP_CREATED").
        """
        return [
            (
                event_type.value
                if isinstance(event_type, WebhookEventType)
                else str(event_type)
            )
            for event_type in event_types
        ]

    def list_subscriptions(
        self, enabled: Optional[bool] = None, next_cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """List all webhook subscriptions.

        Args:
            enabled: Filter results by enabled subscriptions.
            next_cursor: Pagination cursor from a previous response.

        Returns:
            Dictionary containing list of webhook subscriptions with metadata

        Raises:
            DotloopError: If the API request fails

        Example:
            ```python
            subscriptions = client.webhook.list_subscriptions()
            for subscription in subscriptions['data']:
                print(f"Subscription ID: {subscription['id']}")
                print(f"  URL: {subscription['url']}")
                print(f"  Enabled: {subscription.get('enabled')}")
                print(f"  Event types: {subscription.get('eventTypes')}")
            ```
        """
        params: Dict[str, Any] = {}
        if enabled is not None:
            params["enabled"] = str(enabled).lower()
        if next_cursor is not None:
            params["next_cursor"] = next_cursor

        return self.get("/subscription", params=params or None)

    def get_subscription(self, subscription_id: Union[str, int]) -> Dict[str, Any]:
        """Retrieve an individual webhook subscription by ID.

        Args:
            subscription_id: ID of the subscription to retrieve (UUID string)

        Returns:
            Dictionary containing subscription information

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the subscription is not found

        Example:
            ```python
            subscription = client.webhook.get_subscription(
                subscription_id="68bc4c39-0366-4faa-885a-5ff4803b2dbb"
            )
            print(f"URL: {subscription['data']['url']}")
            print(f"Enabled: {subscription['data']['enabled']}")
            ```
        """
        return self.get(f"/subscription/{subscription_id}")

    def create_subscription(
        self,
        *,
        url: str,
        target_type: WebhookTargetTypeInput,
        target_id: Union[int, str],
        event_types: Iterable[WebhookEventTypeInput],
        enabled: bool = True,
        signing_key: Optional[str] = None,
        external_id: Optional[str] = None,
        validate: bool = False,
    ) -> Dict[str, Any]:
        """Create a new webhook subscription.

        Args:
            url: Public HTTPS URL Dotloop should POST events to.
            target_type: Dotloop subscription target type (e.g. "PROFILE").
            target_id: ID of the target (e.g. profile id).
            event_types: Event types accepted by Dotloop (e.g. "LOOP_CREATED").
            enabled: Whether the subscription is enabled.
            signing_key: Optional secret key used to sign webhook requests.
            external_id: Optional identifier included in every webhook event.
            validate: If True, validate that `event_types` are compatible with
                `target_type` and normalize `target_id` into an integer.

        Returns:
            Dictionary containing created subscription information

        Raises:
            DotloopError: If the API request fails
            ValidationError: If parameters are invalid

        Example:
            ```python
            subscription = client.webhook.create_subscription(
                url="https://myapp.com/webhook",
                target_type="PROFILE",
                target_id=15637525,
                event_types=[
                    WebhookEventType.LOOP_CREATED,
                    WebhookEventType.LOOP_UPDATED,
                ],
                enabled=True,
            )
            print(f"Created subscription: {subscription['data']['id']}")
            ```
        """
        target_type_value = (
            target_type.value
            if isinstance(target_type, WebhookTargetType)
            else str(target_type)
        )
        normalized_event_types = self._normalize_event_types(event_types)
        if not normalized_event_types:
            raise ValueError("event_types must not be empty.")

        normalized_target_id: Union[int, str] = target_id
        if validate:
            normalized_target_type = self._normalize_target_type(target_type)
            normalized_target_id = self._normalize_target_id(target_id)
            self.validate_event_types(
                target_type=normalized_target_type, event_types=event_types
            )
            target_type_value = normalized_target_type.value

        payload: Dict[str, Any] = {
            "targetType": target_type_value,
            "targetId": normalized_target_id,
            "url": str(url),
            "eventTypes": normalized_event_types,
            "enabled": bool(enabled),
        }

        if signing_key is not None:
            payload["signingKey"] = str(signing_key)
        if external_id is not None:
            payload["externalId"] = str(external_id)

        return self.post("/subscription", data=payload)

    def update_subscription(
        self,
        subscription_id: Union[str, int],
        *,
        url: Optional[str] = None,
        event_types: Optional[Iterable[WebhookEventTypeInput]] = None,
        enabled: Optional[bool] = None,
        signing_key: Optional[str] = None,
        external_id: Optional[str] = None,
        validate: bool = False,
    ) -> Dict[str, Any]:
        """Update an existing webhook subscription.

        Args:
            subscription_id: ID of the subscription to update (UUID string)
            url: New URL endpoint.
            event_types: New list of event types to subscribe to.
            enabled: Whether the subscription should be enabled.
            signing_key: Secret key used to sign webhook requests.
            external_id: Identifier included in every webhook event.
            validate: If True and `event_types` is provided, fetch the current
                subscription to validate that the new `event_types` are compatible
                with the subscription's target type.

        Returns:
            Dictionary containing updated subscription information

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the subscription is not found
            ValidationError: If parameters are invalid

        Example:
            ```python
            subscription = client.webhook.update_subscription(
                subscription_id="68bc4c39-0366-4faa-885a-5ff4803b2dbb",
                url="https://myapp.com/new-webhook",
                enabled=False
            )
            ```
        """
        data: Dict[str, Any] = {}

        if url is not None:
            data["url"] = str(url)
        if event_types is not None:
            if validate:
                existing = self.get_subscription(subscription_id)
                existing_target_type = self._normalize_target_type(
                    existing.get("data", {}).get("targetType")
                )
                self.validate_event_types(
                    target_type=existing_target_type, event_types=event_types
                )
            data["eventTypes"] = self._normalize_event_types(event_types)
        if enabled is not None:
            data["enabled"] = bool(enabled)
        if signing_key is not None:
            data["signingKey"] = str(signing_key)
        if external_id is not None:
            data["externalId"] = str(external_id)

        if not data:
            raise ValueError("At least one field must be provided to update.")

        return self.patch(f"/subscription/{subscription_id}", data=data)

    def delete_subscription(self, subscription_id: Union[str, int]) -> Dict[str, Any]:
        """Delete a webhook subscription.

        Args:
            subscription_id: ID of the subscription to delete (UUID string)

        Returns:
            Dictionary containing deletion confirmation

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the subscription is not found

        Example:
            ```python
            result = client.webhook.delete_subscription(subscription_id=123)
            ```
        """
        return self.delete(f"/subscription/{subscription_id}")

    def _iter_subscriptions_raw(
        self, enabled: Optional[bool] = None
    ) -> Iterable[Dict[str, Any]]:
        """Iterate over all subscriptions (auto-paginates).

        Args:
            enabled: Optional filter to return only enabled subscriptions.

        Yields:
            Subscription objects (not wrapped in {"data": ...}).
        """
        next_cursor: Optional[str] = None
        while True:
            response = self.list_subscriptions(enabled=enabled, next_cursor=next_cursor)
            data = response.get("data", [])
            if isinstance(data, list):
                for subscription in data:
                    if isinstance(subscription, dict):
                        yield subscription

            meta = response.get("meta", {}) or {}
            next_cursor = meta.get("nextCursor") or meta.get("next_cursor")
            if not next_cursor:
                break

    def ensure_subscription(
        self,
        *,
        url: str,
        target_type: WebhookTargetTypeInput,
        target_id: Union[int, str],
        event_types: Iterable[WebhookEventTypeInput],
        enabled: bool = True,
        signing_key: Optional[str] = None,
        external_id: Optional[str] = None,
        validate: bool = True,
        dry_run: bool = False,
    ) -> EnsureWebhookSubscriptionResult:
        """Ensure a webhook subscription exists and matches the desired configuration.

        This method implements an idempotent "make it so" workflow:
        - Find an existing subscription matching `(targetType, targetId)` and update it if
          it differs.
        - If multiple subscriptions exist for the same target pair, it will prefer an
          exact URL match. If no URL match is found, a new subscription will be created.

        Args:
            url: Desired webhook endpoint URL.
            target_type: Subscription target type (PROFILE or USER).
            target_id: Target id (numeric). String numeric values are accepted.
            event_types: Desired event types. Order is not significant.
            enabled: Desired enabled state.
            signing_key: Optional signing key. If provided, ensure this value matches.
            external_id: Optional external id. If provided, ensure this value matches.
            validate: If True, validate `event_types` against `target_type`, and
                normalize `target_id` into an integer.
            dry_run: If True, do not perform create/update calls; return the planned
                action and diff only.

        Returns:
            Result describing whether the subscription was created, updated, or already
            matched the desired configuration.

        Raises:
            ValueError: If validation fails or required inputs are invalid.
            DotloopError: If the API request fails.
        """
        normalized_target_type = self._normalize_target_type(target_type)
        normalized_target_id = self._normalize_target_id(target_id)

        normalized_event_types = self._normalize_event_types(event_types)
        if not normalized_event_types:
            raise ValueError("event_types must not be empty.")

        desired_event_types = tuple(sorted(set(normalized_event_types)))

        if validate:
            self.validate_event_types(
                target_type=normalized_target_type, event_types=event_types
            )

        candidates: List[WebhookSubscription] = []
        for subscription_raw in self._iter_subscriptions_raw():
            try:
                candidate = WebhookSubscription.from_api(subscription_raw)
            except ValueError:
                continue
            if (
                candidate.target_type == normalized_target_type
                and candidate.target_id == normalized_target_id
            ):
                candidates.append(candidate)

        selected: Optional[WebhookSubscription] = None
        if not candidates:
            action = EnsureWebhookSubscriptionAction.CREATED
        elif len(candidates) == 1:
            selected = candidates[0]
            action = EnsureWebhookSubscriptionAction.UPDATED
        else:
            for candidate in candidates:
                if candidate.url == url:
                    selected = candidate
                    break
            action = (
                EnsureWebhookSubscriptionAction.UPDATED
                if selected is not None
                else EnsureWebhookSubscriptionAction.CREATED
            )

        if action == EnsureWebhookSubscriptionAction.CREATED:
            changes: Dict[str, Dict[str, Any]] = {
                "targetType": {"to": normalized_target_type.value},
                "targetId": {"to": normalized_target_id},
                "url": {"to": url},
                "enabled": {"to": bool(enabled)},
                "eventTypes": {"to": list(desired_event_types)},
            }
            if signing_key is not None:
                changes["signingKey"] = {"to": signing_key}
            if external_id is not None:
                changes["externalId"] = {"to": external_id}

            if dry_run:
                return EnsureWebhookSubscriptionResult(
                    action=EnsureWebhookSubscriptionAction.CREATED,
                    target_type=normalized_target_type,
                    target_id=normalized_target_id,
                    url=url,
                    subscription_id=None,
                    enabled_event_types=desired_event_types,
                    changes=changes,
                    dry_run=True,
                )

            response = self.create_subscription(
                url=url,
                target_type=normalized_target_type,
                target_id=normalized_target_id,
                event_types=desired_event_types,
                enabled=enabled,
                signing_key=signing_key,
                external_id=external_id,
                validate=False,
            )
            created_id = response.get("data", {}).get("id")

            return EnsureWebhookSubscriptionResult(
                action=EnsureWebhookSubscriptionAction.CREATED,
                target_type=normalized_target_type,
                target_id=normalized_target_id,
                url=url,
                subscription_id=str(created_id) if created_id is not None else None,
                enabled_event_types=desired_event_types,
                changes=changes,
                dry_run=False,
            )

        if selected is None:  # pragma: no cover
            raise ValueError("Unexpected state: selected subscription is missing.")

        changes = {}
        update_kwargs: Dict[str, Any] = {}

        if selected.url != url:
            changes["url"] = {"from": selected.url, "to": url}
            update_kwargs["url"] = url

        if bool(selected.enabled) != bool(enabled):
            changes["enabled"] = {"from": bool(selected.enabled), "to": bool(enabled)}
            update_kwargs["enabled"] = bool(enabled)

        if set(selected.event_type_values()) != set(desired_event_types):
            changes["eventTypes"] = {
                "from": list(sorted(set(selected.event_type_values()))),
                "to": list(desired_event_types),
            }
            update_kwargs["event_types"] = desired_event_types

        if signing_key is not None and signing_key != selected.signing_key:
            changes["signingKey"] = {"from": selected.signing_key, "to": signing_key}
            update_kwargs["signing_key"] = signing_key

        if external_id is not None and external_id != selected.external_id:
            changes["externalId"] = {"from": selected.external_id, "to": external_id}
            update_kwargs["external_id"] = external_id

        if not update_kwargs:
            return EnsureWebhookSubscriptionResult(
                action=EnsureWebhookSubscriptionAction.NOOP,
                target_type=normalized_target_type,
                target_id=normalized_target_id,
                url=url,
                subscription_id=selected.id,
                enabled_event_types=desired_event_types,
                changes={},
                dry_run=False,
            )

        if dry_run:
            return EnsureWebhookSubscriptionResult(
                action=EnsureWebhookSubscriptionAction.UPDATED,
                target_type=normalized_target_type,
                target_id=normalized_target_id,
                url=url,
                subscription_id=selected.id,
                enabled_event_types=desired_event_types,
                changes=changes,
                dry_run=True,
            )

        self.update_subscription(
            selected.id,
            validate=False,
            **update_kwargs,
        )

        return EnsureWebhookSubscriptionResult(
            action=EnsureWebhookSubscriptionAction.UPDATED,
            target_type=normalized_target_type,
            target_id=normalized_target_id,
            url=url,
            subscription_id=selected.id,
            enabled_event_types=desired_event_types,
            changes=changes,
            dry_run=False,
        )

    def ensure_default_subscriptions(
        self,
        url: str,
        *,
        enabled: bool = True,
        signing_key: Optional[str] = None,
        external_id: Optional[str] = None,
        dry_run: bool = False,
    ) -> List[EnsureWebhookSubscriptionResult]:
        """Ensure default webhook subscriptions for both PROFILE and USER targets.

        Dotloop webhook event types are target-specific. In many real-world integrations,
        "subscribe to everything valid" means creating two subscriptions:
        - PROFILE subscription (loop + participant events) for `account.defaultProfileId`
        - USER subscription (contact + membership events) for `account.id`

        Args:
            url: Webhook endpoint URL.
            enabled: Whether the subscriptions should be enabled.
            signing_key: Optional signing key to set on subscriptions.
            external_id: Optional external id to set on subscriptions.
            dry_run: If True, do not perform create/update calls; return planned actions.

        Returns:
            List of ensure results (PROFILE first, USER second).

        Raises:
            ValueError: If account fields required for defaults are missing.
            DotloopError: If API requests fail.
        """
        account_client = AccountClient(
            api_key=self._api_key, base_url=self._base_url, timeout=self._timeout
        )
        account = account_client.get_account()
        account_data = account.get("data", {}) if isinstance(account, dict) else {}

        user_id_raw = account_data.get("id")
        default_profile_id_raw = account_data.get("defaultProfileId")
        if user_id_raw is None:
            raise ValueError("Account response missing required field: data.id")
        if default_profile_id_raw is None:
            raise ValueError(
                "Account response missing required field: data.defaultProfileId"
            )

        user_id = self._normalize_target_id(user_id_raw)
        default_profile_id = self._normalize_target_id(default_profile_id_raw)

        profile_events = SUPPORTED_WEBHOOK_EVENT_TYPES_BY_TARGET[
            WebhookTargetType.PROFILE
        ]
        user_events = SUPPORTED_WEBHOOK_EVENT_TYPES_BY_TARGET[WebhookTargetType.USER]

        results: List[EnsureWebhookSubscriptionResult] = [
            self.ensure_subscription(
                url=url,
                target_type=WebhookTargetType.PROFILE,
                target_id=default_profile_id,
                event_types=profile_events,
                enabled=enabled,
                signing_key=signing_key,
                external_id=external_id,
                validate=True,
                dry_run=dry_run,
            ),
            self.ensure_subscription(
                url=url,
                target_type=WebhookTargetType.USER,
                target_id=user_id,
                event_types=user_events,
                enabled=enabled,
                signing_key=signing_key,
                external_id=external_id,
                validate=True,
                dry_run=dry_run,
            ),
        ]

        return results

    def list_events(
        self,
        subscription_id: Union[str, int],
        delivery_status: Optional[str] = None,
        next_cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List events for a webhook subscription.

        Args:
            subscription_id: ID of the subscription (UUID string)
            delivery_status: Optional filter for event delivery status.
            next_cursor: Pagination cursor from a previous response.

        Returns:
            Dictionary containing list of webhook events

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the subscription is not found

        Example:
            ```python
            events = client.webhook.list_events(
                subscription_id="68bc4c39-0366-4faa-885a-5ff4803b2dbb"
            )
            for event in events['data']:
                print(f"Event: {event['eventType']} at {event['createdOn']}")
                print(f"  Status: {event['deliveryStatus']}")
                print(f"  Attempts: {event['deliveryAttempts']}")
            ```
        """
        params: Dict[str, Any] = {}
        if delivery_status is not None:
            params["delivery_status"] = delivery_status
        if next_cursor is not None:
            params["next_cursor"] = next_cursor

        return self.get(f"/subscription/{subscription_id}/event", params=params or None)

    def get_event(
        self, subscription_id: Union[str, int], event_id: Union[str, int]
    ) -> Dict[str, Any]:
        """Retrieve an individual webhook event by ID.

        Args:
            subscription_id: ID of the subscription (UUID string)
            event_id: ID of the event to retrieve (UUID string)

        Returns:
            Dictionary containing event information

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the event is not found

        Example:
            ```python
            event = client.webhook.get_event(
                subscription_id="68bc4c39-0366-4faa-885a-5ff4803b2dbb",
                event_id="5f6667e3-4b65-4025-9d64-f8d695b3ebb5",
            )
            print(f"Event: {event['data']['eventType']}")
            print(f"Event data: {event['data']['eventData']}")
            print(f"Response data: {event['data']['responseData']}")
            ```
        """
        return self.get(f"/subscription/{subscription_id}/event/{event_id}")

    def activate_subscription(self, subscription_id: Union[str, int]) -> Dict[str, Any]:
        """Activate a webhook subscription.

        Convenience method to set a subscription as active.

        Args:
            subscription_id: ID of the subscription to activate

        Returns:
            Dictionary containing updated subscription information

        Example:
            ```python
            subscription = client.webhook.activate_subscription(
                subscription_id="68bc4c39-0366-4faa-885a-5ff4803b2dbb"
            )
            ```
        """
        return self.update_subscription(subscription_id, enabled=True)

    def deactivate_subscription(
        self, subscription_id: Union[str, int]
    ) -> Dict[str, Any]:
        """Deactivate a webhook subscription.

        Convenience method to set a subscription as inactive.

        Args:
            subscription_id: ID of the subscription to deactivate

        Returns:
            Dictionary containing updated subscription information

        Example:
            ```python
            subscription = client.webhook.deactivate_subscription(
                subscription_id="68bc4c39-0366-4faa-885a-5ff4803b2dbb"
            )
            ```
        """
        return self.update_subscription(subscription_id, enabled=False)

    def get_failed_events(self, subscription_id: Union[str, int]) -> Dict[str, Any]:
        """Get failed webhook events for a subscription.

        Args:
            subscription_id: ID of the subscription (UUID string)

        Returns:
            Dictionary containing failed events

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the subscription is not found

        Example:
            ```python
            failed_events = client.webhook.get_failed_events(
                subscription_id="68bc4c39-0366-4faa-885a-5ff4803b2dbb"
            )
            print(f"Failed events: {len(failed_events['data'])}")
            for event in failed_events['data']:
                print(
                    f"- {event['eventType']} failed {event['deliveryAttempts']} times"
                )
            ```
        """
        all_events = self.list_events(subscription_id)

        # Filter for failed events (assuming status indicates failure)
        failed_events = [
            event
            for event in all_events["data"]
            if (
                (event.get("deliveryStatus") or event.get("status") or "")
                .upper()
                .strip()
                in ["FAILED", "FAILURE", "ERROR", "TIMEOUT"]
            )
        ]

        return {
            "data": failed_events,
            "meta": {
                "total": len(failed_events),
                "filtered_from": all_events["meta"]["total"],
                "subscription_id": subscription_id,
            },
        }

    def get_subscription_summary(
        self, subscription_id: Union[str, int]
    ) -> Dict[str, Any]:
        """Get a summary of webhook events for a subscription.

        Args:
            subscription_id: ID of the subscription (UUID string)

        Returns:
            Dictionary containing event summary statistics

        Raises:
            DotloopError: If the API request fails
            NotFoundError: If the subscription is not found

        Example:
            ```python
            summary = client.webhook.get_subscription_summary(subscription_id=123)
            print(f"Total events: {summary['total_events']}")
            print(f"Successful: {summary['successful_events']}")
            print(f"Failed: {summary['failed_events']}")
            print(f"Success rate: {summary['success_rate']:.1f}%")
            ```
        """
        events = self.list_events(subscription_id)
        event_list = events["data"]

        total_events = len(event_list)
        successful_events = 0
        failed_events = 0

        event_types: Dict[str, int] = {}

        for event in event_list:
            # Count event types
            event_type = event.get("eventType") or event.get("type") or "UNKNOWN"
            event_types[event_type] = event_types.get(event_type, 0) + 1

            # Count success/failure
            status = (event.get("deliveryStatus") or event.get("status") or "").upper()
            if status in ["SUCCESS", "DELIVERED", "OK"]:
                successful_events += 1
            elif status in ["FAILED", "FAILURE", "ERROR", "TIMEOUT"]:
                failed_events += 1

        success_rate = (
            (successful_events / total_events * 100) if total_events > 0 else 0
        )

        return {
            "subscription_id": subscription_id,
            "total_events": total_events,
            "successful_events": successful_events,
            "failed_events": failed_events,
            "success_rate": success_rate,
            "event_types": event_types,
            "most_common_event": (
                max(event_types.items(), key=lambda x: x[1])[0] if event_types else None
            ),
        }

    def get_all_subscriptions_summary(self) -> Dict[str, Any]:
        """Get a summary of all webhook subscriptions.

        Returns:
            Dictionary containing summary statistics for all subscriptions

        Raises:
            DotloopError: If the API request fails

        Example:
            ```python
            summary = client.webhook.get_all_subscriptions_summary()
            print(f"Total subscriptions: {summary['total_subscriptions']}")
            print(f"Active subscriptions: {summary['active_subscriptions']}")
            print(f"Inactive subscriptions: {summary['inactive_subscriptions']}")
            ```
        """
        subscriptions = self.list_subscriptions()
        subscription_list = subscriptions["data"]

        total_subscriptions = len(subscription_list)
        active_subscriptions = 0
        inactive_subscriptions = 0

        subscription_urls: Set[str] = set()
        event_types: Set[str] = set()

        for subscription in subscription_list:
            # Count active/inactive
            enabled = subscription.get("enabled")
            if enabled is None:
                enabled = subscription.get("active") or subscription.get("isActive")

            if bool(enabled):
                active_subscriptions += 1
            else:
                inactive_subscriptions += 1

            # Collect unique URLs and event types
            if "url" in subscription:
                subscription_urls.add(subscription["url"])

            event_types_list = subscription.get("eventTypes") or subscription.get(
                "events"
            )
            if isinstance(event_types_list, list):
                for event in event_types_list:
                    event_types.add(event)

        return {
            "total_subscriptions": total_subscriptions,
            "active_subscriptions": active_subscriptions,
            "inactive_subscriptions": inactive_subscriptions,
            "unique_urls": len(subscription_urls),
            "unique_event_types": len(event_types),
            "event_types": list(event_types),
        }
