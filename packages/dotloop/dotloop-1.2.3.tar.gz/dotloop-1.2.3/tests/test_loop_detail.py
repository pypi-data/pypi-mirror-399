"""Tests for the LoopDetailClient."""

import pytest
import responses

from dotloop.exceptions import AuthenticationError, DotloopError, NotFoundError
from dotloop.loop_detail import LoopDetailClient


class TestLoopDetailClientInit:
    """Test LoopDetailClient initialization."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with provided API key."""
        client = LoopDetailClient(api_key="test_key")
        assert client._api_key == "test_key"

    def test_init_without_api_key_raises_error(self) -> None:
        """Test initialization without API key raises error."""
        with pytest.raises(AuthenticationError):
            LoopDetailClient()


class TestLoopDetailClientMethods:
    """Test LoopDetailClient methods."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = LoopDetailClient(api_key="test_key")

    @responses.activate
    def test_get_loop_details_success(self) -> None:
        """Test successful loop details retrieval."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/detail",
            json={
                "data": {
                    "Property Address": {
                        "Street Number": "123",
                        "Street Name": "Main St",
                        "City": "San Francisco",
                        "State/Prov": "CA",
                        "Zip/Postal Code": "94105",
                    },
                    "Financials": {
                        "Purchase/Sale Price": "750000",
                        "Sale Commission Rate": "6",
                    },
                }
            },
            status=200,
        )

        result = self.client.get_loop_details(profile_id=123, loop_id=456)

        assert result["data"]["Property Address"]["Street Number"] == "123"
        assert result["data"]["Financials"]["Purchase/Sale Price"] == "750000"

    @responses.activate
    def test_update_loop_details_success(self) -> None:
        """Test successful loop details update."""
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/detail",
            json={
                "data": {
                    "Property Address": {
                        "Street Number": "456",
                        "Street Name": "Oak Avenue",
                    }
                }
            },
            status=200,
        )

        details = {
            "Property Address": {"Street Number": "456", "Street Name": "Oak Avenue"}
        }

        result = self.client.update_loop_details(
            profile_id=123, loop_id=456, details=details
        )

        assert result["data"]["Property Address"]["Street Number"] == "456"

    @responses.activate
    def test_update_property_address_success(self) -> None:
        """Test successful property address update."""
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/detail",
            json={
                "data": {
                    "Property Address": {
                        "Street Number": "789",
                        "Street Name": "Pine Street",
                        "City": "San Francisco",
                        "State/Prov": "CA",
                    }
                }
            },
            status=200,
        )

        result = self.client.update_property_address(
            profile_id=123,
            loop_id=456,
            street_number="789",
            street_name="Pine Street",
            city="San Francisco",
            state="CA",
        )

        assert result["data"]["Property Address"]["Street Number"] == "789"
        assert result["data"]["Property Address"]["City"] == "San Francisco"

    @responses.activate
    def test_update_financials_success(self) -> None:
        """Test successful financials update."""
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/detail",
            json={
                "data": {
                    "Financials": {
                        "Purchase/Sale Price": "500000",
                        "Sale Commission Rate": "6",
                        "Earnest Money Amount": "10000",
                    }
                }
            },
            status=200,
        )

        result = self.client.update_financials(
            profile_id=123,
            loop_id=456,
            purchase_sale_price="500000",
            sale_commission_rate="6",
            earnest_money_amount="10000",
        )

        assert result["data"]["Financials"]["Purchase/Sale Price"] == "500000"
        assert result["data"]["Financials"]["Earnest Money Amount"] == "10000"

    @responses.activate
    def test_update_contract_dates_success(self) -> None:
        """Test successful contract dates update."""
        responses.add(
            responses.PATCH,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/detail",
            json={
                "data": {
                    "Contract Dates": {"Closing Date": "02/28/2024"},
                    "Offer Dates": {"Offer Date": "01/15/2024"},
                }
            },
            status=200,
        )

        result = self.client.update_contract_dates(
            profile_id=123,
            loop_id=456,
            offer_date="01/15/2024",
            closing_date="02/28/2024",
        )

        assert result["data"]["Contract Dates"]["Closing Date"] == "02/28/2024"
        assert result["data"]["Offer Dates"]["Offer Date"] == "01/15/2024"

    @responses.activate
    def test_get_loop_details_not_found(self) -> None:
        """Test loop details retrieval with not found error."""
        responses.add(
            responses.GET,
            "https://api-gateway.dotloop.com/public/v2/profile/123/loop/456/detail",
            json={"message": "Loop not found"},
            status=404,
        )

        with pytest.raises(NotFoundError) as exc_info:
            self.client.get_loop_details(profile_id=123, loop_id=456)

        assert "Resource not found" in str(exc_info.value)
        assert exc_info.value.status_code == 404
