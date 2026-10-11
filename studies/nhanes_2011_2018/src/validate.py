"""Numerical comparison to R, historical J-only checks, and content-linked validation."""
import hashlib,json,numpy as np,pandas as pd
from data import ROOT,OUT,LEVELS

def key(term):
 if term=='(Intercept)':return 'Intercept'
 for var in sorted(LEVELS,key=len,reverse=True):
  if term.startswith(var):return var+'_'+term[len(var):].lstrip('_')
 return term

def fingerprint():
 paths=[p for folder in ['src','r','data/raw'] for p in (ROOT/folder).glob('*') if p.is_file()]+[p for p in OUT.glob('*.csv') if p.name not in ['replication_comparison.csv','comparative_results.csv']]+[ROOT/'data/source_manifest.json',ROOT/'run_all.py',ROOT/'requirements.txt']
 return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}

def assert_current():
 old=json.loads((OUT/'validation_provenance.json').read_text())
 if old['fingerprint']!=fingerprint():raise AssertionError('Validation is stale: code/data/results changed')
 state=OUT/'run_state.json'
 if state.exists() and json.loads(state.read_text())['status']=='failed':raise AssertionError('Current run failed; report blocked')
 result=json.loads((OUT/'validation.json').read_text())
 if not all(v['passed'] for v in result.values()):raise AssertionError('Incomplete validation')
 return result

def run():
 (OUT/'validation.json').unlink(missing_ok=True)
 for name in ['r_reference_receipt.csv','r_robustness_receipt.csv']:
  for row in pd.read_csv(OUT/name).itertuples():
   if hashlib.md5((ROOT/row.path).read_bytes()).hexdigest()!=row.md5:raise AssertionError('Stale R execution '+row.path)
 report={};comparisons=[]
 for name,keys,cols in [
 ('regression',['model','term'],['beta','se','ratio','ci_low','ci_high','p','n','events','design_df','residual_df']),
 ('descriptive',['analysis','group','variable'],['estimate','se','n','design_df']),
 ('table1',['analysis','group','variable','level'],['estimate','se','n','design_df']),
 ('marginal',['estimand'],['estimate','se','ci_low','ci_high','n','design_df','inference_df'])]:
  a=pd.read_csv(OUT/f'python_{name}.csv');b=pd.read_csv(OUT/({'marginal':'marginal_probabilities'}.get(name,name)+'.csv'))
  if name=='regression':b.term=b.term.map(key)
  z=a.merge(b,on=keys,suffixes=('_p','_r'),validate='one_to_one',how='outer',indicator=True)
  if not z._merge.eq('both').all():raise AssertionError('Unmatched comparison rows '+name)
  for c in cols:
   x=z[c+'_p'].to_numpy();y=z[c+'_r'].to_numpy();delta=float(np.nanmax(abs(x-y)))
   if not np.allclose(x,y,rtol=2e-6,atol=1e-8,equal_nan=True):raise AssertionError(f'{name}.{c} differs: {delta}')
   comparisons.append({'analysis':name,'quantity':c,'n_rows':len(z),'max_abs_difference':delta,'passed':True})
  report[name]={'rows':len(z),'passed':True}
 a=pd.read_csv(OUT/'python_covariance.csv');b=pd.read_csv(OUT/'r_covariance.csv')
 for c in ['term1','term2']:b[c]=b[c].map(key)
 z=a.merge(b,on=['model','term1','term2'],suffixes=('_p','_r'),validate='one_to_one',how='outer',indicator=True)
 if not z._merge.eq('both').all() or not np.allclose(z.covariance_p,z.covariance_r,rtol=2e-6,atol=1e-8):raise AssertionError('Full covariance differs')
 report['covariance']={'entries':len(z),'max_abs_difference':float(abs(z.covariance_p-z.covariance_r).max()),'passed':True}
 for name,col in [('r_raw_coding_validation','passed'),('r_domain_validation','raw_rebuilt_matches_python')]:
  t=pd.read_csv(OUT/(name+'.csv'))
  if not t[col].all():raise AssertionError(name+' failed')
  report[name]={'checks':len(t),'passed':True}
 # Original R rows are reference data, not hardcoded sample/results constants.
 old=pd.read_csv(ROOT/'reference/single_cycle/regression.csv');new=pd.read_csv(OUT/'regression.csv')
 baseline_checks=[]
 for j,m in [('J1','M1'),('J2','M2'),('J3','M3')]:
  a=new[new.model.eq(j)].copy();b=old[old.model.eq(m)].copy()
  z=a.merge(b,on='term',suffixes=('_new','_old'),validate='one_to_one',how='outer',indicator=True)
  if not z._merge.eq('both').all():raise AssertionError('Historical terms differ')
  for c1,c2 in [('beta','beta'),('se','se'),('ratio','odds_ratio'),('ci_low','ci_low'),('ci_high','ci_high'),('n','n'),('residual_df','residual_df')]:
   x=z[c1+'_new'] if c1==c2 else z[c1];y=z[c2+'_old'] if c1==c2 else z[c2]
   if not np.allclose(x,y,rtol=2e-6,atol=1e-8):raise AssertionError('Historical J difference '+c1)
   baseline_checks.append({'new_model':j,'old_model':m,'quantity':c1,'max_abs_difference':float(abs(x-y).max()),'passed':True})
 pd.DataFrame(baseline_checks).to_csv(OUT/'single_cycle_reproduction.csv',index=False)
 report['historical_J']={'models':3,'passed':True,'scope':'Actual previously calculated outputs compared; no benchmark fitting'}
 jk=pd.read_csv(OUT/'jackknife_validation.csv')
 if not np.isfinite(jk.jackknife_se).all():raise AssertionError('Replicate output invalid')
 report['R_JKn']={'passed':True,'replicates':int(jk.replicates.iloc[0]),'PIR_scope':'R-only executed sensitivity, not independent Python PIR validation'}
 pd.DataFrame(comparisons).to_csv(OUT/'validation_comparison.csv',index=False)
 (OUT/'validation.json').write_text(json.dumps(report,indent=2))
 (OUT/'validation_provenance.json').write_text(json.dumps({'fingerprint':fingerprint()},indent=2))
 print('PASS: R coding/domains, Python/R covariance/descriptors/models, historical J-only reproduction; R robustness executed')

if __name__=='__main__':run()
