# Executed QA report

Completed October10,2026 using the final self-contained prompt; no PDF required. Final Study A methods are constructed, not Calixte's verified full formula. Final plan was documented before revised fitting, but preliminary pooled results were already known and that chronology is disclosed.

## Files and preservation

New extension: studies/nhanes_2011_2018. Original working-tree files verified unchanged: 187. Original code/results/manuscripts were not overwritten. Historical tests returncode: 0; execution scope: Historical tests ran in isolated copy; baseline not rerun in place. Exact generated file inventory: outputs/artifact_manifest.json. Existing preliminary exploration remains distinct from the final project. No remote/commit/publication was created.

## Data and populations

Active sources: four ordinary G/H/I/J cycles,seven components,28XPORT +28HTML codebooks. Cached preliminary extra components are not used. Authentic hashes and CDC URLs are preserved. Full positive-exam frame n=37,399,strata=59,PSUs=121,full design df=62. WTMEC8YR=WTMEC2YR/4; native versusnamespace design equivalence passed. Domains were defined after the full survey object.

Study A: measured case-eligible n=5,571; primary complete model n=4,930; PR 1.265(CI 1.176–1.361),p=3.65e-08. Published benchmark n5345,unawareness56.2%,routine81.7%,PR1.20[1.12,1.29]. Actual differences and denominators are in REPLICATION_COMPARISON.md. This is an approximate independent reconstruction, not a successful exact reproduction. Routine/ER/multiple care classification, averaging, true published adjustment/exclusions and missingness remain unknown.

Study B: case-eligible n=6,864; primary n=6,191; OR 0.604(CI 0.488–0.747),PR 0.806(CI 0.731–0.888). Matched J-only n=1,534,OR 0.601(CI 0.223–1.619) reproduced from stored historical values. Cycles are absent from matched primarycovariates and present only in a labeled sensitivity. No skipped medication status was inferred; positive-case comparability is verified separately from negative-status denominators.

## Executed verification

- 17 extension tests run; 17 passed; 0 skipped; 0 failures; 0 errors. Historical tests ran only in an isolated copy when available; logs retained locally.
- R independently reconstructed 39 variables and 40 model masks from authentic raw components. Python/R 393 coefficient rows, 4,653 covariance entries (maximum absolute discrepancy 3.47e-09), descriptors,Tables1 and bounded logistic marginals compared within fixed rtol2e-6/atol1e-8. Different beta/Wald descriptor endpoints are not equated.
- Three matched J-only models compared to aggregate baseline outputs without hardcoded results. Local person-ID membership check ran when the historical derived frame was available; it intentionally skips in portable exports that exclude person-level frames.
- Refitted JKn used 121PSU replicates. SE ratios 1.000–1.001 versusTaylor are diagnostic, not exact equivalence. Supplemental PIR response weighting executed all 121 refits, maximum inverse response factor 1.74; MAR/positivity remain assumptions. No independent Python response-sensitivity verification is claimed.
- 16 Poisson model specifications have fitted means>1 and are explicitly flagged. These are unconstrained working-model limitations; no such values were presented as individual probabilities. Logistic standardization is bounded.
- Separate flows,aggregate figures(300DPI PNG/vectorPDF),Tables1–3,benchmark comparisons, manuscript andfaculty summary were generated from actual validated tables. Publication benchmark constants enter only reporting, never case construction/fitting. No novelty or causal claim.

## Reproduction and outstanding review

One command: `python run_all.py`; local-cache rerun: `python run_all.py --offline`. R survey4.5 is authoritative. R execution checksums and source/output fingerprints protect against stale success; failed stages invalidate success stamps. Exactversions/session information are local metadata. Raw/person-level/RDS/cache artifacts are gitignored; source/aggregate outputs are intended forGit export. A clean-copy rerun is recorded separately only after executed; no inherited old clean-copy stamp is reused.

Outstanding: exact published formula/exclusions/BP andcare coding; causality/temporal ordering; true chronic hypertension; residual confounding/treatment selection; MAR/MNAR andincomplete-case representation; sparse combinations/positivity; log-mean fit limitations; historical2011–2018 nonresponse andcurrent generalizability. Faculty/survey review,actual applicant contributions/funding/conflicts/licensing/institutional requirements andbroader literature review remain. No software check can manufacture novelty or recover missing longitudinal history.
