# INC-2026-04-20 Club Znakomstv Duplicate Event Cards

Status: open
Severity: sev2
Service: Smart Event Update / production event cards
Opened: 2026-04-20
Closed: `—`
Owners: Codex, product operator
Related incidents: `—`
Related docs: `docs/features/smart-event-update/README.md`, `docs/features/linked-events/README.md`, `docs/operations/incident-management.md`, `docs/operations/release-governance.md`

## Summary

На production один и тот же слот шоу `Клуб знакомств` на `2026-04-22 20:00` в `Форма пицца-бар` размножился в несколько активных карточек с разными `event_id` и Telegraph URL. Отдельно появился ложный `19:00` sibling, потому что один импорт взял `сбор гостей 19:00` как `event.time`, хотя в тексте того же источника явно было `начало 20:00`.

## User / Business Impact

- Пользователь видел 3-4 карточки вместо одной и не мог понять, какая ссылка каноническая.
- Month/day pages и подборки рисковали публиковать один и тот же анонс несколько раз.
- `linked_events` дополнительно маскировал проблему, показывая дубли как `Другие даты`, хотя это были не другие даты, а duplicate rows одного слота.

## Detection

- Incident поднят по пользовательскому репорту `2026-04-20`.
- Production evidence подтверждён прямым SQL-запросом к `/data/db.sqlite` на Fly.
- Observability gap: дубли обнаружились только user-visible способом; автоматического guardrail или алерта на duplicate cluster не было.

## Timeline

- `2026-04-16 14:05 UTC`: создан канонический `event_id=3957` (`20:00`, `https://telegra.ph/SHOU-KLUB-ZNAKOMSTV-04-16`) из `https://t.me/locostandup/3321`.
- `2026-04-18 23:27 UTC`: создан ложный sibling `event_id=4042` (`19:00`, `https://telegra.ph/Komedijnoe-shou-Klub-znakomstv-04-18`) из `https://t.me/locostandup/3334`.
- `2026-04-19 04:17 UTC`: создан duplicate `event_id=4043` (`20:00`, `https://telegra.ph/Klub-znakomstv-komedijnoe-shou-04-19`) из `https://vk.com/wall-214027639_11110`.
- `2026-04-20 04:19 UTC`: создан duplicate `event_id=4051` (`20:00`, `https://telegra.ph/Klub-znakomstv-komedijnoe-shou-04-20`) из `https://vk.com/wall-219175543_156`.
- `2026-04-20`: пользователь сообщил о duplicate cards; investigation started.

## Root Cause

1. Deterministic duplicate guards сходились на `same date + venue + title`, но не имели отдельного safe-path для nearly-identical copy posts, если разные каналы несли разные ticket URLs (`shortlink` vs generic site / button-only CTA).
2. Doors/start кейс (`сбор гостей 19:00, начало 20:00`) не мостился без ticket anchor, поэтому импорт с `19:00` создавал второй row вместо merge в уже существующее `20:00` событие.
3. После создания duplicate rows `linked_events` честно связал их как siblings, но это не устраняло duplicate cluster и делало symptom менее очевидным для операторов.

## Contributing Factors

- VK/TG copy posts были почти идентичны по `source_text`, но differed by ticket-link surface and wording.
- В одном из импортов public title был слабее (`Клуб Знакомств`), поэтому только strict exact-title guard было недостаточно.
- Не было автоматического incident check на `same date + same venue + near-identical source_text` duplicate clusters.

## Automation Contract

### Treat as regression guard when

- меняется logic в `smart_event_update.py` вокруг duplicate matching / shortlist rescue / cross-source repost merge;
- меняется VK/TG intake/extraction времени (`doors` vs `start`);
- меняется rebuild path для event cards и month/day pages;
- расследуются user-visible duplicate cards на production.

### Affected surfaces

- `smart_event_update.py`
- `vk_intake.py`
- `linked_events.py`
- production SQLite rows: `event`, `event_source`, `event_source_fact`, `eventposter`
- month/day page rebuild path (`telegraph_build`, month pages)

### Mandatory checks before closure or deploy

- unit/regression tests:
  - duplicate same-day copy post with different ticket URL must merge;
  - `doors/start` same-text duplicate must merge into one event instead of creating `19:00` sibling.
- production evidence:
  - query duplicate cluster for `2026-04-22` + `Форма пицца-бар` + `Клуб знакомств` and confirm only one active row remains.
- release discipline:
  - fix commit reachable from `origin/main`;
  - deployed SHA recorded;
  - month/day surfaces rebuilt or otherwise confirmed clean.

### Required evidence

- test output for targeted regression suite;
- production SQL output before/after cleanup;
- deployed SHA and branch;
- confirmation that the user-visible pages now expose only one active card.

## Immediate Mitigation

- Investigate all active prod rows in the cluster and identify canonical survivor (`event_id=3957`).
- Remove duplicate prod rows after reattaching useful source/fact evidence to the canonical event and rebuild affected pages.

## Corrective Actions

- Add deterministic same-day copy-post merge guard based on near-identical `source_text` + same venue, even when ticket links differ.
- Add deterministic `doors/start` bridge without ticket-anchor requirement for clearly identical copy posts.
- Add regression tests with the exact `Клуб знакомств` incident shape.

## Follow-up Actions

- [ ] Decide whether to add an operator-facing duplicate-cluster report for `same date + venue + near-identical source_text`.
- [ ] Audit whether existing duplicate rows from older imports need one-time cleanup beyond this incident.

## Release And Closure Evidence

- deployed SHA: `—`
- deploy path: `—`
- regression checks: `—`
- post-deploy verification: `—`

## Prevention

- Duplicate matching now treats near-identical repost text as a first-class anchor instead of over-relying on ticket URL parity.
- `doors/start` copy-posts are bridged explicitly, so `сбор гостей 19:00` cannot silently fork a second event when `начало 20:00` already exists for the same slot.
