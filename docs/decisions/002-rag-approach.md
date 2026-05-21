# 002 — RAG Approach

**Дата:** TBD  
**Статус:** Предстои

## Контекст
Избор на framework за RAG pipeline.

## Опции
- LangChain — по-популярен, повече ресурси
- LlamaIndex — по-фокусиран върху document retrieval

## Решение

TBD — framework choice (LangChain vs LlamaIndex).

**Constraint (ADR 003):** RAG must support **dual-tier retrieval** — separate indexes or metadata filter for `clinical` vs `peer`. Clinical chunks always retrieved first.

## Референции

- [003 — Two-tier knowledge](003-two-tier-knowledge.md)
- [concept.md](../concept.md)
