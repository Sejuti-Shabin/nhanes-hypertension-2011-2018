# Variable harmonization

All selected variables were checked against official cycle-specific codebooks. data_dictionary.csv contains source wording,target populations andlinks; outputs/harmonization_audit.json also records valid code labels. Source component joins are validated in merge_integrity.csv. Raw numerical tiny-zero decoding is normalized consistently in Python/R.

| Cycle suffix | Type-of-place variable | Smoking100-cigarette target | Adult education target | Hypertension-diagnosis target |
|---|---|---|---|---|
| G | HUQ040 | Both males and females 20 YEARS -
			150 YEARS | Both males and females 20 YEARS -
			150 YEARS | Both males and females 16 YEARS -
			150 YEARS |
| H | HUQ041 | Both males and females 18 YEARS -
			150 YEARS | Both males and females 20 YEARS -
			150 YEARS | Both males and females 16 YEARS -
			150 YEARS |
| I | HUQ041 | Both males and females 18 YEARS -
			150 YEARS | Both males and females 20 YEARS -
			150 YEARS | Both males and females 16 YEARS -
			150 YEARS |
| J | HUQ041 | Both males and females 18 YEARS -
			150 YEARS | Both males and females 20 YEARS -
			150 YEARS | Both males and females 16 YEARS -
			150 YEARS |

Common BP variables retain first3 and optional4th measurements; primary means are available first3, with strict/available2–3 alternatives. Known zero DBP is retained, no BP imputation. Fourth attempts are not silently counted as additional visits. BPQ020 yes/no is diagnosis history; BPQ050A is current prescribed medication; BPQ040A is ever advised medication. Extension medication stays missing when skipped; historical positive-case membership still matches.

HUQ0301/2/3 labels are verified; main non-emergency proxy also uses the per-cycle type variable. Type3 is an emergency department; type1/2/4/5 supports the constructed non-emergency category. Later type6 and refusal/unknowns are not forced into a care group. G type refusal codes differ from later ones, so all unrecognized codes remain missing. No ER-only-care history is established from a most-often-place question.

RIDRETH3 supports six groups in B and a declared four-group collapse in A. DMDEDUC2 applies20+; youth DMDEDUC3 known grades establish below-college but code15 remains ambiguous. Adult smoking is20+ inG,18+ thereafter; skippedG younger records are not never-smokers. PIR0–5 is top-coded5. Grouped income alternatives preserve broad code12 as unknown. Clinical obesity uses BMI≥30; no unpublished clinical exclusion is invented. No DPQ/DIQ/MCQ enters final primary models.

WTMEC8YR=WTMEC2YR/4. Native strata do not collide between these cycles; cycle namespaces and native design produce the same coefficients/covariance. Actual design size is reported, not assumed. Missing percentages, younger-age support, per-cycle counts and sparse event groups are provided in aggregate outputs.
