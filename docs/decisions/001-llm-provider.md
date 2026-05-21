# 001 — LLM Provider

**Дата:** 2026-05-19  
**Статус:** Прието (2026-05-21)

## Контекст

Избор между OpenAI и Anthropic за основен LLM provider. Имаме платен Anthropic бюджет.

## Решение

**Anthropic** — единствен provider за MVP.

- Модел по подразбиране: `claude-sonnet-4-5` (override с `ANTHROPIC_MODEL`)
- Auth: `ANTHROPIC_API_KEY` в `.env`
- Имплементация: `src/llm.py`

## Последствия

- Един API ключ и един SDK (`anthropic`) — по-прост код и конфигурация
- OpenAI не се използва; `openai` пакетът е премахнат от dependencies
- При нужда от по-силен модел: `ANTHROPIC_MODEL=claude-opus-4-5` (по-скъп)

## Конфигурация

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-5   # optional
ANTHROPIC_MAX_TOKENS=2000                  # optional
```

## When to reconsider

Останете на **един Anthropic provider** до Phase 2. Преди да добавите втори vendor, пробвайте **два модела в Anthropic** (Sonnet vs Opus) — по-евтино и без разминаване в тон/терминология.

Преоценете решението само ако:

| Тригер | Действие |
|--------|----------|
| **Повтарящи се outages** при Anthropic | Optional fallback provider (само при недостъпност, не в основния flow) |
| **Eval на BG въпроси** показва систематични грешки в мед. език, които друг модел поправя | A/B тест с втори provider; миграция само при ясна полза |
| **Бюджет или latency** блокират мащабиране | Първо по-евтин модел / по-кратък контекст; втори vendor само ако не стига |
| **Regulatory / geographic** изискване | Provider, който покрива data residency или compliance |

**Не си струва** втори provider за: load balancing, „just in case“ без метрики, или паралелни отговори от два модела (усложнява QA и двуслоен UX).

Критерий за успех преди промяна: фиксиран eval set (~20–30 реални BG/EN въпроса) + review на терминология и disclaimer.
