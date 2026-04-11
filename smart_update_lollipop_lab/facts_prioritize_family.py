from __future__ import annotations

import copy
import re
import textwrap
from typing import Any


BUCKET_ORDER = [
    "event_core",
    "program_list",
    "people_and_roles",
    "forward_looking",
    "logistics_infoblock",
    "support_context",
    "uncertain",
]


def _flat_facts(pack: dict[str, Any]) -> list[dict[str, Any]]:
    flat: list[dict[str, Any]] = []
    for bucket in BUCKET_ORDER:
        for item in list(pack.get(bucket) or []):
            if isinstance(item, dict):
                flat.append(item)
    return flat


def _event_type_label(event_type: str | None) -> str:
    return (event_type or "").strip().lower()


def _title_is_bare(title: str, event_type: str | None) -> bool:
    lowered = title.strip().lower()
    if not lowered:
        return False
    anchor_words = (
        "лекци",
        "концерт",
        "спектак",
        "показ",
        "киноклуб",
        "кинопоказ",
        "презентац",
        "выстав",
        "вечер",
        "опера",
        "балет",
        "мюзикл",
        "фестиваль",
        "экскурси",
    )
    if any(word in lowered for word in anchor_words):
        return False
    return _event_type_label(event_type) in {"кинопоказ", "screening", "презентация", "presentation", "лекция", "lecture"}


def _title_needs_format_anchor(title: str, event_type: str | None) -> bool:
    return _title_is_bare(title, event_type)


def _augment_fact_pack_from_raw_facts(
    fact_pack: dict[str, Any],
    *,
    event_type: str,
    raw_facts: list[str],
) -> dict[str, Any]:
    augmented = copy.deepcopy(fact_pack)
    rescued: list[str] = []
    if _event_type_label(event_type) == "выставка":
        next_idx = len(list(augmented.get("support_context") or [])) + 1
        existing = {item.get("text") for item in list(augmented.get("support_context") or []) if isinstance(item, dict)}
        for raw in raw_facts:
            text = re.sub(r"\s+", " ", str(raw or "")).strip()
            if not text or text in existing:
                continue
            if re.search(r"(?iu)(великая депрессия|вторая мировая|влияние.+на)", text):
                augmented.setdefault("support_context", []).append(
                    {
                        "fact_id": f"SC{next_idx:02d}",
                        "text": text,
                        "literal_items": [],
                        "evidence_record_ids": [],
                    }
                )
                rescued.append(f"SC{next_idx:02d}")
                next_idx += 1
    augmented["rescue_stats"] = {"rescued_fact_ids": rescued}
    return augmented


def _apply_narrative_policies(weighted_pack: dict[str, Any], *, event_type: str | None = None) -> dict[str, Any]:
    pack = copy.deepcopy(weighted_pack)
    suppressed = 0
    promoted = 0
    etype = _event_type_label(event_type)
    for item in _flat_facts(pack):
        item.setdefault("narrative_policy", "include")
        text = str(item.get("text") or "")
        if re.search(r"(?iu)(другие постановки|в афише указаны даты ближайших спектаклей|даты ближайших спектаклей)", text):
            item["narrative_policy"] = "suppress"
            suppressed += 1
        elif re.search(r"(?iu)(печенье|чай будет предоставлен|чай предоставлен)", text):
            item["narrative_policy"] = "suppress"
            suppressed += 1
        elif re.search(r"(?iu)(будет интересно|широкой аудитории|без возрастных ограничений)", text):
            item["narrative_policy"] = "suppress"
            suppressed += 1
        elif re.search(r"(?iu)\b(?:6|12|16|18)\+\b|возрастн", text):
            item["narrative_policy"] = "suppress"
            suppressed += 1

    if etype in {"кинопоказ", "screening"} and not list(pack.get("event_core") or []) and not list(pack.get("forward_looking") or []):
        for item in list(pack.get("support_context") or []):
            text = str(item.get("text") or "")
            if re.search(r"(?iu)(экранизац|действие фильма|в центре сюжета|история|рассказывает о)", text) and item.get("weight") == "low":
                item["weight"] = "medium"
                promoted += 1

    pack["policy_stats"] = {"suppressed_count": suppressed, "promoted_count": promoted}
    return pack


def _find_fact(pack: dict[str, Any], fact_id: str) -> dict[str, Any] | None:
    for item in _flat_facts(pack):
        if item.get("fact_id") == fact_id:
            return item
    return None


def _weight_rank(weight: str | None) -> int:
    return {"high": 0, "medium": 1, "low": 2}.get(str(weight or "").strip().lower(), 3)


def _is_list_heavy_program_fact(item: dict[str, Any] | None) -> bool:
    if not isinstance(item, dict):
        return False
    return str(item.get("bucket") or "").strip() == "program_list" and bool(item.get("literal_items"))


def _best_non_program_lead_support(
    weighted_pack: dict[str, Any],
    *,
    exclude_fact_ids: set[str],
) -> str:
    candidates: list[tuple[int, int, int, str]] = []
    bucket_order = ["support_context", "forward_looking", "event_core", "people_and_roles", "program_list"]
    for bucket_idx, bucket in enumerate(bucket_order):
        for item_idx, item in enumerate(list(weighted_pack.get(bucket) or [])):
            fact_id = str(item.get("fact_id") or "").strip()
            if not fact_id or fact_id in exclude_fact_ids:
                continue
            if item.get("narrative_policy") == "suppress":
                continue
            if _is_list_heavy_program_fact(item):
                continue
            candidates.append((bucket_idx, _weight_rank(item.get("weight")), item_idx, fact_id))
    if not candidates:
        return ""
    candidates.sort()
    return candidates[0][3]


def _best_narrative_support_over_secondary_credit(
    weighted_pack: dict[str, Any],
    *,
    exclude_fact_ids: set[str],
) -> str:
    candidates: list[tuple[int, int, int, str]] = []
    bucket_order = ["support_context", "forward_looking", "event_core"]
    for bucket_idx, bucket in enumerate(bucket_order):
        for item_idx, item in enumerate(list(weighted_pack.get(bucket) or [])):
            fact_id = str(item.get("fact_id") or "").strip()
            if not fact_id or fact_id in exclude_fact_ids:
                continue
            if item.get("narrative_policy") == "suppress":
                continue
            if _is_list_heavy_program_fact(item):
                continue
            candidates.append((bucket_idx, _weight_rank(item.get("weight")), item_idx, fact_id))
    if not candidates:
        return ""
    candidates.sort()
    return candidates[0][3]


def _clean_lead(
    payload: dict[str, Any],
    weighted_pack: dict[str, Any],
    *,
    title: str,
    event_type: str | None,
) -> dict[str, Any]:
    cleaned = dict(payload)
    fallback_reasons: list[str] = []
    lead_fact_id = str(cleaned.get("lead_fact_id") or "").strip()
    lead_support_id = str(cleaned.get("lead_support_id") or "").strip()
    if not lead_fact_id:
        first = next((item["fact_id"] for item in _flat_facts(weighted_pack) if item.get("narrative_policy") != "suppress"), "")
        lead_fact_id = first

    if _title_needs_format_anchor(title, event_type):
        lead_item = _find_fact(weighted_pack, lead_fact_id)
        if lead_item and lead_item.get("bucket") == "people_and_roles":
            fallback = next(
                (
                    item["fact_id"]
                    for item in _flat_facts(weighted_pack)
                    if item.get("bucket") in {"event_core", "forward_looking", "support_context"}
                    and item.get("narrative_policy") != "suppress"
                ),
                lead_fact_id,
            )
            if fallback != lead_fact_id:
                lead_support_id = lead_fact_id
                lead_fact_id = fallback
                fallback_reasons.append("lead_missing_format_anchor")
        elif lead_item and lead_item.get("bucket") == "event_core" and _event_type_label(event_type) in {"presentation", "презентация"}:
            fallback = next(
                (
                    item["fact_id"]
                    for item in list(weighted_pack.get("forward_looking") or [])
                    if item.get("narrative_policy") != "suppress"
                ),
                lead_fact_id,
            )
            if fallback != lead_fact_id:
                lead_support_id = lead_fact_id
                lead_fact_id = fallback
                fallback_reasons.append("lead_missing_format_anchor")

    lead_item = _find_fact(weighted_pack, lead_fact_id)
    support_item = _find_fact(weighted_pack, lead_support_id) if lead_support_id else None
    if _is_list_heavy_program_fact(lead_item):
        fallback = _best_non_program_lead_support(weighted_pack, exclude_fact_ids={lead_fact_id, lead_support_id} - {""})
        if fallback:
            lead_support_id = lead_fact_id if not lead_support_id else lead_support_id
            lead_fact_id = fallback
            fallback_reasons.append("lead_program_list_reserved_for_program_block")
            lead_item = _find_fact(weighted_pack, lead_fact_id)
            support_item = _find_fact(weighted_pack, lead_support_id) if lead_support_id else None

    if _is_list_heavy_program_fact(support_item):
        fallback = _best_non_program_lead_support(weighted_pack, exclude_fact_ids={lead_fact_id, lead_support_id} - {""})
        if fallback:
            lead_support_id = fallback
            fallback_reasons.append("lead_support_program_list_reserved_for_program_block")
            support_item = _find_fact(weighted_pack, lead_support_id) if lead_support_id else None

    if isinstance(support_item, dict) and support_item.get("bucket") == "people_and_roles":
        fallback = _best_narrative_support_over_secondary_credit(
            weighted_pack,
            exclude_fact_ids={lead_fact_id, lead_support_id} - {""},
        )
        if fallback:
            lead_support_id = fallback
            fallback_reasons.append("lead_support_secondary_credit_replaced_by_narrative_hook")

    cleaned["lead_fact_id"] = lead_fact_id
    cleaned["lead_support_id"] = lead_support_id or ""
    cleaned["cleaning_stats"] = {"fallback_reasons": fallback_reasons}
    return cleaned


def _build_weight_prompt(*, title: str, event_type: str, weighted_pack: dict[str, Any], gemma4: bool = False) -> str:
    return textwrap.dedent(
        f"""
        {'SYSTEM' if gemma4 else 'PROMPT'}
        You do one small step: facts.prioritize.weight.v1.
        Return only JSON.
        Keep every fact_id exactly once.
        Assign weight high|medium|low.
        Do not write prose.
        Prefer keeping scarce scheduling detail, named people with explicit roles, and event-defining support context.
        Do not use suppress as a trash bucket for useful grounded facts.

        TITLE: {title}
        EVENT_TYPE: {event_type}
        FACT_PACK:
        {weighted_pack}
        """
    ).strip()


def _build_lead_prompt(*, event_id: int, title: str, event_type: str, weighted_pack: dict[str, Any], gemma4: bool = False) -> str:
    title_is_bare = _title_is_bare(title, event_type)
    title_needs_anchor = _title_needs_format_anchor(title, event_type)
    return textwrap.dedent(
        f"""
        {'SYSTEM' if gemma4 else 'PROMPT'}
        You do one small step: facts.prioritize.lead.v1.
        Return only JSON.
        Select exactly one lead_fact_id and optional lead_support_id.
        Lead must explain what kind of attendable event is this.
        Lead support selection priority:
        1. grounded rarity / scarcity / anticipation fact;
        2. grounded atmosphere / emotional characterisation fact;
        3. distinguishing format/program/action fact;
        4. secondary role credit only if 1-3 are absent.
        Lead support should prefer rarity, atmosphere, or attendance value when a grounded support fact makes the event feel more specific than a second dry summary.
        Reserve list-heavy program/repertoire title lists with literal_items for a downstream program block when a grounded non-list support fact exists.
        For concert and list-heavy cultural cases, prefer a hook that sounds like an announcement of the evening, not a catalog preamble.
        Do not default to lead choices that would force a dry opening like `событие посвящено ...`, if rarity, atmosphere, or attendance-shaping support can ground a stronger lead.
        title_is_bare: {str(title_is_bare).lower()}
        title_needs_format_anchor: {str(title_needs_anchor).lower()}
        WRONG lead: biography-only, cast-only, `Режиссёр фильма — ...`, project definition without event action.
        For opaque titles, prefer an event-facing anchor over people-only facts.
        Use event_type and ask what kind of attendable event is this.

        EVENT_ID: {event_id}
        TITLE: {title}
        EVENT_TYPE: {event_type}
        PACK:
        {weighted_pack}
        """
    ).strip()
