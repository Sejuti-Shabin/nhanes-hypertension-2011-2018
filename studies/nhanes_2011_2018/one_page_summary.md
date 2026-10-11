# NHANES 2011–2018: replication and insurance extension

**Research-training portfolio · AI-assisted · not peer reviewed**

**Questions.** A: Does lacking an operational routine non-emergency care place relate to reported hypertension unawareness in ages 18–64 with measured≥130/80? B: Does lack of insurance relate to awareness in ages 20–64 with measured elevation or reported medication, preserving earlier study rules?

**Methods.** Four authentic CDC cycles; full examination design, WTMEC2YR/4, strata and PSUs; R survey Taylor inference, independent Python comparisons and R JKn checks. A's age/sex/social race/education/PIR/obesity/smoking formula and non-emergency proxy are reconstructed, not verified published methods. B matches original covariates; cycle is a sensitivity.

**Actual findings.** A4 n=4,930,unawareness55.9%,routine non-ER care78.9%,aPR1.27 (95% CI 1.18–1.36); published n=5,345,56.2%,81.7%,aPR1.20[1.12,1.29]. This is not exact replication. B3 n=6,191,aOR0.60 (95% CI 0.49–0.75),aPR0.81 (95% CI 0.73–0.89). Awareness insured58.2% versusuninsured45.7%; standardized difference-11.4points(CI -16.1–-6.6). Historical J-only aOR0.60 (95% CI 0.22–1.62) reproduced numerically.

**Learned.** Definitions of care and hypertension change target populations; current insurance and lifetime diagnosis do not share a known timeline. Distinguishing OR/PR, cohort/model denominators and measurement versus reported recognition matters. Numerical benchmark similarity cannot replace verified methods.

**Validation and limits.** Python/R equivalent calculations and historical models were compared; refitted JKn nonlinear/MAR sensitivities executed. Exact author methods, MAR, clinical truth and causal effects remain unverified. Poisson>1 fitted means are flagged and not treated as probabilities. Applicant must personally rerun/explain the work, verify contributions and disclose AI assistance before outreach. No faculty supervision/publication is claimed.

**Next review.** Faculty/survey review of reconstruction, youth eligibility, treatment selection, missingness and log-mean specification; fuller literature evidence and actual author code if later available. Repository includes protocol/ledger,source provenance,tests,Tables1–3,figures and manuscript.
