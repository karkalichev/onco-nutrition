# Concept: Onco Nutrition Assistant

AI assistant for **nutrition during cancer treatment** — with **two clearly separated knowledge layers** and a single, honest UX. The product is **bilingual (English + Bulgarian)** in code and content; the **demo and portfolio narrative are English-first**.

---

## The problem

Oncology patients look for nutrition advice in two places:

1. **Official guidelines** — ACS, NCI, ESPEN, hospital handouts, onco.bg
2. **Peer experience** — Facebook groups, forums, “what worked for me”

They often **conflict** (e.g. “eat whatever you can” vs “avoid antioxidants” vs “BRAT-style diets”). A flat RAG stack without labels is risky — users cannot tell medicine from anecdote.

---

## The solution: two-tier model

```
┌─────────────────────────────────────────────────────────────┐
│                    ASSISTANT RESPONSE                        │
├──────────────────────────┬──────────────────────────────────┤
│  LAYER 1 — CLINICAL       │  LAYER 2 — PEER / PATIENT       │
│  (official documentation) │  (reviews and shared experience)  │
├──────────────────────────┼──────────────────────────────────┤
│  Trust: authoritative     │  Trust: orientation, not fact     │
│  Sources: guidelines,     │  Sources: forums, interviews,    │
│  patient booklets from    │  “what worked for me”, practical  │
│  medical organizations    │  tips                             │
├──────────────────────────┼──────────────────────────────────┤
│  UI label:                │  UI label:                       │
│  “Recommended from         │  “What other patients share”     │
│   clinical guidelines”    │  + warning                        │
└──────────────────────────┴──────────────────────────────────┘
                              ↓
              “What the app suggests…” (synthesis)
                              ↓
              “Discuss changes with your oncologist or dietitian.”
```

### Layer 1 — Clinical (`tier: clinical`)

**What it is:** Published guidance from medical organizations, hospitals, oncology societies, official patient education materials.

**Rule:** Treat as the **authoritative base** for the answer. Do not invent — cite or paraphrase retrieved chunks.

**Examples in this project:** ESPEN, NCI, ACS, onco.bg (ACS BG), CancerInfo.bg, SEOM, AND.

### Layer 2 — Peer (`tier: peer`)

**What it is:** Forum threads, archived patient chats, future user queries, practical tips from communities.

**Rule:** **Do not** treat as medical fact. Show as “what others experienced”, with a clear disclaimer. **Never override Layer 1** without flagging the conflict.

**Examples in this project:** CSN/Macmillan forums, `data/raw/user-queries/`, Neogenezis BRAT (experiential).

---

## UX: what an answer looks like

Every recommendation follows this template (labels are localized BG/EN in the app; examples below in English):

### 1. Clinical guidelines (Layer 1)

> **Recommended from clinical guidelines:** For nausea — small, frequent meals every 2–3 hours; bland foods at room temperature; avoid greasy and strong-smelling dishes.  
> *Source: ACS / onco.bg*

### 2. Patient experience (Layer 2) — optional block

> **What other patients share:** Some use ginger or find cold “white” foods helpful (rice, potatoes). This is personal experience — **not confirmed for every case.**

### 3. App suggestion (synthesis)

> **What the app suggests:** Try a light snack every 2–3 h — e.g. crackers with a little cheese or oatmeal if you tolerate it. Sip fluids between meals.

### 4. Required footer

> ⚕️ This is **general nutrition information**, not medical advice. Your treatment is individual — **discuss diet changes with your oncologist or dietitian.**

---

## Conflict rules

| Situation | Behavior |
|-----------|----------|
| Peer advice **aligns** with clinical | Show peer as “supported by patient experience” |
| Peer **contradicts** clinical | Clinical layer **first**; peer with note “some patients share X, but guidelines recommend Y” |
| Peer pushes **supplements/diets** (keto, fasting, BRAT) | Layer 2 only + “ask your doctor before changing diet” |
| No peer match | Answer from Layer 1 only — OK |
| No clinical match | **Do not** answer safety topics from peer alone; say “not enough information — talk to your care team” |

---

## RAG implications

| Aspect | Clinical | Peer |
|--------|----------|------|
| Vector metadata | `tier: clinical` | `tier: peer` |
| Extra metadata | `source`, `language`, `symptom_tags` | + `source_type: forum\|interview` |
| Retrieval | **Always first**, top-k=5 | Additional top-k=3 when relevant |
| Prompt | Section `[CLINICAL_CONTEXT]` | Section `[PEER_CONTEXT]` — explicit “do not treat as medical fact” |
| Chunking | By section/symptom | By post/comment thread |

See: [`decisions/003-two-tier-knowledge.md`](decisions/003-two-tier-knowledge.md)

---

## Weekly menu + same-day corrections

Nutrition during oncology treatment **is not a static diet** — it changes with **cycle phase** and **today’s symptoms**. The app should reflect that.

### How it works

```
[Profile]                    [Base weekly menu]
 treatment: chemo             Mon–Sun: breakfast / lunch / dinner / 2 snacks
 cycle: day 3 of 21              ↓
         │                  each day has a “phase” (see below)
         ▼
[Patient says today]    →  [Adjust today (+ maybe tomorrow)]
 “nauseous, no appetite”     swap meals, smaller portions, add snack
         │
         ▼
[Menu for the day]        rest of week = template, not wiped
```

**Principle:** the weekly plan is a **flexible template**, not a rigid meal plan. A complaint **overrides specific meals**, not the whole approach.

### Week phases (example: chemo every 3 weeks)

| Phase | Usually | Nutrition focus |
|-------|---------|-----------------|
| `pre_chemo` | 2–3 days before | Protein, calories, hydration — “loading” |
| `chemo_day` | Infusion/tablet day | Light, small portions, bland |
| `post_chemo_early` | Days 1–3 after | Nausea, dry mouth — cold, low odor, frequent |
| `post_chemo_late` | Days 4–10 | Appetite returns; gradual variety |
| `recovery` | Between cycles | More balanced menu, weight maintenance |
| `corticosteroid_day` | Dexamethasone and similar | ↑ appetite, ↑ blood sugar — different rules |

The patient may not know the phase — the app asks: *“Is today a chemo day? How do you feel?”*

### Inputs for correction

| Complaint | How the menu changes |
|-----------|----------------------|
| Nausea / vomiting | Bland, cold, small portions; drop greasy/spicy |
| No appetite | Snacks every 2–3 h; calorie-dense (nuts, cheese), not large plates |
| Diarrhea | BRAT-like; low fiber/fat; yogurt, banana |
| Constipation | Fiber, warm drinks, prunes |
| Metallic taste | Acid/marinades; avoid red meat; smoothies |
| Dry mouth | Soft, sauces, soups; avoid dry/crunchy |
| Fatigue | Steady protein+fat combos; not sugar alone |

### Menu MVP (Phase 2, after symptom → answer)

1. Generate **7 days × 3–5 meals** from clinical tier
2. “How is today?” → **re-generate day N**
3. Optional history of what worked (peer tier)

---

## Patient context — what we track

Meaningful menus and corrections need more than “nausea” and “what should I eat”. We use a **context profile** at three levels.

### Level A — required (menu MVP)

| Field | Why | How we ask |
|-------|-----|------------|
| **Treatment type** | Different side effects | chemo / radiation / hormonal / post-surgery |
| **Cycle day** or **phase** | Calories vs balance priority | “Day ___ of cycle” or “chemo today?” |
| **Symptoms today** | Overrides today’s menu | multi-select + free text |
| **Weight / trend** | Weight loss → calories first | “Losing weight recently?” |

### Level B — strongly recommended

| Field | Why | Example |
|-------|-----|---------|
| **Diagnosis / site** | Head/neck → swallowing; GI → different diet | breast, colorectal, H&N |
| **Regimen / drugs** | Corticosteroids, targeted therapy | dexamethasone days 1–3, not just “chemo” |
| **Comorbidities** | Diabetes, kidney, celiac | type 2 diabetes |
| **Dietary restrictions** | Allergies, religion, vegan | lactose-free |
| **Country / city** | Seasonal local produce | `US`, `BG`, `Sofia` |

### Level C — medical values (optional, self-reported)

> **We are not a lab.** The patient enters **approximate** values — we do not replace blood tests.

| Value | Effect on nutrition | How we ask |
|-------|---------------------|------------|
| **Blood glucose** | Steroids + diabetes → limit simple sugars | “High recently? (yes/no/unsure)” |
| **Neutrophils / immunity** | Neutropenia → strict food hygiene | “Any infection-risk warning?” |
| **Albumin / malnutrition flag** | ONS, high-calorie | from dietitian / “weakness, weight loss” |
| **Creatinine / kidney** | Protein, fluids | comorbidity checkbox |
| **Recent weight (kg)** | Building-up diet | number, optional |

**Rule:** if data is missing → ask **1–2 key questions**, not 20. If labs are unclear → conservative clinical advice + “ask your team”.

### How context changes logic (example: sugar)

```
IF weight_trend == losing AND phase in (post_chemo_early, chemo_day):
    priority = CALORIES_FIRST          # banana, honey, ice cream — OK if tolerated

ELIF diabetes OR on_corticosteroids OR glucose == high:
    priority = BLOOD_SUGAR_AWARE         # fewer simple sugars, protein+fiber

ELIF phase == recovery AND symptoms == none:
    priority = BALANCED                  # normal balanced meals
```

### What we **do not** do

- Interpret lab values as a diagnosis
- Adjust insulin or medications
- Store PHI in git (`data/patient/` → gitignored, local only)

### Minimal JSON profile (target)

```json
{
  "treatment": {
    "types": ["chemotherapy"],
    "protocol_hint": "EC-T",
    "cycle_day": 4,
    "cycle_length_days": 21,
    "on_corticosteroids_today": false
  },
  "diagnosis": {
    "site": "breast",
    "stage": null
  },
  "comorbidities": ["diabetes_type_2"],
  "vitals_self_report": {
    "weight_kg": 62,
    "weight_trend": "losing",
    "glucose": "high_recently",
    "neutropenia_risk": "unknown"
  },
  "today": {
    "symptoms": ["nausea", "no_appetite"],
    "phase_override": null
  },
  "locale": {
    "country": "US",
    "city": "Boston"
  }
}
```

**Location and seasonality:** `country` + `city` steer toward local, in-season produce. MVP passes fields into the prompt; a **per-region produce calendar** (structured data) is Phase 2 — until then the model uses general knowledge + “check what’s available locally”.

**Example questions (demo / eval):**

- Weekly menu: *Plan a 7-day menu for my chemo cycle — day 4, still nauseous.*
- Daily menu: *What should I eat today? Cycle day 2, no appetite.*
- Substitute: *You suggested banana but it makes me nauseous — what instead?*
- Seasonal/local: *Soft fruits for nausea this season — Boston, US.*

Cycle phase can be **derived** from `cycle_day` or **overridden** by the patient (“today feels like day 2 after chemo”).

---

## Why “sugar OK one day, not the next” is not random

The patient is describing **different context each day**, not a contradiction. Guidelines do not say sugar is always OK or always bad — they say **what matters today**.

### 1. Different priority: calories vs control

| Situation | Logic for sugar/sweets |
|-----------|------------------------|
| Losing weight, cannot eat | **Calories first** — ice cream, honey, banana may be the only intake (“eat what you can” — CSN/Macmillan peer) |
| Doing better, has appetite | **More balanced** — simple sugars spike and crash (onco.bg on fatigue) |

One day the body **needs** any intake; another day it can tolerate normal meals.

### 2. Chemo cycle phase

- **Chemo day / 1–2 days after:** nausea → crackers, banana, honey in tea may work; cake — often not
- **Days 5–10:** appetite returns → sugar may be OK again or trigger nausea — depends on taste/stomach

### 3. Corticosteroids (common in breast, lymphoma, myeloma)

Dexamethasone and others **raise appetite and blood glucose**. On/after steroid days:

- more hunger, sometimes cravings for sweets
- with diabetes or after steroids stop — glucose may spike/crash

### 4. Symptom, not calendar

| Symptom today | Sugar/sweets |
|---------------|--------------|
| Nausea | Ginger candy, lemon — small sugar OK; heavy dessert — not |
| Diarrhea | Banana (sugar + potassium) — OK; sorbitol in “sugar-free” — often worse |
| Fatigue | onco.bg: avoid sugar spikes → protein + nuts |
| Metallic taste | Sometimes sweets tolerate better than meat |

### 5. Confusion from conflicting advice

Patients hear at once:

- “Eat whatever you want” (forums)
- “Cut sugar” (general wellness)
- “Bananas help diarrhea” (BRAT)
- “Bananas are too sugary” (anti-cancer blogs)

**The app should explain why:** *“Today the priority is calories because…”* vs *“Today the priority is steady energy because…”*

### How we encode it

```python
# pseudocode — not random, but state
day_state = {
    "phase": "post_chemo_early",      # from profile / calendar
    "symptoms": ["nausea"],           # from patient today
    "weight_trend": "losing",         # optional
    "on_corticosteroids": False,
}
# → priority: CALORIES_FIRST | BALANCED | BLOOD_SUGAR_AWARE
```

---

## MVP scope (current)

### In scope

- Symptom → structured answer with **two visible blocks** (clinical + optional peer)
- Disclaimer on every answer
- **Bilingual** responses (`bg` / `en`); knowledge base includes BG and EN sources
- Vector RAG (Chroma or pgvector) + keyword fallback

### Phase 2

- **Weekly menu** with treatment phases
- **Daily correction** on complaint (override one day)
- Explain *why* rules differ today (e.g. sugar)

### Out of scope (MVP)

- Automatic drug–nutrient interaction checking
- Personalization to a specific chemo protocol
- Live patient community moderation

---

## Differentiator

Generic nutrition chatbots mix everything into one answer. **Onco-nutrition** states clearly:

- what **doctors and guidelines** say
- what **patients** share
- what the **app** suggests
- and that the **clinician has the final word**

---

## Related documents

- [Architecture](architecture.md)
- [ADR 003 — Two-tier knowledge](decisions/003-two-tier-knowledge.md)
- [Sources — classification](references/sources/README.md)
- [Forums (Tier 2)](references/forums/README.md)
