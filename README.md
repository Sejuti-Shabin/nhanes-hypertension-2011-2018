# Hypertension awareness and healthcare access | NHANES 2011–2018

**Reproducible epidemiology research-training portfolio** · Four NHANES cycles · Python + R · Not peer reviewed

This repository examines two related but **distinct** questions using nationally representative U.S. health-survey data. It builds on an earlier single-cycle analysis, transparently reconstructs a published healthcare-access study, and extends the insurance–awareness association to 2011–2018. This is **observational research, not evidence of causation**.

## Research questions

| Analysis | Question | Population and primary method |
| --- | --- | --- |
| **Study A — approximate published-study reconstruction** | Is lacking an operational *non-emergency* usual place of care associated with greater reported hypertension **unawareness**? | Adults 18–64 with exam BP ≥130/80; survey-adjusted modified Poisson models |
| **Study B — insurance extension** | Is current lack of health insurance associated with lower reported hypertension **awareness**? | Adults 20–64 with measured BP ≥130/80 **or** reported current BP medication; survey-adjusted logistic and modified Poisson models |

The populations, exposures and outcomes are **not interchangeable**. The primary Study A proxy is an explicit reconstruction; exact exposure coding and adjustment choices in Calixte et al. are unavailable in the materials consulted. Neither study should be presented as the causal effect of obtaining insurance or regular care.

## Findings at a glance

| Estimate | Result | Interpretation |
| --- | --- | --- |
| Study A: fully adjusted sample | **4,930** | Versus 5,345 published by Calixte et al.; not an exact replication |
| Study A: reported hypertension unawareness | **55.9%** (95% CI 54.0–57.9) | Published benchmark: 56.2% |
| Study A: association for lacking non-ER usual care | **aPR 1.27** (95% CI 1.18–1.36) | Published adjusted PR: 1.20 (1.12–1.29); formulas not known to be identical |
| Study B: insured awareness | **58.2%** (95% CI 56.0–60.5) | Weighted descriptive estimate; insured descriptive n=5,408 |
| Study B: uninsured awareness | **45.7%** (95% CI 42.1–49.3) | Weighted descriptive estimate; uninsured descriptive n=1,443 |
| Study B: adjusted association | **OR 0.60** (95% CI 0.49–0.75); **PR 0.81** (0.73–0.89) | Model n=6,191; associations, not causal effects |
| Study B: standardized awareness gap | **−11.4 percentage points** (95% CI −16.1 to −6.6) | Model-based marginal comparison |
| Earlier single-cycle comparison | **OR 0.60** (95% CI 0.22–1.62) | 2017–2018 model n=1,534; less precise and overlaps pooled data |

**Key result:** Extending Study B from one cycle to four yields a similar adjusted point estimate with narrower uncertainty. This does **not** make the two time periods independent validation samples, and it does not establish a novel or causal discovery.

## Selected figures

![Survey-weighted outcome comparisons](studies/nhanes_2011_2018/figures/weighted_outcomes.png)

*Figure 1. Weighted descriptive outcomes with design-based 95% confidence intervals. Study A and B have different eligible populations and differently coded outcomes.*

![Adjusted associations and comparison with 2017–2018](studies/nhanes_2011_2018/figures/association_forest.png)

*Figure 2. Adjusted estimates from the reconstruction, multicycle insurance extension, and original one-cycle analysis. Odds and prevalence ratios are different measures and should not be compared as though identical.*

## Compare with the published study

The reconstruction uses **Calixte et al. (2024), Preventive Medicine, DOI: [10.1016/j.ypmed.2023.107843](https://doi.org/10.1016/j.ypmed.2023.107843)** as a literature benchmark. The paper reports n=5,345; 56.2% unawareness; 81.7% with routine care; and an adjusted prevalence ratio of 1.20 (95% CI 1.12–1.29) for lacking routine care. Our reconstructed n=4,930, 55.9%, 78.9%, and aPR 1.27 (1.18–1.36) differ. Because the exact original model formula, exclusions, BP averaging and healthcare-place coding could not be verified, **this work is an approximate reconstruction, not a completed exact replication**.

[Detailed benchmark comparison](studies/nhanes_2011_2018/REPLICATION_COMPARISON.md) · [Definitions and harmonization](studies/nhanes_2011_2018/VARIABLE_HARMONIZATION.md)

## Read the work

- **[Eight-page academic writing sample (PDF)](studies/nhanes_2011_2018/docs/academic_writing_sample_2011_2018.pdf)** — an edited research-paper-style presentation suitable for faculty review after individual verification.
- [Editable writing sample (Word)](studies/nhanes_2011_2018/docs/academic_writing_sample_2011_2018.docx)
- [Full manuscript draft](studies/nhanes_2011_2018/manuscript.md)
- [One-page faculty summary](studies/nhanes_2011_2018/one_page_summary.md)
- [Protocol](studies/nhanes_2011_2018/protocol.md), [methods ledger](studies/nhanes_2011_2018/METHODS_LEDGER.md) and [quality-assurance report](studies/nhanes_2011_2018/QA_REPORT.md)
- [Results tables](studies/nhanes_2011_2018/TABLES.md) and [source documentation](studies/nhanes_2011_2018/DATA_PROVENANCE.md)

## Reproduce the analysis

```bash
cd studies/nhanes_2011_2018
python -m pip install -r requirements.txt
Rscript -e 'install.packages(c("survey", "foreign"), repos="https://cloud.r-project.org")'
python run_all.py
```

The first online run fetches official NHANES XPORT data and codebook files. Offline reruns with existing authentic caches use `python run_all.py --offline`; `python run_all.py --check-only` checks outputs. **R and the `survey` package are required for the full validated workflow.** The repository's QA report documents the environment in which the stored analyses were executed; a new user must rerun it in their own environment before claiming independent reproduction. CDC's multicycle examination weights are constructed as `WTMEC8YR = WTMEC2YR / 4` for the four included cycles, with survey strata and PSUs retained. [Reproducibility instructions](studies/nhanes_2011_2018/REPRODUCIBILITY.md).

## Limitations and responsible use

- Cross-sectional associations; current insurance and lifetime reported diagnosis have ambiguous temporal order.
- Single-visit blood pressure is **not** a confirmed clinical diagnosis. Medication-inclusive and measured-only case definitions select different populations.
- Exact Calixte author choices are unknown; the quantitative differences must not be hidden or forced to match.
- Some modified-Poisson fitted means exceed one. These are working-model limitations; they are not interpreted as probabilities.
- Complete-case analyses and income-response-weighted sensitivity checks depend on assumptions about missingness.
- Source data are historical (2011–2018), not current U.S. hypertension estimates.

**Authorship and research integrity.** This is an AI-assisted research-training project, **not** a peer-reviewed article or faculty-supervised study. The person using this as an application portfolio must check the code, understand the epidemiology, document what they personally contributed, and follow program-specific AI-disclosure rules. No individual applicant, supervisor, funding source or IRB determination is asserted here.

The repository intentionally excludes raw XPORT files, respondent-level derived files, model binaries and private local backups. It includes code, public documentation, aggregate results and publication-style figures. See the [data provenance](studies/nhanes_2011_2018/DATA_PROVENANCE.md) and [QA documentation](studies/nhanes_2011_2018/QA_REPORT.md).
