"""Tests for the LoopItClient."""

import pytest
import responses

from dotloop.enums import LoopStatus, ParticipantRole, TransactionType
from dotloop.exceptions import AuthenticationError, DotloopError, NotFoundError
from dotloop.loop_it import LoopItClient


class TestLoopItClientInit:
    """Test LoopItClient initialization."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with provided API key."""
        client = LoopItClient(api_key="test_key")
        assert client._api_key == "test_key"

    def test_init_without_api_key_raises_error(self) -> None:
        """Test initialization without API key raises error."""
        with pytest.raises(AuthenticationError):
            LoopItClient()


class TestLoopItClientMethods:
    """Test LoopItClient methods."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = LoopItClient(api_key="test_key")

    @responses.activate
    def test_create_loop_success(self) -> None:
        """Test successful loop creation from template."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/loop-it",
            json={
                "data": {
                    "id": 999,
                    "name": "123 Main St Purchase",
                    "status": "PRE_OFFER",
                    "transactionType": "PURCHASE_OFFER",
                    "loopUrl": "https://dotloop.com/loop/999",
                    "created": "2024-01-15T10:00:00Z",
                }
            },
            status=201,
        )

        result = self.client.create_loop(
            name="123 Main St Purchase",
            transaction_type=TransactionType.PURCHASE_OFFER,
            status=LoopStatus.PRE_OFFER,
            profile_id=123,
        )

        assert result["data"]["name"] == "123 Main St Purchase"
        assert result["data"]["transactionType"] == "PURCHASE_OFFER"
        assert result["data"]["status"] == "PRE_OFFER"

    @responses.activate
    def test_create_loop_with_property_details(self) -> None:
        """Test loop creation with property details."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/loop-it",
            json={
                "data": {
                    "id": 999,
                    "name": "456 Oak Ave Listing",
                    "status": "PRE_LISTING",
                    "transactionType": "LISTING_FOR_SALE",
                }
            },
            status=201,
        )

        result = self.client.create_loop(
            name="456 Oak Ave Listing",
            transaction_type=TransactionType.LISTING_FOR_SALE,
            status=LoopStatus.PRE_LISTING,
            profile_id=123,
            street_number="456",
            street_name="Oak Ave",
            city="San Francisco",
            state="CA",
            zip_code="94102",
        )

        assert result["data"]["name"] == "456 Oak Ave Listing"
        assert result["data"]["transactionType"] == "LISTING_FOR_SALE"

    @responses.activate
    def test_create_loop_with_participants(self) -> None:
        """Test loop creation with participants."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/loop-it",
            json={
                "data": {
                    "id": 999,
                    "name": "Transaction with Participants",
                    "status": "PRE_OFFER",
                    "transactionType": "PURCHASE_OFFER",
                }
            },
            status=201,
        )

        participants = [
            {
                "fullName": "John Buyer",
                "email": "john@example.com",
                "role": ParticipantRole.BUYER.value,
            },
            {
                "fullName": "Jane Agent",
                "email": "jane@realty.com",
                "role": ParticipantRole.BUYING_AGENT.value,
            },
        ]

        result = self.client.create_loop(
            name="Transaction with Participants",
            transaction_type=TransactionType.PURCHASE_OFFER,
            status=LoopStatus.PRE_OFFER,
            profile_id=123,
            participants=participants,
        )

        assert result["data"]["name"] == "Transaction with Participants"

    @responses.activate
    def test_create_loop_with_string_enums(self) -> None:
        """Test loop creation with string enum values."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/loop-it",
            json={
                "data": {
                    "id": 999,
                    "name": "String Enum Loop",
                    "status": "SOLD",
                    "transactionType": "PURCHASED",
                }
            },
            status=201,
        )

        result = self.client.create_loop(
            name="String Enum Loop",
            transaction_type="PURCHASED",
            status="SOLD",
            profile_id=123,
        )

        assert result["data"]["transactionType"] == "PURCHASED"
        assert result["data"]["status"] == "SOLD"

    @responses.activate
    def test_create_loop_comprehensive(self) -> None:
        """Test loop creation with all optional parameters."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/loop-it",
            json={
                "data": {
                    "id": 999,
                    "name": "Complete Transaction",
                    "status": "PRE_OFFER",
                    "transactionType": "PURCHASE_OFFER",
                }
            },
            status=201,
        )

        participants = [
            {
                "fullName": "Complete Buyer",
                "email": "buyer@example.com",
                "role": ParticipantRole.BUYER.value,
                "phone": "+1 (555) 123-4567",
            }
        ]

        result = self.client.create_loop(
            name="Complete Transaction",
            transaction_type=TransactionType.PURCHASE_OFFER,
            status=LoopStatus.PRE_OFFER,
            profile_id=123,
            street_number="789",
            street_name="Complete Street",
            unit="Unit 5",
            city="Complete City",
            state="CA",
            zip_code="90210",
            county="Complete County",
            mls_property_id="MLS123456",
            participants=participants,
        )

        assert result["data"]["name"] == "Complete Transaction"

    @responses.activate
    def test_create_loop_validation_error(self) -> None:
        """Test loop creation with validation error."""
        responses.add(
            responses.POST,
            "https://api-gateway.dotloop.com/public/v2/loop-it",
            json={"message": "Invalid transaction type"},
            status=400,
        )

        with pytest.raises(DotloopError):
            self.client.create_loop(
                name="Invalid Loop",
                transaction_type="INVALID_TYPE",
                status=LoopStatus.PRE_OFFER,
                profile_id=123,
            )
