# Reproducibility

Python3.10+ with pinned requirements; R4.x with `survey` (tested4.5) and `foreign`. Install dependencies, then from this study:

```bash
python -m pip install -r requirements.txt
Rscript -e 'install.packages(c("survey","foreign"), repos="https://cloud.r-project.org")'
python run_all.py
```

Default run obtains56 authentic active XPORT/HTML files, prepares cohorts, executes R reference/robustness, compares equivalent Python calculations, audits baseline tests in an isolated copy when available, executes extension tests, regenerates figures/report/QA. `--offline` requires cached sources; `--check-only` checks existing outputs. No PDF, publication table lookup or network access is needed after data/dependency installation. The optional userR/library search is portable and does not bundle compiled libraries.

Single-cycle reference: the original working-tree copy lives at ../nhanes_2017_2018. Its tests run only in a disposable isolated copy; checksums verify immutability. The full historical tree and person-level frames are excluded from the portable Git export. If absent after a fresh Git checkout, the audit explicitly records that historical tests were not rerun there, and the person-ID comparison test skips. Stored aggregate baseline coefficient comparisons still execute. Local full workspace executes those additional historical checks.

Independent R reconstruction uses `foreign::read.xport`, including all case/exposure/outcome/covariate code mappings and every model domain. R constructs native masked-design objects before `subset`; namespace equivalence is checked. Python calculates weighted scores and Taylor covariance separately from ordinary GLM SE. Validation compares full covariance, coefficients, SE, count/df, descriptor and logistic marginal estimates with rtol2e-6/atol1e-8. Different beta versus Wald descriptor endpoints are intentionally not equated. Every J-only old covariate model is compared with stored original R outputs, not hardcoded values.

JKn refits the nonlinear models and estimated empirical standardization distribution across all actual PSUs (121 in this snapshot). Supplemental PIR response weighting refits auxiliary transformations, response and outcome models within each replicate; it assumes MAR/positivity and is executed only in R, without falsely claiming independent Python reproduction. Poisson fitted means above1 are diagnosed; only logistic predictions are used as bounded probabilities. Numerical/reference calibration choices are explicit in the protocol.

The runner deletes prior success stamps before work, records failed stage/status, and blocks downstream reporting. R execution receipts anchor exact source/input/output hashes; Python refuses stale receipts. Source/output fingerprints prevent current reporting against changed computation artifacts. Publishing benchmark metadata is separate from cohort construction and model fitting. Models are deterministic; seed20261010 is used only for a row-order test. Source/code/data hashes define reproducibility more reliably than PDF metadata or timestamps.

Git exports ignore raw caches, participant-derived CSVs, modelRDS,replicate matrices,local logs and compiled/cache dependencies. Preserve aggregate output/source/figures and relative links. A clean-copy full run and numerical comparison are recorded only after executed; unexecuted checks are not called verified. No source-code license is assigned without the user's choice.
