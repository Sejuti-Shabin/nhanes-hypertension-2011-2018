"""Prepare pooled sources, prespecified model cohorts and independent Python checks."""
import json,numpy as np,pandas as pd
from data import ROOT,OUT,RAW,LEVELS,load,prepare,insurance_domain,care_domain
from survey import complete,fit,ratio,standardized
COV_I=['uninsured','age10','sex','race','education','pir']
COV_A=['no_routine_non_emergency_care','age10','sex','race4','college','pir','obese','smoking']


def run():
 OUT.mkdir(exist_ok=True)
 raw,audit,joins=load();all_d=prepare(raw)
 d=all_d.loc[all_d.RIDSTATR.eq(2)&all_d.WTMEC2YR.gt(0)].reset_index(drop=True)
 if d[['SDMVSTRA','SDMVPSU']].isna().any().any():raise ValueError('Missing positive-exam design keys')
 (OUT/'harmonization_audit.json').write_text(json.dumps(audit,indent=2))
 pd.DataFrame([{k:v for k,v in a.items() if k!='codes'} for a in audit]).to_csv(ROOT/'data_dictionary.csv',index=False)
 joins.to_csv(OUT/'merge_integrity.csv',index=False)
 core=care_domain(d);ins=insurance_domain(d)
 care_final=complete(d,core,'unawareness',COV_A)
 ins_final=complete(d,ins,'awareness',COV_I)
 domains={'care_measured':core,'care_complete':care_final,'insurance_cases':ins,'insurance_complete':ins_final}
 for name,mask in domains.items():d['domain_'+name]=mask.astype(int)
 specs=[];results=[];covariances=[];diagnostics=[];cells=[]
 def model(name,mask,outcome,variables,family='logit',kind='primary',scope='pooled',rule='',info=False):
  frame=d if scope=='pooled' else d.loc[d.suffix.eq('J')].reset_index(drop=True)
  if scope=='single_J':mask=insurance_domain(frame)
  weight='WTMEC8YR' if scope=='pooled' else 'WTMEC2YR'
  table,diag,fitted=fit(frame,mask,outcome,variables,name,family,weight)
  results.append(table);diagnostics.append(diag)
  full_keep=pd.Series(False,index=d.index)
  if scope=='pooled':full_keep=fitted['keep']
  else:full_keep.loc[d.suffix.eq('J')]=fitted['keep'].to_numpy()
  column='model_domain_'+name;d[column]=full_keep.astype(int)
  specs.append({'model':name,'outcome':outcome,'variables':variables,'formula':outcome+' ~ '+' + '.join(variables),'family':family,'kind':kind,'scope':scope,'domain_column':column,'rule':rule})
  for i,v1 in enumerate(fitted['names']):
   for j,v2 in enumerate(fitted['names']):covariances.append({'model':name,'term1':v1,'term2':v2,'covariance':float(fitted['cov'][i,j])})
  sample=frame.loc[fitted['keep']]
  for v in variables:
   if v in LEVELS or v in ['uninsured','no_routine','obese','depressed']:
    for level,sub in sample.groupby(v,observed=True):cells.append({'model':name,'variable':v,'level':str(level),'n':len(sub),'events':int(sub[outcome].sum()),'nonevents':int(len(sub)-sub[outcome].sum())})
  return fitted if info else None
 models_a={'A1':['no_routine_non_emergency_care'],
  'A2':['no_routine_non_emergency_care','age10','sex','race4'],
  'A3':['no_routine_non_emergency_care','age10','sex','race4','college','pir'],
  'A4':COV_A}
 for name,variables in models_a.items():model(name,care_final,'unawareness',variables,'poisson','reconstructed approximate replication',rule='care_common')
 for name in ['A1','A2','A3']:model(name+'_stage',core,'unawareness',models_a[name],'poisson','missingness sensitivity',rule='care_stage')
 for name,mask,variables,rule in [
  ('A4_strict23',care_domain(d,strict23=True),COV_A,'care_strict23'),
  ('A4_available23',care_domain(d,available=True),COV_A,'care_available'),
  ('A4_age20',care_domain(d,age=(20,64)),COV_A,'care_age20'),
  ('A4_no_place_only',core,[v if v!='no_routine_non_emergency_care' else 'no_any_place' for v in COV_A],'care_stage'),
  ('A4_single_place',core,[v if v!='no_routine_non_emergency_care' else 'no_routine' for v in COV_A],'care_stage'),
  ('A4_exclude_ER',core&~d.place_type.eq(3),COV_A,'care_exclude_ER'),
  ('A4_no_clinical',core,models_a['A3'],'care_stage'),
  ('A4_adult_education',core,[v if v!='college' else 'college_adult' for v in COV_A],'care_stage'),
  ('A4_household_income',core,[v if v!='pir' else 'income' for v in COV_A],'care_stage'),
  ('A4_cycle',core,COV_A+['cycle'],'care_stage')]:
  model(name,mask,'unawareness',variables,'poisson','predeclared reconstruction sensitivity',rule=rule)
 models_i={'I1':['uninsured'],'I2':['uninsured','age10','sex'],'I3':COV_I}
 primary=None
 for name,variables in models_i.items():
  fitted=model(name,ins,'awareness',variables,rule='insurance',info=True)
  if name=='I3':primary=fitted
  model(name+'_PR',ins,'awareness',variables,'poisson','insurance prevalence ratio',rule='insurance')
 for name in ['I1','I2']:model(name+'_common',ins_final,'awareness',models_i[name],kind='common sample sensitivity',rule='insurance_common')
 for name,mask,variables in [
   ('I3_measured',insurance_domain(d,definition='elevated_130'),COV_I),
   ('I3_140',insurance_domain(d,definition='hypertension_140'),COV_I),
   ('I3_bp_complete',insurance_domain(d,bp_complete=True),COV_I),
   ('I3_readings23',insurance_domain(d,definition='hypertension_23_available'),COV_I),
   ('I3_measured23',insurance_domain(d,definition='elevated_23'),COV_I),
   ('I3_measured23_age18',insurance_domain(d,age=(18,64),definition='elevated_23'),COV_I),
   ('I3_not_pregnant',insurance_domain(d,exclude_pregnancy=True),COV_I),
   ('I3_omit_PIR',ins,[v for v in COV_I if v!='pir']),
   ('I3_cycle',ins,COV_I+['cycle']),
   ('I3_quadratic_age',ins,COV_I+['age10_sq']),
   ('I3_categorical_PIR',ins,[v if v!='pir' else 'pir_group' for v in COV_I])]:
  model(name,mask,'awareness',variables,kind='insurance sensitivity',rule=name)
  if name=='I3_measured':model(name+'_PR',mask,'awareness',variables,'poisson','measured-only PR sensitivity',rule='I3_measured')
 for name,variables in [('J1',['uninsured']),('J2',['uninsured','age10','sex']),('J3',COV_I)]:
  model(name,None,'awareness',variables,scope='single_J',kind='prior cycle reproduction',rule='single_J')
 standardized(d,primary).to_csv(OUT/'python_marginal.csv',index=False)
 pd.concat(results).to_csv(OUT/'python_regression.csv',index=False)
 pd.DataFrame(covariances).to_csv(OUT/'python_covariance.csv',index=False)
 pd.DataFrame(cells).to_csv(OUT/'model_cells.csv',index=False)
 (OUT/'python_diagnostics.json').write_text(json.dumps(diagnostics,indent=2))
 (OUT/'model_specifications.json').write_text(json.dumps(specs,indent=2))
 pd.DataFrame([{k:v for k,v in x.items() if k!='variables'} for x in specs]).to_csv(OUT/'model_specifications.csv',index=False)
 flows=[]
 for name,age,case,final in [('Calixte attempt',(18,64),care_domain(all_d),care_final),('Insurance extension',(20,64),insurance_domain(all_d),ins_final)]:
  age_mask=all_d.RIDAGEYR.between(*age);exam=age_mask&all_d.RIDSTATR.eq(2)&all_d.WTMEC2YR.gt(0)
  validbp=(all_d.sbp.notna()&all_d.dbp.notna()) if name=='Calixte attempt' else all_d.hypertension_130.notna()
  outvar='unawareness' if name=='Calixte attempt' else 'awareness';expvar='no_routine_non_emergency_care' if name=='Calixte attempt' else 'uninsured'
  stages=[('All respondents',len(all_d)),('Age eligible',int(age_mask.sum())),('Examined positive MEC weight',int(exam.sum())),('Valid first3 BP means' if name=='Calixte attempt' else 'Direct case status classifiable',int((exam&validbp).sum())),('Case eligibility',int(case.sum())),('Outcome/exposure complete',int((case&all_d[outvar].notna()&all_d[expvar].notna()).sum())),('Fully adjusted complete cases',int(final.sum()))]
  previous=None
  for stage,n in stages:
   flows.append({'analysis':name,'stage':stage,'n':n,'excluded_since_previous':0 if previous is None else previous-n});previous=n
 pd.DataFrame(flows).to_csv(OUT/'participant_flow.csv',index=False)
 requests=[]
 def desc(name,group,y,domain):
  requests.append({'analysis':name,'group':group,'variable':y,**ratio(d,d[y],domain)})
 for var in ['unawareness','routine_non_emergency']:
  desc('Calixte attempt','All',var,care_final)
  desc('Calixte measured domain','All',var,core)
 for label,status in [('Routine non-emergency place',0),('No routine non-emergency place',1)]:desc('Calixte attempt',label,'unawareness',care_final&d.no_routine_non_emergency_care.eq(status))
 for label,status in [('All',None),('Insured',0),('Uninsured',1)]:
  domain=ins&d.awareness.notna()&d.uninsured.notna()
  if status is not None:domain &= d.uninsured.eq(status)
  desc('Insurance extension',label,'awareness',domain)
 pd.DataFrame(requests).to_csv(OUT/'python_descriptive.csv',index=False)
 # Table1 requests: variables own nonmissing denominators, category count separate.
 table=[]
 for name,mask,exposure,groups,continuous,categorical in [
  ('Calixte attempt',care_final,'no_routine_non_emergency_care',[(0,'Routine non-emergency place'),(1,'No routine non-emergency place')],['RIDAGEYR','pir','BMXBMI','unawareness'],['sex','race4','college','smoking']),
  ('Insurance extension',ins&d.awareness.notna()&d.uninsured.notna(),'uninsured',[(0,'Insured'),(1,'Uninsured')],['RIDAGEYR','pir','sbp','dbp','awareness'],['sex','race','education','pir_group'])]:
  for value,label in groups:
   domain=mask&d[exposure].eq(value)
   for var in continuous:table.append({'analysis':name,'group':label,'variable':var,'level':'Mean','group_n':int(domain.sum()),'category_n':np.nan,**ratio(d,d[var],domain)})
   for var in categorical:
    for level in LEVELS[var]:
     y=d[var].eq(level).astype(float).where(d[var].notna())
     table.append({'analysis':name,'group':label,'variable':var,'level':level,'group_n':int(domain.sum()),'category_n':int((domain&d[var].eq(level)).sum()),**ratio(d,y,domain)})
 pd.DataFrame(table).to_csv(OUT/'python_table1.csv',index=False)
 missing=[];availability=[]
 for cycle,group in d.groupby('cycle'):
  masks={'Examined18–64':group.RIDAGEYR.between(18,64),'Calixte measured':care_domain(group),'Insurance cases':insurance_domain(group)}
  for population,mask in masks.items():
   for var in ['sbp','dbp','sbp23','dbp23','awareness','no_routine_non_emergency_care','college','college_adult','income','income_family','smoking','obese','pir','uninsured','medication']:
    missing.append({'cycle':cycle,'population':population,'variable':var,'domain_n':int(mask.sum()),'missing_n':int(group.loc[mask,var].isna().sum()),'missing_percent':float(100*group.loc[mask,var].isna().mean())})
  young=group.RIDAGEYR.between(18,19)
  availability.append({'cycle':cycle,'examined18_19_n':int(young.sum()),'adult_education_observed18_19_n':int((young&group.college_adult.notna()).sum()),'harmonized_college_observed18_19_n':int((young&group.college.notna()).sum()),'smoking_observed18_19_n':int((young&group.smoking.notna()).sum()),'paper_final18_19_n':int((young&care_final.loc[group.index]).sum())})
 pd.DataFrame(missing).to_csv(OUT/'missingness.csv',index=False)
 pd.DataFrame(availability).to_csv(OUT/'younger_age_availability.csv',index=False)
 retention=[]
 for name,case,final in [('Calixte attempt',core,care_final),('Insurance extension',ins,ins_final)]:retention.append({'analysis':name,**ratio(d,final.astype(float),case)})
 pd.DataFrame(retention).to_csv(OUT/'weighted_complete_case_retention.csv',index=False)
 (OUT/'design_summary.json').write_text(json.dumps({'full_examined_n':len(d),'strata':int(d.stratum_id.nunique()),'PSUs':int(d.psu_id.nunique()),'design_df':int(d.psu_id.nunique()-d.stratum_id.nunique()),'cycles':list(LEVELS['cycle']),'weight_rule':'WTMEC8YR=WTMEC2YR/4','native_stratum_collision_across_cycles':bool(d.groupby('SDMVSTRA').cycle.nunique().gt(1).any()),'insurance_case_n':int(ins.sum()),'insurance_unresolved_direct_status_exam20_64_n':int((d.RIDAGEYR.between(20,64)&d.hypertension_130.isna()).sum()),'case_definition_note':'No skipped medication imputation in extension; positive-case membership matches original', 'care_case_n':int(core.sum()),'care_complete_n':int(care_final.sum()),'insurance_complete_n':int(ins_final.sum())},indent=2))
 sensitivity_counts=[]
 for label,mask in [('A first3 main',care_domain(d)),('A strict23',care_domain(d,strict23=True)),('A available23',care_domain(d,available=True)),('A age20',care_domain(d,age=(20,64)))]:
  sensitivity_counts.append({'definition':label,'case_eligible_n':int(mask.sum()),'outcome_exposure_complete_n':int((mask&d.unawareness.notna()&d.no_routine_non_emergency_care.notna()).sum()),'full_adjustment_n':int(complete(d,mask,'unawareness',COV_A).sum())})
 pd.DataFrame(sensitivity_counts).to_csv(OUT/'sensitivity_case_counts.csv',index=False)
 counts=[]
 for cycle,g in d.groupby('cycle'):
  c=care_domain(g);b=insurance_domain(g)
  counts.append({'cycle':cycle,'examined_n':len(g),'A_cases_n':int(c.sum()),'A_complete_n':int(care_final.loc[g.index].sum()),'B_cases_n':int(b.sum()),'B_complete_n':int(ins_final.loc[g.index].sum()),'B_uninsured_cases_n':int((b&g.uninsured.eq(1)&g.awareness.notna()).sum())})
 pd.DataFrame(counts).to_csv(OUT/'per_cycle_counts.csv',index=False)
 d.to_csv(OUT/'design_frame.csv',index=False)
 print('Pooled processing complete;',int(care_final.sum()),'Calixte attempted complete cases;',int(ins_final.sum()),'insurance I3 complete cases')

if __name__=='__main__':run()
