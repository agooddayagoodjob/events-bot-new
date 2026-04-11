from __future__ import annotations

from pathlib import Path
import re
import textwrap
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_ROOT = PROJECT_ROOT / "artifacts" / "codex"


STAGE_SPECS: list[dict[str, Any]] = [
    {
        "stage_id": "baseline_fact_extractor.v1",
        "focus": "Lift compact grounded raw facts across all scoped sources before specialized family passes.",
        "default_bucket": "support_context",
    },
    {
        "stage_id": "facts.extract_subject.v1",
        "focus": "Lift the main event-facing identity: what kind of attendable event this is and what it is about.",
        "default_bucket": "event_core",
    },
    {
        "stage_id": "facts.extract_card.v1",
        "focus": "Lift card-level defining facts: repertoire frame, named program identity, format, institutional context.",
        "default_bucket": "event_core",
    },
    {
        "stage_id": "facts.extract_agenda.v1",
        "focus": "Lift explicit program and repertoire items exactly as listed in the sources.",
        "default_bucket": "program_list",
    },
    {
        "stage_id": "facts.extract_support.v1",
        "focus": "Lift supporting context and attendance-relevant notices that are explicitly stated by the sources.",
        "default_bucket": "support_context",
    },
    {
        "stage_id": "facts.extract_profiles.v1",
        "focus": "Lift maker / profile / creative-person detail that adds real specificity beyond the title.",
        "default_bucket": "people_and_roles",
    },
    {
        "stage_id": "facts.extract_performer.v1",
        "focus": "Lift named performers, soloists, conductors, directors, and their roles when the role is explicit.",
        "default_bucket": "people_and_roles",
    },
    {
        "stage_id": "facts.extract_participation.v1",
        "focus": "Lift ensembles, troupes, orchestras, choirs, guest formations, and collective participation facts.",
        "default_bucket": "people_and_roles",
    },
    {
        "stage_id": "facts.extract_stage.tightened.v1",
        "focus": "Lift stage/presentation details that materially affect attendance or staging.",
        "default_bucket": "support_context",
    },
    {
        "stage_id": "facts.extract_theme.challenger.v1",
        "focus": "Lift historical, thematic, or conceptual context that is explicitly grounded in the source.",
        "default_bucket": "support_context",
    },
]


def _stage_suffix(stage_id: str) -> str:
    suffix = stage_id.split(".")[-2] if stage_id.endswith(".v1") else stage_id
    return suffix.replace(".", "_")


def _build_run_artifact_paths(date_tag: str, run_label: str) -> tuple[str, Path, Path, Path]:
    run_slug = f"smart_update_lollipop_facts_extract_family_{run_label}_{date_tag}"
    trace_root = ARTIFACTS_ROOT / run_slug
    out_json_path = ARTIFACTS_ROOT / f"{run_slug}.json"
    report_label = run_label.split("_batch", 1)[0]
    report_slug = (
        "smart-update-gemma-event-copy-v2-16-2-lollipop-family-facts-extract-lab-"
        f"{report_label.split('v2_16_2_', 1)[-1].replace('_', '-')}-{date_tag}.md"
    )
    out_report_path = PROJECT_ROOT / "docs" / "reports" / report_slug
    return run_slug, trace_root, out_json_path, out_report_path


def _event_type_label(event_type: str | None) -> str:
    return (event_type or "").strip().lower()


def _build_prompt(
    *,
    stage: dict[str, Any],
    title: str,
    event_type: str,
    source_excerpt: str,
    raw_facts: list[str],
    gemma4: bool = False,
) -> str:
    stage_id = str(stage["stage_id"])
    rules: list[str] = [
        f"ROLE: You do one small step: {stage_id}.",
        f"FOCUS: {stage['focus']}",
        "Return only JSON.",
        "Do not write public prose.",
        "Keep facts compact, literal, and grounded in the source excerpt.",
        "Prefer source-shaped natural Russian over abstract report formulas when both preserve the same fact.",
        "If a fact is not explicitly supported by the excerpt or the supplied raw facts, omit it.",
        "SOURCE-LOCAL UNIQUENESS OBLIGATION: treat this excerpt as one source block that may carry facts no other source carries.",
        "If this source block carries a unique grounded fact, preserve that fact instead of repeating only the safest cross-source summary.",
        "When this source contributes a meaningful atmosphere, rarity, or staging hook, emit that source-local fact as a first-class record rather than collapsing it into a generic overview.",
        "Use literal_items only for explicit program or repertoire lists that should survive verbatim in final copy.",
        "Do not put event title, dates, person names, venue names, scarcity markers, or ensemble categories into literal_items.",
        "LITERAL TITLE FIDELITY: when extracting names of works, preserve exact source spelling with no declension, abbreviation, or normalization.",
        "FACT TEXT VOICE: preserve event-facing action wording from the source like `звучат`, `собраны`, `идет`, `показывают`; do not auto-rewrite into `посвящен`, `характеризуется`, `наполнена`, or `представлены`.",
    ]
    if gemma4:
        rules.extend(
            [
                "Use raw JSON only, no markdown fences.",
                "If a meaningful source fact does not fit this stage, omit it rather than paraphrasing it into another bucket.",
            ]
        )

    etype = _event_type_label(event_type)
    if stage_id in {"facts.extract_subject.v1", "facts.extract_card.v1"}:
        rules.append(
            "If the source excerpt is short promotional text, still extract the strongest stage-local fact you can from the available evidence."
        )
        rules.append(
            "Prefer event-facing action wording like `звучат`, `собраны`, `идет`, `показывают`, if grounded, instead of flattening everything into `посвящен`."
        )
    if stage_id == "facts.extract_card.v1" and etype == "выставка":
        rules.extend(
            [
                "Для выставок считай curator/history/collection-detail facts релевантными.",
                "Для выставки card-facts могут включать название экспозиции, размер коллекции, эпоху и институциональную связку.",
            ]
        )
    if stage_id == "facts.extract_profiles.v1" and etype == "выставка":
        rules.extend(
            [
                "Если персон нет, stage всё равно релевантен: можно сохранять maker/designer/item-level detail.",
                "Не обрезай lines вроде `за каждым шедевром стоит художник-дизайнер...`, если это grounded profile/context detail.",
            ]
        )
    if stage_id == "facts.extract_support.v1" and etype == "выставка":
        rules.extend(
            [
                "Не делай выводы о широкой аудитории, возрасте или доступности из friendly title или marketing tone.",
                "Для выставок support-stage: не выводи широкую аудиторию, возрастные ограничения или accessibility без явного source evidence.",
            ]
        )
    if stage_id == "facts.extract_support.v1":
        rules.extend(
            [
                "Keep explicit scarcity/frequency/rarity facts when they affect attendance value.",
                "Examples that should survive when grounded: `раз в сезоне`, `два вечера подряд`, `редкий гость в афише`, `долгожданный гость`.",
                "Do not drop official-source rarity/anticipation lines just because they sound promotional if they materially explain why attending this event is special.",
                "If the source explicitly frames the event as rare, infrequent, long-awaited, or available only on a narrow cadence, keep that as a fact.",
                "Rarity/scarcity/anticipation signals are first-class attendance facts, not promo filler.",
            ]
        )
    if stage_id in {"baseline_fact_extractor.v1", "facts.extract_theme.challenger.v1"}:
        rules.extend(
            [
                "Official-source atmosphere or emotional framing can be extracted when it characterises the event experience rather than giving generic praise.",
                "Examples that may survive when grounded: `романтические истории`, `истории о любви, надежде, одиночестве, радости, удивлении`, `наполненный легкой, волшебной музыкой`.",
                "Preserve such mood/context facts close to source wording when possible: `романтические истории из оперетт Кальмана`, `легкая волшебная музыка`, `атмосфера интриги и игры` are better than dry rewrites with `характеризуется`, `представлены`, or `наполнена`.",
                "Official organiser atmosphere lines are first-class event-characterisation, not promo filler, when they describe what this evening feels like.",
                "Do not import audience reactions or third-party reviews into this stage.",
            ]
        )
    if stage_id == "facts.extract_participation.v1":
        rules.extend(
            [
                "Collective formations like 'солисты, оркестр, хор и балет театра' count as participation even without individual names.",
                "If the source names ensemble categories with an institutional anchor, extract them as participation.",
            ]
        )
    if stage_id == "facts.extract_performer.v1" and etype == "выставка":
        rules.extend(
            [
                "Имя без роли, статуса, attribution или credibility-line не возвращай.",
                "Для выставок performer-stage обычно пустой.",
            ]
        )

    schema = {
        "facts": [
            {
                "text": "string",
                "evidence": "short grounded quote or source paraphrase",
                "source_refs": ["source_id"],
                "literal_items": ["string"],
                "strength": "high|medium|low",
            }
        ]
    }
    return textwrap.dedent(
        f"""
        {'SYSTEM' if gemma4 else 'PROMPT'}
        {chr(10).join('- ' + item for item in rules)}

        TITLE: {title}
        EVENT_TYPE: {event_type}

        RAW_FACTS:
        {chr(10).join(f"- {item}" for item in raw_facts) if raw_facts else "- (none)"}

        SOURCE_EXCERPT:
        {source_excerpt}

        OUTPUT_SCHEMA:
        {schema}
        """
    ).strip()


def normalize_stage_items(
    *,
    stage: dict[str, Any],
    payload: dict[str, Any],
    record_prefix: str,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for idx, raw_item in enumerate(list(payload.get("facts") or []), start=1):
        if not isinstance(raw_item, dict):
            continue
        text = re.sub(r"\s+", " ", str(raw_item.get("text") or "")).strip()
        if not text:
            continue
        source_refs = [
            str(item).strip()
            for item in list(raw_item.get("source_refs") or [])
            if str(item).strip()
        ]
        items.append(
            {
                "record_id": f"{record_prefix}{idx:02d}",
                "stage_id": str(stage["stage_id"]),
                "bucket_hint": str(stage.get("default_bucket") or "support_context"),
                "text": text,
                "evidence": re.sub(r"\s+", " ", str(raw_item.get("evidence") or "")).strip(),
                "source_refs": source_refs,
                "literal_items": [
                    re.sub(r"\s+", " ", str(item or "")).strip()
                    for item in list(raw_item.get("literal_items") or [])
                    if re.sub(r"\s+", " ", str(item or "")).strip()
                ],
                "strength": str(raw_item.get("strength") or "medium").strip() or "medium",
            }
        )
    return items
