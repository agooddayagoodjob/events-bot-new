from __future__ import annotations

import re
from typing import Any, Mapping

PERSONAL_SOURCE_KINDS = {"guide_personal"}
_WORD_RE = re.compile(r"[A-Za-zА-Яа-яЁё-]+")


def collapse_ws(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _source_kind(row: Mapping[str, Any]) -> str:
    return collapse_ws(str(row.get("source_kind") or ""))


def allow_fallback_guide_name(source_kind: str | None) -> bool:
    return collapse_ws(source_kind) in PERSONAL_SOURCE_KINDS


def _fact_pack_value(row: Mapping[str, Any], key: str) -> Any:
    fact_pack = row.get("fact_pack")
    if isinstance(fact_pack, Mapping):
        return fact_pack.get(key)
    return None


def _string_list(value: Any, *, limit: int = 8) -> list[str]:
    out: list[str] = []
    if isinstance(value, str):
        raw = collapse_ws(value)
        items = re.split(r"\s*[;,]\s*", raw) if raw else []
    elif isinstance(value, (list, tuple, set)):
        items = list(value)
    else:
        return out
    for item in items:
        text = collapse_ws(item)
        if not text or text in out:
            continue
        out.append(text)
        if len(out) >= limit:
            break
    return out


def _explicit_guide_names(row: Mapping[str, Any]) -> list[str]:
    raw = row.get("guide_names") or _fact_pack_value(row, "guide_names") or []
    return [item for item in _string_list(raw, limit=6) if item]


def _candidate_anchor(value: str | None) -> str:
    return collapse_ws(str(value or "").split(",", 1)[0])


def _candidate_tokens(value: str | None) -> list[str]:
    return [token for token in _WORD_RE.findall(_candidate_anchor(value)) if len(token) >= 3]


def _names_overlap(left: str | None, right: str | None) -> bool:
    left_anchor = _candidate_anchor(left).lower()
    right_anchor = _candidate_anchor(right).lower()
    if not left_anchor or not right_anchor:
        return False
    if left_anchor == right_anchor:
        return True
    left_tokens = _candidate_tokens(left)
    right_tokens = _candidate_tokens(right)
    if not left_tokens or not right_tokens:
        return False
    return left_tokens[-1].lower() == right_tokens[-1].lower()


def _occurrence_text_haystack(row: Mapping[str, Any]) -> str:
    parts = [
        row.get("dedup_source_text"),
        row.get("post_excerpt"),
        row.get("text_excerpt"),
        row.get("summary_one_liner"),
        row.get("canonical_title"),
        _fact_pack_value(row, "post_excerpt"),
        _fact_pack_value(row, "text_excerpt"),
        _fact_pack_value(row, "summary_one_liner"),
        _fact_pack_value(row, "canonical_title"),
    ]
    return " ".join(collapse_ws(part) for part in parts if collapse_ws(part)).lower()


def guide_line_has_occurrence_support(candidate: str | None, row: Mapping[str, Any]) -> bool:
    text = collapse_ws(candidate)
    if not text:
        return False

    explicit_names = _explicit_guide_names(row)
    if explicit_names and any(_names_overlap(text, name) for name in explicit_names):
        return True

    haystack = _occurrence_text_haystack(row)
    if not haystack:
        return False

    anchor = _candidate_anchor(text).lower()
    if anchor and anchor in haystack:
        return True

    tokens = _candidate_tokens(text)
    if not tokens:
        return False
    if len(tokens) == 1:
        return tokens[0].lower() in haystack
    return tokens[-1].lower() in haystack


def guide_line_is_publishable(candidate: str | None, row: Mapping[str, Any]) -> bool:
    text = collapse_ws(candidate)
    if not text:
        return False
    source_kind = _source_kind(row)
    if not source_kind or source_kind in PERSONAL_SOURCE_KINDS:
        return True
    return guide_line_has_occurrence_support(text, row)
