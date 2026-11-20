# Narration — NCPT explainer

One block per scene. Start/end come from `index.base.html` (`data-s` / `data-e`); `retime.py` stretches scenes to fit.
Wording follows the SNOMED CT Implementation Guide for the Nutrition Care Process Terminology (docs.snomed.org).
Clinical case and codes are taken from the guide's Use Case 1 (Examples 1.1–1.4); all codes validated as active in the International Edition.

| # | Time | Budget | Narration |
|---|------|--------|-----------|
| 1 | 0.5–6 | ~12 | Nutrition care, documented with the same precision as the rest of clinical care. |
| 2 | 6.3–15 | ~22 | Dietitians follow the Nutrition Care Process: assessment, diagnosis, intervention, and monitoring and evaluation. Its standard language is the Nutrition Care Process Terminology. |
| 3 | 15.3–24 | ~20 | The SNOMED CT NCPT Reference Set brings these terms into the EHR: nutrition diagnoses, interventions, and assessment, monitoring and evaluation terms. |
| 4 | 24.3–37 | ~30 | A patient with newly diagnosed type 2 diabetes is referred to a dietitian. In the nutrition assessment, the dietitian records carbohydrate intake — over five hundred grams a day — and poor nutrition knowledge. |
| 5 | 37.3–49 | ~26 | Next, the nutrition diagnosis, as a PES statement: excessive intake of carbohydrate, related to an unbalanced diet, as evidenced by the assessment findings. |
| 6 | 49.3–59 | ~24 | The nutrition intervention: the dietitian delivers content-related nutrition education, and records what it covers — estimated carbohydrate intake in twenty-four hours — to support carbohydrate control and portion sizes. |
| 7 | 59.3–68 | ~20 | At follow-up, monitoring and evaluation uses the same coded observables, so progress is tracked over time instead of retyped. |
| 8 | 68.3–79 | ~24 | Because it's coded, the whole team can read it: endocrinologist, primary care and nurses. And with HL7 FHIR, nutrition data follows the patient across transitions of care. |
| 9 | 79.3–88 | ~18 | Coded nutrition data also supports clinical decision support and research — for example, tailored recommendations in chronic kidney disease. |
| 10 | 88.3–94 | ~14 | Standard terms, better nutrition care. Learn more in the NCPT Implementation Guide at docs.snomed.org. |
