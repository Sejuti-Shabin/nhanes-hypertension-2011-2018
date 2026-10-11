"""Synthetic definitions and executed integration checks; no hardcoded publication targets."""
import sys,unittest,tempfile,shutil,json,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np,pandas as pd
from data import ROOT,OUT,load,prepare,merge,income_category,classification,care_domain,insurance_domain
from survey import ratio,fit,standardized

class Definitions(unittest.TestCase):
 def test_three_valued_case_logic(self):
  m,c=classification(pd.Series([140.,120.,np.nan,120.]),pd.Series([np.nan,70.,np.nan,70.]),pd.Series([np.nan,np.nan,1.,0.]))
  np.testing.assert_allclose(m,[1,0,np.nan,0],equal_nan=True)
  np.testing.assert_allclose(c,[1,np.nan,1,0],equal_nan=True)
 def test_income_ambiguous_code_preserved(self):
  x=income_category(pd.Series([1,13,5,7,8,10,14,15,12,77,99,np.nan]))
  self.assertEqual(x.iloc[:8].tolist(),['<20,000','<20,000','20,000–44,999','20,000–44,999','45,000–74,999','45,000–74,999','75,000+','75,000+'])
  self.assertTrue(x.iloc[8:].isna().all())
 def test_merge_integrity(self):
  d={'DEMO':pd.DataFrame({'SEQN':[1,2]}),'BPX':pd.DataFrame({'SEQN':[1,2],'x':[2,3]})}
  self.assertEqual(len(merge(d)),2)
  d['BPX']=pd.DataFrame({'SEQN':[1,1]})
  with self.assertRaises(ValueError):merge(d)
  d['BPX']=pd.DataFrame({'SEQN':[3]})
  with self.assertRaises(ValueError):merge(d)
 def test_synthetic_full_domain_variance(self):
  d=pd.DataFrame({'stratum_id':['a','a','b','b'],'psu_id':['a1','a2','b1','b2'],'WTMEC8YR':[1.,1.,1.,1.]})
  x=ratio(d,pd.Series([0.,1.,0.,1.]),pd.Series([True]*4))
  self.assertAlmostEqual(x['estimate'],.5);self.assertAlmostEqual(x['se']**2,.125)
  x=ratio(d,pd.Series([0.,1.,0.,1.]),pd.Series([True,True,False,False]))
  self.assertAlmostEqual(x['se'],.5);self.assertEqual(x['full_design_df'],2)
 def test_nchs_edges(self):
  p=subprocess.run(['Rscript',str(ROOT/'tests/test_reliability.R'),str(ROOT)],capture_output=True,text=True)
  self.assertEqual(p.returncode,0,p.stdout+p.stderr)
 def test_failed_run_invalidates_success(self):
  with tempfile.TemporaryDirectory() as temp:
   d=Path(temp);shutil.copy(ROOT/'run_all.py',d/'run_all.py');shutil.copytree(ROOT/'src',d/'src',ignore=shutil.ignore_patterns('__pycache__'))
   (d/'outputs').mkdir();(d/'outputs/validation.json').write_text('{"previous":{"passed":true}}')
   p=subprocess.run([sys.executable,str(d/'run_all.py'),'--check-only'],capture_output=True,text=True)
   self.assertNotEqual(p.returncode,0);self.assertFalse((d/'outputs/validation.json').exists())
   self.assertEqual(json.loads((d/'outputs/run_state.json').read_text())['status'],'failed')

class Authentic(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw,cls.audit,cls.joins=load();cls.all=prepare(cls.raw)
  cls.d=cls.all.loc[cls.all.RIDSTATR.eq(2)&cls.all.WTMEC2YR.gt(0)].reset_index(drop=True)
 def test_source_cycles_and_unique_ids(self):
  self.assertEqual(set(self.all.suffix),{'G','H','I','J'})
  self.assertFalse(self.all.duplicated(['cycle','SEQN']).any())
  self.assertTrue(self.joins.unique_SEQN.all())
 def test_weight_divisor_and_design(self):
  np.testing.assert_allclose(self.d.WTMEC8YR,self.d.WTMEC2YR/4,rtol=0,atol=0)
  self.assertTrue(self.d.WTMEC8YR.gt(0).all())
  self.assertTrue(self.d.groupby('stratum_id').psu_id.nunique().ge(2).all())
  self.assertTrue(self.d[['SDMVSTRA','SDMVPSU']].notna().all().all())
 def test_unknown_codes_not_outcomes(self):
  d=self.d
  self.assertTrue(d.loc[~d.BPQ020.isin([1,2]),'awareness'].isna().all())
  self.assertTrue(d.loc[~d.HIQ011.isin([1,2]),'uninsured'].isna().all())
  self.assertTrue(d.loc[d.BPQ050A.isna(),'medication'].isna().all())
 def test_bp_mean_zero_and_alternative(self):
  r=self.raw.iloc[[0]].copy()
  r[['BPXSY1','BPXSY2','BPXSY3']]=[120,np.nan,140]
  r[['BPXDI1','BPXDI2','BPXDI3']]=[0,np.nan,80]
  z=prepare(r)
  self.assertAlmostEqual(z.sbp.iloc[0],130);self.assertAlmostEqual(z.dbp.iloc[0],40)
  self.assertTrue(z.sbp23.isna().all());self.assertAlmostEqual(z.sbp23_available.iloc[0],140)
 def test_routine_non_emergency_mapping(self):
  raw=pd.concat([self.raw.iloc[[0]]]*7,ignore_index=True)
  raw.HUQ030=[1,1,3,2,3,7,1];raw.place_type=[2,3,4,np.nan,6,2,77]
  z=prepare(raw)
  np.testing.assert_allclose(z.no_routine_non_emergency_care,[0,1,0,1,np.nan,np.nan,np.nan],equal_nan=True)
 def test_medication_only_excluded_from_A(self):
  d=self.d;b=insurance_domain(d);a=care_domain(d)
  controlled=d.medication.eq(1)&d.sbp.lt(130)&d.dbp.lt(80)&d.RIDAGEYR.between(20,64)
  self.assertTrue(b[controlled].all());self.assertFalse(a[controlled].any())
  missing=d.medication.eq(1)&(d.sbp.isna()|d.dbp.isna())&d.RIDAGEYR.between(20,64)
  self.assertTrue(b[missing].all())
 def test_age_appropriate_schooling(self):
  d=self.d;young=d.RIDAGEYR.between(18,19)
  self.assertTrue(d.loc[young,'college_adult'].isna().all())
  ambiguous=young&d.DMDEDUC3.eq(15)
  self.assertTrue(d.loc[ambiguous,'college'].isna().all())
 def test_source_type_variable_harmonization(self):
  a=pd.DataFrame(self.audit)
  for suffix,source in [('G','HUQ040'),('H','HUQ041'),('I','HUQ041'),('J','HUQ041')]:
   self.assertTrue(((a.suffix==suffix)&(a.source_variable==source)).any())
 def test_J_case_ids_match_original(self):
  path=ROOT.parent/'nhanes_2017_2018/outputs/design_frame.csv'
  if not path.exists():self.skipTest('Historical person-level frame is intentionally absent from portable Git export; coefficient comparisons still run')
  historical=pd.read_csv(path)
  j=self.d[self.d.suffix.eq('J')].reset_index(drop=True)
  expected=set(historical.loc[historical.domain_m3.eq(1),'SEQN'])
  keep=insurance_domain(j)&j[['awareness','uninsured','age10','sex','race','education','pir']].notna().all(axis=1)
  self.assertEqual(set(j.loc[keep,'SEQN']),expected)
 def test_scale_order_and_model_standardization(self):
  d=self.d[self.d.suffix.eq('J')].reset_index(drop=True);variables=['uninsured','age10','sex','race','education','pir']
  a,_,info=fit(d,insurance_domain(d),'awareness',variables,'test')
  z=d.copy();z.WTMEC8YR*=19.7
  b,_,_=fit(z,insurance_domain(z),'awareness',variables,'test')
  np.testing.assert_allclose(a[['beta','se']],b[['beta','se']],rtol=1e-8,atol=1e-10)
  z=d.sample(frac=1,random_state=20261010).reset_index(drop=True)
  b,_,_=fit(z,insurance_domain(z),'awareness',variables,'test')
  np.testing.assert_allclose(a[['beta','se']],b[['beta','se']],rtol=1e-8,atol=1e-10)
  m=standardized(d,info);self.assertTrue(m.iloc[:2].ci_low.between(0,1).all());self.assertTrue(m.iloc[:2].ci_high.between(0,1).all())
 def test_R_comparisons_and_replicates(self):
  from validate import run
  run()
  k=pd.read_csv(OUT/'jackknife_validation.csv');replicas=self.d.psu_id.nunique()
  self.assertTrue(k.replicates.eq(replicas).all());self.assertTrue(np.isfinite(k.jackknife_se).all())
  p=pd.read_csv(OUT/'pir_response_summary.csv').iloc[0]
  self.assertGreater(p.min_response_probability,0);self.assertLess(p.max_response_probability,1);self.assertEqual(p.replicates,replicas)

if __name__=='__main__':unittest.main()
