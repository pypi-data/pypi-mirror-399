"""Webhook client for the Dotloop API wrapper."""

from typing import Any, Dict, Iterable, List, Optional, Set, Union

from .base_client import BaseClient
from .enums import WebhookEventType


class WebhookClient(BaseClient):
    """Client for webhook subscription and event API endpoints."""

    @staticmethod
    def _normalize_event_types(
        event_types: Iterable[Union[WebhookEventType, str]],
    ) -> List[str]:
        """Normalize event type values to Dotloop API strings.

        Args:
            event_types: Event types as `WebhookEventType` enum values or raw strings.

        Returns:
            List of event type strings accepted by Dotloop (e.g. "LOOP_CREATED").
        """
        return [
            event_type.value
            if isinstance(event_type, WebhookEventType)
            else str(event_type)
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
        target_type: str,
        target_id: Union[int, str],
        event_types: Iterable[Union[WebhookEventType, str]],
        enabled: bool = True,
        signing_key: Optional[str] = None,
        external_id: Optional[str] = None,
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
        normalized_event_types = self._normalize_event_types(event_types)
        if not normalized_event_types:
            raise ValueError("event_types must not be empty.")

        payload: Dict[str, Any] = {
            "targetType": str(target_type),
            "targetId": target_id,
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
        event_types: Optional[Iterable[Union[WebhookEventType, str]]] = None,
        enabled: Optional[bool] = None,
        signing_key: Optional[str] = None,
        external_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing webhook subscription.

        Args:
            subscription_id: ID of the subscription to update (UUID string)
            url: New URL endpoint.
            event_types: New list of event types to subscribe to.
            enabled: Whether the subscription should be enabled.
            signing_key: Secret key used to sign webhook requests.
            external_id: Identifier included in every webhook event.

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

            event_types_list = subscription.get("eventTypes") or subscription.get("events")
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
