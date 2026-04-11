# INC-2026-04-10 CrumpleVideo Audio Source Drift

## Summary

`/v` завершил рендер и отдал mp4, но в финальном ролике после точки старта аудио (`1:17`) звучал `Pulsarium`, хотя канонический контракт `CrumpleVideo` требует только `The_xx_-_Intro.mp3`.

## Impact

- production `/v` публиковал ролик с неверным музыкальным треком;
- оператор видел “успешный render”, но итоговый артефакт уже нарушал утверждённый audio contract;
- дефект не ловился по обычным render-логам, потому что ffmpeg аудио-merge сам по себе завершался успешно.

## Detection

- пользователь скачал финальный mp4 напрямую из Kaggle output и вручную проверил звуковую дорожку;
- в notebook log было видно только успешное `Audio added`, без явного имени “не того” трека;
- разбор server-side dataset assembly показал, что в non-test session dataset по-прежнему клался `Pulsarium.mp3`.

## Timeline

- `2026-04-10`: пользователь сообщил, что в финальном `CrumpleVideo` вместо `The xx` звучит `Pulsarium`.
- Разбор показал, что notebook уже ожидает `The_xx_-_Intro.mp3`, но orchestration path `video_announce/scenario.py` всё ещё подменяет audio asset для non-test runs.
- В ответ server-side audio selection переведён на единый track contract для test и prod.

## Root Cause

1. Канонический audio contract был уже зафиксирован в docs/notebook, но не был доведён до server-side dataset builder.
2. `video_announce/scenario.py` собирал Kaggle session dataset по legacy правилу: `The_xx_-_Intro.mp3` только для test, `Pulsarium.mp3` для non-test.
3. Из-за этого Kaggle run честно использовал тот mp3, который ему положили в dataset, и производил “технически успешный”, но продуктово неверный mp4.

## Corrective Actions

- перевести `CrumpleVideo` на единый server-side helper выбора аудио, который возвращает только `The_xx_-_Intro.mp3`;
- закрепить регрессионный тест на audio contract для test/prod;
- синхронизировать feature docs и task docs на одном offset `1:17` и одном треке.

## Prevention

- считать audio asset selection частью production contract `/v`, а не “внутренней деталью” dataset assembly;
- перед deploy `/v` делать incident regression check не только по story publish, но и по audio contract;
- при ручной smoke-проверке `CrumpleVideo` валидировать не только наличие mp4, но и фактический audio source в готовом output.
