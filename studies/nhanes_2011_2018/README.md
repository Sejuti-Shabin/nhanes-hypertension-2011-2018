# NHANES 2011–2018: approximate routine-care replication and matched insurance extension

Two distinct historical association studies, not an exact Calixte reproduction or a causal analysis.

| Study | Population/outcome/exposure | Main calculated result |
|---|---|---|
| A |18–64,measured≥130/80;unawareness; reconstructed lack of non-ER routine care |n=4,930,aPR1.27 (95% CI 1.18–1.36) |
| B |20–64,measured≥130/80 or reported medication;awareness;uninsured vsinsured |n=6,191,aOR0.60 (95% CI 0.49–0.75),aPR0.81 (95% CI 0.73–0.89) |
| Preserved2017–2018 |Original matched insurance model |n=1,534,aOR0.60 (95% CI 0.22–1.62) |

A's unawareness55.9% and routine-care78.9% differ from published56.2%/81.7%. Its adjusted n differs from5345. The exact paper formula, BP rule, exclusions and care coding are unknown; all choices and differences are explicit. Study B preserves original positive-case membership and covariates. No skipped medication status is imputed in the extension.

![Aggregate outcomes](figures/weighted_outcomes.png)

## Read and reproduce

- [Protocol](protocol.md),[methods ledger](METHODS_LEDGER.md),[harmonization](VARIABLE_HARMONIZATION.md),[provenance](DATA_PROVENANCE.md).
- [Tables1–3](TABLES.md),[replication discrepancies](REPLICATION_COMPARISON.md),[manuscript](manuscript.md).
- [Faculty summary](one_page_summary.md),[QA/execution limits](QA_REPORT.md).
- Historical working-tree copy: `../nhanes_2017_2018/`; aggregate historical reference data are bundled in `reference/single_cycle/` and survive a portable export.

```bash
python -m pip install -r requirements.txt
Rscript -e 'install.packages(c("survey","foreign"), repos="https://cloud.r-project.org")'
python run_all.py
```

`python run_all.py --offline` uses locally cached raw files; `--check-only` verifies current artifacts. First online run downloads56 official XPORT/codebook files for7 components×4cycles. No PDF is required. R survey4.5 is the tested reference; exact Python versions and R session metadata are recorded. Code paths are relative and portable; no local dependency binaries are bundled.

## Scientific checks and limits

WTMEC8YR=WTMEC2YR/4, full design before domains, actual pooled df=62. Covariate/sample counts, group-specific df, NCHS screening, full covariance comparisons, independent R raw-variable/mask checks and J-only comparison are explicit. R JKn uses121PSU replicates. Poisson fitted means>1 are flagged; only logistic predictions supply bounded probabilities. PIR response weighting is MAR-dependent and R-only, not independently verified in Python.

Cross-sectional temporal ambiguity, treatment/awareness-linked selection, complete cases, uncertain published details, sparse support and historical nonresponse remain. There is no novelty/publication/causal or current-population claim.

## GitHub-ready layout

Raw sources, participant-level `outputs/design_frame.csv`,RDS models,replicate matrices,cache folders andlocal logs are gitignored. Source code, documentation,small aggregate tables andfigures are the intended export. The unchanged historical working tree and preliminary exploration are preserved locally but excluded from the new portable Git export; small aggregate baseline references remain. Authorship,code licensing,funding andinstitutional review status require factual applicant input; none is invented.
