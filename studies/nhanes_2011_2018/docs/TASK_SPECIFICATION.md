# Codex task: NHANES 2011–2018 replication and insurance-analysis extension

You are an epidemiologist, survey statistician, and senior Python/R research engineer working inside my existing `nhanes-dataset-hypertension` Git repository.

**Complete the work, do not only describe a plan.** Inspect the repository, implement the multicycle analysis, run code and tests, and produce reproducible results. The Calixte et al. PDF is **not available**. Everything you may treat as verified from that paper is written below. Do not require the paper to proceed, and do not invent unpublished or unverified methods to make results match.

## Scientific goals

Preserve the existing NHANES 2017–2018 study **unchanged** as a historical baseline. Create a separate extension under `studies/nhanes_2011_2018/` with two linked but scientifically distinct analyses:

**Study A — independent, approximate replication of Calixte et al. (2024):** Investigate the association between lacking a routine, non-emergency place of healthcare and *hypertension unawareness* among US adults aged 18–64 with **measured elevated blood pressure** using NHANES 2011–2018. Aim to compare published sample and estimates, without fitting to the expected results.

**Study B — insurance extension of our existing study:** Investigate the association between lacking health insurance and hypertension **awareness** using NHANES 2011–2018. Hold the population, hypertension definition, outcome coding, and adjustment set comparable with our existing 2017–2018 project in the primary extension. Also provide a harmonized measured-BP-only comparison on 2011–2018 where possible. Do not confuse the exposures or outcomes of Studies A and B.

## Verified published-study reference (the ONLY paper-specific facts you may assume)

Calixte R, Chahal K, Besson A, Kaplan MS. “Access to routine health care and awareness of hypertension status among adults: Results from the National Health and Nutrition Examination Survey, 2011–2018.” *Preventive Medicine*. 2024;179:107843. DOI `10.1016/j.ypmed.2023.107843`. PMID `38176445`.

The accessible abstract and excerpts establish:

- NHANES **2011–2018**, four ordinary 2-year cycles (not 2017–March 2020 prepandemic files).
- US adults **18–64** (not 20–64) for the reported replication population.
- Hypertension eligibility based on *measured* systolic BP **>=130 mmHg** or diastolic BP **>=80 mmHg**, under 2017 ACC/AHA stage 1/2 thresholds. Do **not** silently add medication-only cases to Study A.
- Outcome: **unawareness** = meeting the measured threshold while reporting **no previous professional diagnosis** of hypertension.
- Primary exposure: **lack of a routine place of healthcare**, with attention to **non-emergency** care.
- Reported analysis: **multivariable Poisson regression** giving a prevalence ratio after adjustment for sociodemographic and clinical factors. The *exact* complete adjustment formula and all exclusion/recoding decisions are **not verified** here.
- Published results to use as **external benchmarks only**: final unweighted analytic sample **n=5,345**; weighted hypertension unawareness **56.2%**; **81.7%** have a routine place of care; adjusted PR for unawareness when lacking routine care vs having it **1.20**, 95% CI **1.12–1.29**, p < 0.001.
- These are **not expected hardcoded outputs**. Never tweak a definition or analysis solely to hit a benchmark. Label the result an **approximate/independent replication**, unless every detail is independently verified from additional reliable source documents. Clearly report mismatches and unknown details.

Publisher: `https://doi.org/10.1016/j.ypmed.2023.107843`
Abstract: `https://pubmed.ncbi.nlm.nih.gov/38176445/`

## Authoritative CDC reference facts

- Four cycles and dataset suffixes: 2011–2012 (`_G`), 2013–2014 (`_H`), 2015–2016 (`_I`), 2017–2018 (`_J`).
- Core files per cycle: `DEMO`, `BPX`, `BPQ`, `HUQ`, `HIQ`. Use `BMX`, `DIQ`, `SMQ` or other files only if a clearly justified prespecified model needs them. Check their eligible populations and weights.
- Download official `.XPT` files from CDC; use source URLs recorded in a provenance manifest. Merge component files **within** cycle by `SEQN`, then append harmonized cycles; preserve a `cycle` variable and verify IDs.
- `RIDAGEYR`: age; `RIAGENDR`: sex; `RIDRETH3`: race/ethnicity; `DMDEDUC2`: education (check eligibility); `INDFMPIR`: income-to-poverty ratio.
- BP measurements: investigate `BPXSY1`, `BPXSY2`, `BPXSY3` and `BPXDI1`, `BPXDI2`, `BPXDI3`, plus any fourth readings if present. Inspect each cycle's examination protocol and codebook; average valid exam measurements using a documented rule. Handle missing, zero DBP, and invalid readings according to CDC guidance rather than silently applying arbitrary thresholds. Include an alternate justified averaging strategy as sensitivity analysis.
- `BPQ020`: ever told by a doctor or other health professional that participant had hypertension. Common coding `1=yes`, `2=no`, `7=refused`, `9=don't know`. Validate **per cycle**. Study A: `unaware=1` for `BPQ020==2` among eligible measured high-BP participants; `BPQ020==1` implies awareness. Missing/refused/don't know are **not** counted as unaware.
- `HUQ030`: whether respondent has a place they usually go when ill or needing health advice. Common responses: `1=yes`, `2=no place`, `3=more than one place`, `7/9=refused/don't know`. Verify per cycle. The type-of-place follow-up variable changes: e.g. `HUQ040` in 2011–2012 vs `HUQ041` in 2017–2018. Verify exact variables and valid categories separately in **all four** codebooks. Consider emergency-room-only routine care separately; do not assume whether/how Calixte excluded it without evidence. Define a main operationalization with explicit justification and sensitivity with alternate handling.
- `HIQ011`: insurance coverage; verify response coding in each cycle. For Study B, insured/uninsured is the primary exposure, **not** a proxy for `HUQ030`.
- If required for Study B's original medication-inclusive hypertension definition, check `BPQ050A` (current prescribed medication) and distinguish from `BPQ040A` (ever instructed to take medicine). Do not infer medication from skip-pattern missingness.
- `WTMEC2YR`, `SDMVSTRA`, `SDMVPSU`: examination survey weight and masked strata/PSUs. For 2011–2018 with four equal 2-year MEC cycles, define `WTMEC8YR = WTMEC2YR / 4`. Use the appropriate component weights if you introduce subsample-specific lab data. Verify eligible records and positive weights.
- Build the full design using the pooled data before domain/subpopulation restrictions. In R, use `survey::svydesign(ids=~SDMVPSU, strata=~SDMVSTRA, weights=~WTMEC8YR, nest=TRUE, data=...)`, then `subset(design, ...)`. Follow CDC procedures for lonely PSUs, survey degrees of freedom, and missingness; record chosen options. Do not treat ordinary frequency-weighted GLMs as valid survey inference.

CDC documentation:
- `https://wwwn.cdc.gov/nchs/nhanes/tutorials/weighting.aspx`
- `https://wwwn.cdc.gov/nchs/nhanes/tutorials/varianceestimation.aspx`
- `https://wwwn.cdc.gov/nchs/nhanes/tutorials/datasets.aspx`
- 2017–2018 BPQ: `https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/BPQ_J.htm`
- 2017–2018 HUQ: `https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/HUQ_J.htm`
- 2011–2012 HUQ: `https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/HUQ_G.htm`

## Execution requirements

### Phase 0 — audit and preserve

1. Inventory current scripts, dependencies, tests, results, and how the 2017–2018 sample was defined.
2. Create `studies/nhanes_2011_2018/`; do **not** overwrite the original manuscript, figures, outputs, or code. If useful, extract reusable functions without breaking the original pipeline.
3. Write `METHODS_LEDGER.md` recording each verified fact, any methodological approximation, each cycle's relevant variable mapping, and any deviations from previous 2017–2018 work.
4. Write a dated `protocol.md` with hypotheses, estimands, prespecified main model, sensitivity analyses, and limitations *before inspecting new outcome estimates*. State that previous single-cycle results were known; do not falsely call this prospectively preregistered.

### Phase 1 — data and cohort construction

1. Implement official CDC XPT downloader with retries, URL provenance, checksum if possible, and local caching. Do not depend on the publication PDF.
2. Harmonize variable schemas and category codes per cycle and create `VARIABLE_HARMONIZATION.md`.
3. Produce separate flowcharts for Study A (18–64, measured BP) and Study B (original comparable 20–64 and existing hypertension rules); show every exclusion as an **unweighted count** and identify survey domain samples.
4. Document blood-pressure averaging, missingness, unusual values, participant IDs, insurance responses, and routine-place-of-care responses.
5. Include per-cycle descriptive counts, missingness percentages and diagnostic tables.

### Phase 2 — Study A: Calixte approximate replication

1. Age 18–64, measured high BP only (SBP >=130 or DBP >=80). Do **not** use medication-only hypertension for this primary replication.
2. Outcome `unaware=1` for `BPQ020==2`; `0` for `BPQ020==1`.
3. Main exposure `no_routine_non_emergency_care`, derived from `HUQ030` and type-of-place follow-ups. Document treatment of respondents reporting multiple locations and emergency-room-only care. Use alternate operationalizations as sensitivity analyses.
4. Calculate survey-weighted unawareness prevalence and routine-care prevalence, with design-based standard errors/CIs and unweighted group n.
5. Run survey-adjusted Poisson regression with log link in R (`svyglm(..., family=quasipoisson(link="log"))`) to estimate adjusted prevalence ratios and 95% CIs. Handle variable selection based on a prespecified, scientifically justified adjustment plan. At minimum consider age, sex, race/ethnicity, socioeconomic status, and other defensible measured confounders; clearly **label this a reconstructed model**, not Calixte's exact formula, because the exact formula is unavailable.
6. Benchmark n=5,345, awareness/unawareness 56.2%, routine-care 81.7%, adjusted PR=1.20 [1.12, 1.29]. Create `REPLICATION_COMPARISON.md` with columns: publication benchmark, our result, difference, plausible reasons. Do not optimize models merely to match the publication.
7. Report both what agrees and what differs, including how the approximation limits replication claims.

### Phase 3 — Study B: 2011–2018 insurance extension

1. Use **our repository's original 2017–2018 primary estimand and model variables** as the starting point. Preserve original age 20–64 and medication-inclusive hypertension definition if that is indeed how existing code specifies it. Audit the definitions instead of relying on narrative summaries.
2. Expand identical rules across 2011–2018, harmonizing covariate and exposure definitions across cycles.
3. Outcome = hypertension **awareness**; exposure = `uninsured` vs `insured`.
4. Report the old single-cycle baseline (from original reproducible outputs), the new eight-year result, and a comparable eight-year measured-BP-only result. Never treat Study A and Study B estimates as interchangeable.
5. Calculate weighted awareness by insurance status, adjusted prevalence ratios using survey Poisson models, adjusted odds ratios using survey logistic models, and adjusted predicted probability differences where reliable and scientifically justified.
6. Prespecify adjustment steps such as unadjusted; age/sex; age/sex/race-ethnicity/education/income; verify stability and design degrees of freedom. If the original primary model used a different covariate set, explicitly report that discrepancy and provide a matched-model comparison.
7. Report no statistical significance unless actually supported by design-based inference.

### Phase 4 — validation and robustness

- Use Python (pandas, NumPy, plotting) for ETL, QA, and figures; use R `survey` as the authoritative survey inference implementation. If R is absent, still write the scripts and mark results **unvalidated**, rather than fabricate results.
- Test CDC sample file consistency, within-cycle `SEQN` uniqueness, no duplicate merges, missing codes, valid BP averaging, exposure/outcome definitions, weight divisors, design variables, and that 2017–2018 extension rows match the original rules when applicable.
- Evaluate 130/80 vs 140/90; measured-only vs medication-inclusive for the insurance extension; routine-care classifications; age 18–64 vs 20–64 only as labeled sensitivity; incomplete covariate cases; alternative scientifically justified income handling.
- Evaluate whether sparse uninsured groups, lonely PSUs, low design degrees of freedom, or missingness make some estimates unreliable. Clearly flag unstable estimates; do not automatically add more variables or subgroups.
- No p-value hunting. No causal language. No extrapolation to the 2021–2023 period.

### Phase 5 — faculty-facing outputs

Under `studies/nhanes_2011_2018/`, generate:

1. `README.md`: questions, data, results, limitations, execution instructions, links to the original work.
2. `protocol.md` and `METHODS_LEDGER.md`.
3. `VARIABLE_HARMONIZATION.md` and `DATA_PROVENANCE.md`.
4. Reproducible Python pipeline and R `survey` analysis scripts.
5. Unit/integration tests; pinned Python/R dependencies or environment instructions.
6. Cohort selection flowchart and Tables 1–3 (descriptives; Calixte benchmark comparison; insurance models).
7. Two or three publication-quality figures (aggregate estimates with CIs, forest plot, sensitivity comparison).
8. `manuscript.md`: scientific 8–10-page-style write-up with the Study A replication and Study B extension clearly separated, honest interpretation, and verifiable citations. Avoid false novelty claims.
9. `one_page_summary.md`: suitable to send a public-health faculty member; emphasize what was genuinely learned, and explain any AI assistance and validation status transparently.
10. `QA_REPORT.md`: what executed; passed/failed tests; reproducibility commands; known mismatches and outstanding validation.

Make the project GitHub-ready: no compiled dependencies, caches, system-specific file paths, secrets, private data, or participant-level derived CSVs committed by default. Download XPT source files locally in a gitignored directory; commit source code, documentation, aggregate results, and small figures.

## Completion criteria and reporting

Actually execute the workflow when data and dependencies are available. If official data downloads fail, do not substitute fabricated inputs or invented figures; keep a runnable pipeline and explicitly report the blocker.

At completion, show: exact files changed, data cycles downloaded, cohort sizes, survey degrees of freedom, published-vs-reproduced Calixte estimates, original-vs-extended insurance results, sensitivity analysis highlights, tests executed, methods that are still approximate, and what remains for faculty review.

**Research integrity rule:** A failure to reproduce Calixte's exact sample or effect size is a legitimate result if documented and carefully investigated. Do not reverse-engineer definitions to force a match. This is a research-training replication and extension, not a claim of an original discovery or peer-reviewed publication.
