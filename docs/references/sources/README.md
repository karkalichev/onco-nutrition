# Източници: хранене при онкоболни

Свалени на **21.05.2026** за проекта `onco-nutrition`. Използвай като база за domain research и RAG pipeline.

> **Забележка:** Тези материали са за образователни цели. Не заменят медицински съвет от лекар или диетолог.

---

## Двустепенен модел (Tier 1 / Tier 2)

| Tier | Доверие | UI етикет | Къде в проекта |
|------|---------|-----------|----------------|
| **`clinical`** | Авторитетна мед. документация | „Препоръчано от медицински насоки“ | Този файл — PDF + web (долу) |
| **`peer`** | Patient опит, не факт | „Това споделят други пациенти“ | [`../forums/`](../forums/), `data/raw/user-queries/` |

Виж [concept.md](../../concept.md) · [ADR 003](../../decisions/003-two-tier-knowledge.md)

---

## PDF документи — Tier 1 (`clinical`)

| Файл | Източник | Език | Описание |
|------|----------|------|----------|
| `acs-nutrition-during-treatment-bg.pdf` | [Българско сдружение „Лимфом"](https://lymphom-bg.com/wp-content/uploads/2019/10/Nutrition-Bg.pdf) | BG | ACS patient booklet (BG) |
| `acs-nutrition-during-treatment-en.pdf` | [American Cancer Society](https://www.cancer.org/content/dam/cancer-org/cancer-control/en/booklets-flyers/nutrition-for-the-patient-with-cancer-during-treatment.pdf) | EN | ACS original |
| `nci-eating-hints.pdf` | [NCI](https://www.cancer.gov/publications/patient-education/eatinghints.pdf) | EN | Eating Hints — symptoms, recipes |
| `espen-clinical-nutrition-in-cancer.pdf` | [ESPEN](https://www.espen.org/files/ESPEN-Guidelines/ESPEN-practical-guideline-clinical-nutrition-in-cancer.pdf) | EN | Clinical nutrition guidelines |
| `seom-nutrition-guidelines-2018.pdf` | [SEOM / Springer](https://link.springer.com/content/pdf/10.1007/s12094-018-02009-3.pdf) | EN | Oncology nutrition guidelines |
| `and-nutrition-therapy-oncology-pq113.pdf` | [Academy of Nutrition and Dietetics](https://www.andeal.org/vault/pq113.pdf) | EN | Nutrition therapy questionnaire |
| `maw-nutrition-oncology-practice-tool.pdf` | [Nutrition Care Org](https://nutritioncare.org/wp-content/uploads/2025/07/MAW-Nutrition-for-Oncology-Patients-Practice-Tool.pdf) | EN | Screening tools (PG-SGA, MUST) |
| `cancerinfo-digestive-cancer-nutrition-journey.pdf` | [CancerInfo.bg](https://cancerinfo.bg/wp-content/uploads/2024/05/24shape1lp_myjourney_fv-19-09-23_approved-1.pdf) | BG | Digestive cancer patient leaflet |

---

## Уеб източници — Tier 1 (`clinical`)

| Файл | URL | Език |
|------|-----|------|
| `../web/onco-bg-problemi-hranene.md` | https://onco.bg/problemi-hranene-onkobolni/ | BG |
| `../web/bgpatients-obshti-preporaki.md` | http://bgpatients.org/.../322-2019-07-17-13-48-43 | BG |
| `../web/cancerinfo-hranene-po-vreme-na-lechenie.md` | https://cancerinfo.bg/.../hranene/ | BG |

## Уеб източници — Tier 2 (`peer`)

| Файл | URL | Бележка |
|------|-----|---------|
| `../web/anticancer-bratan-dieta.md` | https://www.anticancer-bg.com/.../ | Experiential tips (BRAТ), не клинична насока |

---

## Tier 2 — форуми и patient queries

| Път | Описание |
|-----|----------|
| [`../forums/`](../forums/) | CSN + Macmillan archived threads |
| [`../../data/raw/user-queries/`](../../data/raw/user-queries/) | Real BG queries from interviews |

---

## Ключови теми, покрити от източниците

- Загуба на апетит, гадене, повръщане
- Промени във вкус и обоняние
- Запек и диария
- Сухота в устата, язви в устата
- Трудности при преглъщане
- Непредвидена загуба/наддаване на тегло
- Имунокомпрометирани пациенти — хигиена на храната
- Белтъци, калории, хранителни добавки (ONS)
- Скрининг за малnutrition (PG-SGA, MUST)

---

## Приоритет за MVP (български потребители)

**Tier 1 (clinical):**
1. `acs-nutrition-during-treatment-bg.pdf`
2. `onco-bg-problemi-hranene.md`
3. `cancerinfo-hranene-po-vreme-na-lechenie.md`
4. `espen-clinical-nutrition-in-cancer.pdf` (EN fallback)

**Tier 2 (peer):**
1. `forums/csn/` + `forums/macmillan/` — patient language & meal tricks
2. `data/raw/user-queries/` — real BG questions (after interview)

---

## Свързани документи

- [Концепция — two-tier model](../../concept.md)
- [Общности и форуми](../communities.md)
- [Събиране на user queries](../../user-query-collection.md)
