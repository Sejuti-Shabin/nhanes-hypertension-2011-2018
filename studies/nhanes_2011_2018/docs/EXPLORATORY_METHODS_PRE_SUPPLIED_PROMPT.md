# Calixte methods concordance and unresolved choices

Evidence: user-supplied Methods2.1–2.4, verified publisher/institution abstract; DOI10.1016/j.ypmed.2023.107843. The signed PDF returned403. Appendix A, final regression table and detailed exclusions were not available to the user. This is an attempted methods reconstruction, not a declaration of exact replication.

| Item | Paper evidence supplied | Implementation | Status |
|---|---|---|---|
| Population | Ages18–64; domain analysis | Ages18–64 positive MEC weights | Matched nominal target |
| BP readings | Average2nd/3rd; discusses at least two | Both2/3 systolic and diastolic required; available-reading sensitivity | Missing-reading policy unknown |
| Cases | Current stage1/2 measurements; normal/elevated excluded | Measured≥130/80; no medication-only cases | Matched described measured construct |
| Outcome | BPQ professional diagnosis; no=unaware | BPQ0202 vs1; unknown missing | Variable identity strongly indicated; unknown handling unstated |
| Exposure | More than one place grouped with none | HUQ0302/3 vs1 | Matched described collapse; no ED restriction |
| Age adjustment | Printed18–24,25–34,45–44,45–54,55–64 |35–44 used for malformed third range | Typographic interpretation flagged |
| Race | White,Black,Hispanic,Other | RIDRETH3 maps1/2 Hispanic;6/7 Other | Matched labels |
| Education | College graduate threshold | AdultDMDEDUC2; known youth-below college viaDMDEDUC3; ambiguous youth15 missing | Appendix harmonization unknown |
| Income | Household four ranges | INDHHIN2; broad≥20k code12 unknown; INDFMIN2 sensitivity | Exact source/coding unverified |
| Smoking | Never/former/current | SMQ020/040 skip-aware; G/H20+,I/J18+ | Author treatment of younger ages unknown |
| Depression | PHQ9, summary as mean; ≥10 discussed | Nine-item complete sum; continuous primary,≥10 sensitivity | Regression form unverified |
| Clinical BMI | <30/≥30 | BMI binary | Matched threshold |
| Models | Poisson; demographics then economics then clinical; significant covariates | C1–C4 all reported covariates, common complete cases | Final selected terms/cohort policy unknown |
| Weights/design | MEC/domain/Taylor/survey package | WTMEC2YR/4, full design before subset, Taylor | CDC-correct pooling; authors' exact code not available |
| Benchmarks | n5345,56.2% unaware,81.7%routine,PR1.20[1.12,1.29] | Comparison metadata only | n/PR checked in abstract; exact percentages supplied by user, tables unverified |

Do not tune missingness rules, covariates or classification until the benchmark matches. All ambiguity sensitivities were listed before outcomes/models were computed. Differences in estimates may be described using observed attrition and changes across these declared specifications; none proves the authors used that specification. Routine care here is a single reported place, not verified primary/non-emergency care. Observed stage1/2 BP at one visit is not clinically confirmed chronic hypertension.
