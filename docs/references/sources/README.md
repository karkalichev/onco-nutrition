# Sources: nutrition for oncology patients

Catalog of **clinical (Tier 1)** and linked **peer (Tier 2)** materials for the `onco-nutrition` RAG demo.

> **Note:** Educational use only — not medical advice.

> **Copyright:** Third-party PDFs and pages belong to their publishers. This repo stores **download links** only. Run `python -m src.cli download-sources` locally to fetch PDFs for ingest (see [MIT / portfolio notice](../../../README.md#data--sources)).

> **Language:** Archived **content** under `../web/` (mostly Bulgarian) and `../forums/` (English) stays in original language for retrieval.

---

## Two-tier model

| Tier | Trust | UI label | In this project |
|------|-------|----------|-----------------|
| **`clinical`** | Authoritative | “Recommended from clinical guidelines” | PDFs (local) + `../web/` |
| **`peer`** | Anecdotal | “What other patients share” | [`../forums/`](../forums/), `data/raw/user-queries/` |

See [concept.md](../../concept.md) · [ADR 003](../../decisions/003-two-tier-knowledge.md)

---

## PDF documents — Tier 1 (`clinical`)

**Not in git.** Manifest: [`pdfs.yaml`](pdfs.yaml)

```bash
python -m src.cli download-sources
# optional: python -m src.cli download-sources --force
```

Files are saved to this directory (`docs/references/sources/*.pdf`, gitignored).

| Local filename (after download) | Official link | Lang |
|---------------------------------|---------------|------|
| `acs-nutrition-during-treatment-bg.pdf` | [Bulgarian Lymphoma Association — ACS booklet BG](https://lymphom-bg.com/wp-content/uploads/2019/10/Nutrition-Bg.pdf) | BG |
| `acs-nutrition-during-treatment-en.pdf` | [American Cancer Society — Nutrition during treatment](https://www.cancer.org/content/dam/cancer-org/cancer-control/en/booklets-flyers/nutrition-for-the-patient-with-cancer-during-treatment.pdf) | EN |
| `nci-eating-hints.pdf` | [NCI — Eating Hints](https://www.cancer.gov/publications/patient-education/eatinghints.pdf) | EN |
| `espen-clinical-nutrition-in-cancer.pdf` | [ESPEN — Clinical nutrition in cancer](https://www.espen.org/files/ESPEN-Guidelines/ESPEN-practical-guideline-clinical-nutrition-in-cancer.pdf) | EN |
| `seom-nutrition-guidelines-2018.pdf` | [SEOM / Springer — 2018 guidelines](https://link.springer.com/content/pdf/10.1007/s12094-018-02009-3.pdf) | EN |
| `and-nutrition-therapy-oncology-pq113.pdf` | [Academy of Nutrition and Dietetics](https://www.andeal.org/vault/pq113.pdf) | EN |
| `maw-nutrition-oncology-practice-tool.pdf` | [Nutrition Care Org — MAW practice tool](https://nutritioncare.org/wp-content/uploads/2025/07/MAW-Nutrition-for-Oncology-Patients-Practice-Tool.pdf) | EN |
| `cancerinfo-digestive-cancer-nutrition-journey.pdf` | [CancerInfo.bg — digestive cancer leaflet](https://cancerinfo.bg/wp-content/uploads/2024/05/24shape1lp_myjourney_fv-19-09-23_approved-1.pdf) | BG |

If a download fails (e.g. Springer paywall), open the link manually, save the PDF under the filename above, then run `ingest`.

---

## Web sources — Tier 1 (`clinical`)

Archived markdown in repo (links for provenance):

| File | URL |
|------|-----|
| [`../web/onco-bg-problemi-hranene.md`](../web/onco-bg-problemi-hranene.md) | https://onco.bg/problemi-hranene-onkobolni/ |
| [`../web/bgpatients-obshti-preporaki.md`](../web/bgpatients-obshti-preporaki.md) | http://bgpatients.org/index.php/en/responsive-layout/grizi/68-2019-07-17-13-45-13/322-2019-07-17-13-48-43 |
| [`../web/cancerinfo-hranene-po-vreme-na-lechenie.md`](../web/cancerinfo-hranene-po-vreme-na-lechenie.md) | https://cancerinfo.bg/za-paczienti-i-semejstvata/po-vreme-na-lechenieto/zdravosloven-nachin-na-zhivot/hranene/ |

## Web sources — Tier 2 (`peer`)

| File | URL | Note |
|------|-----|------|
| [`../web/anticancer-bratan-dieta.md`](../web/anticancer-bratan-dieta.md) | https://www.anticancer-bg.com/nutrition-in-cancer/eating-to-during-after-combination-therapy/ | Experiential (BRAT), not clinical guideline |

---

## Tier 2 — forums and patient queries

| Path | Description |
|------|-------------|
| [`../forums/`](../forums/) | CSN + Macmillan archived threads |
| [`../../data/raw/user-queries/`](../../data/raw/user-queries/) | Interview queries (local, often gitignored) |

---

## MVP ingest priority

**Tier 1:** ACS BG PDF + `onco-bg` + `cancerinfo` web + ESPEN PDF (after download)  
**Tier 2:** `forums/` + future `user-queries/`

Then: `python -m src.cli ingest`

---

## Related documents

- [Concept](../../concept.md)
- [Communities](../communities.md)
- [User query collection](../../user-query-collection.md)
