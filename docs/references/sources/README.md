# Sources: nutrition for oncology patients

Downloaded **2026-05-21** for the `onco-nutrition` project. Use as the domain research and RAG knowledge base.

> **Note:** These materials are for educational purposes. They do not replace medical advice from a doctor or dietitian.

> **Language:** This README is in English. **Archived content files** under `../web/` (mostly Bulgarian) and `../forums/` (mostly English) are kept in **original language** for RAG — do not translate them in place.

---

## Two-tier model (Tier 1 / Tier 2)

| Tier | Trust | UI label | Location in project |
|------|-------|----------|---------------------|
| **`clinical`** | Authoritative medical documentation | “Recommended from clinical guidelines” | This file — PDFs + web (below) |
| **`peer`** | Patient experience, not fact | “What other patients share” | [`../forums/`](../forums/), `data/raw/user-queries/` |

See [concept.md](../../concept.md) · [ADR 003](../../decisions/003-two-tier-knowledge.md)

---

## PDF documents — Tier 1 (`clinical`)

| File | Source | Language | Description |
|------|--------|----------|-------------|
| `acs-nutrition-during-treatment-bg.pdf` | [Bulgarian Lymphoma Association](https://lymphom-bg.com/wp-content/uploads/2019/10/Nutrition-Bg.pdf) | BG | ACS patient booklet (BG) |
| `acs-nutrition-during-treatment-en.pdf` | [American Cancer Society](https://www.cancer.org/content/dam/cancer-org/cancer-control/en/booklets-flyers/nutrition-for-the-patient-with-cancer-during-treatment.pdf) | EN | ACS original |
| `nci-eating-hints.pdf` | [NCI](https://www.cancer.gov/publications/patient-education/eatinghints.pdf) | EN | Eating Hints — symptoms, recipes |
| `espen-clinical-nutrition-in-cancer.pdf` | [ESPEN](https://www.espen.org/files/ESPEN-Guidelines/ESPEN-practical-guideline-clinical-nutrition-in-cancer.pdf) | EN | Clinical nutrition guidelines |
| `seom-nutrition-guidelines-2018.pdf` | [SEOM / Springer](https://link.springer.com/content/pdf/10.1007/s12094-018-02009-3.pdf) | EN | Oncology nutrition guidelines |
| `and-nutrition-therapy-oncology-pq113.pdf` | [Academy of Nutrition and Dietetics](https://www.andeal.org/vault/pq113.pdf) | EN | Nutrition therapy questionnaire |
| `maw-nutrition-oncology-practice-tool.pdf` | [Nutrition Care Org](https://nutritioncare.org/wp-content/uploads/2025/07/MAW-Nutrition-for-Oncology-Patients-Practice-Tool.pdf) | EN | Screening tools (PG-SGA, MUST) |
| `cancerinfo-digestive-cancer-nutrition-journey.pdf` | [CancerInfo.bg](https://cancerinfo.bg/wp-content/uploads/2024/05/24shape1lp_myjourney_fv-19-09-23_approved-1.pdf) | BG | Digestive cancer patient leaflet |

---

## Web sources — Tier 1 (`clinical`)

| File | URL | Language |
|------|-----|----------|
| `../web/onco-bg-problemi-hranene.md` | https://onco.bg/problemi-hranene-onkobolni/ | BG |
| `../web/bgpatients-obshti-preporaki.md` | http://bgpatients.org/.../322-2019-07-17-13-48-43 | BG |
| `../web/cancerinfo-hranene-po-vreme-na-lechenie.md` | https://cancerinfo.bg/.../hranene/ | BG |

## Web sources — Tier 2 (`peer`)

| File | URL | Note |
|------|-----|------|
| `../web/anticancer-bratan-dieta.md` | https://www.anticancer-bg.com/.../ | Experiential tips (BRAT), not clinical guideline |

---

## Tier 2 — forums and patient queries

| Path | Description |
|------|-------------|
| [`../forums/`](../forums/) | CSN + Macmillan archived threads |
| [`../../data/raw/user-queries/`](../../data/raw/user-queries/) | Real queries from interviews |

---

## Topics covered by sources

- Loss of appetite, nausea, vomiting
- Taste and smell changes
- Constipation and diarrhea
- Dry mouth, mouth sores
- Difficulty swallowing
- Unintended weight loss/gain
- Immunocompromised patients — food safety
- Protein, calories, oral nutritional supplements (ONS)
- Malnutrition screening (PG-SGA, MUST)

---

## MVP priority (multilingual knowledge base)

**Tier 1 (clinical):**

1. `acs-nutrition-during-treatment-bg.pdf`
2. `onco-bg-problemi-hranene.md`
3. `cancerinfo-hranene-po-vreme-na-lechenie.md`
4. `espen-clinical-nutrition-in-cancer.pdf` (EN fallback)

**Tier 2 (peer):**

1. `forums/csn/` + `forums/macmillan/` — patient language and meal tricks
2. `data/raw/user-queries/` — real questions (after interviews)

---

## Related documents

- [Concept — two-tier model](../../concept.md)
- [Communities and forums](../communities.md)
- [Collecting user queries](../../user-query-collection.md)
