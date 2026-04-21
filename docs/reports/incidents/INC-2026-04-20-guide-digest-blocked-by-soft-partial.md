# INC-2026-04-20-guide-digest-blocked-by-soft-partial Guide digest was skipped after a soft-partial monitor run

Status: open
Severity: sev2
Service: guide excursions scheduled monitoring + digest publish
Opened: 2026-04-20
Closed: —
Owners: Codex / events-bot
Related incidents: `INC-2026-04-16-prod-disk-pressure-runtime-logs`
Related docs: `docs/features/guide-excursions-monitoring/README.md`, `docs/operations/runtime-logs.md`, `docs/operations/release-governance.md`

## Summary

On April 20, 2026 the scheduled evening guide-monitoring full slot (`20:10 Europe/Kaliningrad`) completed with materialized occurrence changes, but the digest was never published. The proximate cause was not a total Kaggle/import failure: one `Gemma 4` screen timeout on a single source turned the run into `partial`, and the scheduler treated any non-empty `result.errors` as a hard stop for digest auto-publish.

## User / Business Impact

- The daily excursions digest did not appear in the public target channels on April 20, 2026.
- At least one new digest-eligible occurrence that should have been considered for that cycle remained unpublished (`guide_occurrence.id=132` on the prod snapshot inspected April 21).
- Operators saw the monitoring run as “completed with errors”, but the system did not perform a compensating digest publish attempt.

## Detection

- User report: “Дайджест экскурсий вчера не вышел”.
- Prod evidence:
  - `ops_run.id=765` shows `kind='guide_monitoring'`, `status='partial'`, `trigger='scheduled'`, started `2026-04-20 18:10:00 UTC`, finished `2026-04-20 18:24:43 UTC`.
  - `/data/guide_monitoring_results/guide-excursions-d299a50d73c0/guide_excursions_results.json` contains `partial=true`.
  - `guide_digest_issue` has no rows created on or after `2026-04-20 00:00:00`, proving auto-publish never started.
- Observability gap:
  - prod still has `/data/runtime_logs`, but the latest rotated file is from `2026-04-16`;
  - current prod env shows `ENABLE_RUNTIME_FILE_LOGGING=0`, so there were no fresh file logs for the April 20 incident.

## Timeline

- `2026-04-20 20:10 Europe/Kaliningrad` — scheduled guide `full` slot starts (`run_id=d299a50d73c0`, `ops_run_id=765`).
- `2026-04-20 20:12-20:22 Europe/Kaliningrad` — Kaggle guide monitor processes 12 sources and writes result bundle under `/data/guide_monitoring_results/guide-excursions-d299a50d73c0/`.
- `2026-04-20 20:22 Europe/Kaliningrad` — source `@vkaliningrade`, post `message_id=4661`, records `llm_deferred_timeout`; result bundle flips to `partial=true`.
- `2026-04-20 20:24 Europe/Kaliningrad` — server import finishes with `status='partial'` and synthetic error `kaggle result marked as partial`; operator sees “Мониторинг экскурсий завершён с ошибками”.
- `2026-04-20 20:24 Europe/Kaliningrad` — scheduler returns early because `result.errors` is non-empty; scheduled digest publish is skipped entirely.
- `2026-04-21 09:06 Europe/Kaliningrad` — a separate light run (`run_id=bfb07004c5e4`) completes successfully, confirming the attached Kaggle JSON/logs were from the next day and not from the failed April 20 full slot.

## Root Cause

1. `Gemma 4` timed out on one mixed multi-announce schedule post (`@vkaliningrade`, `message_id=4661`), producing `llm_deferred_timeout`.
2. The Kaggle result contract marks the whole run `partial=true` whenever any source is non-`ok`, even if the rest of the run imported useful occurrences successfully.
3. The scheduled/recovery digest auto-publish gate treated any non-empty `GuideMonitorResult.errors` as publish-blocking, so the single synthetic partial marker cancelled the entire daily digest.

## Contributing Factors

- The timed-out post was a dense schedule card with multiple dated excursions, so the LLM timeout happened on exactly the kind of post most likely to affect digest coverage.
- Runtime file-log mirroring was disabled in prod, so the rotated `/data/runtime_logs` archive could not provide same-day post-factum traces.
- The scheduler did not distinguish “soft partial with imported data” from “hard failure before digest candidates exist”.

## Automation Contract

### Treat as regression guard when

- changing `guide_excursions/service.py` monitor/import status handling;
- changing `scheduling.py` guide scheduled publish flow;
- changing recovery logic for guide monitor jobs;
- changing the Kaggle result contract or what counts as `partial` for guide runs.

### Affected surfaces

- `guide_excursions/service.py`
- `scheduling.py`
- guide monitor recovery job path
- Kaggle result bundle contract (`guide_excursions_results.json.partial`)
- prod sqlite tables `ops_run`, `guide_occurrence`, `guide_digest_issue`
- operator-facing scheduler notifications

### Mandatory checks before closure or deploy

- targeted pytest for scheduled guide digest auto-publish on:
  - no items;
  - soft partial (`kaggle result marked as partial`);
  - hard monitor error.
- verify recovery path uses the same soft-partial gating rule.
- confirm docs/changelog are updated.
- for prod delivery: prove the missed daily digest was compensated by rerun/catch-up if still relevant.

### Required evidence

- test output for the targeted pytest file(s);
- git SHA containing the fix;
- prod evidence that the fix is reachable from `origin/main`;
- post-deploy proof that a soft-partial guide run no longer suppresses digest publish.

## Immediate Mitigation

- Investigated prod state directly on Fly machine `48e42d5b714228`.
- Verified the incident run via `ops_run.id=765` and the persisted result bundle for `run_id=d299a50d73c0`.
- Confirmed the file-log archive could not help because fresh runtime file logging was disabled in production.

## Corrective Actions

- Add a shared soft-partial classifier for guide monitor results.
- Allow scheduled and recovery digest auto-publish to proceed when the only monitor error is `kaggle result marked as partial`.
- Keep hard failures publish-blocking.
- Add targeted scheduler tests and document the contract in the guide-monitoring README.

## Follow-up Actions

- [ ] Verify after deploy whether the missed April 20 digest needs a manual/catch-up publish, or document why the window is no longer actionable.
- [ ] Add a targeted live smoke for a soft-partial guide run once a safe canary input is available.
- [ ] Decide whether `llm_deferred_timeout` on multi-announce schedule cards needs a dedicated prompt/runtime hardening task for `Gemma 4`.

## Release And Closure Evidence

- deployed SHA: —
- deploy path: —
- regression checks: pending
- post-deploy verification: pending

## Prevention

- Scheduler and recovery paths must distinguish soft partials from genuinely publish-blocking failures.
- Operator-facing warning surfaces should remain noisy about partial runs, but public digest delivery must not be skipped when usable candidates were already materialized.
