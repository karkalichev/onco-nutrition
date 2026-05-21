# Collecting real user queries

Guide for a meeting with a user (oncology patient / caregiver) — how to collect natural questions and context for the `onco-nutrition` MVP.

**Goal:** 15–30 real phrasings (English and/or Bulgarian) + minimal context (symptom, treatment, restrictions).

---

## Before the meeting (5 min)

1. Explain the project: AI assistant for **nutrition during cancer treatment**, does not replace doctor/dietitian
2. Ask for **verbal consent** to record questions (no name, no detailed diagnosis if they prefer)
3. Prepare: phone/voice memo **or** shared Google Doc / Notes
4. Create file: `data/raw/user-queries/YYYY-MM-DD-session.md`

---

## Interview script (~20–30 min)

### 1. Context (not for publication, for you only)


| Field               | Example                                     |
| ------------------- | ------------------------------------------- |
| Role                | patient / caregiver                         |
| Diagnosis (general) | breast, colorectal, H&N — no TNM details    |
| Stage               | before chemo / during / after / remission   |
| Treatment           | chemo, radiation, corticosteroids, combined |
| **Cycle day**       | “day 3 after chemo”, “infusion day”         |
| **Comorbidities**   | diabetes, high glucose on steroids          |
| Language            | English / Bulgarian                         |


> Do not record national ID, address, doctor name, exact lab values (mmol/L).

### 1b. Context questions (for menu + glucose)

1. *“Which day of the cycle are you usually on — chemo day, 1–2 days after, or feeling better?”*
2. *“Are you on corticosteroids (e.g. dexamethasone) — and on those days is appetite/blood sugar different?”*
3. *“Do you have diabetes or has a doctor mentioned high blood sugar?”*
4. *“When you say ‘sugar OK one day, not the next’ — what is different between those days?”*
5. *“Are you tracking weight — losing without trying?”*

### 2. Open questions (most important)

Read aloud and record **their exact words**:

1. *“When you have a problem with eating during treatment — what exactly do you ask? Who do you ask first?”*
2. *“How would you phrase a question to a phone/chat app if you’re nauseous and don’t know what to eat?”*
3. *“What did you search on Google or Facebook? Copy the phrase for me.”*
4. *“What annoys you about advice online — what is wrong or confusing?”*
5. *“Are there foods that helped / made things worse?”*
6. *“Have you asked a dietitian? What did they say that you remember?”*

### 3. Symptom map (at least 3 scenarios)

Ask them to **role-play** a question for each row — as they would type in chat:


| Symptom              | Prompt                                                         |
| -------------------- | -------------------------------------------------------------- |
| Nausea / vomiting    | “Imagine you’re nauseous after chemo — what do you ask?”       |
| No appetite          | “You haven’t eaten properly for 3 days — what do you ask?”     |
| Taste change         | “Everything tastes metallic — what do you ask?”                |
| Dry mouth            | “Your mouth is dry and sore — what do you ask?”                |
| Diarrhea             | “You have treatment-related diarrhea — what do you ask?”       |
| Constipation         | “You’re constipated from medication — what do you ask?”        |
| Weight loss          | “You’re losing weight — what do you ask?”                      |
| Immunity / infection | “You’re worried about infection — what do you ask about food?” |


### 4. “Bad” questions (also valuable)

- *“Have you asked about ‘healing’ diets, superfoods, BRAT, keto? What exactly did you type?”*
- *“Was there a time you got contradictory advice?”*

---

## Recording format

### Markdown (quick)

```markdown
## Query 001
- **text:** "What can I eat when I'm nauseous after chemo?"
- **symptom:** nausea
- **treatment_phase:** during_chemo
- **language:** en
- **source:** user_interview
- **date:** 2026-05-22
- **notes:** wants easy, low odor

## Query 002
...
```

### JSON (for pipeline later)

Save in `data/raw/user-queries/queries.json`:

```json
[
  {
    "id": "uq-001",
    "text": "What can I eat when I'm nauseous after chemo?",
    "symptom": ["nausea"],
    "treatment_phase": "during_chemo",
    "language": "en",
    "source": "user_interview",
    "date": "2026-05-22",
    "expected_topics": ["small_frequent_meals", "bland_foods", "cold_foods"],
    "notes": "wants easy, low odor"
  }
]
```

### CSV (if you prefer a spreadsheet)

```csv
id,text,symptom,treatment_phase,language,date,notes
uq-001,"What can I eat when I'm nauseous after chemo?",nausea,during_chemo,en,2026-05-22,"low odor"
```

---

## After the meeting (10 min)

1. **Transcribe** — move voice recording into `text` fields
2. **Tag** — mark symptom(s) from the list in `week-01.md`
3. **Test** — run 3–5 queries through `python -m src.cli ask` and check usefulness
4. **Compare** — with forum phrases in `docs/references/forums/` — does language match?

---

## Minimum success


| Metric                      | Target                       |
| --------------------------- | ---------------------------- |
| Real questions              | ≥ 10                         |
| Symptoms covered            | ≥ 3 different                |
| Context (treatment/stage)   | general only, no PHI         |
| “Bad” / edge-case questions | ≥ 2 (supplements, fad diets) |


---

## Privacy

- **Do not commit** names, phones, addresses, hospital IDs
- `data/raw/` — sensitive session files are gitignored
- For demo use **anonymized** or **synthetically rephrased** queries

---

## Quick template

Copy and fill in: `[data/raw/user-queries/TEMPLATE.md](../data/raw/user-queries/TEMPLATE.md)`

---

## Related resources

- [Communities catalog](references/communities.md) — where EN peer phrases come from
- [PDF/Web sources](references/sources/README.md) — evidence base for answers
- [Week 01 — symptoms](weekly/week-01.md)

