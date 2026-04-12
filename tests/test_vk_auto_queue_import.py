import asyncio
import json
import os
import sys

import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import vk_auto_queue
import vk_intake
from main import Database
from ops_run import start_ops_run as real_start_ops_run


class DummyBot:
    def __init__(self) -> None:
        self.messages: list[tuple[int, str]] = []

    async def send_message(self, chat_id, text, **_kwargs):
        self.messages.append((int(chat_id), str(text)))

    async def get_me(self):
        class Me:
            username = "eventsbotTestBot"

        return Me()


@pytest.mark.asyncio
async def test_vk_auto_import_scheduler_records_error_when_runner_crashes(tmp_path, monkeypatch):
    db = Database(str(tmp_path / "db.sqlite"))
    await db.init()

    async with db.raw_conn() as conn:
        await conn.execute(
            'INSERT INTO "user"(user_id, username, is_superadmin, blocked) VALUES(?, ?, 1, 0)',
            (185169715, "max"),
        )
        await conn.commit()

    monkeypatch.setenv("ENABLE_VK_AUTO_IMPORT", "1")

    captured: dict[str, object] = {}

    async def fake_run(_db, _bot, **kwargs):
        captured.update(kwargs)
        raise RuntimeError("queue exploded")

    monkeypatch.setattr(vk_auto_queue, "run_vk_auto_import", fake_run)

    bot = DummyBot()
    await vk_auto_queue.vk_auto_import_scheduler(db, bot, run_id="sched-runner-crash")

    assert int(captured["ops_run_id"]) > 0
    async with db.raw_conn() as conn:
        cur = await conn.execute(
            "SELECT status, details_json FROM ops_run WHERE kind='vk_auto_import' ORDER BY id ASC"
        )
        row = await cur.fetchone()

    assert row is not None
    status, details_raw = row
    details = json.loads(details_raw)
    assert status == "error"
    assert details["run_id"] == "sched-runner-crash"
    assert "queue exploded" in details["fatal_error"]


@pytest.mark.asyncio
async def test_run_vk_auto_import_uses_existing_ops_run_id(tmp_path, monkeypatch):
    db = Database(str(tmp_path / "db.sqlite"))
    await db.init()

    ops_run_id = await real_start_ops_run(
        db,
        kind="vk_auto_import",
        trigger="scheduled",
        operator_id=0,
        details={"run_id": "sched-existing"},
    )

    async def fake_start_ops_run(*_args, **_kwargs):
        raise AssertionError("start_ops_run should not be called when ops_run_id is provided")

    async def fake_pick_next(*_args, **_kwargs):
        return None

    monkeypatch.setattr(vk_auto_queue, "start_ops_run", fake_start_ops_run)
    monkeypatch.setattr(vk_auto_queue.vk_review, "pick_next", fake_pick_next)

    bot = DummyBot()
    await vk_auto_queue.run_vk_auto_import(
        db,
        bot,
        chat_id=1,
        limit=1,
        operator_id=123,
        trigger="scheduled",
        run_id="sched-existing",
        ops_run_id=ops_run_id,
    )

    async with db.raw_conn() as conn:
        cur = await conn.execute(
            "SELECT id, status, details_json FROM ops_run WHERE kind='vk_auto_import' ORDER BY id ASC"
        )
        rows = await cur.fetchall()

    assert len(rows) == 1
    row_id, status, details_raw = rows[0]
    details = json.loads(details_raw)
    assert int(row_id) == int(ops_run_id)
    assert status == "success"
    assert details["run_id"] == "sched-existing"


@pytest.mark.asyncio
async def test_vk_auto_import_marks_row_failed_on_timeout(tmp_path, monkeypatch):
    db = Database(str(tmp_path / "db.sqlite"))
    await db.init()

    async with db.raw_conn() as conn:
        await conn.execute(
            "INSERT INTO vk_source(group_id, screen_name, name, location, default_time, default_ticket_link) VALUES(?,?,?,?,?,?)",
            (1, "club1", "Test Community", "Научная библиотека", None, None),
        )
        await conn.execute(
            "INSERT INTO vk_inbox(id, group_id, post_id, date, text, matched_kw, has_date, event_ts_hint, status) VALUES(?,?,?,?,?,?,?,?,?)",
            (1, 1, 100, 0, "stub", vk_intake.OCR_PENDING_SENTINEL, 0, None, "pending"),
        )
        await conn.commit()

    monkeypatch.setenv("VK_AUTO_IMPORT_ROW_TIMEOUT_SEC", "0.01")

    async def fake_process(*_args, **_kwargs):
        await asyncio.sleep(0.05)

    monkeypatch.setattr(vk_auto_queue, "_process_vk_inbox_row", fake_process)

    bot = DummyBot()
    report = await vk_auto_queue.run_vk_auto_import(db, bot, chat_id=1, limit=1, operator_id=123)

    assert report.inbox_failed == 1
    assert any("timeout_failed https://vk.com/wall-1_100" in err for err in report.errors)
    assert any("таймаут обработки поста" in text for _, text in bot.messages)

    async with db.raw_conn() as conn:
        cur = await conn.execute("SELECT status FROM vk_inbox WHERE id=1")
        row = await cur.fetchone()
        assert row is not None
        assert row[0] == "failed"
