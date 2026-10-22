from bot.workflow_lark_wallet_group import _build_digest_text


def test_digest_keeps_original_body_and_ats_finance():
    text = _build_digest_text(
        "2026-09-22",
        [
            ("ProjectA", [("主网合约", 5)]),
            ("ProjectB", [("主网合约", 4)]),
            ("ProjectC", [("主网合约", 5)]),
        ],
        at_open_id="ou_finance",
        at_name="财务",
    )
    assert text.startswith('<at user_id="ou_finance">财务</at>\n')
    assert "【项目方地址日报】2026-09-22" in text
    assert "今日新增项目：3 个" in text
    assert "主网合约 14" in text
    assert "1. ProjectA：主网合约 5 个" in text


def test_digest_without_open_id_has_no_at():
    text = _build_digest_text("2026-09-22", [])
    assert "<at " not in text
    assert text.startswith("【项目方地址日报】2026-09-22")
    assert "今日暂无新的项目方地址写入。" in text
