# Week 01 — Onco Nutrition Assistant

**Period:** Week 1 of AI Engineer transition  
**Project:** `onco-nutrition` — AI-powered nutritional assistant for oncology patients

---

## Goals for this week

- [x] Setup Python environment + Anthropic SDK
- [x] First successful API call (structured nutritional response)
- [x] Domain research on oncology nutrition
- [ ] Define MVP scope and user flows
- [x] Two-tier knowledge model (clinical + peer) — see `docs/concept.md`
- [ ] Build first real prompt (symptom → recommendation)

---

## Domain Research: Oncology Nutrition

*Source: Public medical guidelines — Memorial Sloan Kettering, Dana-Farber, Stanford Health Care, Johns Hopkins, UCSF, ESPEN, Tufts Medical Center, Chemocare, Oncology Nursing Society, PubMed.*

### The problem

- 88% of patients undergoing chemo/radiation experience at least one nutrition-related side effect
- 67%+ report taste/smell changes; ~40% report reduced appetite
- Malnutrition is common and leads to worse treatment outcomes and delayed cycles
- Unintentional weight loss makes it harder for the body to rebuild healthy cells between chemo cycles

### Common symptoms the assistant must handle

| Symptom | Frequency |
|---|---|
| Loss of appetite | Very common |
| Nausea / vomiting | Very common |
| Taste and smell changes | 67%+ |
| Fatigue | 80%+ |
| Mouth sores / dry mouth | Common |
| Diarrhea | Common |
| Constipation | Common |
| Difficulty swallowing | Situational (head/neck cancers, radiation) |
| Weight loss | Common |
| Weight gain | Common with corticosteroid-based regimens (breast cancer, blood cancers) |

### Evidence-based recommendations by symptom

**Nausea / poor appetite**
- Small, frequent meals every 2–3 hours (5–6x/day), not 3 large meals
- Bland foods: toast, dry crackers, oatmeal, eggs
- Cold or room-temperature foods (less odor = less nausea trigger)
- Avoid fatty, greasy, spicy, strong-smelling foods
- Calorie-dense additions: nut butters, avocado, whole-fat Greek yogurt, olive oil, honey

**Diarrhea**
- Increase soluble fiber: rice, bananas, oats, bread, potatoes, applesauce
- Avoid gas-forming foods: cruciferous vegetables, beans, lentils, soda, sugar-free candies
- Replenish electrolytes: sodium (broth, sports drinks), potassium (bananas, fruit juices)

**Constipation**
- Plenty of water
- Add vegetables, beans, fiber supplement (consult dietitian)

**Mouth sores / difficulty swallowing**
- Soft, moist, cool foods
- Mashed potatoes, sweet potatoes, butternut squash, carrots, applesauce, tofu, ground meat
- Cut food into small pieces; avoid hard, dry, or crunchy foods
- Cold foods may be more soothing

**Fatigue**
- Stay hydrated (fluid loss worsens fatigue)
- Small meals throughout the day to maintain energy
- Light physical activity (walking) can help

**Dry mouth / taste changes**
- Wet, creamy textures work best
- Experiment with different spices and marinades
- Oatmeal is particularly good: neutral flavor, creamy texture, nutrient-dense

**Hydration (general)**
- Minimum 80–100 oz (2.4–3L) per day
- Water is best; also: broth, herbal tea (ginger, mint), diluted fruit juice, popsicles

### General nutrition goals for oncology patients

- At least 3 meals + snacks daily
- Protein at every meal: chicken, fish, eggs, Greek yogurt, cottage cheese, beans, nuts, tofu
- Two-thirds of each plate = plant foods (fruits, vegetables, whole grains, beans)
- One-third = lean animal protein

### Treatment-specific notes

- **Chemo days specifically:** eat lightly; small portions slowly; avoid fatty/greasy/spicy
- **Corticosteroid-based regimens** (breast cancer, blood cancers): may cause weight gain + increased blood sugar — opposite problem to typical weight loss
- **Head/neck radiation:** swallowing difficulties are common; soft/liquid diet critical

---

## MVP Scope (defined this week)

### User inputs

| Input | Type | Notes |
|---|---|---|
| Treatment type | Select | Chemotherapy / Radiation / Hormone therapy / Surgery recovery |
| Current symptoms | Multi-select | From symptom list above |
| Dietary restrictions | Free text | Allergies, preferences, cultural/religious |
| Appetite level | Scale 1–5 | Guides calorie density of recommendations |

### Expected output (two-tier model)

Every response has **four labeled sections**:

| Section | Source tier | Label (EN; localized in app) |
|---------|-------------|--------------------------------|
| 1. Clinical recommendations | Tier 1 | “Recommended from clinical guidelines” |
| 2. Peer insights (optional) | Tier 2 | “What other patients share” + disclaimer |
| 3. App synthesis | LLM | “What the app suggests…” |
| 4. Footer | — | “Discuss with your oncologist or dietitian” |

**Content per section:**
1. What to eat / avoid (clinical) + source reference
2. Practical tips from forums/patients (if relevant) — explicitly not medical fact
3. 2–3 example meals/snacks + hydration (synthesis of 1 + 2)
4. Mandatory disclaimer

See [`docs/concept.md`](../concept.md) for conflict rules (peer vs clinical).

### Out of scope for MVP

- Medical diagnosis or treatment advice
- Drug-nutrient interactions (requires clinical validation)
- Calorie/macro tracking
- Integration with EHR systems

---

## Market positioning

- No focused oncology nutrition LLM product exists as a consumer/B2B offering
- Generic nutrition chatbots don't account for treatment-specific side effects
- AI in oncology is growing but mostly focused on diagnostics, not patient support tools
- This is a real gap — patients and caregivers actively search for this kind of guidance

**Differentiator for portfolio:** HIPAA/healthcare SaaS background → credibility to build this properly (data handling, disclaimers, compliance awareness)

---

## Decisions this week

- See `docs/decisions/001-llm-provider.md`
- See `docs/decisions/002-rag-approach.md`
- See `docs/decisions/003-two-tier-knowledge.md` — clinical vs peer knowledge split
- See `docs/concept.md` — product concept

---

## Next week

- [ ] Build core prompt (symptom input → structured recommendation output)
- [ ] Add LangChain basic chain
- [ ] Define RAG knowledge base structure (ESPEN guidelines, ACS guidelines as source docs)
- [ ] First working CLI demo