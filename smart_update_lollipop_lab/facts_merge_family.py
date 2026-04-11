from __future__ import annotations

from pathlib import Path
from typing import Any


ITER3_TRACE_ROOT = Path("artifacts/codex/iter3")


class _Base:
    @staticmethod
    async def _run_bucket_stage(*, event_ctx: dict[str, Any], trace_root: Path, baseline_facts: list[str], merge_records: list[dict[str, Any]]) -> dict[str, Any]:
        return {"payload": {"decisions": [{"record_id": item["record_id"]} for item in merge_records]}}

    @staticmethod
    def _filter_event_ids(event_ids: list[int], wanted_ids: set[int]) -> list[int]:
        return [event_id for event_id in event_ids if event_id in wanted_ids]


base = _Base()


def _bucket_result_matches_merge_records(bucket_result: dict[str, Any], merge_records: list[dict[str, Any]]) -> bool:
    expected = sorted(str(item["record_id"]) for item in merge_records)
    actual = sorted(str(item.get("record_id")) for item in list((bucket_result.get("payload") or {}).get("decisions") or []))
    return expected == actual


def _hydrate_bucket_result(event_id: int, trace_root: Path) -> dict[str, Any] | None:
    result_path = trace_root / str(event_id) / "facts.merge.bucket.v2" / "result.json"
    if not result_path.exists():
        return None
    import json

    return json.loads(result_path.read_text(encoding="utf-8"))


async def _load_or_rerun_bucket_result(
    *,
    event_ctx: dict[str, Any],
    trace_root: Path,
    baseline_facts: list[str],
    merge_records: list[dict[str, Any]],
) -> dict[str, Any]:
    event_id = int(event_ctx["event"]["id"])
    hydrated = _hydrate_bucket_result(event_id, trace_root)
    stage_dir = trace_root / str(event_id) / "facts.merge.bucket.v2"
    if hydrated and _bucket_result_matches_merge_records(hydrated, merge_records):
        return hydrated
    if stage_dir.exists():
        import shutil

        shutil.rmtree(stage_dir)
    return await base._run_bucket_stage(
        event_ctx=event_ctx,
        trace_root=trace_root,
        baseline_facts=baseline_facts,
        merge_records=merge_records,
    )
