from __future__ import annotations

from bot.workflow_live_onboard import (
    _RETRY_NOTIFY,
    _SKIP_NOTIFY_SOURCES,
    build_onboard_message,
    classify_case,
    parse_bd_person,
    sends_lark_notify,
)


def test_classify_cases():
    assert classify_case(True, True) == 1
    assert classify_case(True, False) == 2
    assert classify_case(False, True) == 3
    assert classify_case(False, False) == 4


def test_parse_bd_person_from_user_field():
    oid, name = parse_bd_person(
        {"BD": [{"id": "ou_bd", "name": "BD"}]},
        "BD",
    )
    assert oid == "ou_bd"
    assert name == "BD"


def test_case1_message_uses_group_title_and_at():
    text = build_onboard_message(
        case=1,
        project="example-project",
        group="example-project <> Botchain",
        bd_name="BD",
        bd_open_id="ou_bd",
        form_sent=True,
    )
    assert text.startswith('<at user_id="ou_bd">BD</at>')
    assert "**Project:** `example-project`" in text
    assert "**Status:** Live on mainnet" in text
    assert "**TG group:** `example-project <> Botchain`" in text
    assert "**Delivery:** The audit account and the delivery account have joined" in text
    assert "**Form:** Onboarding Google Form has been sent" in text
    assert "Add the delivery account" not in text
    assert "1. Help the project submit Twitter and the contract address to the form" in text
    assert (
        "2. Share the mainnet-live PR tweet in the TG group and @ the audit account and the delivery account"
        in text
    )


def test_case2_asks_to_add_delivery():
    text = build_onboard_message(
        case=2,
        project="example-project",
        group="example-project <> Botchain",
        bd_name="BD",
        bd_open_id="ou_bd",
        form_sent=True,
    )
    assert (
        "**Delivery:** The audit account has joined; the delivery account has not been added"
        in text
    )
    assert "1. Add the delivery account to the TG group" in text


def test_case3_asks_to_add_audit():
    text = build_onboard_message(
        case=3,
        project="example-project",
        group="example-project <> Botchain",
        bd_name="BD",
        bd_open_id="ou_bd",
        form_sent=True,
    )
    assert (
        "**Delivery:** The delivery account has joined; the audit account has not been added"
        in text
    )
    assert "1. Add the audit account to the TG group" in text


def test_case4_form_not_sent():
    text = build_onboard_message(
        case=4,
        project="example-project",
        group="",
        bd_name="BD",
        bd_open_id="ou_bd",
        form_sent=False,
    )
    assert "**Delivery:** Neither account was detected in a TG group" in text
    assert "**Form:** Onboarding Google Form was not sent" in text
    assert (
        "1. Create the project TG group, add the audit account and the delivery account, then trigger the form send"
        in text
    )
    assert "**TG group:** `not matched`" in text


def test_only_audit_sends_lark_notify():
    class Cfg:
        def __init__(self, account: str, replies: bool = False):
            self.workflow_live_onboard_account = account
            self.group_replies_enabled = replies

    assert sends_lark_notify(Cfg("auditor")) is True
    assert sends_lark_notify(Cfg("deliverer")) is False
    assert sends_lark_notify(Cfg("", replies=True)) is True
    assert sends_lark_notify(Cfg("", replies=False)) is False


def test_join_catchup_does_not_send_live_notify():
    assert "join_catchup" in _SKIP_NOTIFY_SOURCES
    assert "startup_catchup" in _SKIP_NOTIFY_SOURCES


def test_retry_covers_stuck_scheduled():
    assert "scheduled" in _RETRY_NOTIFY
    assert "need_audit" in _RETRY_NOTIFY
    assert "sending" in _RETRY_NOTIFY
    assert "sent" not in _RETRY_NOTIFY
