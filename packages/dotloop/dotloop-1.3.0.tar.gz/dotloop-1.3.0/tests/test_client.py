"""Tests for the main DotloopClient."""

import pytest

from dotloop import DotloopClient
from dotloop.exceptions import AuthenticationError


class TestDotloopClientInit:
    """Test DotloopClient initialization."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with provided API key."""
        client = DotloopClient(api_key="test_key")
        assert client._api_key == "test_key"
        assert client._base_url is None
        assert client._timeout == 30

    def test_init_with_custom_params(self) -> None:
        """Test initialization with custom parameters."""
        client = DotloopClient(
            api_key="test_key", base_url="https://custom.api.com", timeout=60
        )
        assert client._api_key == "test_key"
        assert client._base_url == "https://custom.api.com"
        assert client._timeout == 60

    def test_property_access(self) -> None:
        """Test that client properties are accessible."""
        client = DotloopClient(api_key="test_key")

        # Test that properties return client instances
        assert hasattr(client.account, "get_account")
        assert hasattr(client.profile, "list_profiles")
        assert hasattr(client.loop, "list_loops")
        assert hasattr(client.loop_it, "create_loop")
        assert hasattr(client.contact, "list_contacts")
        assert hasattr(client.loop_detail, "get_loop_details")
        assert hasattr(client.folder, "list_folders")
        assert hasattr(client.document, "list_documents")
        assert hasattr(client.participant, "list_participants")
        assert hasattr(client.task, "list_task_lists")
        assert hasattr(client.activity, "list_loop_activity")
        assert hasattr(client.template, "list_loop_templates")
        assert hasattr(client.webhook, "list_subscriptions")

    def test_property_caching(self) -> None:
        """Test that client properties are cached."""
        client = DotloopClient(api_key="test_key")

        # First access
        account1 = client.account
        profile1 = client.profile
        loop1 = client.loop
        loop_it1 = client.loop_it
        contact1 = client.contact
        loop_detail1 = client.loop_detail
        folder1 = client.folder
        document1 = client.document
        participant1 = client.participant
        task1 = client.task
        activity1 = client.activity
        template1 = client.template
        webhook1 = client.webhook

        # Second access should return same instances
        account2 = client.account
        profile2 = client.profile
        loop2 = client.loop
        loop_it2 = client.loop_it
        contact2 = client.contact
        loop_detail2 = client.loop_detail
        folder2 = client.folder
        document2 = client.document
        participant2 = client.participant
        task2 = client.task
        activity2 = client.activity
        template2 = client.template
        webhook2 = client.webhook

        assert account1 is account2
        assert profile1 is profile2
        assert loop1 is loop2
        assert loop_it1 is loop_it2
        assert contact1 is contact2
        assert loop_detail1 is loop_detail2
        assert folder1 is folder2
        assert document1 is document2
        assert participant1 is participant2
        assert task1 is task2
        assert activity1 is activity2
        assert template1 is template2
        assert webhook1 is webhook2
