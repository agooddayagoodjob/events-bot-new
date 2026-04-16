# Runtime Logs

Каноническая политика краткоживущих runtime-логов на prod-машине.

## Purpose

- сохранить эксплуатационные логи на volume машины, чтобы можно было разбирать реальные scheduler/job инциденты постфактум;
- не полагаться только на краткий буфер Fly logs;
- не держать логи дольше суток, чтобы не раздувать `/data`.

## Current Production Policy

- production currently keeps this mirror **disabled** (`ENABLE_RUNTIME_FILE_LOGGING=0`) after the April 16, 2026 disk-pressure incident on Fly volume `/data`;
- the file-logging path remains available as an incident/debug tool, but should not stay permanently enabled on the current volume size without explicit space budgeting;
- when temporarily enabled, it:
- пишет существующий root logger приложения в файловый mirror;
- путь по умолчанию: `RUNTIME_LOG_DIR=/data/runtime_logs`;
- имя файла по умолчанию: `RUNTIME_LOG_BASENAME=events-bot.log`;
- ротация: каждый час;
- retention: около 24 часов через `RUNTIME_LOG_RETENTION_HOURS=24`.

Практически это значит:

- активный текущий час пишется в `events-bot.log`;
- прошлые часы уходят в hourly rotated файлы рядом;
- старые rotated файлы автоматически удаляются примерно после суток хранения.

## Scope

В файл попадает уже существующий runtime stream root logger, поэтому туда идут:

- scheduler/job события (`tg_monitoring`, `guide_monitoring`, `vk_auto_import`, `video_tomorrow` и т.д.);
- traceback'и и runtime warnings;
- обычные `INFO/WARNING/ERROR` сообщения приложения.

Это не отдельная “спец-диагностика по одной фиче”, а единый эксплуатационный журнал.

## Environment

- `ENABLE_RUNTIME_FILE_LOGGING` — включает file logging mirror.
- `RUNTIME_LOG_DIR` — директория хранения логов.
- `RUNTIME_LOG_BASENAME` — базовое имя текущего файла.
- `RUNTIME_LOG_RETENTION_HOURS` — сколько часов хранить rotated logs.
- `RUNTIME_LOG_LEVEL` — optional override для file handler; если не задан, используется текущий уровень root logger.

## Operational Notes

- на Fly production лог-файлы должны жить только на volume (`/data/...`), а не в ephemeral filesystem контейнера;
- этот механизм предназначен для короткой incident-retention, а не для долгого архивирования;
- если нужен длительный аудит, данные нужно отдельно выгружать/переносить, а не увеличивать retention на машине без оценки места на диске.
