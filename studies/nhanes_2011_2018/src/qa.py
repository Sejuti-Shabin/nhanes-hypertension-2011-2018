"""Generate evidence-based QA and harmonization documentation; never claim unexecuted checks."""
from pathlib import Path
import json,hashlib
import pandas as pd
from data import ROOT,OUT
from validate import assert_current
from audit_baseline import verify_preservation

def run():
 validation=assert_current();tests=json.loads((OUT/'tests.json').read_text());state=json.loads((OUT/'run_state.json').read_text())
 if not tests['passed'] or any(s['returncode'] for s in state['stages']):raise AssertionError('Required stage failed')
 namespace=pd.read_csv(OUT/'r_design_namespace_validation.csv')
 if not namespace.coefficients_equal.all() or not namespace.covariance_equal.all():raise AssertionError('Namespace check failed')
 preserved=verify_preservation();baseline=json.loads((OUT/'baseline_audit.json').read_text())
 r=pd.read_csv(OUT/'regression.csv');design=json.loads((OUT/'design_summary.json').read_text());flow=pd.read_csv(OUT/'participant_flow.csv');audit=json.loads((OUT/'harmonization_audit.json').read_text())
 diagnostics=pd.read_csv(OUT/'r_diagnostics.csv');jack=pd.read_csv(OUT/'jackknife_validation.csv');response=pd.read_csv(OUT/'pir_response_summary.csv').iloc[0]
 def get(name,term='uninsured'):return r[(r.model==name)&(r.term==term)].iloc[0]
 a=get('A4','no_routine_non_emergency_care');b=get('I3');pr=get('I3_PR');j=get('J3')
 records=[]
 for suffix in ['G','H','I','J']:
  subset=[x for x in audit if x['suffix']==suffix]
  smoking=next(x for x in subset if x['source_variable']=='SMQ020');school=next(x for x in subset if x['source_variable']=='DMDEDUC2');bpq=next(x for x in subset if x['source_variable']=='BPQ020');place=next(x for x in subset if x['source_variable'] in ['HUQ040','HUQ041'])
  records.append(f"| {suffix} | {place['source_variable']} | {smoking['target']} | {school['target']} | {bpq['target']} |")
 harmonization='''# Variable harmonization

All selected variables were checked against official cycle-specific codebooks. data_dictionary.csv contains source wording,target populations andlinks; outputs/harmonization_audit.json also records valid code labels. Source component joins are validated in merge_integrity.csv. Raw numerical tiny-zero decoding is normalized consistently in Python/R.

| Cycle suffix | Type-of-place variable | Smoking100-cigarette target | Adult education target | Hypertension-diagnosis target |
|---|---|---|---|---|
'''+ '\n'.join(records)+'''

Common BP variables retain first3 and optional4th measurements; primary means are available first3, with strict/available2–3 alternatives. Known zero DBP is retained, no BP imputation. Fourth attempts are not silently counted as additional visits. BPQ020 yes/no is diagnosis history; BPQ050A is current prescribed medication; BPQ040A is ever advised medication. Extension medication stays missing when skipped; historical positive-case membership still matches.

HUQ0301/2/3 labels are verified; main non-emergency proxy also uses the per-cycle type variable. Type3 is an emergency department; type1/2/4/5 supports the constructed non-emergency category. Later type6 and refusal/unknowns are not forced into a care group. G type refusal codes differ from later ones, so all unrecognized codes remain missing. No ER-only-care history is established from a most-often-place question.

RIDRETH3 supports six groups in B and a declared four-group collapse in A. DMDEDUC2 applies20+; youth DMDEDUC3 known grades establish below-college but code15 remains ambiguous. Adult smoking is20+ inG,18+ thereafter; skippedG younger records are not never-smokers. PIR0–5 is top-coded5. Grouped income alternatives preserve broad code12 as unknown. Clinical obesity uses BMI≥30; no unpublished clinical exclusion is invented. No DPQ/DIQ/MCQ enters final primary models.

WTMEC8YR=WTMEC2YR/4. Native strata do not collide between these cycles; cycle namespaces and native design produce the same coefficients/covariance. Actual design size is reported, not assumed. Missing percentages, younger-age support, per-cycle counts and sparse event groups are provided in aggregate outputs.
'''
 (ROOT/'VARIABLE_HARMONIZATION.md').write_text(harmonization)
 census=pd.read_csv(OUT/'comparative_results.csv');comparison=pd.read_csv(OUT/'replication_comparison.csv')
 files=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and 'data/raw' not in str(p.relative_to(ROOT))]
 (OUT/'artifact_manifest.json').write_text(json.dumps(files,indent=2))
 failed_predictions=diagnostics[diagnostics.predictions_above_one_n.gt(0)]
 report=f'''# Executed QA report

Completed October10,2026 using the final self-contained prompt; no PDF required. Final Study A methods are constructed, not Calixte's verified full formula. Final plan was documented before revised fitting, but preliminary pooled results were already known and that chronology is disclosed.

## Files and preservation

New extension: studies/nhanes_2011_2018. Original working-tree files verified unchanged: {preserved if preserved is not None else 'historical tree absent from portable checkout; not rechecked here'}. Original code/results/manuscripts were not overwritten. Historical tests returncode: {baseline.get('tests_returncode')}; execution scope: {baseline['execution']}. Exact generated file inventory: outputs/artifact_manifest.json. Existing preliminary exploration remains distinct from the final project. No remote/commit/publication was created.

## Data and populations

Active sources: four ordinary G/H/I/J cycles,seven components,28XPORT +28HTML codebooks. Cached preliminary extra components are not used. Authentic hashes and CDC URLs are preserved. Full positive-exam frame n={design['full_examined_n']:,},strata={design['strata']},PSUs={design['PSUs']},full design df={design['design_df']}. WTMEC8YR=WTMEC2YR/4; native versusnamespace design equivalence passed. Domains were defined after the full survey object.

Study A: measured case-eligible n={design['care_case_n']:,}; primary complete model n={int(a.n):,}; PR {a.ratio:.3f}(CI {a.ci_low:.3f}–{a.ci_high:.3f}),p={a.p:.3g}. Published benchmark n5345,unawareness56.2%,routine81.7%,PR1.20[1.12,1.29]. Actual differences and denominators are in REPLICATION_COMPARISON.md. This is an approximate independent reconstruction, not a successful exact reproduction. Routine/ER/multiple care classification, averaging, true published adjustment/exclusions and missingness remain unknown.

Study B: case-eligible n={design['insurance_case_n']:,}; primary n={int(b.n):,}; OR {b.ratio:.3f}(CI {b.ci_low:.3f}–{b.ci_high:.3f}),PR {pr.ratio:.3f}(CI {pr.ci_low:.3f}–{pr.ci_high:.3f}). Matched J-only n={int(j.n):,},OR {j.ratio:.3f}(CI {j.ci_low:.3f}–{j.ci_high:.3f}) reproduced from stored historical values. Cycles are absent from matched primarycovariates and present only in a labeled sensitivity. No skipped medication status was inferred; positive-case comparability is verified separately from negative-status denominators.

## Executed verification

- {tests['tests']} extension tests run; {tests.get('passed_count',tests['tests'])} passed; {tests.get('skipped',0)} skipped; {tests['failures']} failures; {tests['errors']} errors. Historical tests ran only in an isolated copy when available; logs retained locally.
- R independently reconstructed {validation['r_raw_coding_validation']['checks']} variables and {validation['r_domain_validation']['checks']} model masks from authentic raw components. Python/R {validation['regression']['rows']} coefficient rows, {validation['covariance']['entries']:,} covariance entries (maximum absolute discrepancy {validation['covariance']['max_abs_difference']:.3g}), descriptors,Tables1 and bounded logistic marginals compared within fixed rtol2e-6/atol1e-8. Different beta/Wald descriptor endpoints are not equated.
- Three matched J-only models compared to aggregate baseline outputs without hardcoded results. Local person-ID membership check ran when the historical derived frame was available; it intentionally skips in portable exports that exclude person-level frames.
- Refitted JKn used {int(jack.replicates.iloc[0])}PSU replicates. SE ratios {jack.ratio.min():.3f}–{jack.ratio.max():.3f} versusTaylor are diagnostic, not exact equivalence. Supplemental PIR response weighting executed all {int(response.replicates)} refits, maximum inverse response factor {response.max_inverse_response_factor:.2f}; MAR/positivity remain assumptions. No independent Python response-sensitivity verification is claimed.
- {len(failed_predictions)} Poisson model specifications have fitted means>1 and are explicitly flagged. These are unconstrained working-model limitations; no such values were presented as individual probabilities. Logistic standardization is bounded.
- Separate flows,aggregate figures(300DPI PNG/vectorPDF),Tables1–3,benchmark comparisons, manuscript andfaculty summary were generated from actual validated tables. Publication benchmark constants enter only reporting, never case construction/fitting. No novelty or causal claim.

## Reproduction and outstanding review

One command: `python run_all.py`; local-cache rerun: `python run_all.py --offline`. R survey4.5 is authoritative. R execution checksums and source/output fingerprints protect against stale success; failed stages invalidate success stamps. Exactversions/session information are local metadata. Raw/person-level/RDS/cache artifacts are gitignored; source/aggregate outputs are intended forGit export. A clean-copy rerun is recorded separately only after executed; no inherited old clean-copy stamp is reused.

Outstanding: exact published formula/exclusions/BP andcare coding; causality/temporal ordering; true chronic hypertension; residual confounding/treatment selection; MAR/MNAR andincomplete-case representation; sparse combinations/positivity; log-mean fit limitations; historical2011–2018 nonresponse andcurrent generalizability. Faculty/survey review,actual applicant contributions/funding/conflicts/licensing/institutional requirements andbroader literature review remain. No software check can manufacture novelty or recover missing longitudinal history.
'''
 (ROOT/'QA_REPORT.md').write_text(report)
 print('QA passed; original preservation, harmonization, actual verification and unresolved limits recorded')

if __name__=='__main__':run()
