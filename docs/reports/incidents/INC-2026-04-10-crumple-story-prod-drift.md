# INC-2026-04-10 CrumpleVideo Story Prod Drift

## Summary

`/v` render завершился в `Kaggle`, но production story publish не выполнился и в логах kernel не было ни preflight, ни publish-следов. Разбор показал не runtime-сбой story helper, а release drift: на проде оказалась линия без активного story-layer и с `VIDEO_ANNOUNCE_STORY_ENABLED=0`.

## Impact

- production `/v` деградировал до mp4-only delivery;
- оператор видел длинный render и успешный финальный mp4, но не получал Telegram stories;
- отсутствие story-логов затрудняло локализацию причины и маскировало проблему как “внутренний сбой Kaggle”.

## Detection

- пользователь зафиксировал, что run завершился, а stories не появились;
- kernel log заканчивался на `Pipeline completed!` без `Story preflight status` / `Story publish status`;
- проверка продового env на Fly показала `VIDEO_ANNOUNCE_STORY_ENABLED=0`.

## Timeline

- `2026-04-10`: пользователь сообщил, что очередной длинный CrumpleVideo run завершился без stories.
- Разбор продового env и кода показал drift между текущим продом и канонической `/v` story-line.
- В канонической prod-line подтверждено наличие полного story-path: `story_publish.json`, encrypted auth datasets, preflight, publish, `story_publish_report.json`.
- В ответ добавлен fail-closed prod guard `VIDEO_ANNOUNCE_STORY_REQUIRED=1`, чтобы `/healthz` сразу краснел при повторном silent downgrade.

## Root Cause

1. Прод был выкачен не из канонической линии CrumpleVideo story rollout.
2. В активном продовом env story-path был фактически выключен через `VIDEO_ANNOUNCE_STORY_ENABLED=0`.
3. Из-за этого Kaggle notebook не получал `story_publish.json` и не заходил в story preflight/publish branch, поэтому kernel log выглядел как “обычный render без упоминаний о stories”.

## Corrective Actions

- вернуть прод на интегрированную линию, где story-layer присутствует целиком;
- включить в prod `VIDEO_ANNOUNCE_STORY_ENABLED=1`;
- добавить `VIDEO_ANNOUNCE_STORY_REQUIRED=1`, чтобы `/healthz` fail-closed сигнализировал об отключённом или явно сломанном story-path;
- держать incident-record как regression-check для всех будущих `/v` deploy и веточных reconciliations.

## Prevention

- перед deploy `/v` проверять не только render-path, но и story-path requirements из `docs/features/crumple-video/README.md`;
- использовать clean worktree на канонической интегрированной базе, а не случайную stale branch;
- считать silent возврат в mp4-only режим production incident'ом, а не допустимым fallback.
