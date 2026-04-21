from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest


_MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "kaggle"
    / "GuideExcursionsMonitor"
    / "guide_excursions_monitor.py"
)
_SPEC = importlib.util.spec_from_file_location("guide_excursions_monitor_local", _MODULE_PATH)
assert _SPEC and _SPEC.loader
monitor = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = monitor
_SPEC.loader.exec_module(monitor)


def _sample_post(text: str) -> monitor.ScannedPost:
    return monitor.ScannedPost(
        message_id=4661,
        grouped_id=None,
        post_date=datetime(2026, 4, 20, 18, 12, 1, tzinfo=timezone.utc),
        source_url="https://t.me/vkaliningrade/4661",
        text=text,
        views=1,
        forwards=0,
        reactions_total=0,
        reactions_json={},
        media_refs=[],
        media_assets=[],
    )


@pytest.mark.asyncio
async def test_screen_post_derives_legacy_fields_from_thin_response(monkeypatch):
    async def fake_ask_gemma(*args, **kwargs):
        del args, kwargs
        return {
            "decision": "announce",
            "extract_family": "announce",
            "multi_announce_likely": True,
            "reasons": ["dense schedule card"],
            "confidence": "high",
        }

    monkeypatch.setattr(monitor, "ask_gemma", fake_ask_gemma)

    screen = await monitor.screen_post(
        {"username": "vkaliningrade", "source_kind": "aggregator", "title": "Народный экскурсовод", "base_region": "Калининград"},
        _sample_post("25 апреля 17:30 Архитектурная прогулка"),
        {"has_date_signal": True, "has_time_signal": True},
    )

    assert screen["decision"] == "announce"
    assert screen["extract_family"] == "announce"
    assert screen["multi_announce_likely"] is True
    assert screen["post_kind"] == "announce_multi"
    assert screen["extract_mode"] == "announce"
    assert screen["base_region_fit"] == "unknown"


def test_should_run_occurrence_semantics_only_for_sparse_long_blocks():
    assert monitor._should_run_occurrence_semantics({"route_summary": "Хуфен"}, "x" * 500) is False
    assert monitor._should_run_occurrence_semantics({"route_summary": ""}, "short excerpt") is False
    assert monitor._should_run_occurrence_semantics({"route_summary": ""}, "x" * 260) is True


@pytest.mark.asyncio
async def test_extract_post_uses_block_router_for_multi_announce(monkeypatch):
    block_calls: list[str] = []

    monkeypatch.setattr(
        monitor,
        "build_occurrence_blocks",
        lambda text, limit=6: [
            {"id": "B1", "text": "19 апреля 18:00 Марауненхоф", "has_schedule_anchor": True, "has_time_signal": True, "looks_detail_pending": False},
            {"id": "B2", "text": "25 апреля 17:30 Архитектурная прогулка", "has_schedule_anchor": True, "has_time_signal": True, "looks_detail_pending": False},
            {"id": "B3", "text": "24 апреля 12:15 Огонь Брюстерорта", "has_schedule_anchor": True, "has_time_signal": True, "looks_detail_pending": False},
        ],
    )
    monkeypatch.setattr(
        monitor,
        "_compact_occurrence_blocks",
        lambda text, limit=6: [
            {"id": "B1", "text": "B1", "has_schedule_anchor": True, "has_time_signal": True, "looks_detail_pending": False},
            {"id": "B2", "text": "B2", "has_schedule_anchor": True, "has_time_signal": True, "looks_detail_pending": False},
            {"id": "B3", "text": "B3", "has_schedule_anchor": True, "has_time_signal": True, "looks_detail_pending": False},
        ],
    )

    async def fake_route_occurrence_blocks(*args, **kwargs):
        del args, kwargs
        return True, [
            {"source_block_id": "B1", "should_extract": True},
            {"source_block_id": "B2", "should_extract": True},
            {"source_block_id": "B3", "should_extract": False},
        ]

    async def fake_extract_occurrence_block(source_payload, *, post, flags, screen, block):
        del source_payload, post, flags, screen
        block_calls.append(block["id"])
        return {
            "source_block_id": block["id"],
            "source_fingerprint": block["id"],
            "canonical_title": block["id"],
            "title_normalized": block["id"].lower(),
            "date": "2026-04-25",
            "time": "17:30",
            "channel_url": "https://t.me/vkaliningrade/4661",
        }

    monkeypatch.setattr(monitor, "route_occurrence_blocks", fake_route_occurrence_blocks)
    monkeypatch.setattr(monitor, "_extract_occurrence_block", fake_extract_occurrence_block)

    items = await monitor.extract_post(
        {"username": "vkaliningrade", "source_kind": "aggregator", "title": "Народный экскурсовод", "base_region": "Калининград"},
        _sample_post("dense multi announce"),
        {"has_date_signal": True, "has_time_signal": True},
        {
            "decision": "announce",
            "extract_family": "announce",
            "multi_announce_likely": True,
            "extract_mode": "announce",
            "post_kind": "announce_multi",
        },
    )

    assert block_calls == ["B1", "B2"]
    assert [item["source_block_id"] for item in items] == ["B1", "B2"]
