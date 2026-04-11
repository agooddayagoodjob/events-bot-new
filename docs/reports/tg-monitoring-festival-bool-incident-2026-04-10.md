# Telegram Monitoring Festival Bool Incident 2026-04-10

Статус: closed with guardrails added

## Что произошло

10 апреля 2026 recovery-import `tg_monitoring` завершился как `partial`, хотя `telegram_results.json` был успешно скачан и большая часть событий импортировалась.

В `ops_run` и runtime-логах зафиксированы одинаковые ошибки для нескольких сообщений:

- `kulturnaya_chaika/7525: 'bool' object has no attribute 'strip'`
- `meowafisha/7100: 'bool' object has no attribute 'strip'`
- `festkantata/1426: 'bool' object has no attribute 'strip'`

Проблема проявилась на server-import этапе и могла повторяться в ежедневном scheduled `tg_monitoring`, если Kaggle снова вернёт `festival` как boolean.

## Корневая причина

На границе данных не было достаточно строгой нормализации optional text fields:

- Telegram importer прокидывал `event_data["festival"]` в `EventCandidate` без приведения типа;
- diagnostic helper `_clip_title(...)` в `smart_event_update` безусловно вызывал `.strip()` и падал на boolean.

Итог: один malformed payload field не ломал весь мониторинг, но переводил run в `partial` и терял часть импортов.

## Почему это плохо

- scheduled `tg_monitoring` может формально запускаться, но фактически каждый день оставаться с частично неимпортированными постами;
- recovery path оказывается ненадёжным именно в момент, когда он должен дозабирать пропущенный результат;
- один upstream schema drift превращается в повторяемый incident, если нет fail-safe на серверной стороне.

## Что изменено

### Runtime guard

- `source_parsing/telegram/handlers.py`: `festival` теперь нормализуется как optional text; boolean и `None` отбрасываются в `None`.
- `smart_event_update.py`: `_clip_title(...)` больше не падает на `bool`/non-string diagnostic values и возвращает пустую строку для boolean.

### Regression tests

- Добавлен тест на `process_telegram_results(...)`, который подтверждает: `festival=true` не валит импорт и попадает в `EventCandidate.festival` как `None`.
- Добавлен unit-test на `_clip_title(True/False)`.

### Каноника

- `docs/features/telegram-monitoring/README.md` теперь явно требует, чтобы malformed optional fields из Kaggle payload не валили server-import.

## Новое обязательное правило

Для любых данных из Kaggle/remote extractors:

1. optional text fields должны нормализоваться на import boundary;
2. diagnostic/logging helpers не имеют права падать на неожиданных типах;
3. если upstream schema drift всё же случился, run может стать `partial` только из-за реальной бизнес-ошибки обработки, а не из-за `.strip()` на boolean.
