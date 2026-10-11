# Four-cycle analysis plan: 2011–2018

Version 1, October 10, 2026. Written after inspecting official variable documentation and before fitting pooled analyses. Previous single-cycle results and publication benchmarks are known. This is a retrospective, protocol-guided replication attempt and extension, not preregistration, independent confirmation, or a causal study. The reviewed 2017–2018 primary definition is preserved; no original file is changed.

## Sources and published-method evidence
Use CDC 2011–2012 G, 2013–2014 H, 2015–2016 I and 2017–2018 J. Core components: DEMO, BPX, BPQ, HIQ, HUQ; Calixte clinical variables additionally require BMX, SMQ and DPQ. DIQ/MCQ were retrieved during source exploration but are not part of the main models. Cache XPORT and codebooks and verify hashes.

Calixte et al. Preventive Medicine. 2024;179:107843, doi:10.1016/j.ypmed.2023.107843. Publisher/institution abstracts were verified. The user supplied Methods sections 2.1–2.4 after the temporary publisher PDF link failed (403). Full PDF, Appendix A, regression tables and supplementary exclusion/missingness details remain unavailable. Therefore do not claim exact replication. Verified/unknown decisions are mapped in REPLICATION_METHODS.md and a machine-readable specification. Benchmarks are comparison metadata, never inputs to data selection or fitting.

## Objective 1: Calixte replication attempt

Nominal population: examined ages 18–64, stage 1/2 measured BP (≥130 SBP or ≥80 DBP), excluding measured normal/elevated below those hypertension thresholds. Medication alone does not establish a Calixte case. Primary readings are arithmetic means of readings 2 and 3, requiring both of each BP type because the supplied Methods invokes averaging at least two. This strict missing-reading interpretation is an assumption; use available 2–3 as a prespecified sensitivity, not a matching algorithm.

Outcome: unawareness, BPQ020=2 versus 1; refusals/don't-know/missing remain missing. Exposure: no single routine place, HUQ030=2 or 3 versus 1. Do not impose an ED exclusion not stated for the primary exposure. HUQ040 in G versus HUQ041 later cycles provides an exploratory care-type variable, not primary eligibility.

Covariates from the supplied Methods: five age groups 18–24,25–34,35–44,45–54,55–64 (the supplied 45–44 is interpreted as an obvious reversed-range typo and flagged); sex; four race/ethnicity groups White, Black, Hispanic (Mexican/other combined), Other (Asian/multiracial); college graduate versus below; household-income categories <20k,20–44,999,45–74,999,≥75k; obesity BMI≥30; never/former/current smoking; PHQ-9.

Use INDHHIN2 because Methods says household income; Appendix variable identity is unknown. Codes 1–4/13 -> <20k,5–7 ->20–44,999,8–10 ->45–74,999,14/15 ->≥75k; code12 only establishes ≥20k and cannot locate one upper category, so preserve as missing. Family INDFMIN2 coding is a separately labeled ambiguity sensitivity. Refusal/unknown income remains missing.

Education: DMDEDUC2 for adults20+; for18–19, DMDEDUC3 grade0–14/55/66 establishes below-college completion, while code15 (more than high school) does not distinguish degree and remains unknown. Adult-only coding is a sensitivity. This author-harmonization detail is unverified. SMQ020/040 are asked at20+ in G/H and18+ in I/J; do not call structurally missing younger adults never-smokers. Never=SMQ0202; former=SMQ0201 and SMQ0403; current=SMQ0201 and SMQ0401/2; otherwise unknown.

PHQ-9: all nine DPQ items0–3 must be observed; sum0–27, no invented zero for missing items. Model continuous score, consistent with the supplied summary of means; model binary≥10 separately as a sensitivity because regression parameterization is unconfirmed. BMI binary≥30. No extra arbitrary clinical trimming.

C1 exposure alone; C2 additionally age group, sex and four-category race; C3 add college and household income; C4 add obesity, smoking and PHQ9. Fit survey quasi-Poisson with log link, Taylor inference. All reported covariates retained instead of recreating an unknown p-value selection algorithm. Primary C1–C4 use a common C4-complete cohort; stage-specific complete cases are sensitivities because paper missingness policy is unknown. CI reference residual design df, alternative full-design df and normal calibration explicitly tabulated; do not choose by benchmark agreement. Poisson fitted values>1 are diagnosed and not plotted as probabilities. PHQ9 internal consistency is an ancillary unweighted alpha with its population explicit, not survey inference.

## Objective 2: Insurance extension

Preserve reviewed primary: ages20–64, first-three available separate BP means, DBP zero valid, case if a known elevated mean component≥130/80 or current BPQ050A medication, admit medication-confirmed cases without BP. Medication skip-no only for BPQ0202 or BPQ0201/BPQ040A2; other unknowns remain missing. Awareness=BPQ0201, uninsured=HIQ0112 (insured=1), unknown responses excluded. Normal BP with unknown medication is not a confirmed negative.

I1 uninsured; I2 add continuous centered age per decade and sex; I3 add six-category race, four-category education and continuous top-coded PIR. Add cycle fixed effects to all pooled insurance models to account for period composition; report a no-cycle sensitivity to distinguish this from the single-cycle specification. Fit logistic for OR and modified quasi-Poisson for PR, with the same I3 complete-case population. Logistic weighted standardization yields adjusted probabilities and uninsured-minus-insured awareness difference over the I3 complete-case covariate distribution. Joint Taylor influence includes coefficient and covariate-distribution uncertainty and is checked by refitted R JKn replicates. Bound probability intervals via logit; primary marginal reference matches model residual df.

Usual care is not a primary insurance covariate because it may mediate access. Current insurance and lifetime diagnosis have unknown temporal ordering; PIR may follow illness. Associations are not identified causal effects; conditional OR comparisons are also affected by noncollapsibility.

## Survey design and comparisons

All examined positive-weight participants define the full pooled design before any domains. WTMEC8YR=WTMEC2YR/4. Use cycle-stratum IDs and nested cycle-stratum-PSU IDs, no FPC, lonely PSU fail. Preserve zero domain influences and retain the full design. Check both native masked design IDs and namespaced IDs; report actual PSUs/strata/df and no accidental release overlap. CDC weighting guidance: https://wwwn.cdc.gov/nchs/nhanes/tutorials/weighting.aspx . Enhanced 2017–2018 weights are used as released.

Replicate the prior J-only I1–I3 models and descriptors in the new directory and compare actual prior stored outputs by numeric tolerance, not hardcoded n or coefficients. Four-row comparison distinguishes published Calixte, attempted Calixte, pooled insurance and reviewed J-only insurance, with outcomes/exposures/populations labeled and comparisons not implied interchangeable.

## Sensitivities, missingness and diagnostics

Calixte: available2–3, adult-only education, family-income substitution, PHQ≥10, alternative 1/3 versus2 care collapse, and stage-specific complete cases. These resolve documented ambiguities transparently; no selecting closest-to-benchmark specification.

Insurance: measured-only130/80, medication-inclusive140/90, BP-complete, readings2–3, excluding known pregnancy, omit-PIR, no cycle, common-sample simpler models, quadratic age and categorical PIR. Complete cases do not establish representativeness. Tabulate every variable's missingness by cycle and analytic domain, unweighted flow and weighted retention. Quantify ascertainment unknowns and medication components. Additional PIR response-weighting under a stated MAR assumption uses survey JKn with nuisance/outcome refits, not fixed-response-weight variance. MNAR remains unidentified.

Diagnose convergence/rank, category/event support, extreme weights, prediction range, Poisson>1, covariance eigenvalues, score equations and sampling-unit influence. Report model failures rather than creating fictitious estimates. No multiple testing significance search or causal interpretation.

## Reproducibility and limitations

One command regenerates authentic-source processing, independent R coding/domain checks, Taylor/descriptive/regression outputs, JKn sensitivities, Python comparisons, tests, figures, report and comparative results. No random estimation; seed20261010 for deterministic reorder tests. Preserve original hashes and enforce stale-success protection. Distinguish verified implementations from unknown published choices. Exact replication remains unverified without Appendix/regression/missingness details even if some benchmarks agree.
