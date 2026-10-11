"""Independent weighted-score/Taylor calculations compared to R survey, never ordinary GLM SE."""
import numpy as np,pandas as pd,statsmodels.api as sm
from scipy.special import expit,logit
from scipy.stats import t
from data import LEVELS

def matrix(d,variables):
 x=[pd.Series(1.,index=d.index,name='Intercept')]
 for v in variables:
  if v in LEVELS:
   for level in LEVELS[v][1:]:x.append(d[v].eq(level).astype(float).rename(v+'_'+level))
  else:x.append(d[v].astype(float).rename(v))
 return pd.concat(x,axis=1)

def complete(d,domain,outcome,variables):
 keep=domain&d[outcome].notna()
 for v in variables:keep &= d[v].notna()
 return keep

def covariance(d,influence):
 x=np.asarray(influence)
 if x.ndim==1:x=x[:,None]
 f=pd.DataFrame(x,index=d.index);f['stratum_id']=d.stratum_id;f['psu_id']=d.psu_id
 g=f.groupby(['stratum_id','psu_id'])[list(range(x.shape[1]))].sum()
 cov=np.zeros((x.shape[1],x.shape[1]));df=0
 for _,sub in g.groupby(level=0):
  m=len(sub)
  if m<2:raise ValueError('Lonely PSU')
  z=sub.to_numpy()-sub.to_numpy().mean(axis=0);cov+=m/(m-1)*z.T@z;df+=m-1
 return cov,df

def ratio(d,y,domain,weight='WTMEC8YR'):
 y=pd.Series(y,index=d.index,dtype=float);keep=domain&y.notna()&d[weight].gt(0)
 w=d[weight].where(keep,0).to_numpy();total=w.sum()
 if not total:return dict(n=0,estimate=np.nan,se=np.nan,design_df=np.nan)
 mu=np.dot(w,y.fillna(0))/total;cov,df=covariance(d,w*(y.fillna(0).to_numpy()-mu)/total)
 domain_frame=d.loc[keep,['stratum_id','psu_id']].drop_duplicates()
 reference_df=domain_frame.psu_id.nunique()-domain_frame.stratum_id.nunique()
 return dict(n=int(keep.sum()),estimate=float(mu),se=float(np.sqrt(cov[0,0])),design_df=int(reference_df),full_design_df=df)

def fit(d,domain,outcome,variables,model,family='logit',weight='WTMEC8YR'):
 keep=complete(d,domain,outcome,variables)&d[weight].gt(0);sub=d.loc[keep]
 x=matrix(sub,variables);a=x.to_numpy();y=sub[outcome].to_numpy();w=sub[weight].to_numpy();w/=w.mean()
 if len(np.unique(y))<2 or np.linalg.matrix_rank(a)<a.shape[1]:raise ValueError('Empty/constant/rank-deficient model')
 fam=sm.families.Binomial() if family=='logit' else sm.families.Poisson()
 r=sm.GLM(y,a,family=fam,freq_weights=w).fit(maxiter=200,tol=1e-12)
 if not r.converged:raise ValueError('GLM did not converge')
 beta=np.asarray(r.params);mu=expit(a@beta) if family=='logit' else np.exp(a@beta)
 variance=mu*(1-mu) if family=='logit' else mu
 bread=(a.T*(w*variance))@a;scores=a*(w*(y-mu))[:,None]
 linearized=np.linalg.solve(bread,scores.T).T
 influence=np.zeros((len(d),a.shape[1]));influence[keep.to_numpy()]=linearized
 cov,df=covariance(d,influence);rdf=df-a.shape[1]+1
 if rdf<=0:raise ValueError('Nonpositive reference df')
 se=np.sqrt(np.diag(cov));q=t.ppf(.975,rdf)
 table=pd.DataFrame({'model':model,'family':family,'term':x.columns,'beta':beta,'se':se,'ratio':np.exp(beta),'ci_low':np.exp(beta-q*se),'ci_high':np.exp(beta+q*se),'p':2*t.sf(np.abs(beta/se),rdf),'n':len(sub),'events':int(y.sum()),'design_df':df,'residual_df':rdf})
 h=w*variance*np.einsum('ij,jk,ik->i',a,np.linalg.inv(bread),a)
 diagnostic={'model':model,'family':family,'n':len(sub),'rank':a.shape[1],'design_df':df,'residual_df':rdf,'converged':bool(r.converged),'max_score':float(abs(scores.sum(axis=0)).max()),'covariance_min_eigenvalue':float(np.linalg.eigvalsh(cov).min()),'information_condition':float(np.linalg.cond(bread)),'min_prediction':float(mu.min()),'max_prediction':float(mu.max()),'predictions_above_one_n':int((mu>1).sum()),'max_leverage':float(h.max())}
 return table,diagnostic,{'keep':keep,'beta':beta,'cov':cov,'influence':influence,'variables':variables,'family':family,'names':list(x.columns),'residual_df':rdf,'weight':weight}

def standardized(d,info):
 if info['family']!='logit':raise ValueError('Only bounded logistic predictions are standardized')
 keep=info['keep'];sub=d.loc[keep];w=sub[info['weight']].to_numpy();total=w.sum();means=[];influences=[]
 for exposure in [0.,1.]:
  z=sub.copy();z['uninsured']=exposure;x=matrix(z,info['variables']).to_numpy();p=expit(x@info['beta']);mu=np.dot(w,p)/total
  grad=np.sum(x*(w*p*(1-p))[:,None],axis=0)/total
  influence=info['influence']@grad;influence[keep.to_numpy()]+=w*(p-mu)/total
  means.append(mu);influences.append(influence)
 means.append(means[1]-means[0]);influences.append(influences[1]-influences[0]);rows=[]
 for label,mu,inf in zip(['Insured','Uninsured','Uninsured minus insured'],means,influences):
  cv,df=covariance(d,inf);se=np.sqrt(cv[0,0]);q=t.ppf(.975,info['residual_df'])
  low,high=mu-q*se,mu+q*se
  if label!='Uninsured minus insured':low,high=expit(logit(mu)+np.array([-1,1])*q*se/(mu*(1-mu)))
  rows.append({'estimand':label,'estimate':mu,'se':se,'ci_low':low,'ci_high':high,'design_df':df,'inference_df':info['residual_df'],'n':len(sub)})
 return pd.DataFrame(rows)
