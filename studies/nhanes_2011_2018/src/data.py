"""Four-cycle authentic-source harmonization; assumptions are explicit, never benchmark-tuned."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from download import CYCLES,COMPONENTS
ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'data/raw';OUT=ROOT/'outputs'
LEVELS={
 'cycle':['2011–2012','2013–2014','2015–2016','2017–2018'],
 'sex':['Female','Male'],
 'race':['White','Black','Mexican American','Other Hispanic','Asian','Other/multiracial'],
 'education':['College graduate','Some college/AA','High school/GED','Below high school'],
 'race4':['White','Black','Hispanic','Other'],
 'age_group':['18–24','25–34','35–44','45–54','55–64'],
 'college':['College graduate','Below college'],
 'college_adult':['College graduate','Below college'],
 'income':['75,000+','45,000–74,999','20,000–44,999','<20,000'],
 'income_family':['75,000+','45,000–74,999','20,000–44,999','<20,000'],
 'smoking':['Never','Former','Current'],
 'pir_group':['PIR >2','PIR >1–2','PIR ≤1']}
VARS={
 'DEMO':['SEQN','RIDAGEYR','RIAGENDR','RIDRETH3','DMDEDUC2','DMDEDUC3','INDHHIN2','INDFMIN2','INDFMPIR','RIDSTATR','WTMEC2YR','SDMVSTRA','SDMVPSU','RIDEXPRG'],
 'BPX':['SEQN']+[f'BPX{kind}{i}' for kind in ['SY','DI'] for i in range(1,5)],
 'BPQ':['SEQN','BPQ020','BPQ040A','BPQ050A'],
 'HIQ':['SEQN','HIQ011','HIQ210'],
 'HUQ':['SEQN','HUQ030'], 'BMX':['SEQN','BMXBMI'], 'SMQ':['SEQN','SMQ020','SMQ040']}

def normzero(frame):
 frame=frame.copy()
 for c in frame.select_dtypes('number'):frame.loc[frame[c].abs().lt(1e-50),c]=0.
 return frame

def merge(frames):
 for name,f in frames.items():
  if f.SEQN.isna().any() or not f.SEQN.is_unique:raise ValueError('Duplicate/missing SEQN '+name)
 d=frames['DEMO'].copy()
 for name,f in frames.items():
  if name=='DEMO':continue
  if not set(f.SEQN).issubset(set(d.SEQN)):raise ValueError('Orphan component SEQN '+name)
  d=d.merge(f,on='SEQN',how='left',validate='one_to_one')
 if len(d)!=len(frames['DEMO']):raise ValueError('Merge changed base rows')
 return d

def codebook(section,variable):
 node=section.find(id=variable)
 if node is None:raise ValueError('Variable missing from codebook '+variable)
 block=node.find_parent('div',class_='pagebreak')
 pairs={}
 for dt in block.find_all('dt'):
  dd=dt.find_next_sibling('dd')
  if dd is not None:pairs[dt.get_text(' ',strip=True).rstrip(': ')]=dd.get_text(' ',strip=True)
 table=block.find('table')
 codes=[]
 if table:
  for tr in table.find_all('tr')[1:]:
   cells=[t.get_text(' ',strip=True) for t in tr.find_all('td')]
   if len(cells)>=2:codes.append({'code':cells[0],'label':cells[1]})
 return {'text':pairs.get('English Text',''),'target':pairs.get('Target',''),'codes':codes,'label':pairs.get('SAS Label','')}

def load():
 manifest=json.loads((ROOT/'data/source_manifest.json').read_text())
 for name,meta in manifest.items():
  if hashlib.sha256((RAW/name).read_bytes()).hexdigest()!=meta['sha256']:raise ValueError('Source hash mismatch '+name)
 allframes=[];audit=[];joins=[]
 for suffix,year in CYCLES.items():
  frames={}
  for comp,variables in VARS.items():
   name=f'{comp}_{suffix}';f=normzero(pd.read_sas(RAW/(name+'.xpt'),format='xport'))
   chosen=variables.copy()
   if comp=='HUQ':chosen+=['HUQ040' if suffix=='G' else 'HUQ041']
   if not set(chosen).issubset(f):raise ValueError('Missing source variables '+name)
   soup=BeautifulSoup((RAW/(name+'.htm')).read_text(errors='replace'),'html.parser')
   for v in chosen:
    if v=='SEQN':continue
    audit.append({'cycle':f'{year}–{year+1}','suffix':suffix,'component':comp,'source_variable':v,**codebook(soup,v),'url':manifest[name+'.htm']['url']+'#'+v})
   frame=f[chosen].copy()
   if comp=='HUQ':frame=frame.rename(columns={'HUQ040':'place_type','HUQ041':'place_type'})
   frames[comp]=frame
   joins.append({'cycle':f'{year}–{year+1}','component':comp,'n':len(frame),'unique_SEQN':bool(frame.SEQN.is_unique)})
  d=merge(frames);d['cycle']=f'{year}–{year+1}';d['suffix']=suffix;allframes.append(d)
 raw=pd.concat(allframes,ignore_index=True)
 if raw.duplicated(['cycle','SEQN']).any():raise ValueError('Repeated person within cycle')
 return raw,audit,pd.DataFrame(joins)

def income_category(values):
 return values.map({**{x:'<20,000' for x in [1,2,3,4,13]},**{x:'20,000–44,999' for x in [5,6,7]},**{x:'45,000–74,999' for x in [8,9,10]},14:'75,000+',15:'75,000+'})

def classification(sbp,dbp,med,s=130,b=80):
 measured=pd.Series(np.nan,index=sbp.index)
 measured.loc[sbp.notna()&dbp.notna()]=0.
 measured.loc[sbp.ge(s)|dbp.ge(b)]=1.
 hypertension=pd.Series(np.nan,index=sbp.index)
 hypertension.loc[measured.eq(1)|med.eq(1)]=1.
 hypertension.loc[measured.eq(0)&med.eq(0)]=0.
 return measured,hypertension

def prepare(raw):
 d=normzero(raw)
 for i in range(1,5):
  sy,di=f'BPXSY{i}',f'BPXDI{i}'
  if (d[sy].notna()&~d[sy].between(1,300)).any() or (d[di].notna()&~d[di].between(0,300)).any():raise ValueError('Invalid BP range')
  if (d[sy].notna()&d[di].notna()&d[sy].le(d[di])).any():raise ValueError('Invalid paired BP')
 d['sbp']=d[[f'BPXSY{i}' for i in [1,2,3]]].mean(axis=1);d['dbp']=d[[f'BPXDI{i}' for i in [1,2,3]]].mean(axis=1)
 d['sbp23']=d[['BPXSY2','BPXSY3']].mean(axis=1,skipna=False);d['dbp23']=d[['BPXDI2','BPXDI3']].mean(axis=1,skipna=False)
 d['sbp23_available']=d[['BPXSY2','BPXSY3']].mean(axis=1);d['dbp23_available']=d[['BPXDI2','BPXDI3']].mean(axis=1)
 d['awareness']=d.BPQ020.map({1:1.,2:0.});d['unawareness']=1-d.awareness
 d['medication']=d.BPQ050A.map({1:1.,2:0.})
 d['medication_original']=d.medication.copy()
 d['medication_structural_no']=d.BPQ050A.isna()&(d.BPQ020.eq(2)|(d.BPQ020.eq(1)&d.BPQ040A.eq(2)))
 d.loc[d.medication_structural_no,'medication_original']=0.
 for tag,sbp,dbp,s,b in [('130','sbp','dbp',130,80),('140','sbp','dbp',140,90),('23','sbp23','dbp23',130,80),('23_available','sbp23_available','dbp23_available',130,80)]:
  d['elevated_'+tag],d['hypertension_'+tag]=classification(d[sbp],d[dbp],d.medication,s,b)
 d['uninsured']=d.HIQ011.map({1:0.,2:1.})
 d['no_routine']=d.HUQ030.map({1:0.,2:1.,3:1.});d['routine']=1-d.no_routine
 d['no_any_place']=d.HUQ030.map({1:0.,2:1.,3:0.})
 d['no_routine_non_emergency_care']=pd.Series(np.nan,index=d.index)
 d.loc[d.HUQ030.eq(2),'no_routine_non_emergency_care']=1.
 d.loc[d.HUQ030.isin([1,3])&d.place_type.eq(3),'no_routine_non_emergency_care']=1.
 d.loc[d.HUQ030.isin([1,3])&d.place_type.isin([1,2,4,5]),'no_routine_non_emergency_care']=0.
 d['routine_non_emergency']=1-d.no_routine_non_emergency_care
 d['sex']=d.RIAGENDR.map({1:'Male',2:'Female'})
 d['race']=d.RIDRETH3.map({1:'Mexican American',2:'Other Hispanic',3:'White',4:'Black',6:'Asian',7:'Other/multiracial'})
 d['race4']=d.RIDRETH3.map({1:'Hispanic',2:'Hispanic',3:'White',4:'Black',6:'Other',7:'Other'})
 d['education']=d.DMDEDUC2.map({1:'Below high school',2:'Below high school',3:'High school/GED',4:'Some college/AA',5:'College graduate'})
 d['college_adult']=d.DMDEDUC2.map({1:'Below college',2:'Below college',3:'Below college',4:'Below college',5:'College graduate'})
 d['college']=d.college_adult.copy()
 youth=d.RIDAGEYR.between(18,19)&(d.DMDEDUC3.between(0,14)|d.DMDEDUC3.isin([55,66]))
 d.loc[youth,'college']='Below college'
 d['income']=income_category(d.INDHHIN2);d['income_family']=income_category(d.INDFMIN2)
 d['pir']=d.INDFMPIR.where(d.INDFMPIR.between(0,5));d['pir_group']=pd.cut(d.pir,[-.001,1,2,5],labels=['PIR ≤1','PIR >1–2','PIR >2']).astype(object)
 d['age10']=(d.RIDAGEYR-40)/10;d['age10_sq']=d.age10**2
 d['age_group']=pd.cut(d.RIDAGEYR,[17,24,34,44,54,64],labels=LEVELS['age_group']).astype(object)
 d['obese']=d.BMXBMI.ge(30).astype(float).where(d.BMXBMI.notna())
 d['smoking']=pd.Series(np.nan,index=d.index,dtype=object)
 d.loc[d.SMQ020.eq(2),'smoking']='Never'
 d.loc[d.SMQ020.eq(1)&d.SMQ040.eq(3),'smoking']='Former'
 d.loc[d.SMQ020.eq(1)&d.SMQ040.isin([1,2]),'smoking']='Current'
 d['WTMEC8YR']=d.WTMEC2YR/4
 d['stratum_id']=d.suffix+'_'+d.SDMVSTRA.astype('Int64').astype(str)
 d['psu_id']=d.stratum_id+'_'+d.SDMVPSU.astype('Int64').astype(str)
 return d

def insurance_domain(d,age=(20,64),definition='hypertension_130',bp_complete=False,exclude_pregnancy=False):
 mask=d.RIDAGEYR.between(*age)&d.RIDSTATR.eq(2)&d.WTMEC2YR.gt(0)&d[definition].eq(1)
 if bp_complete:mask &= d.sbp.notna()&d.dbp.notna()
 if exclude_pregnancy:mask &= ~d.RIDEXPRG.eq(1)
 return mask

def care_domain(d,available=False,strict23=False,age=(18,64)):
 definition='elevated_23' if strict23 else 'elevated_23_available' if available else 'elevated_130'
 sy,di=('sbp23','dbp23') if strict23 else ('sbp23_available','dbp23_available') if available else ('sbp','dbp')
 return d.RIDAGEYR.between(*age)&d.RIDSTATR.eq(2)&d.WTMEC2YR.gt(0)&d[sy].notna()&d[di].notna()&d[definition].eq(1)
