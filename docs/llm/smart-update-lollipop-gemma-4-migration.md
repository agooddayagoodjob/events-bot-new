# Smart Update Lollipop / Gemma 4 Migration

Статус: `planning`

Назначение: канонический reference-doc для перехода `lollipop`-каскада с `Gemma 3` на `Gemma 4` без изменения финального public writer.

Важно:

- `lollipop g4` в этом проекте означает только `Gemma 4 upstream + final 4o`;
- `writer.final_4o` остаётся единственным финальным public writer stage;
- любые эксперименты, где `Gemma 4` пишет финальный публичный текст, не являются канонической целью этой миграции;
- live-пробы, fixture-ы и benchmark-логи вынесены в отдельный eval-doc:
  [smart-update-lollipop-gemma-4-eval.md](/workspaces/events-bot-new/docs/llm/smart-update-lollipop-gemma-4-eval.md).

## Каноническая цель миграции

`lollipop g4` должен улучшать итоговое качество текста не за счёт замены `4o`, а за счёт более сильного upstream-процессинга:

```text
source.scope
-> facts.extract
-> facts.dedup
-> facts.merge
-> facts.prioritize
-> editorial.layout
-> writer_pack.compose
-> writer_pack.select
-> writer.final_4o
```

Где:

- `Gemma 4` рассматривается только для Gemma-backed upstream families;
- `writer_pack.compose` и `writer_pack.select` остаются deterministic;
- `writer.final_4o` остаётся последним и единственным финальным writer call.

Практический смысл:

- `baseline` остаётся эталоном сравнения;
- `lollipop` остаётся текущим каноническим funnel с final `4o`;
- `lollipop g4` отличается от `lollipop` только тем, что upstream Gemma-стадии адаптированы под `Gemma 4`.

## Non-goals

Вне канонической области этой миграции:

- замена `writer.final_4o` на `Gemma 4`;
- giant-prompt redesign вместо small-stage `lollipop`;
- rollout по одному красивому writer-case без upstream family audit;
- включение `thinking` по умолчанию на финальном public prose stage.

## Почему Gemma 4 имеет смысл именно upstream

Для `lollipop` ценность `Gemma 4` прежде всего в этом:

- нативная `system`-роль вместо legacy `Gemma 3` prompt style;
- более сильный long-context профиль для multi-source fact packs;
- управляемый `thinking`, который полезен для планирования и disambiguation, но не обязан жить в финальном writer;
- нативный `tool`-протокол как задел под future retrieval-interleaving;
- более удобный transport/runtime contract для stage-oriented structured work.

То есть основной выигрыш ожидается в:

- лучшем выделении и сохранении grounded facts;
- более устойчивом salience/planning;
- меньшем prompt drift между family stages;
- лучшем контроле над schema-following и validator-driven reruns.

## Ключевой контракт `lollipop g4`

При любой реализации `lollipop g4` должны одновременно сохраняться три инварианта:

1. Финальный публичный текст пишет только `writer.final_4o`.
2. Все Gemma-этапы upstream работают как маленькие self-contained requests с явным schema contract.
3. Успех миграции измеряется качеством итогового public текста относительно `baseline`, а не субъективной "силой" отдельного Gemma-stage.

## Сравнение Gemma 3 и Gemma 4 по ключевым атрибутам

| Атрибут | Gemma 3 | Gemma 4 | Что это означает для `lollipop` |
| --- | --- | --- | --- |
| Контекст | до `128K` для больших text-моделей | до `256K` для `31B` и `26B A4B` | Больше пространства для multi-source payload, но растут требования к token budgeting и prompt discipline |
| System role | официально не first-class для `IT`-моделей | нативная `system`-роль | Prompt-family можно разделить на policy (`system`) и payload (`user`) |
| Thinking | не оформлен как отдельный протокол | есть отдельный thought-channel и `thinking` policy | Нужно проектировать, где reasoning полезен, а где его надо выключить |
| Tool use | в основном внешняя обвязка | нативный tool protocol | Открывает future path для retrieval-aware stages, но не обязателен в phase 1 |
| Prompt formatting | legacy turn-format | новый turn/token contract | Нельзя просто переиспользовать Gemma-3 prompt style без stage audit |
| Лицензия и экосистема | более жёсткая / старый стек | `Apache 2.0`, очень свежий стек | Проще юридически, но выше риск ранней нестабильности SDK/runtime tooling |

## Что именно должно поменяться в `lollipop g4`

Ниже перечислены только те family changes, которые совместимы с канонической архитектурой `Gemma 4 upstream + final 4o`.

### `source.scope`

Назначение при миграции:

- лучше отделять target event scope от source noise;
- устойчивее работать с mixed-phase и multi-event contamination;
- жёстче маркировать `in_scope / background / uncertain`.

Что менять:

- перевести stage prompts на `system + user`;
- сократить prose-instructions и усилить target JSON contract;
- явно передавать scope objective, target date/event anchor и expected evidence ledger;
- держать `thinking = off` по умолчанию;
- разрешать `LOW thinking` только для реально ambiguous phase-selection cases.

Сигнал успеха:

- меньше ложных future/past leakage;
- меньше downstream rescue-логики из-за плохого scope split.

### `facts.extract`

Это главный кандидат на выигрыш от `Gemma 4`.

Что менять:

- переписать все extract-family prompts под `system`-policy + compact `user` payload;
- tighten JSON schema и field-by-field contracts;
- прямо запрещать premature prose synthesis;
- требовать, чтобы meaningful source facts либо сохранялись, либо явно маркировались как weak/uncertain/background;
- держать family как набор узких prompts, а не объединять их в один universal extractor.

Режим reasoning:

- `thinking = off` по умолчанию;
- `LOW thinking` допустим точечно на dense cases, где extractor должен удержать несколько смысловых пластов, а не только поверхностную карточку.

Сигнал успеха:

- richer grounded pack до `facts.merge`;
- меньше потерь curator/history/context facts;
- меньше downstream "writer looks dry because upstream pack is thin".

### `facts.dedup`

Что менять:

- жёстче фиксировать relation labels (`covered`, `reframe`, `enrichment`, `conflict`);
- вынести инструкцию "не терять новый смысл ради агрессивного collapse";
- явно разделять semantic overlap и source-unique enrichment.

Режим reasoning:

- `thinking = off`;
- если нужен reasoning, он должен быть очень узким и не превращать stage в essay.

Сигнал успеха:

- меньше silent fact loss;
- меньше ложных collapse в cases со схожими, но не идентичными описаниями.

### `facts.merge`

Что менять:

- сохранить canonical pack shape, но перепроверить prompt/style под Gemma 4;
- жёстче закрепить bucket contracts;
- явно передавать provenance expectations и запрет на invented bridging text;
- не смешивать merge с prioritization или layout planning.

Режим reasoning:

- `LOW thinking` допустим только если merge реально упирается в multi-source reconciliation;
- по умолчанию stage должен оставаться structured and bounded.

Сигнал успеха:

- более чистый canonical pack без потери provenance;
- меньше manual/heuristic rescue before prioritization.

### `facts.prioritize`

Что менять:

- переработать salience prompts под `system`-policy;
- явно разделять `must_keep`, `support`, `suppress`, `uncertain`;
- усилить contract для opaque-title / format-anchor / narrative-policy signals.

Режим reasoning:

- `LOW thinking` допустим, если stage реально принимает salience decisions между competing facts;
- reasoning не должен превращаться в hidden second writer.

Сигнал успеха:

- лучшее lead selection;
- меньше dry or taxonomy-heavy openings в final text, потому что pack уже лучше приоритизирован.

### `editorial.layout`

Это второй сильный кандидат на выигрыш от `Gemma 4`.

Что менять:

- использовать нативную `system`-роль для layout policy;
- усилить contract для section boundaries, heading permissions и body split;
- чётче передавать `title_is_bare`, `title_needs_format_anchor`, `non_logistics_total`, `body_cluster_count`;
- запрещать stage писать публичную прозу вместо structure plan.

Режим reasoning:

- `LOW thinking` здесь наиболее оправдан;
- если где-то в `lollipop g4` и нужен limited planning mode, то прежде всего здесь, а не в финальном writer.

Сигнал успеха:

- более устойчивые structure plans;
- меньше collapsed one-blob outputs в list-heavy и dense narrative cases.

### `writer_pack.compose` / `writer_pack.select`

Канонический статус не меняется:

- остаются deterministic;
- не мигрируются на Gemma 4;
- только принимают более сильный upstream payload.

### `writer.final_4o`

Канонический статус не меняется:

- остаётся final public writer;
- prompt family не переезжает на Gemma 4;
- acceptance для `lollipop g4` измеряется именно на итоговом `4o`-тексте.

## Prompt-contract deltas для Gemma 4

Независимо от family, переход на `Gemma 4` требует одинаковых базовых правил.

### 1. `system` и `user` должны быть разделены

В `system` живут:

- stage objective;
- anti-filler / anti-invention policy;
- schema rules;
- allowed/forbidden behaviors.

В `user` живут:

- stage payload;
- source excerpts;
- current pack;
- explicit task-local variables.

### 2. Нельзя переносить legacy Gemma-3 prompt style как есть

Нужно переписать:

- turn formatting;
- role separation;
- examples;
- failure instructions;
- correction prompts.

Иначе `Gemma 4` будет формально "работать", но stage contracts останутся не оптимизированными под её реальный protocol shape.

### 3. `Thinking` должен быть stage-scoped, а не глобальным

Рабочее правило для `lollipop g4`:

- по умолчанию `thinking = off`;
- `LOW thinking` допускается только на planning/disambiguation-heavy upstream stages;
- final public prose stage не использует Gemma 4 и не должен быть зависим от thought-channel вообще.

### 4. Structured output важнее prose cleverness

`Gemma 4` в `lollipop` нужна не для "красивого текста" upstream, а для:

- удержания сложного source pack;
- аккуратного split по buckets;
- лучшего schema following;
- более сильного planning.

Если stage начинает "писать за downstream", это регрессия.

### 5. Примеры должны быть короткими и family-local

Для Gemma 4 полезнее:

- `1-2` коротких positive/negative examples на stage;
- чем один длинный abstract prompt с большой редакторской философией.

Это особенно важно для `source.scope`, `facts.extract` и `editorial.layout`.

## Transport и runtime-дельты

Это часть миграции, а не факультативная обвязка.

### Thought handling

Если выбранный transport отдаёт separate thought channel, нужны жёсткие гарантии:

- thought content не попадает в public output;
- thought content не попадает в persisted multi-turn history;
- thought content не попадает в operator-facing final preview по умолчанию;
- при debug-mode thoughts хранятся отдельно от final answer.

### SDK / API path

Нужно использовать поддерживаемый transport path, а не проектировать `lollipop g4` на deprecated integration assumptions.

### Token budgeting

Из-за нового context profile и другой tokenization нужно пересмотреть:

- per-stage payload caps;
- long-source chunking;
- conservative TPM budgeting;
- retry policy на dense multi-source cases.

## Почему tool-calling пока не обязателен

`Gemma 4` делает tool interleaving более естественным, но для `lollipop g4 phase 1` это не обязательное условие.

Правильный порядок:

1. Сначала довести `Gemma 4` prompts и transport для существующих upstream stages.
2. Потом отдельно решать, нужен ли `tool_call` хотя бы для части retrieval-heavy stages.

То есть `tool use` здесь рассматривается как future expansion path, а не как blocker для первой версии `lollipop g4`.

## План миграции

### Phase 0. Каноника и eval frame

- зафиксировать правильную цель: `Gemma 4 upstream + final 4o`;
- держать reference-doc отдельно от eval-log;
- зафиксировать benchmark protocol, где final writer не меняется.

### Phase 1. Family audit

- пройти по всем Gemma-backed upstream stages;
- для каждой family выписать prompt deltas, schema deltas, retry/validator deltas;
- определить, где `thinking` запрещён, а где допускается в `LOW` режиме.

### Phase 2. Prompt rewrite

- переписать prompts под `system + user`;
- сократить oversized instructions;
- добавить family-local positive/negative examples;
- обновить validators, если schema contract ужесточается.

### Phase 3. Runtime hardening

- подтвердить supported transport;
- внедрить thought filtering;
- обновить token budgeting и pacing;
- проверить logging/debug contracts.

### Phase 4. Canonical eval

- взять свежий synthetic benchmark с несколькими multi-source fixtures;
- прогнать `baseline`, `lollipop`, `lollipop g4`;
- во всех трёх вариантах сохранить один и тот же final `writer.final_4o`;
- сравнивать итоговый public text, а не локальную красоту upstream fragments.

### Phase 5. Rollout gate

`lollipop g4` может считаться готовым кандидатом только если:

1. итоговый текст стабильно лучше `baseline`;
2. нет явной регрессии относительно текущего `lollipop`;
3. transport/runtime contract чистый: без thought leakage и без сломанного latency profile.

## Acceptance criteria

Минимальная цель для реализации:

- `lollipop g4 > baseline` по качеству итогового public текста на серии canary fixtures.

Более строгая цель для реального прод-замещения текущего `lollipop`:

- `lollipop g4 >= current lollipop` по качеству текста при сопоставимой стабильности.

При этом успешная миграция должна давать не просто "другой текст", а лучшее сочетание:

- grounding;
- format clarity;
- preservation of meaningful facts;
- structure quality;
- отсутствие infoblock leakage;
- отсутствие dry card-style collapse.

## Чек-лист по компонентам

| Компонент | Что менять в рамках `lollipop g4` | Почему |
| --- | --- | --- |
| Prompt families | Переписать Gemma-backed upstream prompts под `system + user` | `Gemma 4` лучше работает на role-separated contracts |
| Validators | Уточнить schema checks там, где prompt contract становится строже | Иначе нельзя честно сравнивать `Gemma 3` и `Gemma 4` |
| Token budgeting | Пересчитать stage caps и pacing | Long-context profile и tokenization меняют бюджет |
| State / history | Гарантировать strip thoughts из persisted history | Это обязательное runtime правило для Gemma 4 |
| Logging | Логировать transport-aware debug traces без thought leakage в public path | Иначе тяжело локализовать regressions |
| Final writer | Не менять `writer.final_4o` | Это базовый архитектурный инвариант миграции |

## Связанные документы

- Канонический funnel: [smart-update-lollipop-funnel.md](/workspaces/events-bot-new/docs/llm/smart-update-lollipop-funnel.md)
- Writer pack contract: [smart-update-lollipop-writer-pack-prompts.md](/workspaces/events-bot-new/docs/llm/smart-update-lollipop-writer-pack-prompts.md)
- Final 4o contract: [smart-update-lollipop-writer-final-prompts.md](/workspaces/events-bot-new/docs/llm/smart-update-lollipop-writer-final-prompts.md)
- Live eval log: [smart-update-lollipop-gemma-4-eval.md](/workspaces/events-bot-new/docs/llm/smart-update-lollipop-gemma-4-eval.md)
