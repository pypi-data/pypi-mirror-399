"""Tests for the TemplateClient."""

import pytest
import responses

from dotloop.exceptions import AuthenticationError, DotloopError, NotFoundError
from dotloop.template import TemplateClient


class TestTemplateClientInit:
    """Test TemplateClient initialization."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with provided API key."""
        client = TemplateClient(api_key="test_key")
        assert client._api_key == "test_key"

    def test_init_without_api_key_raises_error(self) -> None:
        """Test initialization without API key raises error."""
        with pytest.raises(AuthenticationError):
            TemplateClient()


class TestTemplateClientMethods:
    """Test TemplateClient methods."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = TemplateClient(api_key="test_key")

    @responses.activate
    def test_list_loop_templates_success(self) -> None:
        """Test successful loop templates listing."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop-template",
            json={
                "data": [
                    {
                        "id": 1,
                        "name": "Purchase Offer Template",
                        "type": "PURCHASE",
                        "isDefault": True,
                        "created": "2024-01-15T10:00:00Z",
                    },
                    {
                        "id": 2,
                        "name": "Listing Agreement Template",
                        "type": "LISTING",
                        "isDefault": False,
                        "created": "2024-01-14T09:00:00Z",
                    },
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        result = self.client.list_loop_templates(profile_id=123)

        assert len(result["data"]) == 2
        assert result["data"][0]["name"] == "Purchase Offer Template"
        assert result["data"][1]["name"] == "Listing Agreement Template"

    @responses.activate
    def test_get_loop_template_success(self) -> None:
        """Test successful loop template retrieval."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop-template/456",
            json={
                "data": {
                    "id": 456,
                    "name": "Purchase Offer Template",
                    "type": "PURCHASE",
                    "isDefault": True,
                    "created": "2024-01-15T10:00:00Z",
                    "description": "Standard purchase offer template",
                }
            },
            status=200,
        )

        result = self.client.get_loop_template(profile_id=123, template_id=456)

        assert result["data"]["name"] == "Purchase Offer Template"
        assert result["data"]["type"] == "PURCHASE"
        assert result["data"]["isDefault"] is True

    @responses.activate
    def test_get_templates_by_type_success(self) -> None:
        """Test filtering templates by type."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop-template",
            json={
                "data": [
                    {
                        "id": 1,
                        "name": "Purchase Template 1",
                        "type": "PURCHASE",
                        "isDefault": True,
                    },
                    {
                        "id": 2,
                        "name": "Listing Template 1",
                        "type": "LISTING",
                        "isDefault": False,
                    },
                    {
                        "id": 3,
                        "name": "Purchase Template 2",
                        "type": "PURCHASE",
                        "isDefault": False,
                    },
                ],
                "meta": {"total": 3},
            },
            status=200,
        )

        result = self.client.get_templates_by_type(
            profile_id=123, template_type="PURCHASE"
        )

        assert len(result["data"]) == 2
        for template in result["data"]:
            assert template["type"] == "PURCHASE"

    @responses.activate
    def test_get_default_templates_success(self) -> None:
        """Test filtering for default templates."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop-template",
            json={
                "data": [
                    {
                        "id": 1,
                        "name": "Default Purchase Template",
                        "type": "PURCHASE",
                        "isDefault": True,
                    },
                    {
                        "id": 2,
                        "name": "Custom Listing Template",
                        "type": "LISTING",
                        "isDefault": False,
                    },
                    {
                        "id": 3,
                        "name": "Default Listing Template",
                        "type": "LISTING",
                        "isDefault": True,
                    },
                ],
                "meta": {"total": 3},
            },
            status=200,
        )

        result = self.client.get_default_templates(profile_id=123)

        assert len(result["data"]) == 2
        for template in result["data"]:
            assert template["isDefault"] is True

    @responses.activate
    def test_get_custom_templates_success(self) -> None:
        """Test filtering for custom templates."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop-template",
            json={
                "data": [
                    {
                        "id": 1,
                        "name": "Default Purchase Template",
                        "type": "PURCHASE",
                        "isDefault": True,
                    },
                    {
                        "id": 2,
                        "name": "Custom Listing Template",
                        "type": "LISTING",
                        "isDefault": False,
                    },
                    {
                        "id": 3,
                        "name": "Custom Purchase Template",
                        "type": "PURCHASE",
                        "isDefault": False,
                    },
                ],
                "meta": {"total": 3},
            },
            status=200,
        )

        result = self.client.get_custom_templates(profile_id=123)

        assert len(result["data"]) == 2
        for template in result["data"]:
            assert template["isDefault"] is False

    @responses.activate
    def test_find_template_by_name_success(self) -> None:
        """Test finding template by name."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop-template",
            json={
                "data": [
                    {"id": 1, "name": "Purchase Offer Template", "type": "PURCHASE"},
                    {"id": 2, "name": "Listing Agreement Template", "type": "LISTING"},
                ],
                "meta": {"total": 2},
            },
            status=200,
        )

        result = self.client.find_template_by_name(
            profile_id=123, template_name="Purchase Offer Template"
        )

        assert result is not None
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "Purchase Offer Template"
        assert result["data"][0]["type"] == "PURCHASE"

    @responses.activate
    def test_find_template_by_name_not_found(self) -> None:
        """Test finding template by name when not found."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop-template",
            json={
                "data": [
                    {"id": 1, "name": "Purchase Offer Template", "type": "PURCHASE"}
                ],
                "meta": {"total": 1},
            },
            status=200,
        )

        result = self.client.find_template_by_name(
            profile_id=123, template_name="Non-existent Template"
        )

        assert len(result["data"]) == 0

    @responses.activate
    def test_get_template_summary_success(self) -> None:
        """Test template summary generation."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop-template",
            json={
                "data": [
                    {
                        "id": 1,
                        "name": "Default Purchase Template",
                        "type": "PURCHASE",
                        "isDefault": True,
                    },
                    {
                        "id": 2,
                        "name": "Custom Listing Template",
                        "type": "LISTING",
                        "isDefault": False,
                    },
                    {
                        "id": 3,
                        "name": "Default Listing Template",
                        "type": "LISTING",
                        "isDefault": True,
                    },
                    {
                        "id": 4,
                        "name": "Custom Purchase Template",
                        "type": "PURCHASE",
                        "isDefault": False,
                    },
                ],
                "meta": {"total": 4},
            },
            status=200,
        )

        result = self.client.get_template_summary(profile_id=123)

        assert result["total_templates"] == 4
        assert result["default_templates"] == 2
        assert result["custom_templates"] == 2
        assert result["template_types"]["PURCHASE"] == 2
        assert result["template_types"]["LISTING"] == 2

    @responses.activate
    def test_get_loop_template_not_found(self) -> None:
        """Test loop template retrieval with not found error."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop-template/999",
            json={"message": "Template not found"},
            status=404,
        )

        with pytest.raises(NotFoundError) as exc_info:
            self.client.get_loop_template(profile_id=123, template_id=999)

        assert "Resource not found" in str(exc_info.value)
        assert exc_info.value.status_code == 404
