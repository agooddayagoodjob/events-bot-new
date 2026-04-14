# INC-2026-04-14 Daily Delay + VK Auto Queue Lock Storm

Status: monitoring
Severity: sev1
Service: Fly production bot scheduler (`/daily`, `/start`, `vk_auto_import`)
Opened: 2026-04-14
Closed: `—`
Owners: runtime / scheduler / VK queue
Related incidents: `—`
Related docs: `docs/operations/incident-management.md`, `docs/operations/cron.md`, `docs/features/vk-auto-queue/README.md`, `docs/operations/release-governance.md`

## Summary

Утром `2026-04-14` production bot вошёл в системную деградацию: ежедневный анонс на `08:00` local вышел с сильной задержкой, `/start` не отвечал до восстановления процесса, а `vk_auto_import` сначала крутил проблемный VK post через repeated rate-limit defer без terminal cutoff, а затем продолжал поднимать crash-interrupted rows после частых рестартов машины.

## User / Business Impact

- Пользовательский `/start` в production не отвечал примерно до восстановления процесса после рестарта Fly.
- Ежедневный анонс, ожидавшийся на `2026-04-14 08:00 Europe/Kaliningrad`, вышел заметно позже.
- Операторский VK auto-import продолжал возвращаться к проблемному post `https://vk.com/wall-26560795_12227`, хотя после нескольких безуспешных попыток он должен был выйти из активной очереди.
- В течение дня production инстанс многократно перезапускался во время тяжёлых VK auto-import rows, что создавало впечатление “бот нездоров” даже вне конкретного окна `08:00`.
- Runtime logs для poster upload вводили в заблуждение legacy-меткой `CATBOX ... msg=storage_primary`, хотя фактически срабатывал managed storage (Yandex), а не Catbox fallback.

## Detection

- Инцидент был замечен по факту пользовательского репорта: “в `08:00` не вышел ежедневный анонс”, “бот не отвечает на `/start`”.
- Fly runtime logs показали серию `sqlite3.OperationalError: database is locked` в scheduler recovery / `ops_run`.
- Дополнительные runtime logs подтвердили поздний `BOOT_OK`, delayed `/daily` recovery и повторные LLM `429` для VK auto-import.
- Monitoring gap: не было отдельного раннего сигнала, что transient SQLite lock storm уже начал срывать scheduler recovery до customer-visible деградации.

## Timeline

- `2026-04-14 05:33:37 UTC` (`07:33:37 Europe/Kaliningrad`): в production логах появляются `sqlite3.OperationalError: database is locked` при `ops_run.start_ops_run`.
- `2026-04-14 05:33:47 UTC` (`07:33:47 Europe/Kaliningrad`): `vk_review.release_stale_locks()` падает с тем же `database is locked`.
- `2026-04-14 05:34:11 UTC` (`07:34:11 Europe/Kaliningrad`): `daily_scheduler` стартует уже на деградированном процессе.
- `2026-04-14 05:43:16 UTC` и `05:44:27 UTC` (`07:43:16` и `07:44:27 Europe/Kaliningrad`): логи `daily_scheduler` показывают сдвинутый `now=07:36:00`, что подтверждает сильный loop lag относительно реального времени.
- `2026-04-14 06:08:17-06:08:28 UTC` (`08:08:17-08:08:28 Europe/Kaliningrad`): Fly отправляет `SIGINT`/`SIGTERM`, VM завершается и поднимается заново.
- `2026-04-14 ~06:12 UTC` (`~08:12 Europe/Kaliningrad`): бот снова materializes startup/`BOOT_OK`; пользовательский `/start` начинает отвечать.
- `2026-04-14 08:17 Europe/Kaliningrad`: admin chat фиксирует `Rate limit exceeded: tpm` при разборе VK post `1/3`.
- `2026-04-14 08:19 Europe/Kaliningrad`: очередь снова доходит до `https://vk.com/wall-26560795_12227`, подтверждая отсутствие terminal cutoff на repeated rate-limit defer.
- `2026-04-14` после восстановления: ежедневный анонс выходит, но уже с заметной задержкой относительно целевого слота `08:00 Europe/Kaliningrad`.

## Root Cause

1. Scheduler recovery path опирался на SQLite write/commit без retry в `ops_run` bootstrap/cleanup и `vk_review.release_stale_locks`/related helpers. При transient single-writer contention это приводило к каскаду `database is locked` и замедляло/ломало materialization служебных run/queue state changes.
2. После деградации процесса Fly перезапустил VM; пока бот не прошёл повторный startup, production `/start` фактически был недоступен.
3. В daily build shortlink enrichment упирался в VK `utils.getShortLink` с ошибкой `code=8 / Application is blocked` на user token path, но этот путь не считался явным fallback trigger на следующий actor/token.
4. VK auto queue сохраняла provider-side `429` как defer без terminal attempt cap, поэтому один и тот же проблемный post мог возвращаться в следующие batch бесконечно.
5. Даже после ввода rate-limit terminal cap queue оставалась уязвима к hard restarts: на маленькой Fly машине (`768 MB`) тяжёлые VK rows держали несколько больших афиш в памяти, а N+1 prefetch/reserve path заранее lock-ил следующий row. После crash startup recovery честно возвращал такие `locked` rows в `pending`, из-за чего уже проблемные posts снова всплывали в очереди.

## Contributing Factors

- SQLite в этом deployment остаётся single-writer хранилищем для scheduler/runtime metadata.
- `vk_auto_import` recovery и `/daily` выполнялись рядом по времени, поэтому degraded loop быстрее стал user-visible.
- Для problematic post не было persisted max-attempt contract; defer защищал от tight loop внутри одного batch, но не от бесконечного resurfacing между batch.
- Production машина работала на `shared-cpu-1x / 768 MB`, что оставляло мало запаса для VK rows с несколькими 3-4MB афишами, OCR и upload pipeline.
- Legacy upload logs всё ещё называли общий pipeline “CATBOX”, хотя Yandex уже был primary backend; это усложняло первичную диагностику и создавало ложный боковой инцидент.

## Automation Contract

### Treat as regression guard when

- Меняются `ops_run` write paths, startup recovery или scheduler bootstrap/cleanup.
- Меняется поведение `vk_review.release_stale_locks` / `release_due_deferred` / `release_all_locks`.
- Меняется rate-limit policy у `vk_auto_import`.
- Меняется VK token fallback logic в `_vk_api`.
- Меняются `/daily` scheduling or shortlink-enrichment paths.

### Affected surfaces

- `ops_run.py`
- `vk_review.py`
- `vk_auto_queue.py`
- `db.py` / `models.py` (`vk_inbox.attempts`)
- `main.py::_vk_api`
- Fly production runtime, `/healthz`, `/start`, `daily_scheduler`

### Mandatory checks before closure or deploy

- `pytest -q tests/test_vk_review.py tests/test_vk_auto_queue_import.py tests/test_vk_actor.py tests/test_ops_run.py tests/test_vk_auto_queue_rate_limit.py tests/test_vk_review_lock_retry.py`
- Verify clean hotfix worktree and production-safe release path per `docs/operations/release-governance.md`.
- Confirm deployed runtime serves `/healthz` and Fly machine is healthy after deploy.
- Inspect production logs for absence of fresh `database is locked` storms in scheduler recovery and for successful startup materialization.

### Required evidence

- Target deployed commit/SHA and branch path used for deploy.
- Test run evidence for the regression suite above.
- Post-deploy `/healthz` or equivalent runtime-health output.
- Fly status/log evidence that the machine is running and serving requests after deploy.

## Immediate Mitigation

- Runtime eventually recovered after Fly restart, which restored `/start` and allowed the delayed daily announcement to finish.
- Hotfix isolated in a clean `hotfix` worktree from `origin/main` to avoid deploying unrelated local dirtiness.

## Corrective Actions

- Added retry-on-`database is locked` to `ops_run` bootstrap/finish/startup-cleanup writes.
- Added the same transient lock retry path to `vk_review.release_stale_locks`, `release_due_deferred`, and `release_all_locks`.
- Added persisted `vk_inbox.attempts` and terminal rate-limit policy: after `VK_AUTO_IMPORT_RATE_LIMIT_MAX_DEFERS` (default `3`) the row becomes `failed`.
- Taught `_vk_api` to treat VK `code=8 / Application is blocked` as a no-retry-for-current-actor condition and continue with the next available token path.
- Startup recovery for `vk_inbox.status='locked'` now distinguishes `auto:*` rows: each crash-recovery unlock increments `attempts`, and after `VK_AUTO_IMPORT_RECOVERY_MAX_ATTEMPTS` (default/fly prod `3`) the row becomes terminal `failed` instead of resurfacing forever.
- `vk_auto_import` now defaults to conservative row-by-row processing (`VK_AUTO_IMPORT_PREFETCH=0`) and production explicitly keeps that mode to avoid lock-ahead on the next row.
- Auto-import live VK fetch is capped by `VK_AUTO_IMPORT_MAX_PHOTOS=4`, reducing RAM spikes from multi-poster posts without changing other upload paths.
- Production Fly machine memory was increased from `768 MB` to `1024 MB` as an operational mitigation.
- Managed poster-upload logs were renamed from legacy `CATBOX ...` summaries to `poster_upload ...` / `storage_msg=...`, so `storage_primary` is now clearly diagnostic evidence of Yandex/Supabase success rather than Catbox activity.

## Follow-up Actions

- [ ] Add explicit alerting on repeated `database is locked` bursts in production runtime logs.
- [ ] Review whether the morning scheduler windows still need more spacing between `vk_auto_import` recovery and the `08:00` daily slot.
- [ ] Decide whether `VK_AUTO_IMPORT_PREFETCH=1` should ever return as a production override, or remain an explicitly opt-in throughput mode only.

## Release And Closure Evidence

- deployed SHA: `8416655584e49c1507376ab114aba30438c5426e`
- deploy path: clean `hotfix` worktree from `origin/main`
- regression checks:
  - previous incident hotfix suite: `pytest -q tests/test_vk_review.py tests/test_vk_auto_queue_import.py tests/test_vk_actor.py tests/test_ops_run.py tests/test_vk_auto_queue_rate_limit.py tests/test_vk_review_lock_retry.py` → `55 passed`
  - current follow-up suite: `pytest -q tests/test_vk_auto_queue_import.py tests/test_vk_auto_queue_rate_limit.py tests/test_vk_review.py tests/test_upload_images.py tests/test_poster_media.py` → `57 passed`
- post-deploy verification:
  - `flyctl status -a events-bot-new-wngqia` → machine `48e42d5b714228`, version `947`, state `started`
  - `flyctl scale show -a events-bot-new-wngqia` → `shared-cpu-1x / 1024 MB`
  - `GET https://events-bot-new-wngqia.fly.dev/healthz` after soak → `{"ok":true,"ready":true,"boot_age_sec":93.5,...,"db":"ok","issues":[]}`
  - post-deploy DB probe on `/data/db.sqlite` → `locked=0`, `ops_run(status='running')=0`, problematic rows `wall-26560795_12227` and `wall-195754292_11027` are `failed, attempts=3`
  - fresh Fly logs after deploy show `BOOT_OK`, recurring `daily_scheduler: done`, and no new `database is locked` entries in the post-deploy tail

## Prevention

- Production queue rows now carry a persisted rate-limit attempt counter, so one permanently problematic VK post cannot recycle forever.
- Scheduler/runtime metadata writes now tolerate short SQLite lock spikes instead of immediately degrading run bootstrap/recovery.
- Daily shortlink enrichment now has an explicit fallback path for blocked VK actor tokens.
- Crash-recovery no longer blindly revives the same auto-import row forever after hard restarts, and the queue no longer reserves N+1 rows by default on production.
- Upload diagnostics now reflect the real storage backend, reducing false-positive operator incidents around Catbox.
