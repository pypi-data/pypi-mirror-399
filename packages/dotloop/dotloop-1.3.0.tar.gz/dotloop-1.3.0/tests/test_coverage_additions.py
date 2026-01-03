import pytest
import requests
import responses

from dotloop.auth import AuthClient
from dotloop.base_client import BaseClient
from dotloop.contact import ContactClient
from dotloop.document import DocumentClient
from dotloop.enums import LoopStatus, ParticipantRole, TransactionType, WebhookEventType
from dotloop.exceptions import DotloopError
from dotloop.loop import LoopClient
from dotloop.loop_detail import LoopDetailClient
from dotloop.loop_it import LoopItClient
from dotloop.profile import ProfileClient
from dotloop.template import TemplateClient
from dotloop.webhook import WebhookClient


class DummyClient(BaseClient):
    def trigger_get(self) -> None:
        self.get("/dummy")

    def trigger_post(self) -> None:
        self.post("/dummy", data={})

    def trigger_patch(self) -> None:
        self.patch("/dummy", data={})

    def trigger_delete(self) -> None:
        self.delete("/dummy")


def test_base_client_request_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    client = DummyClient(api_key="k")

    # Each method raises RequestException to enter except path
    # Cover default path without headers
    monkeypatch.setattr(
        "dotloop.base_client.requests.get",
        lambda *a, **k: (_ for _ in ()).throw(requests.RequestException("err")),
    )
    with pytest.raises(DotloopError):
        client.get("/dummy")
    # Cover branch with headers update
    with pytest.raises(DotloopError):
        client.get("/dummy", headers={"X": "1"})

    # For POST, ensure headers path is covered
    monkeypatch.setattr(
        "dotloop.base_client.requests.post",
        lambda *a, **k: (_ for _ in ()).throw(requests.RequestException("err")),
    )
    with pytest.raises(DotloopError):
        client.post("/dummy", data={}, headers={"X": "1"})

    monkeypatch.setattr(
        "dotloop.base_client.requests.patch",
        lambda *a, **k: (_ for _ in ()).throw(requests.RequestException("err")),
    )
    with pytest.raises(DotloopError):
        client.patch("/dummy", data={}, headers={"X": "1"})

    monkeypatch.setattr(
        "dotloop.base_client.requests.delete",
        lambda *a, **k: (_ for _ in ()).throw(requests.RequestException("err")),
    )
    with pytest.raises(DotloopError):
        client.delete("/dummy", headers={"X": "1"})


def test_auth_client_request_exceptions(monkeypatch: pytest.MonkeyPatch) -> None:
    auth = AuthClient(
        client_id="id",
        client_secret="sec",
        redirect_uri="https://example.com/cb",
        api_key="k",
    )

    # Patch the requests.post referenced in dotloop.auth module by importing module and replacing symbol
    def raise_req(*args, **kwargs):
        raise requests.RequestException("err")

    monkeypatch.setattr(requests, "post", raise_req)

    with pytest.raises(DotloopError):
        auth.exchange_code_for_token("code")
    with pytest.raises(DotloopError):
        auth.refresh_access_token("rt")
    with pytest.raises(DotloopError):
        auth.revoke_token("tok")


@responses.activate
def test_contact_update_all_fields() -> None:
    client = ContactClient(api_key="k")
    responses.add(
        responses.PATCH,
        "https://api-gateway.dotloop.com/public/v2/contact/123",
        json={"data": {"id": 123}},
        status=200,
    )
    result = client.update_contact(
        contact_id=123,
        first_name="A",
        last_name="B",
        email="e@example.com",
        phone="1",
        company="C",
        address="addr",
        city="city",
        state="ST",
        zip_code="00000",
        country="US",
    )
    assert result["data"]["id"] == 123


@responses.activate
def test_profile_create_and_update_all_fields() -> None:
    client = ProfileClient(api_key="k")
    responses.add(
        responses.POST,
        "https://api-gateway.dotloop.com/public/v2/profile",
        json={"data": {"id": 1}},
        status=201,
    )
    responses.add(
        responses.PATCH,
        "https://api-gateway.dotloop.com/public/v2/profile/1",
        json={"data": {"id": 1}},
        status=200,
    )
    created = client.create_profile(
        name="Name",
        company="Co",
        phone="1",
        fax="2",
        address="addr",
        city="city",
        state="ST",
        zip_code="00000",
        country="US",
    )
    assert created["data"]["id"] == 1
    updated = client.update_profile(
        profile_id=1,
        name="New",
        company="NewCo",
        phone="3",
        fax="4",
        address="addr2",
        city="city2",
        state="NY",
        zip_code="11111",
        country="US",
    )
    assert updated["data"]["id"] == 1


@responses.activate
def test_loop_detail_helpers_cover_all() -> None:
    client = LoopDetailClient(api_key="k")
    # update_loop_details
    responses.add(
        responses.PATCH,
        "https://api-gateway.dotloop.com/public/v2/profile/9/loop/8/detail",
        json={"data": {}},
        status=200,
    )
    # property address
    responses.add(
        responses.PATCH,
        "https://api-gateway.dotloop.com/public/v2/profile/9/loop/8/detail",
        json={"data": {}},
        status=200,
    )
    # financials
    responses.add(
        responses.PATCH,
        "https://api-gateway.dotloop.com/public/v2/profile/9/loop/8/detail",
        json={"data": {}},
        status=200,
    )
    # contract dates
    responses.add(
        responses.PATCH,
        "https://api-gateway.dotloop.com/public/v2/profile/9/loop/8/detail",
        json={"data": {}},
        status=200,
    )
    client.update_loop_details(9, 8, {"k": "v"})
    client.update_property_address(
        9,
        8,
        street_number="1",
        street_name="Main",
        unit_number="U",
        city="C",
        state="ST",
        zip_code="00000",
        county="X",
        country="US",
        mls_number="MLS",
        parcel_tax_id="PID",
    )
    client.update_financials(
        9,
        8,
        purchase_sale_price="1",
        sale_commission_rate="2",
        sale_commission_split_buy_percent="3",
        sale_commission_split_sell_percent="4",
        sale_commission_total="5",
        earnest_money_amount="6",
        earnest_money_held_by="7",
        sale_commission_split_buy_dollar="8",
        sale_commission_split_sell_dollar="9",
    )
    client.update_contract_dates(
        9,
        8,
        contract_agreement_date="01/01/2024",
        closing_date="02/02/2024",
        inspection_date="03/03/2024",
        offer_date="04/04/2024",
        offer_expiration_date="05/05/2024",
        occupancy_date="06/06/2024",
    )


@responses.activate
def test_loop_update_string_and_enum() -> None:
    client = LoopClient(api_key="k")
    # Use enum branch
    responses.add(
        responses.PATCH,
        "https://api-gateway.dotloop.com/public/v2/profile/1/loop/2",
        json={"data": {"id": 2}},
        status=200,
    )
    client.update_loop(
        1, 2, status=LoopStatus.SOLD, transaction_type=TransactionType.PURCHASE_OFFER
    )
    # Use string branch
    responses.add(
        responses.PATCH,
        "https://api-gateway.dotloop.com/public/v2/profile/1/loop/3",
        json={"data": {"id": 3}},
        status=200,
    )
    client.update_loop(1, 3, status="SOLD", transaction_type="LISTING_FOR_SALE")


@responses.activate
def test_loop_list_with_sort_and_filter_and_details() -> None:
    client = LoopClient(api_key="k")
    responses.add(
        responses.GET,
        "https://api-gateway.dotloop.com/public/v2/profile/5/loop",
        json={"data": [], "meta": {"total": 0}},
        status=200,
    )
    res = client.list_loops(
        profile_id=5,
        batch_size=10,
        batch_number=2,
        sort="updated:desc",
        filter_params="created_min=2024-01-01",
        include_details=True,
    )
    assert res["meta"]["total"] == 0


@responses.activate
def test_webhook_update_and_failed_events() -> None:
    client = WebhookClient(api_key="k")
    # update
    responses.add(
        responses.PATCH,
        "https://api-gateway.dotloop.com/public/v2/subscription/10",
        json={"data": {"id": "10"}},
        status=200,
    )
    client.update_subscription(
        10,
        url="https://u",
        event_types=["LOOP_CREATED"],
        enabled=True,
    )

    # list events and filter failed
    responses.add(
        responses.GET,
        "https://api-gateway.dotloop.com/public/v2/subscription/99/event",
        json={
            "data": [
                {"type": "LOOP_UPDATED", "status": "SUCCESS"},
                {"type": "LOOP_CREATED", "status": "FAILED"},
                {"type": "LOOP_CREATED", "status": "ERROR"},
            ],
            "meta": {"total": 3},
        },
        status=200,
    )
    failed = client.get_failed_events(99)
    assert failed["meta"]["total"] == 2
    # summary
    summary = client.get_subscription_summary(99)
    assert isinstance(summary["success_rate"], (int, float))


@responses.activate
def test_template_summary_no_types() -> None:
    client = TemplateClient(api_key="k")
    responses.add(
        responses.GET,
        "https://api-gateway.dotloop.com/public/v2/profile/7/loop-template",
        json={"data": [], "meta": {"total": 0}},
        status=200,
    )
    summary = client.get_template_summary(7)
    assert summary["most_common_type"] is None


@responses.activate
def test_template_find_by_name_exact_and_partial() -> None:
    client = TemplateClient(api_key="k")
    responses.add(
        responses.GET,
        "https://api-gateway.dotloop.com/public/v2/profile/7/loop-template",
        json={
            "data": [
                {"id": 1, "name": "Alpha"},
                {"id": 2, "name": "Beta"},
            ],
            "meta": {"total": 2},
        },
        status=200,
    )
    res = client.find_template_by_name(7, "Alpha", exact_match=True)
    assert len(res["data"]) == 1
    res2 = client.find_template_by_name(7, "a")
    assert len(res2["data"]) == 2


@responses.activate
def test_loop_it_create_with_participants_and_all_fields() -> None:
    client = LoopItClient(api_key="k")
    responses.add(
        responses.POST,
        "https://api-gateway.dotloop.com/public/v2/loop-it",
        json={"data": {"loopUrl": "https://loop"}},
        status=201,
    )
    res = client.create_loop(
        name="Name",
        transaction_type=TransactionType.PURCHASE_OFFER,
        status=LoopStatus.PRE_OFFER,
        profile_id=1,
        street_name="Main",
        street_number="1",
        unit="U",
        city="C",
        state="ST",
        zip_code="00000",
        county="X",
        country="US",
        participants=[
            {"fullName": "A", "email": "a@b.com", "role": ParticipantRole.BUYER}
        ],
        template_id=9,
        mls_property_id="MP",
        mls_id="MID",
        mls_agent_id="AID",
        nrds_id="N",
    )
    assert "data" in res


@responses.activate
def test_document_download_error_no_url() -> None:
    client = DocumentClient(api_key="k")
    # metadata without url
    responses.add(
        responses.GET,
        "https://api-gateway.dotloop.com/public/v2/profile/1/loop/2/document/3",
        json={"data": {"id": 3}},
        status=200,
    )
    with pytest.raises(DotloopError):
        client.download_document(1, 2, 3)


@responses.activate
def test_document_download_request_exception() -> None:
    client = DocumentClient(api_key="k")
    # metadata with url
    responses.add(
        responses.GET,
        "https://api-gateway.dotloop.com/public/v2/profile/1/loop/2/document/4",
        json={"data": {"id": 4, "downloadUrl": "https://u"}},
        status=200,
    )
    # No mocked response for https://u → responses will raise ConnectionError
    with pytest.raises(DotloopError):
        client.download_document(1, 2, 4)


@responses.activate
def test_document_folder_wrappers_and_listing() -> None:
    client = DocumentClient(api_key="k")
    # list_documents_in_folder
    responses.add(
        responses.GET,
        "https://api-gateway.dotloop.com/public/v2/profile/9/loop/8/folder/7/document",
        json={"data": [], "meta": {"total": 0}},
        status=200,
    )
    res = client.list_documents_in_folder(9, 8, 7)
    assert res["meta"]["total"] == 0

    # get_document_in_folder
    responses.add(
        responses.GET,
        "https://api-gateway.dotloop.com/public/v2/profile/9/loop/8/folder/7/document/6",
        json={"data": {"id": 6, "downloadUrl": "https://dl"}},
        status=200,
    )
    doc = client.get_document_in_folder(9, 8, 7, 6)
    assert doc["data"]["id"] == 6

    # download_document_in_folder
    responses.add(responses.GET, "https://dl", body=b"X", status=200)
    content = client.download_document_in_folder(9, 8, 7, 6)
    assert content == b"X"

    # download_document_to_file wrapper path
    responses.add(
        responses.GET,
        "https://api-gateway.dotloop.com/public/v2/profile/9/loop/8/document/5",
        json={"data": {"id": 5, "downloadUrl": "https://dl2"}},
        status=200,
    )
    responses.add(responses.GET, "https://dl2", body=b"Y", status=200)
    import tempfile

    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    client.download_document_to_file(9, 8, 5, tmp.name)
    with open(tmp.name, "rb") as f:
        assert f.read() == b"Y"


@responses.activate
def test_webhook_create_and_summary_all() -> None:
    client = WebhookClient(api_key="k")
    responses.add(
        responses.POST,
        "https://api-gateway.dotloop.com/public/v2/subscription",
        json={"data": {"id": "1"}},
        status=200,
    )
    res = client.create_subscription(
        url="https://u",
        target_type="PROFILE",
        target_id=1,
        event_types=[WebhookEventType.LOOP_CREATED],
        enabled=True,
    )
    assert res["data"]["id"] == "1"

    responses.add(
        responses.GET,
        "https://api-gateway.dotloop.com/public/v2/subscription",
        json={
            "data": [
                {
                    "id": "1",
                    "url": "https://u",
                    "eventTypes": ["LOOP_CREATED"],
                    "enabled": True,
                },
                {
                    "id": "2",
                    "url": "https://u2",
                    "eventTypes": ["LOOP_UPDATED"],
                    "enabled": False,
                },
            ],
            "meta": {"total": 2},
        },
        status=200,
    )
    all_summary = client.get_all_subscriptions_summary()
    assert all_summary["total_subscriptions"] == 2
    assert all_summary["unique_urls"] == 2
    assert (
        "LOOP_CREATED" in all_summary["event_types"]
        or "LOOP_UPDATED" in all_summary["event_types"]
    )
