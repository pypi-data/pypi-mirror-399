"""Tests for the WebhookClient."""

import json
from urllib.parse import parse_qs, urlparse

import pytest
import responses

from dotloop.enums import (
    SUPPORTED_WEBHOOK_EVENT_TYPES_BY_TARGET,
    WebhookEventType,
    WebhookTargetType,
)
from dotloop.exceptions import AuthenticationError, DotloopError, NotFoundError
from dotloop.webhook import (
    EnsureWebhookSubscriptionAction,
    WebhookClient,
    WebhookSubscription,
)


class TestWebhookClientInit:
    """Test WebhookClient initialization."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with provided API key."""
        client = WebhookClient(api_key="test_key")
        assert client._api_key == "test_key"

    def test_init_without_api_key_raises_error(self) -> None:
        """Test initialization without API key raises error."""
        with pytest.raises(AuthenticationError):
            WebhookClient()


class TestWebhookClientMethods:
    """Test WebhookClient methods."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = WebhookClient(api_key="test_key")

    @responses.activate
    def test_list_subscriptions_success(self) -> None:
        """Test successful subscriptions listing."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/subscription",
            json={
                "data": [
                    {
                        "id": "68bc4c39-0366-4faa-885a-5ff4803b2dbb",
                        "targetType": "PROFILE",
                        "targetId": "15637525",
                        "url": "https://myapp.com/webhook",
                        "enabled": True,
                        "eventTypes": ["LOOP_CREATED", "LOOP_UPDATED"],
                    },
                    {
                        "id": "7dbf7306-6015-48aa-8e9b-205363514d32",
                        "targetType": "PROFILE",
                        "targetId": "15637525",
                        "url": "https://test.com/webhook",
                        "enabled": False,
                        "eventTypes": ["CONTACT_CREATED"],
                    },
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        result = self.client.list_subscriptions()

        assert len(result["data"]) == 2
        assert result["data"][0]["url"] == "https://myapp.com/webhook"
        assert result["data"][0]["enabled"] is True
        assert result["data"][1]["enabled"] is False

    @responses.activate
    def test_list_subscriptions_with_query_params(self) -> None:
        """Test listing subscriptions with enabled and next_cursor query params."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/subscription",
            json={"data": [], "meta": {"total": 0}},
            status=200,
        )

        self.client.list_subscriptions(enabled=True, next_cursor="cursor123")

        request_url = responses.calls[-1].request.url
        parsed = urlparse(request_url)
        query = parse_qs(parsed.query)
        assert query["enabled"] == ["true"]
        assert query["next_cursor"] == ["cursor123"]

    @responses.activate
    def test_get_subscription_success(self) -> None:
        """Test successful subscription retrieval."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/subscription/68bc4c39-0366-4faa-885a-5ff4803b2dbb",
            json={
                "data": {
                    "id": "68bc4c39-0366-4faa-885a-5ff4803b2dbb",
                    "targetType": "PROFILE",
                    "targetId": "15637525",
                    "url": "https://myapp.com/webhook",
                    "enabled": True,
                    "eventTypes": ["LOOP_CREATED", "LOOP_UPDATED"],
                }
            },
            status=200,
        )

        result = self.client.get_subscription(
            subscription_id="68bc4c39-0366-4faa-885a-5ff4803b2dbb"
        )

        assert result["data"]["url"] == "https://myapp.com/webhook"
        assert result["data"]["enabled"] is True
        assert len(result["data"]["eventTypes"]) == 2

    @responses.activate
    def test_create_subscription_success(self) -> None:
        """Test successful subscription creation."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/subscription",
            json={
                "data": {
                    "id": "68bc4c39-0366-4faa-885a-5ff4803b2dbb",
                    "targetType": "PROFILE",
                    "targetId": "15637525",
                    "url": "https://newapp.com/webhook",
                    "enabled": True,
                    "eventTypes": ["LOOP_CREATED", "LOOP_PARTICIPANT_CREATED"],
                }
            },
            status=201,
        )

        result = self.client.create_subscription(
            url="https://newapp.com/webhook",
            target_type="PROFILE",
            target_id=15637525,
            event_types=[
                WebhookEventType.LOOP_CREATED,
                WebhookEventType.LOOP_PARTICIPANT_CREATED,
            ],
            enabled=True,
        )

        assert (
            responses.calls[-1].request.url
            == "https://api-gateway.dotloop.com/public/v2/subscription"
        )
        assert json.loads(responses.calls[-1].request.body) == {
            "targetType": "PROFILE",
            "targetId": 15637525,
            "url": "https://newapp.com/webhook",
            "eventTypes": ["LOOP_CREATED", "LOOP_PARTICIPANT_CREATED"],
            "enabled": True,
        }
        assert result["data"]["enabled"] is True

    @responses.activate
    def test_create_subscription_with_string_events(self) -> None:
        """Test subscription creation with string event types."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/subscription",
            json={
                "data": {
                    "id": "68bc4c39-0366-4faa-885a-5ff4803b2dbb",
                    "targetType": "PROFILE",
                    "targetId": "15637525",
                    "url": "https://app.com/webhook",
                    "enabled": True,
                    "eventTypes": ["CONTACT_CREATED"],
                }
            },
            status=201,
        )

        result = self.client.create_subscription(
            url="https://app.com/webhook",
            target_type="PROFILE",
            target_id="15637525",
            event_types=["CONTACT_CREATED"],
        )

        assert json.loads(responses.calls[-1].request.body) == {
            "targetType": "PROFILE",
            "targetId": "15637525",
            "url": "https://app.com/webhook",
            "eventTypes": ["CONTACT_CREATED"],
            "enabled": True,
        }
        assert result["data"]["url"] == "https://app.com/webhook"

    def test_create_subscription_empty_event_types_raises(self) -> None:
        """Test create_subscription rejects empty event_types."""
        with pytest.raises(ValueError):
            self.client.create_subscription(
                url="https://app.com/webhook",
                target_type="PROFILE",
                target_id=15637525,
                event_types=[],
            )

    def test_update_subscription_without_fields_raises(self) -> None:
        """Test update_subscription rejects empty update payload."""
        with pytest.raises(ValueError):
            self.client.update_subscription(
                subscription_id="68bc4c39-0366-4faa-885a-5ff4803b2dbb"
            )

    @responses.activate
    def test_create_subscription_with_signing_and_external_id(self) -> None:
        """Test create_subscription includes signingKey and externalId when provided."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/subscription",
            json={"data": {"id": "68bc4c39-0366-4faa-885a-5ff4803b2dbb"}},
            status=200,
        )

        self.client.create_subscription(
            url="https://newapp.com/webhook",
            target_type="PROFILE",
            target_id=15637525,
            event_types=[WebhookEventType.LOOP_CREATED],
            enabled=True,
            signing_key="super_secret_key",
            external_id="my_external_id",
        )

        assert json.loads(responses.calls[-1].request.body) == {
            "targetType": "PROFILE",
            "targetId": 15637525,
            "url": "https://newapp.com/webhook",
            "eventTypes": ["LOOP_CREATED"],
            "enabled": True,
            "signingKey": "super_secret_key",
            "externalId": "my_external_id",
        }

    @responses.activate
    def test_update_subscription_with_signing_and_external_id(self) -> None:
        """Test update_subscription includes signingKey and externalId when provided."""
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/subscription/68bc4c39-0366-4faa-885a-5ff4803b2dbb",
            json={"data": {"id": "68bc4c39-0366-4faa-885a-5ff4803b2dbb"}},
            status=200,
        )

        self.client.update_subscription(
            subscription_id="68bc4c39-0366-4faa-885a-5ff4803b2dbb",
            signing_key="super_secret_key",
            external_id="my_external_id",
        )

        assert json.loads(responses.calls[-1].request.body) == {
            "signingKey": "super_secret_key",
            "externalId": "my_external_id",
        }

    @responses.activate
    def test_update_subscription_success(self) -> None:
        """Test successful subscription update."""
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/subscription/68bc4c39-0366-4faa-885a-5ff4803b2dbb",
            json={
                "data": {
                    "id": "68bc4c39-0366-4faa-885a-5ff4803b2dbb",
                    "targetType": "PROFILE",
                    "targetId": "15637525",
                    "url": "https://updated.com/webhook",
                    "enabled": False,
                    "eventTypes": ["LOOP_CREATED"],
                }
            },
            status=200,
        )

        result = self.client.update_subscription(
            subscription_id="68bc4c39-0366-4faa-885a-5ff4803b2dbb",
            url="https://updated.com/webhook",
            enabled=False,
            event_types=[WebhookEventType.LOOP_CREATED],
        )

        assert json.loads(responses.calls[-1].request.body) == {
            "url": "https://updated.com/webhook",
            "eventTypes": ["LOOP_CREATED"],
            "enabled": False,
        }
        assert result["data"]["enabled"] is False

    @responses.activate
    def test_delete_subscription_success(self) -> None:
        """Test successful subscription deletion."""
        responses.add(
            responses.DELETE,
            "https://api-gateway.dotloop.com/public/v2/subscription/123",
            status=204,
        )

        result = self.client.delete_subscription(subscription_id=123)

        assert result == {}

    @responses.activate
    def test_list_events_success(self) -> None:
        """Test successful events listing."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/subscription/68bc4c39-0366-4faa-885a-5ff4803b2dbb/event",
            json={
                "data": [
                    {
                        "id": "5f6667e3-4b65-4025-9d64-f8d695b3ebb5",
                        "eventType": "LOOP_CREATED",
                        "deliveryStatus": "SUCCESS",
                        "deliveryAttempts": 1,
                        "createdOn": "2024-01-15T10:00:00Z",
                    },
                    {
                        "id": "3bc982f6-7029-40ae-81aa-62f93a5ea1a8",
                        "eventType": "CONTACT_CREATED",
                        "deliveryStatus": "FAILED",
                        "deliveryAttempts": 3,
                        "createdOn": "2024-01-15T11:00:00Z",
                    },
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        result = self.client.list_events(
            subscription_id="68bc4c39-0366-4faa-885a-5ff4803b2dbb"
        )

        assert len(result["data"]) == 2
        assert result["data"][0]["eventType"] == "LOOP_CREATED"
        assert result["data"][0]["deliveryStatus"] == "SUCCESS"
        assert result["data"][1]["deliveryStatus"] == "FAILED"

    @responses.activate
    def test_list_events_with_query_params(self) -> None:
        """Test listing events with delivery_status and next_cursor query params."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/subscription/68bc4c39-0366-4faa-885a-5ff4803b2dbb/event",
            json={"data": [], "meta": {"total": 0}},
            status=200,
        )

        self.client.list_events(
            subscription_id="68bc4c39-0366-4faa-885a-5ff4803b2dbb",
            delivery_status="FAILED",
            next_cursor="cursor456",
        )

        request_url = responses.calls[-1].request.url
        parsed = urlparse(request_url)
        query = parse_qs(parsed.query)
        assert query["delivery_status"] == ["FAILED"]
        assert query["next_cursor"] == ["cursor456"]

    @responses.activate
    def test_get_event_success(self) -> None:
        """Test successful event retrieval."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/subscription/68bc4c39-0366-4faa-885a-5ff4803b2dbb/event/5f6667e3-4b65-4025-9d64-f8d695b3ebb5",
            json={
                "data": {
                    "id": "5f6667e3-4b65-4025-9d64-f8d695b3ebb5",
                    "eventType": "LOOP_CREATED",
                    "deliveryStatus": "SUCCESS",
                    "deliveryAttempts": 1,
                    "eventData": {"id": 789},
                    "responseData": [{"responseCode": 200}],
                }
            },
            status=200,
        )

        result = self.client.get_event(
            subscription_id="68bc4c39-0366-4faa-885a-5ff4803b2dbb",
            event_id="5f6667e3-4b65-4025-9d64-f8d695b3ebb5",
        )

        assert result["data"]["eventType"] == "LOOP_CREATED"
        assert result["data"]["deliveryStatus"] == "SUCCESS"
        assert result["data"]["eventData"]["id"] == 789

    @responses.activate
    def test_activate_subscription_success(self) -> None:
        """Test successful subscription activation."""
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/subscription/68bc4c39-0366-4faa-885a-5ff4803b2dbb",
            json={
                "data": {
                    "id": "68bc4c39-0366-4faa-885a-5ff4803b2dbb",
                    "enabled": True,
                }
            },
            status=200,
        )

        result = self.client.activate_subscription(
            subscription_id="68bc4c39-0366-4faa-885a-5ff4803b2dbb"
        )

        assert json.loads(responses.calls[-1].request.body) == {"enabled": True}
        assert result["data"]["enabled"] is True

    @responses.activate
    def test_deactivate_subscription_success(self) -> None:
        """Test successful subscription deactivation."""
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/subscription/68bc4c39-0366-4faa-885a-5ff4803b2dbb",
            json={
                "data": {
                    "id": "68bc4c39-0366-4faa-885a-5ff4803b2dbb",
                    "enabled": False,
                }
            },
            status=200,
        )

        result = self.client.deactivate_subscription(
            subscription_id="68bc4c39-0366-4faa-885a-5ff4803b2dbb"
        )

        assert json.loads(responses.calls[-1].request.body) == {"enabled": False}
        assert result["data"]["enabled"] is False

    @responses.activate
    def test_get_subscription_summary_success(self) -> None:
        """Test successful subscription summary generation."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/subscription/68bc4c39-0366-4faa-885a-5ff4803b2dbb/event",
            json={
                "data": [
                    {
                        "id": "1",
                        "eventType": "LOOP_CREATED",
                        "deliveryStatus": "SUCCESS",
                    },
                    {
                        "id": "2",
                        "eventType": "CONTACT_CREATED",
                        "deliveryStatus": "SUCCESS",
                    },
                    {
                        "id": "3",
                        "eventType": "LOOP_CREATED",
                        "deliveryStatus": "FAILED",
                    },
                ],
                "meta": {"total": 3},
            },
            status=200,
        )

        result = self.client.get_subscription_summary(
            subscription_id="68bc4c39-0366-4faa-885a-5ff4803b2dbb"
        )

        assert result["subscription_id"] == "68bc4c39-0366-4faa-885a-5ff4803b2dbb"
        assert result["total_events"] == 3
        assert result["successful_events"] == 2
        assert result["failed_events"] == 1
        assert result["success_rate"] == 66.66666666666666

    @responses.activate
    def test_get_all_subscriptions_summary_success(self) -> None:
        """Test all subscriptions summary generation."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/subscription",
            json={
                "data": [
                    {
                        "id": "68bc4c39-0366-4faa-885a-5ff4803b2dbb",
                        "url": "https://app1.com/webhook",
                        "enabled": True,
                        "eventTypes": ["LOOP_CREATED", "CONTACT_CREATED"],
                    },
                    {
                        "id": "7dbf7306-6015-48aa-8e9b-205363514d32",
                        "url": "https://app2.com/webhook",
                        "enabled": False,
                        "eventTypes": ["CONTACT_UPDATED"],
                    },
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        result = self.client.get_all_subscriptions_summary()

        assert result["total_subscriptions"] == 2
        assert result["active_subscriptions"] == 1
        assert result["inactive_subscriptions"] == 1
        assert result["unique_urls"] == 2
        assert result["unique_event_types"] == 3

    @responses.activate
    def test_get_all_subscriptions_summary_fallback_active_keys(self) -> None:
        """Test summary fallback for legacy active/isActive subscription fields."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/subscription",
            json={
                "data": [
                    {
                        "id": "1",
                        "url": "https://app1.com/webhook",
                        "isActive": True,
                        "events": ["LOOP_CREATED"],
                    },
                    {
                        "id": "2",
                        "url": "https://app2.com/webhook",
                        "active": False,
                        "events": ["CONTACT_CREATED"],
                    },
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        result = self.client.get_all_subscriptions_summary()

        assert result["total_subscriptions"] == 2
        assert result["active_subscriptions"] == 1
        assert result["inactive_subscriptions"] == 1

    @responses.activate
    def test_get_subscription_not_found(self) -> None:
        """Test subscription retrieval with not found error."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/subscription/68bc4c39-0366-4faa-885a-5ff4803b2dbb",
            json={"message": "Subscription not found"},
            status=404,
        )

        with pytest.raises(NotFoundError) as exc_info:
            self.client.get_subscription(
                subscription_id="68bc4c39-0366-4faa-885a-5ff4803b2dbb"
            )

        assert "Resource not found" in str(exc_info.value)
        assert exc_info.value.status_code == 404


class TestWebhookClientValidation:
    """Test webhook target/event validation helpers."""

    def test_validate_event_types_profile_rejects_user_events(self) -> None:
        """Test PROFILE target rejects USER-only event types."""
        with pytest.raises(ValueError) as exc_info:
            WebhookClient.validate_event_types(
                target_type=WebhookTargetType.PROFILE,
                event_types=[WebhookEventType.CONTACT_CREATED],
            )

        assert "Invalid event_types for target_type PROFILE" in str(exc_info.value)

    def test_validate_event_types_user_accepts_contact_events(self) -> None:
        """Test USER target accepts contact events."""
        WebhookClient.validate_event_types(
            target_type=WebhookTargetType.USER,
            event_types=[
                WebhookEventType.CONTACT_CREATED,
                WebhookEventType.CONTACT_UPDATED,
            ],
        )


class TestWebhookClientEnsureSubscription:
    """Test idempotent webhook subscription ensure helpers."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = WebhookClient(api_key="test_key")

    @responses.activate
    def test_ensure_subscription_creates_when_missing(self) -> None:
        """Test ensure creates a subscription when none exists."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/subscription",
            json={"data": [], "meta": {"total": 0}},
            status=200,
        )
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/subscription",
            json={"data": {"id": "sub-1"}},
            status=200,
        )

        result = self.client.ensure_subscription(
            url="https://example.com/webhook",
            target_type=WebhookTargetType.PROFILE,
            target_id="123",
            event_types=[WebhookEventType.LOOP_CREATED],
            enabled=True,
        )

        assert result.action == EnsureWebhookSubscriptionAction.CREATED
        assert result.subscription_id == "sub-1"
        assert result.target_type == WebhookTargetType.PROFILE
        assert result.target_id == 123
        assert set(result.enabled_event_types) == {"LOOP_CREATED"}

        body = json.loads(responses.calls[-1].request.body)
        assert body["targetType"] == "PROFILE"
        assert body["targetId"] == 123
        assert body["url"] == "https://example.com/webhook"
        assert set(body["eventTypes"]) == {"LOOP_CREATED"}
        assert body["enabled"] is True

    @responses.activate
    def test_ensure_subscription_updates_when_mismatched(self) -> None:
        """Test ensure updates an existing subscription when it differs."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/subscription",
            json={
                "data": [
                    {
                        "id": "sub-1",
                        "targetType": "PROFILE",
                        "targetId": "123",
                        "url": "https://old.example.com/webhook",
                        "enabled": False,
                        "eventTypes": ["LOOP_CREATED"],
                    }
                ],
                "meta": {"total": 1},
            },
            status=200,
        )
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/subscription/sub-1",
            json={"data": {"id": "sub-1"}},
            status=200,
        )

        result = self.client.ensure_subscription(
            url="https://new.example.com/webhook",
            target_type=WebhookTargetType.PROFILE,
            target_id=123,
            event_types=[WebhookEventType.LOOP_CREATED, WebhookEventType.LOOP_UPDATED],
            enabled=True,
        )

        assert result.action == EnsureWebhookSubscriptionAction.UPDATED
        assert result.subscription_id == "sub-1"
        assert "url" in result.changes
        assert "enabled" in result.changes
        assert "eventTypes" in result.changes

        body = json.loads(responses.calls[-1].request.body)
        assert body["url"] == "https://new.example.com/webhook"
        assert body["enabled"] is True
        assert set(body["eventTypes"]) == {"LOOP_CREATED", "LOOP_UPDATED"}

    @responses.activate
    def test_ensure_subscription_noop_when_already_correct(self) -> None:
        """Test ensure returns noop when an existing subscription already matches."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/subscription",
            json={
                "data": [
                    {
                        "id": "sub-1",
                        "targetType": "PROFILE",
                        "targetId": 123,
                        "url": "https://example.com/webhook",
                        "enabled": True,
                        "eventTypes": ["LOOP_UPDATED", "LOOP_CREATED"],
                    }
                ],
                "meta": {"total": 1},
            },
            status=200,
        )

        result = self.client.ensure_subscription(
            url="https://example.com/webhook",
            target_type=WebhookTargetType.PROFILE,
            target_id=123,
            event_types=[WebhookEventType.LOOP_CREATED, WebhookEventType.LOOP_UPDATED],
            enabled=True,
        )

        assert result.action == EnsureWebhookSubscriptionAction.NOOP
        assert result.subscription_id == "sub-1"
        assert result.changes == {}
        assert len(responses.calls) == 1  # GET only, no PATCH/POST

    @responses.activate
    def test_ensure_default_subscriptions(self) -> None:
        """Test ensure_default_subscriptions derives USER/PROFILE targets from account."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/account",
            json={"data": {"id": 100, "defaultProfileId": 789}},
            status=200,
        )

        # Each ensure call lists subscriptions (empty) and then creates a subscription.
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/subscription",
            json={"data": [], "meta": {"total": 0}},
            status=200,
        )
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/subscription",
            json={"data": [], "meta": {"total": 0}},
            status=200,
        )

        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/subscription",
            json={"data": {"id": "profile-sub"}},
            status=200,
        )
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/subscription",
            json={"data": {"id": "user-sub"}},
            status=200,
        )

        results = self.client.ensure_default_subscriptions(
            "https://example.com/webhook", enabled=True
        )

        assert len(results) == 2
        assert results[0].target_type == WebhookTargetType.PROFILE
        assert results[0].target_id == 789
        assert results[1].target_type == WebhookTargetType.USER
        assert results[1].target_id == 100

        # Verify payload event sets match the canonical mapping.
        profile_expected = {
            event.value
            for event in SUPPORTED_WEBHOOK_EVENT_TYPES_BY_TARGET[
                WebhookTargetType.PROFILE
            ]
        }
        user_expected = {
            event.value
            for event in SUPPORTED_WEBHOOK_EVENT_TYPES_BY_TARGET[WebhookTargetType.USER]
        }

        post_calls = [
            call
            for call in responses.calls
            if call.request.method == "POST"
            and call.request.url
            == "https://api-gateway.dotloop.com/public/v2/subscription"
        ]
        assert len(post_calls) == 2

        profile_body = json.loads(post_calls[0].request.body)
        user_body = json.loads(post_calls[1].request.body)

        assert profile_body["targetType"] == "PROFILE"
        assert profile_body["targetId"] == 789
        assert set(profile_body["eventTypes"]) == profile_expected

        assert user_body["targetType"] == "USER"
        assert user_body["targetId"] == 100
        assert set(user_body["eventTypes"]) == user_expected


class TestWebhookSubscriptionModel:
    """Test typed webhook subscription parsing helpers."""

    def test_subscription_from_api_missing_required_fields_raises(self) -> None:
        """Test WebhookSubscription.from_api validates required fields."""
        with pytest.raises(ValueError):
            WebhookSubscription.from_api({})

        with pytest.raises(ValueError):
            WebhookSubscription.from_api({"id": "sub-1"})

        with pytest.raises(ValueError):
            WebhookSubscription.from_api(
                {"id": "sub-1", "targetType": "PROFILE", "url": "https://x"}
            )

        with pytest.raises(ValueError):
            WebhookSubscription.from_api(
                {"id": "sub-1", "targetType": "PROFILE", "targetId": 1}
            )

        with pytest.raises(ValueError):
            WebhookSubscription.from_api(
                {
                    "id": "sub-1",
                    "targetType": "PROFILE",
                    "targetId": 1,
                    "url": "https://x",
                    "eventTypes": "LOOP_CREATED",
                }
            )

    def test_subscription_from_api_enabled_fallback_keys(self) -> None:
        """Test enabled can be derived from active/isActive when enabled is absent."""
        active_sub = WebhookSubscription.from_api(
            {
                "id": "sub-1",
                "targetType": "PROFILE",
                "targetId": 1,
                "url": "https://x",
                "active": True,
                "eventTypes": ["LOOP_CREATED"],
            }
        )
        assert active_sub.enabled is True

        is_active_sub = WebhookSubscription.from_api(
            {
                "id": "sub-2",
                "targetType": "PROFILE",
                "targetId": 1,
                "url": "https://x",
                "isActive": False,
                "eventTypes": ["LOOP_CREATED"],
            }
        )
        assert is_active_sub.enabled is False

    def test_subscription_from_api_unknown_event_type_preserved(self) -> None:
        """Test unknown event types are preserved as strings."""
        subscription = WebhookSubscription.from_api(
            {
                "id": "sub-1",
                "targetType": "PROFILE",
                "targetId": 1,
                "url": "https://x",
                "enabled": True,
                "eventTypes": ["SOME_FUTURE_EVENT"],
            }
        )
        assert subscription.event_types == ("SOME_FUTURE_EVENT",)
        assert subscription.event_type_values() == ("SOME_FUTURE_EVENT",)

    def test_subscription_normalize_target_id_validates_type(self) -> None:
        """Test target id normalization rejects invalid values."""
        with pytest.raises(ValueError):
            WebhookSubscription._normalize_target_id(True)

        with pytest.raises(ValueError):
            WebhookSubscription._normalize_target_id("not-a-number")


class TestWebhookClientAdditionalCoverage:
    """Additional tests to cover ensure/validation branches."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = WebhookClient(api_key="test_key")

    @responses.activate
    def test_create_subscription_validate_normalizes_target_id(self) -> None:
        """Test create_subscription(validate=True) normalizes numeric string target_id."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/subscription",
            json={"data": {"id": "sub-1"}},
            status=200,
        )

        self.client.create_subscription(
            url="https://example.com/webhook",
            target_type=WebhookTargetType.PROFILE,
            target_id="123",
            event_types=[WebhookEventType.LOOP_CREATED],
            validate=True,
        )

        body = json.loads(responses.calls[-1].request.body)
        assert body["targetId"] == 123

    @responses.activate
    def test_update_subscription_validate_fetches_target_type(self) -> None:
        """Test update_subscription(validate=True) validates event types against target."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/subscription/sub-1",
            json={
                "data": {
                    "id": "sub-1",
                    "targetType": "PROFILE",
                    "targetId": 123,
                    "url": "https://example.com/webhook",
                    "enabled": True,
                    "eventTypes": ["LOOP_CREATED"],
                }
            },
            status=200,
        )
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/subscription/sub-1",
            json={"data": {"id": "sub-1"}},
            status=200,
        )

        self.client.update_subscription(
            subscription_id="sub-1",
            event_types=[WebhookEventType.LOOP_CREATED],
            validate=True,
        )

        body = json.loads(responses.calls[-1].request.body)
        assert body["eventTypes"] == ["LOOP_CREATED"]

    def test_ensure_subscription_empty_event_types_raises(self) -> None:
        """Test ensure_subscription rejects empty event_types."""
        with pytest.raises(ValueError):
            self.client.ensure_subscription(
                url="https://example.com/webhook",
                target_type="PROFILE",
                target_id=123,
                event_types=[],
            )

    @responses.activate
    def test_ensure_subscription_skips_invalid_subscription_objects(self) -> None:
        """Test ensure_subscription skips unparseable subscription entries."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/subscription",
            json={"data": [{"targetType": "PROFILE"}], "meta": {"total": 1}},
            status=200,
        )
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/subscription",
            json={"data": {"id": "sub-1"}},
            status=200,
        )

        result = self.client.ensure_subscription(
            url="https://example.com/webhook",
            target_type="PROFILE",
            target_id=123,
            event_types=[WebhookEventType.LOOP_CREATED],
        )

        assert result.action == EnsureWebhookSubscriptionAction.CREATED

    @responses.activate
    def test_ensure_subscription_multiple_candidates_prefers_url_match(self) -> None:
        """Test ensure_subscription prefers exact URL match when multiple candidates exist."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/subscription",
            json={
                "data": [
                    {
                        "id": "sub-other",
                        "targetType": "PROFILE",
                        "targetId": 123,
                        "url": "https://other.example.com/webhook",
                        "enabled": False,
                        "eventTypes": ["LOOP_CREATED"],
                    },
                    {
                        "id": "sub-match",
                        "targetType": "PROFILE",
                        "targetId": 123,
                        "url": "https://example.com/webhook",
                        "enabled": False,
                        "eventTypes": ["LOOP_CREATED"],
                    },
                ],
                "meta": {"total": 2},
            },
            status=200,
        )
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/subscription/sub-match",
            json={"data": {"id": "sub-match"}},
            status=200,
        )

        result = self.client.ensure_subscription(
            url="https://example.com/webhook",
            target_type="PROFILE",
            target_id=123,
            event_types=[WebhookEventType.LOOP_CREATED],
            enabled=True,
        )

        assert result.action == EnsureWebhookSubscriptionAction.UPDATED
        assert result.subscription_id == "sub-match"
        assert responses.calls[-1].request.url.endswith("/subscription/sub-match")

    @responses.activate
    def test_ensure_subscription_create_dry_run_includes_optional_fields(self) -> None:
        """Test ensure_subscription dry_run create includes signingKey/externalId changes."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/subscription",
            json={"data": [], "meta": {"total": 0}},
            status=200,
        )

        result = self.client.ensure_subscription(
            url="https://example.com/webhook",
            target_type="PROFILE",
            target_id=123,
            event_types=[WebhookEventType.LOOP_CREATED],
            enabled=True,
            signing_key="signing",
            external_id="external",
            dry_run=True,
        )

        assert result.dry_run is True
        assert result.action == EnsureWebhookSubscriptionAction.CREATED
        assert "signingKey" in result.changes
        assert "externalId" in result.changes
        assert len(responses.calls) == 1  # GET only

    @responses.activate
    def test_ensure_subscription_update_dry_run_optional_fields(self) -> None:
        """Test ensure_subscription dry_run update includes signingKey/externalId diffs."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/subscription",
            json={
                "data": [
                    {
                        "id": "sub-1",
                        "targetType": "PROFILE",
                        "targetId": 123,
                        "url": "https://example.com/webhook",
                        "enabled": True,
                        "eventTypes": ["LOOP_CREATED"],
                        "signingKey": "old",
                        "externalId": "old",
                    }
                ],
                "meta": {"total": 1},
            },
            status=200,
        )

        result = self.client.ensure_subscription(
            url="https://example.com/webhook",
            target_type="PROFILE",
            target_id=123,
            event_types=[WebhookEventType.LOOP_CREATED],
            enabled=True,
            signing_key="new",
            external_id="new",
            dry_run=True,
        )

        assert result.dry_run is True
        assert result.action == EnsureWebhookSubscriptionAction.UPDATED
        assert "signingKey" in result.changes
        assert "externalId" in result.changes
        assert len(responses.calls) == 1  # GET only

    @responses.activate
    def test_ensure_default_subscriptions_missing_account_fields_raises(self) -> None:
        """Test ensure_default_subscriptions validates required account fields."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/account",
            json={"data": {"defaultProfileId": 789}},
            status=200,
        )

        with pytest.raises(ValueError):
            self.client.ensure_default_subscriptions("https://example.com/webhook")

        responses.reset()
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/account",
            json={"data": {"id": 100}},
            status=200,
        )

        with pytest.raises(ValueError):
            self.client.ensure_default_subscriptions("https://example.com/webhook")
