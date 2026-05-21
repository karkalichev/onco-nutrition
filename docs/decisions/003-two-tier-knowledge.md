# 003 — Two-Tier Knowledge Model

**Date:** 2026-05-21  
**Status:** Accepted

## Context

Two types of material were collected:

- **Official guidelines** (ESPEN, ACS, NCI, onco.bg, CancerInfo.bg)
- **Patient forums and peer advice** (CSN, Macmillan, future user interviews)

Mixing them in one RAG index without labeling creates risk — the LLM may present a forum anecdote as medical recommendation.

## Decision

Split the knowledge base into **two tiers** with different trust, retrieval priority, and UI presentation.

| | Tier 1: `clinical` | Tier 2: `peer` |
|---|-------------------|----------------|
| **Content** | Medical guidelines, official patient booklets | Forums, patient chats, experiential tips |
| **Trust** | Authoritative base | Orientation, not fact |
| **Retrieval** | Primary, always queried | Secondary, optional |
| **UI label** | “Recommended from clinical guidelines” | “What other patients share” |
| **Override** | Never overridden by peer | Never overrides clinical without conflict flag |

## Response structure (required)

1. Clinical recommendations (+ source)
2. Peer insights (optional, with disclaimer)
3. App synthesis (“What the app suggests…”)
4. Footer: “Discuss with your doctor or dietitian”

## RAG implementation

- Two vector collections **or** one index with metadata filter `tier: clinical | peer`
- Prompt template with separate `[CLINICAL_CONTEXT]` and `[PEER_CONTEXT]`
- System prompt: peer context explicitly marked as anecdotal

## Consequences

- `docs/references/sources/` → predominantly Tier 1
- `docs/references/forums/` → Tier 2
- `data/raw/user-queries/` → Tier 2
- Chunk pipeline must tag every document at ingest time

## Alternatives (rejected)

- **Single index, no tier** — rejected (trust/safety)
- **Clinical only, no peer** — rejected (lose patient language and practical tips)
- **Peer as separate “community tab”** — possible later; for MVP peer is a section in the same answer

## References

- [concept.md](../concept.md)
- [architecture.md](../architecture.md)
