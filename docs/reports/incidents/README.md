# Инциденты

Канонический индекс продовых инцидентов и разборов, которые должны использоваться для regression-check перед новыми изменениями.

- `INC-2026-04-10-crumple-story-prod-drift.md` — `/v` завершал рендер без Telegram stories из-за branch/config drift в проде.
- `INC-2026-04-10-crumple-audio-source-drift.md` — `/v` собрал финальный mp4 с `Pulsarium` вместо обязательного `The_xx_-_Intro.mp3` из-за server-side dataset assembly drift.
