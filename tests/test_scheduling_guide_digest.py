from __future__ import annotations

from types import SimpleNamespace

import pytest

import scheduling


@pytest.mark.asyncio
async def test_scheduled_guide_digest_notifies_operator_when_no_new_items(monkeypatch):
    monkeypatch.setenv("ENABLE_GUIDE_DIGEST_SCHEDULED", "1")

    async def fake_resolve_superadmin_chat_id(_db):
        return 4242

    async def fake_run_guide_monitor(_db, _bot, **kwargs):
        assert kwargs["trigger"] == "scheduled"
        assert kwargs["mode"] == "full"
        assert kwargs["chat_id"] == 4242
        return SimpleNamespace(errors=[])

    async def fake_publish_guide_digest(_db, _bot, **kwargs):
        assert kwargs["family"] == "new_occurrences"
        assert kwargs["chat_id"] == 4242
        return {
            "issue_id": 901,
            "published": False,
            "reason": "no_items",
        }

    monkeypatch.setattr(scheduling, "resolve_superadmin_chat_id", fake_resolve_superadmin_chat_id)

    class _DummyBot:
        def __init__(self) -> None:
            self.sent_messages: list[tuple[int, str]] = []

        async def send_message(self, chat_id, text, **kwargs):
            del kwargs
            self.sent_messages.append((int(chat_id), text))
            return None

    bot = _DummyBot()

    import guide_excursions.service as guide_service

    monkeypatch.setattr(guide_service, "run_guide_monitor", fake_run_guide_monitor)
    monkeypatch.setattr(guide_service, "publish_guide_digest", fake_publish_guide_digest)

    await scheduling._run_scheduled_guide_excursions(object(), bot, mode="full")

    assert bot.sent_messages == [
        (
            4242,
            "ℹ️ Scheduled guide digest: новых экскурсионных находок нет\nissue_id=901",
        )
    ]


@pytest.mark.asyncio
async def test_scheduled_guide_digest_still_publishes_after_soft_partial(monkeypatch):
    monkeypatch.setenv("ENABLE_GUIDE_DIGEST_SCHEDULED", "1")

    async def fake_resolve_superadmin_chat_id(_db):
        return 4242

    async def fake_run_guide_monitor(_db, _bot, **kwargs):
        assert kwargs["trigger"] == "scheduled"
        assert kwargs["mode"] == "full"
        return SimpleNamespace(errors=["kaggle result marked as partial"])

    async def fake_publish_guide_digest(_db, _bot, **kwargs):
        assert kwargs["family"] == "new_occurrences"
        assert kwargs["chat_id"] == 4242
        return {
            "issue_id": 902,
            "published": True,
            "target_chats": ["@wheretogo39", "@youwillsee39"],
        }

    monkeypatch.setattr(scheduling, "resolve_superadmin_chat_id", fake_resolve_superadmin_chat_id)

    class _DummyBot:
        def __init__(self) -> None:
            self.sent_messages: list[tuple[int, str]] = []

        async def send_message(self, chat_id, text, **kwargs):
            del kwargs
            self.sent_messages.append((int(chat_id), text))
            return None

    bot = _DummyBot()

    import guide_excursions.service as guide_service

    monkeypatch.setattr(guide_service, "run_guide_monitor", fake_run_guide_monitor)
    monkeypatch.setattr(guide_service, "publish_guide_digest", fake_publish_guide_digest)

    await scheduling._run_scheduled_guide_excursions(object(), bot, mode="full")

    assert bot.sent_messages == [
        (
            4242,
            "📣 Scheduled guide digest published\nissue_id=902\ntarget=—",
        )
    ]


@pytest.mark.asyncio
async def test_scheduled_guide_digest_stops_on_hard_monitor_error(monkeypatch):
    monkeypatch.setenv("ENABLE_GUIDE_DIGEST_SCHEDULED", "1")

    async def fake_resolve_superadmin_chat_id(_db):
        return 4242

    async def fake_run_guide_monitor(_db, _bot, **kwargs):
        assert kwargs["trigger"] == "scheduled"
        assert kwargs["mode"] == "full"
        return SimpleNamespace(errors=["Kaggle path failed: RuntimeError: boom"])

    async def fake_publish_guide_digest(_db, _bot, **kwargs):
        raise AssertionError("publish should not run for hard monitor errors")

    monkeypatch.setattr(scheduling, "resolve_superadmin_chat_id", fake_resolve_superadmin_chat_id)

    class _DummyBot:
        async def send_message(self, chat_id, text, **kwargs):
            del chat_id, text, kwargs
            return None

    bot = _DummyBot()

    import guide_excursions.service as guide_service

    monkeypatch.setattr(guide_service, "run_guide_monitor", fake_run_guide_monitor)
    monkeypatch.setattr(guide_service, "publish_guide_digest", fake_publish_guide_digest)

    await scheduling._run_scheduled_guide_excursions(object(), bot, mode="full")
