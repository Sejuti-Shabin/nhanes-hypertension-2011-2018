"""Faculty-facing reporting from current validated aggregates; benchmarks never enter estimation."""
import json,re
import pandas as pd
from data import ROOT,OUT
from validate import assert_current

def table(head,rows):return '| '+' | '.join(head)+' |\n| '+' | '.join(['---']*len(head))+' |\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows)
def percent(r):return f'{100*r.estimate:.1f}% (95% CI {100*r.ci_low:.1f}–{100*r.ci_high:.1f})'
def effect(r):return f'{r.ratio:.2f} (95% CI {r.ci_low:.2f}–{r.ci_high:.2f})'

def run():
 validation=assert_current();r=pd.read_csv(OUT/'regression.csv');d=pd.read_csv(OUT/'descriptive.csv');t=pd.read_csv(OUT/'table1.csv');flow=pd.read_csv(OUT/'participant_flow.csv');diag=pd.read_csv(OUT/'r_diagnostics.csv')
 marginal=pd.read_csv(OUT/'marginal_probabilities.csv');design=json.loads((OUT/'design_summary.json').read_text());missing=pd.read_csv(OUT/'missingness.csv');casecounts=pd.read_csv(OUT/'sensitivity_case_counts.csv')
 jk=pd.read_csv(OUT/'jackknife_validation.csv');ipw=pd.read_csv(OUT/'pir_response_weighting.csv');ips=pd.read_csv(OUT/'pir_response_summary.csv').iloc[0]
 oldr=pd.read_csv(ROOT/'reference/single_cycle/regression.csv');oldd=pd.read_csv(ROOT/'reference/single_cycle/descriptive.csv')
 def get(model,term='uninsured'):return r[(r.model==model)&(r.term==term)].iloc[0]
 a=get('A4','no_routine_non_emergency_care');b=get('I3');pr=get('I3_PR');j=get('J3');measured=get('I3_measured');measured_pr=get('I3_measured_PR')
 au=d[(d.analysis=='Calixte attempt')&(d.group=='All')&(d.variable=='unawareness')].iloc[0];ac=d[(d.analysis=='Calixte attempt')&(d.group=='All')&(d.variable=='routine_non_emergency')].iloc[0]
 aware_ins=d[(d.analysis=='Insurance extension')&(d.group=='Insured')].iloc[0];aware_unins=d[(d.analysis=='Insurance extension')&(d.group=='Uninsured')].iloc[0]
 oldins=oldd[(oldd.group=='Insured')&(oldd.variable=='awareness')].iloc[0];oldunins=oldd[(oldd.group=='Uninsured')&(oldd.variable=='awareness')].iloc[0]
 md=marginal.iloc[2];ipwor=ipw[ipw.estimand=='Uninsured OR'].iloc[0]
 # External published constants live ONLY here and a metadata table, never in processing/fitting.
 published={'reported_n':5345,'unawareness':.562,'routine_care':.817,'adjusted_PR':1.20,'CI_low':1.12,'CI_high':1.29,'source':'Only verified benchmark facts supplied in final task; paper formula/exclusions remain unknown'}
 (ROOT/'reference/published_benchmarks.json').write_text(json.dumps(published,indent=2))
 comparisons=[
  ['Reported analytic n',published['reported_n'],int(a.n),int(a.n)-published['reported_n'],'Reconstructed complete-case clinical cohort versus unspecified published exclusions; eligible cases also reported separately'],
  ['Measured case-eligible n','Published analytic count only',design['care_case_n'],'Not directly comparable','Case eligibility is not the same as final regression n'],
  ['Weighted unawareness (%)',100*published['unawareness'],round(100*au.estimate,3),round(100*(au.estimate-published['unawareness']),3),'Different averaging, sample and missingness policy possible'],
  ['Routine-care prevalence (%)',100*published['routine_care'],round(100*ac.estimate,3),round(100*(ac.estimate-published['routine_care']),3),'Our non-emergency proxy and multiple-place handling are reconstructed'],
  ['Adjusted PR',published['adjusted_PR'],round(a.ratio,6),round(a.ratio-published['adjusted_PR'],6),'Our explicit all-covariate model is not the unverified publication formula'],
  ['95% CI','1.12–1.29',f'{a.ci_low:.3f}–{a.ci_high:.3f}','Not a statistical difference test','Different design-reference calibration/formula/sample possible']]
 pd.DataFrame(comparisons,columns=['measure','publication_benchmark','our_result','difference','plausible_reasons']).to_csv(OUT/'replication_comparison.csv',index=False)
 (ROOT/'REPLICATION_COMPARISON.md').write_text('# Approximate replication comparison\n\n'+table(['Measure','Published benchmark','Our result','Difference','Plausible reasons'],comparisons)+'\n\nAll differences are descriptive, not tests against an independent study. No methods were selected by benchmark proximity. Our case-eligible, descriptive and model counts differ by documented exclusions. The published exact formula and missing-data/averaging/care recodings are unverified. This is not exact replication.\n\n'+table(['BP sensitivity','Eligible cases','Outcome/exposure complete','Adjusted model n'],casecounts.values.tolist())+'\n\nEven if an eligible-case sensitivity count equals5,345, that does not verify the publication’s final analytic sample or its averaging rule.\n')
 comparison_rows=[
  ['Calixte published','18–64; measured≥130/80','No routine care (exact recoding unknown)','Unawareness',5345,'56.2% unaware','81.7%', 'PR1.20[1.12,1.29]','Exact formula/exclusions unverified'],
  ['Study A reconstruction','18–64;first3 measured≥130/80','No operational non-ER routine place','Unawareness',int(a.n),percent(au),percent(ac),'PR '+effect(a),'Approximate comparison only'],
  ['Study B pooled','20–64;first3≥130/80 orreported medication','Uninsured versus insured','Awareness',int(b.n),f'{100*aware_ins.estimate:.1f}% insured;{100*aware_unins.estimate:.1f}% uninsured','Not an insurance endpoint','OR '+effect(b)+';PR '+effect(pr),'Matched original covariates; different outcome/exposure thanA'],
  ['Prior reviewed2017–2018','20–64;first3≥130/80 orreported medication','Uninsured versus insured','Awareness',int(j.n),f'{100*oldins.estimate:.1f}% insured;{100*oldunins.estimate:.1f}% uninsured','Not an insurance endpoint','OR '+effect(j),'Historical baseline, different period; reproduced numerically']]
 columns=['analysis','population_case','exposure','outcome','model_n','weighted_prevalence','routine_prevalence','adjusted_estimate','comparability']
 pd.DataFrame(comparison_rows,columns=columns).to_csv(OUT/'comparative_results.csv',index=False)
 # Tables1–3 include all required domains and preserve variable-specific denominators.
 table1=[]
 for x in t.itertuples():
  estimate=percent(x) if x.variable not in ['RIDAGEYR','BMXBMI','pir','sbp','dbp'] else f'{x.estimate:.2f} ({x.ci_low:.2f}–{x.ci_high:.2f})'
  if str(x.reliability).startswith('suppress:'):estimate='Suppressed: '+str(x.reliability)
  table1.append([x.analysis,x.group,x.variable,x.level,estimate,'' if pd.isna(x.category_n) else int(x.category_n),int(x.n),int(x.group_n-x.n),x.complement_reliability])
 tab1=table(['Study','Group','Variable','Category','Weighted estimate(95%CI)','Category n','Valid denominator n','Missing n','Complement screen'],table1)
 model_rows=[]
 for name in ['I1','I2','I3','I1_PR','I2_PR','I3_PR','I3_measured','I3_measured_PR','I1_common','I2_common','I3_cycle','J1','J2','J3']:
  x=get(name);model_rows.append([name,'OR' if x.family=='logit' else 'PR',int(x.n),effect(x),f'{x.p:.5g}',int(x.residual_df)])
 tab3=table(['Model','Measure','N','Uninsured versus insured(95%CI)','Design-based p','Residual reference df'],model_rows)
 (ROOT/'TABLES.md').write_text('# Table1. Descriptive estimates\n\n'+tab1+'\n\nVariable-specific denominators and category/missing counts are unweighted. Percentages/means are survey weighted. Complement suppression is disclosed. No probability claim is made from Poisson fitted means.\n\n# Table2. Scientific comparability\n\n'+table(columns,comparison_rows)+'\n\n# Table3. Insurance models\n\n'+tab3+'\n\nI1/I2/I3 match original covariates; cycle terms appear only in the labeled sensitivity. I1/I2 common fits use I3 sample. OR≠PR; differences across models are not purely confounding.\n')
 a_diag=diag[diag.model=='A4'].iloc[0];p_diag=diag[diag.model=='I3_PR'].iloc[0]
 census=flow[flow.analysis=='Calixte attempt'];insuranceflow=flow[flow.analysis=='Insurance extension']
 results=f'''Study A included {design['care_case_n']:,} measured case-eligible adults and {int(a.n):,} fully adjusted complete cases. Its weighted unawareness prevalence was {percent(au)}, compared with the56.2% benchmark; operational non-emergency routine-care prevalence was {percent(ac)}, compared with81.7%. The reconstructed aPR for lack of care was {effect(a)} (p={a.p:.3g}); published aPR was1.20[1.12,1.29]. Our adjusted sample was {published['reported_n']-int(a.n):,} fewer than the publication benchmark. These differences cannot establish what unpublished recoding/exclusion decisions were used.

Study B included {design['insurance_case_n']:,} medication-inclusive case-eligible adults, with {int(b.n):,} complete cases in the fully adjusted model. Descriptive awareness was {percent(aware_ins)} among insured(n={int(aware_ins.n):,}) and {percent(aware_unins)} among uninsured(n={int(aware_unins.n):,}). These descriptive denominators differ from the covariate-complete regression sample. Matched-model aOR was {effect(b)} (p={b.p:.3g}); modified-Poisson aPR was {effect(pr)} (p={pr.p:.3g}). The measured-only first3 comparison yielded aOR {effect(measured)} and aPR {effect(measured_pr)}, n={int(measured.n):,}.

The preserved2017–2018 fully adjusted model had n={int(j.n):,} and aOR {effect(j)}, p={j.p:.3g}. Three J-only model specifications were rerun in the extension and compared with stored original outputs. The pooled point estimate is similar, with a narrower interval, but these are overlapping historical periods and not independent validation datasets. The cycle-adjusted sensitivity yielded aOR {effect(get('I3_cycle'))}; it is deliberately not the matched primary specification.

Logistic standardized awareness was {percent(marginal.iloc[0])} under insured coding and {percent(marginal.iloc[1])} under uninsured coding, over the weighted I3 complete-case distribution. The difference was {100*md.estimate:.1f} percentage points(95%CI {100*md.ci_low:.1f}–{100*md.ci_high:.1f}). This standardization is associational and model-dependent.

Independent R JKn/Taylor SE ratios ranged {jk.ratio.min():.3f}–{jk.ratio.max():.3f}, with {int(jk.replicates.iloc[0])} sampling-unit replicates. Exact equality is not expected. The R-only missing-PIR response sensitivity yielded OR {ipwor.estimate:.2f}(95%CI {ipwor.ci_low:.2f}–{ipwor.ci_high:.2f}), target n={int(ips.target_n):,}, maximum inverse response factor {ips.max_inverse_response_factor:.2f}. Every replicate refit response and outcome models; the MAR assumption remains unverified. This sensitivity was not independently implemented in Python.

Poisson diagnostics identified {int(a_diag.predictions_above_one_n)} fitted means above1 in A4 and {int(p_diag.predictions_above_one_n)} in I3_PR. These identify limitations of the unconstrained log-mean working models, not valid individual probabilities. Logistic predictions alone supplied standardized awareness probabilities. Sparse category/event counts and complete-case retention are retained in aggregate diagnostics; convergence is not proof of adequate overlap.
'''
 # Scientific narrative: sourced facts and own interpretation clearly distinguished.
 manuscript=f'''# Routine healthcare access, insurance coverage and reported hypertension recognition: NHANES 2011–2018

**Research-training manuscript draft, not peer reviewed.** Final specification follows the self-contained prompt. Prior single-cycle and preliminary pooled findings were known; revised operationalizations were documented before final fitting but are post-exploration. AI assisted coding and writing; applicant contributions require factual verification.

## Structured abstract

**Background:** Routine healthcare access and insurance are related but distinct aspects of care. This study pairs an approximate reconstruction of published routine-care/unawareness research with an insurance/awareness extension preserving a prior project's definitions.

**Methods:** Four official NHANES cycles2011–2018 were pooled with WTMEC8YR=WTMEC2YR/4. Study A targeted examined adults18–64 with measured BP≥130/80, using an explicit HUQ-based non-emergency-care proxy and reported diagnosis unawareness. Its Poisson model adjusted for selected demographic, socioeconomic and clinical variables; the exact published formula is unknown. Study B targeted ages 20–64 with measured elevation or current reported medication, with awareness as outcome and current insurance as exposure. Models matched original age/sex/race/education/PIR adjustment; cycle effects were sensitivity terms. Full survey design preceded domains; R survey was authoritative, with independent Python Taylor comparisons and R JKn refits.

**Results:** A4 n={int(a.n):,}; unawareness{100*au.estimate:.1f}%, non-emergency routine-care{100*ac.estimate:.1f}%, aPR{effect(a)}. These differ from published n=5,345,56.2%,81.7%,aPR1.20[1.12,1.29]. Study B n={int(b.n):,}; aOR{effect(b)} and aPR{effect(pr)} for uninsured versus insured awareness. Standardized difference{100*md.estimate:.1f}percentage points(CI {100*md.ci_low:.1f}–{100*md.ci_high:.1f}). Prior J-only n={int(j.n):,},aOR{effect(j)}.

**Conclusions:** The care reconstruction supports a directionally compatible association but is not exact replication. Insurance was associated with lower reported awareness under matched pooled models. Temporal ambiguity, selection, missingness and working-model limitations prohibit causal claims.

## Introduction

Hypertension recognition is a healthcare-history construct, while measured blood pressure is a physiological observation at a survey visit. A person can report a previous diagnosis while current treatment controls measured pressure. Conversely, a participant can have an elevated examination measurement without recalling a professional diagnosis. A coherent study must distinguish these constructs, rather than label everyone with one elevated visit as clinically confirmed disease or everyone reporting no diagnosis as a proven detection failure.

Routine access may create opportunities for screening and communication, whereas insurance may affect affordability and care continuity. Neither construct can be replaced by the other. A usual healthcare place can be an emergency department, and a person with coverage can still lack an accessible provider. Current insurance is also observed after an unspecified lifetime diagnosis history. Illness-related employment or eligibility changes can therefore create reverse temporal pathways. We estimate descriptive adjusted associations, not the effect of supplying insurance or creating a care site.

Calixte and colleagues used NHANES 2011–2018 to relate routine-care access to unawareness in nonelderly adults[1]. Verified facts supplied for this task establish the period, measured130/80 case threshold, age18–64, unawareness construct, survey Poisson approach and benchmarks. They do not identify every exclusion, exposure recoding, BP averaging rule or final regression term. Our Study A accordingly reconstructs an explicit defensible analysis and reports disagreements. Numerical proximity alone does not verify a missing method.

Study B extends a preserved2017–2018 research-training project. Its target and medication-inclusive definition differ from Study A. Retaining the original adjustment variables permits a matched historical comparison while pooling four cycles offers more survey information. We hypothesized higher unawareness with lack of operational routine non-emergency care in A, and lower awareness among uninsured case-eligible adults in B. Both are established public-health questions, not claims of novel discovery.

## Related research and contribution

Egan et al. examined insurance-related hypertension care-cascade gaps in earlier NHANES periods[2]. Duru et al. studied insurance and hypertension monitoring/control[3]; CDC describes awareness by insurance and utilization in2011–2014[4]. Muntner et al. provides historical hypertension-control context through2017–2018[5]. Control, treatment and awareness are distinct endpoints. Different thresholds, ages, medication inclusion and periods preclude casual numerical comparisons across these studies.

Our limited contribution is a transparent reconstruction and an auditable extension: authentic source harmonization, maintained original definitions, explicit non-emergency-care assumptions, design-aware estimates, independent computations and honest incomplete replication. A focused literature comparison is not a systematic novelty assessment. Academic application materials should describe a reproducible training project rather than a peer-reviewed discovery or supervised investigation unless those facts are independently established.

## Methods

### Data, setting and preservation

Official CDC DEMO,BPX,BPQ,HUQ,HIQ files were obtained for G(2011–2012),H(2013–2014),I(2015–2016),J(2017–2018)[6]. Study A's prespecified obesity and smoking variables additionally required BMX and SMQ. No laboratory subsample was introduced. Preliminary unused DIQ/MCQ/DPQ caches are not part of final models. Components were merged within cycle using uniqueSEQN with one-to-one checks, then appended with cycle identifiers. No2017–March2020 prepandemic records were used. Raw codebooks, source URLs and SHA256 checks define the snapshot.

The original2017–2018 directory, results and writing remained unchanged. A historical copy accompanies the workspace, with file hashes; small aggregate reference results accompany the portable extension. Original tests run in an isolated copy, and J-only models execute anew in this extension. New protocol and ledger disclose earlier result knowledge; the project is retrospective and not prospectively preregistered.

### Blood-pressure and questionnaire definitions

Primary BP is the separate mean of available first3 systolic and diastolic readings under the original rule. Valid DBP0 remains valid; tiny XPORT zero representations are normalized. Missing values are not imputed and documented invalid paired readings fail validation. Study A requires both resulting means and a130/80 crossing. Alternate strict/available2–3 means are declared sensitivities, not verified author methods or benchmark-selected choices.

A unawareness is BPQ0202 among measured-high cases; BPQ0201 is awareness. Refused, don't-know and missing diagnosis are not coded unawareness. B uses the complementary reported-awareness outcome. B eligibility is a known elevated component or reported current BPQ050A1 medication at ages 20–64, including medication cases without measured BP. BPQ040A is ever advised medication and does not establish current use. In the extension skipped current-medication responses stay missing. The historical code's documented skip-no logic is recorded for audit; positive-case membership is unchanged, but negative-status denominators are not treated as interchangeable. No overall medication-inclusive national hypertension prevalence is inferred from those differing unknown-status rules.

### Exposures and harmonization

Study A's main lack-of-care variable combines HUQ030 with type-of-place follow-up HUQ040 inG and HUQ041 later. A no-place response denotes lack even when type is skipped. A reported usual/most-often emergency department is classified as lacking the operational non-emergency place. One/multiple places with known clinic,office,outpatient orother non-ER type indicate access. Unknown type and later code6 remain unknown where the primary place response does not resolve non-emergency status. Reporting an ER as usual/most-often is not proof that it is the only provider used. The construction is our proxy; exact Calixte handling is not verified.

Study B exposure is HIQ011 insurance status, insured1 versusuninsured2, with unknown responses excluded. Insurance is not a surrogate forHUQ. Different published and reconstructed care definitions are compared using declared sensitivities: no-place-only, single-place-only, and excluding ER-coded participants. These alter the estimand and support, not simply measurement precision.

Race/ethnicity is a social descriptor. A combines Hispanic categories and uses White/Black/Hispanic/Other; B retains the six original public-use groups. Adult education DMDEDUC2 applies at20+. For A18–19, known youth grades establish below-college status while “more than high school” does not establish degree and stays unknown. Smoking questions are20+ inG and18+ thereafter; structural ineligibility is not never-smoking. Never/former/current coding respects SMQ020/040 skip logic. Household-income alternatives preserve broad≥20k code12 as unresolved instead of inventing an upper income group. Continuous PIR is top-coded5; linearity is examined in sensitivity analysis.

### Models and survey inference

Study A1–A4 sequentially add demographics, SES and obesity/smoking to the operational exposure; all main steps use a common A4-complete population. A staged-sample alternative distinguishes missingness selection from added variables. The chosen adjustment set is scientifically motivated, not a reconstructed significance screen or a verified Calixte formula. Clinical traits can influence screening and may also follow diagnosis, so adjustment cannot identify a causal pathway.

B1 is unadjusted uninsured versus insured; B2 adds continuous age and sex; B3 adds original six-category race, four-category education and continuous PIR. Primary pooled formulas have no cycle term to match the historical model. Explicit cycle-adjusted, omit-PIR, functional-form and common-sample alternatives are reported. Logistic OR and modified-Poisson PR use the same covariates and eligibility within each step. ORs are not risk or prevalence ratios, and nested-model OR changes can reflect noncollapsibility as well as confounding and sample shifts.

The full positive-weight examination design precedes all domains, using WTMEC2YR/4, native masked strata andPSUs, nest=TRUE, noFPC and lonely-PSU fail[7]. Namespace equivalence is checked. This dataset has {design['strata']} strata,{design['PSUs']}PSUs and {design['design_df']} full design degrees of freedom, rather than an assumed60. Rsvyglm provides Taylor covariance and model-residual-df coefficient intervals. Alternative full-design/normal calibrations are explicitly labeled. Group descriptors use their supported domain reference df and bounded beta/Korn–Graubard-type intervals with numericNCHS reliability screening[8].

### Missingness, standardization and checks

Complete cases are not presumed representative; MEC weights do not repair every later item missingness mechanism. Counts and percentages are tabulated by variable/cycle, with weighted retention and exposure/event support. A supplemental PIR response model uses observed outcome/exposure, demographics, auxiliary BP with a missing-BP flag, log exam weight andcycle. Nuisance auxiliary means, response and outcome models are refit inside survey JKn replicates. This assumes MAR conditional on measured predictors, positivity and model adequacy; it does not establish MAR or solve MNAR. Remaining non-PIR exclusions remain explicit.

B logistic predictions are standardized over its weighted complete-case covariate distribution. Joint Taylor influence includes coefficient and empirical-distribution uncertainty, with logit-transformed probability intervals and model-residual reference for the difference. Independent JKn model refits assess this nonlinear estimator. Poisson models can yield fitted means above1, which are flagged and never treated as individual probabilities. Python provides ETL, unit tests, figures and separate equivalent Taylor calculations; R survey is authoritative[9]. Full covariance matrices and independently rebuilt R masks/variables are compared, while R-only response weighting is not falsely called independently reproduced in Python.

## Results

{results}

### Tables and sensitivity findings

[Tables1–3 with denominators and scientific comparability](TABLES.md) and [publication discrepancy analysis](REPLICATION_COMPARISON.md) accompany this report. The published sample count is not automatically the adjusted-model denominator in our reconstruction. All alternate case/exposure/model estimates are retained in regression.csv and their diagnostic tables; no closest-to-benchmark specification is promoted to primary.

''' 
 # Results highlight every selected sensitivity via actual files.
 for name in ['A4_strict23','A4_no_place_only','A4_single_place','A4_household_income','A4_no_clinical']:
  term='no_any_place' if name=='A4_no_place_only' else 'no_routine' if name=='A4_single_place' else 'no_routine_non_emergency_care';x=get(name,term)
  manuscript+=f'- {name}: PR {effect(x)},n={int(x.n):,}.\n'
 for name in ['I3_measured','I3_140','I3_bp_complete','I3_readings23','I3_cycle','I3_omit_PIR']:
  x=get(name);manuscript+=f'- {name}: OR {effect(x)},n={int(x.n):,}.\n'
 manuscript+='''

![Weighted outcomes](figures/weighted_outcomes.png)

![Association forest](figures/association_forest.png)

![Sensitivity comparisons](figures/sensitivity_comparison.png)

Separate participant flows and captions are in figures/. Images also have vectorPDF versions.

## Discussion

The two analyses support different statements. A relates a reconstructed usual non-emergency-care proxy to reported unawareness within measured-high cases. B relates current insurance to reported awareness within a medication-inclusive case domain. A higher unawareness PR and a lower awareness OR/PR can both reflect recognition opportunity, but their magnitudes are not interchangeable and do not establish a common causal effect. Medication-only B cases are frequently aware by questionnaire linkage, whereas A excludes some successfully controlled aware adults. That conditioning can induce selection tied to treatment, recognition and access.

Approximate replication succeeded in implementing a transparent related analysis, not in verifying the exact published study. Differences in care prevalence are plausible under ER/multiple-place recoding; sample differences can arise through averaging and covariate missingness. Those explanations remain possibilities, not evidence that the authors used any particular unobserved method. Even an eligible-case sensitivity count matching5,345 would not verify final model inclusion. Benchmark comparisons are descriptive and correlated through the shared survey data; overlapping confidence intervals are not a formal reproduction test.

The pooled insurance association was more precise than the earlier single-cycle result under matched covariates. More sampled strata/PSUs support smaller design-based uncertainty, but this does not transform an observational association into a policy effect. Current coverage can follow diagnosis or illness-related changes in employment. Unmeasured geography, benefit generosity, coverage history, comorbidity and health literacy remain potential sources of residual explanation. CurrentPIR and clinical traits may occupy different temporal roles, and a conceptual adjustment story cannot order these variables empirically.

Complete-case and response-weighted estimates answer related targets under different assumptions. Modest observed inverse response factors are reassuring diagnostics but cannot establish response positivity in unobserved combinations or MAR for true missing income. The response sensitivity propagates estimation uncertainty; it does not recover unknown diagnosis/exposure histories or show how far any estimate is from truth. Full questionnaire and codebook checks improve consistency without eliminating recall, measurement or selection errors.

Unconstrained Poisson fitted means above1 warn against presenting the fitted values as probabilities or using them for policy standardization. Reported ratios remain modified-Poisson working-model associations with survey covariance, requiring adequate log-mean approximation. The logistic probability analysis supplies bounded descriptive standardization; it is not a replacement validation of every Poisson specification. Model and reference-distribution sensitivities should guide interpretation rather than select significance.

## Strengths and limitations

Strengths include authentic cached sources, cycle-specific mapping, unchanged historical work, matched baseline comparisons, full design before domains, independent raw-variable/mask/covariance checks, refitted nonlinear sampling-unit checks and aggregate-only faculty outputs. Automatic tests and failure state prevent stale success claims. Scientific interpretation explicitly tolerates unsuccessful exact replication and different estimands.

Limitations include unverified publication details, nominal-versus-supported younger ages, structural smoking/education gaps, incomplete cases, single-visit BP, self-reported lifetime diagnosis and current insurance, treatment-linked case selection, sparse category combinations, Poisson working-model violations, MAR/MNAR uncertainty and residual confounding. CDC documented cycle-specific nonresponse/location characteristics and enhanced calibration in2017–2018[10]; pooled analysis uses released weights but cannot independently remove every representation error. Findings concern2011–2018 and are not current prevalence or2021–2023 effects.

## Conclusion

A reproducible approximate Calixte reconstruction and a matched insurance extension produced interpretable historical associations with explicit uncertainty and methodological limits. The care reconstruction differs from published sample and estimates and cannot be described as exact replication. The pooled insurance estimate supports lower reported awareness among uninsured operational cases under the chosen model; causal and clinical interpretations remain unsupported. The contribution is research reasoning and transparent implementation, not an original discovery or a peer-reviewed publication.

## Contributions, ethics and funding

The applicant must verify actual independent contributions, funding/conflicts and institutional review requirements before external submission. This iteration includes substantial AI assistance. Public NHANES data have their own CDC ethical review/consent; no applicant-specific exemption or approval, faculty supervision or peer review was supplied or claimed.

## References

1. Calixte R,Chahal K,Besson A,Kaplan MS. Preventive Medicine2024;179:107843. [doi:10.1016/j.ypmed.2023.107843](https://doi.org/10.1016/j.ypmed.2023.107843),[PubMed](https://pubmed.ncbi.nlm.nih.gov/38176445/). Exact full formula/exclusions remain unverified; only final-task verified facts are used.
2. Egan BM etal. The growing gap in hypertension control between insured and uninsured adults:NHANES 1988–2010. Hypertension. 2014;64:997–1004. [doi](https://doi.org/10.1161/HYPERTENSIONAHA.114.04276).
3. Duru OK etal. Health insurance status and hypertension monitoring and control in the United States. American Journal of Hypertension2007;20:348–353. [doi](https://doi.org/10.1016/j.amjhyper.2006.11.007).
4. CDC/NCHS. [DataBrief278,2011–2014 hypertension unawareness](https://www.cdc.gov/nchs/products/databriefs/db278.htm).
5. Muntner P etal. Trends in blood pressure control among US adults with hypertension,1999–2000 to2017–2018. JAMA. 2020;324:1190–1200. [doi](https://doi.org/10.1001/jama.2020.14545).
6. CDC/NCHS. [Dataset documentation](https://wwwn.cdc.gov/nchs/nhanes/tutorials/datasets.aspx); exact official codebooks/URLs/hashes in the source manifest.
7. CDC/NCHS. [Weighting](https://wwwn.cdc.gov/nchs/nhanes/tutorials/weighting.aspx),[variance](https://wwwn.cdc.gov/nchs/nhanes/tutorials/varianceestimation.aspx).
8. Parker JD etal. [NCHS proportion presentation standards](https://www.cdc.gov/nchs/data/series/sr_02/sr02_175.pdf). Numeric screening is not agency clearance.
9. R survey package4.5,installed help/source and [CRAN](https://cran.r-project.org/package=survey).
10. CDC/NCHS. [2017–2018 nonresponse/sample-characteristics summary](https://wwwn.cdc.gov/nchs/data/nhanes/analyticguidelines/17-18-sampling-variability-nonresponse-508.pdf).
11. [STROBE observational reporting guidance](https://www.strobe-statement.org/).
'''
 (ROOT/'manuscript.md').write_text(manuscript)
 (OUT/'manuscript_metadata.json').write_text(json.dumps({'word_count_excluding_references':len(re.findall(r'\b[\w–]+\b',manuscript.split('## References')[0]))},indent=2))
 summary=f'''# NHANES 2011–2018: replication and insurance extension

**Research-training portfolio · AI-assisted · not peer reviewed**

**Questions.** A: Does lacking an operational routine non-emergency care place relate to reported hypertension unawareness in ages 18–64 with measured≥130/80? B: Does lack of insurance relate to awareness in ages 20–64 with measured elevation or reported medication, preserving earlier study rules?

**Methods.** Four authentic CDC cycles; full examination design, WTMEC2YR/4, strata and PSUs; R survey Taylor inference, independent Python comparisons and R JKn checks. A's age/sex/social race/education/PIR/obesity/smoking formula and non-emergency proxy are reconstructed, not verified published methods. B matches original covariates; cycle is a sensitivity.

**Actual findings.** A4 n={int(a.n):,},unawareness{100*au.estimate:.1f}%,routine non-ER care{100*ac.estimate:.1f}%,aPR{effect(a)}; published n=5,345,56.2%,81.7%,aPR1.20[1.12,1.29]. This is not exact replication. B3 n={int(b.n):,},aOR{effect(b)},aPR{effect(pr)}. Awareness insured{100*aware_ins.estimate:.1f}% versusuninsured{100*aware_unins.estimate:.1f}%; standardized difference{100*md.estimate:.1f}points(CI {100*md.ci_low:.1f}–{100*md.ci_high:.1f}). Historical J-only aOR{effect(j)} reproduced numerically.

**Learned.** Definitions of care and hypertension change target populations; current insurance and lifetime diagnosis do not share a known timeline. Distinguishing OR/PR, cohort/model denominators and measurement versus reported recognition matters. Numerical benchmark similarity cannot replace verified methods.

**Validation and limits.** Python/R equivalent calculations and historical models were compared; refitted JKn nonlinear/MAR sensitivities executed. Exact author methods, MAR, clinical truth and causal effects remain unverified. Poisson>1 fitted means are flagged and not treated as probabilities. Applicant must personally rerun/explain the work, verify contributions and disclose AI assistance before outreach. No faculty supervision/publication is claimed.

**Next review.** Faculty/survey review of reconstruction, youth eligibility, treatment selection, missingness and log-mean specification; fuller literature evidence and actual author code if later available. Repository includes protocol/ledger,source provenance,tests,Tables1–3,figures and manuscript.
'''
 (ROOT/'one_page_summary.md').write_text(summary)
 readme=f'''# NHANES 2011–2018: approximate routine-care replication and matched insurance extension

Two distinct historical association studies, not an exact Calixte reproduction or a causal analysis.

| Study | Population/outcome/exposure | Main calculated result |
|---|---|---|
| A |18–64,measured≥130/80;unawareness; reconstructed lack of non-ER routine care |n={int(a.n):,},aPR{effect(a)} |
| B |20–64,measured≥130/80 or reported medication;awareness;uninsured vsinsured |n={int(b.n):,},aOR{effect(b)},aPR{effect(pr)} |
| Preserved2017–2018 |Original matched insurance model |n={int(j.n):,},aOR{effect(j)} |

A's unawareness{100*au.estimate:.1f}% and routine-care{100*ac.estimate:.1f}% differ from published56.2%/81.7%. Its adjusted n differs from5345. The exact paper formula, BP rule, exclusions and care coding are unknown; all choices and differences are explicit. Study B preserves original positive-case membership and covariates. No skipped medication status is imputed in the extension.

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

WTMEC8YR=WTMEC2YR/4, full design before domains, actual pooled df={design['design_df']}. Covariate/sample counts, group-specific df, NCHS screening, full covariance comparisons, independent R raw-variable/mask checks and J-only comparison are explicit. R JKn uses{int(jk.replicates.iloc[0])}PSU replicates. Poisson fitted means>1 are flagged; only logistic predictions supply bounded probabilities. PIR response weighting is MAR-dependent and R-only, not independently verified in Python.

Cross-sectional temporal ambiguity, treatment/awareness-linked selection, complete cases, uncertain published details, sparse support and historical nonresponse remain. There is no novelty/publication/causal or current-population claim.

## GitHub-ready layout

Raw sources, participant-level `outputs/design_frame.csv`,RDS models,replicate matrices,cache folders andlocal logs are gitignored. Source code, documentation,small aggregate tables andfigures are the intended export. The unchanged historical working tree and preliminary exploration are preserved locally but excluded from the new portable Git export; small aggregate baseline references remain. Authorship,code licensing,funding andinstitutional review status require factual applicant input; none is invented.
'''
 (ROOT/'README.md').write_text(readme)
 print('Generated manuscript, Tables1–3, benchmark/comparability reports, README and faculty summary')

if __name__=='__main__':run()
