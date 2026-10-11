"""Aggregate statistical graphics only; 300dpi PNG and vector PDF, no invented data."""
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FixedLocator,FuncFormatter,NullFormatter
from data import ROOT,OUT
from validate import assert_current
FIG=ROOT/'figures'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
COLOR='#17656a';OTHER='#b16b39'
def save(fig,name):
 FIG.mkdir(exist_ok=True)
 for ext in ['png','pdf']:fig.savefig(FIG/f'{name}.{ext}',dpi=300,bbox_inches='tight')
 plt.close(fig)
def forest(ax,rows,labels,title):
 y=np.arange(len(rows))[::-1]
 ax.errorbar(rows.ratio,y,xerr=np.vstack([rows.ratio-rows.ci_low,rows.ci_high-rows.ratio]),fmt='o',capsize=3,color=COLOR)
 ax.set_yticks(y,labels);ax.axvline(1,color='gray',ls='--',lw=1);ax.set_xscale('log')
 lo=float(rows.ci_low.min());hi=float(rows.ci_high.max())
 ticks=[1,1.1,1.2,1.3,1.4,1.5,1.6,1.8] if lo>=.8 and hi<2 else [.1,.2,.3,.5,.75,1,1.5,2,3,5,10]
 ax.xaxis.set_major_locator(FixedLocator(ticks));ax.xaxis.set_major_formatter(FuncFormatter(lambda v,pos:f'{v:g}'));ax.xaxis.set_minor_formatter(NullFormatter())
 ax.set_xlabel('Ratio estimate (95% survey CI; log scale)');ax.set_title(title);ax.grid(axis='x',alpha=.15)
def run():
 assert_current();flow=pd.read_csv(OUT/'participant_flow.csv');reg=pd.read_csv(OUT/'regression.csv');desc=pd.read_csv(OUT/'descriptive.csv');marginal=pd.read_csv(OUT/'marginal_probabilities.csv')
 for analysis,name in [('Calixte attempt','flow_study_A'),('Insurance extension','flow_study_B')]:
  rows=flow[flow.analysis.eq(analysis)];fig,ax=plt.subplots(figsize=(8,9));ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off');ys=np.linspace(.92,.12,len(rows))
  for i,((_,r),y) in enumerate(zip(rows.iterrows(),ys)):
   ax.add_patch(FancyBboxPatch((.08,y-.035),.82,.07,boxstyle='round,pad=.012',facecolor='#edf5f5',edgecolor=COLOR))
   ax.text(.49,y,f'{r.stage}\nn = {r.n:,}',ha='center',va='center')
   if i:ax.annotate('',xy=(.49,y+.046),xytext=(.49,ys[i-1]-.045),arrowprops={'arrowstyle':'->','color':COLOR});ax.text(.96,(y+ys[i-1])/2,f'−{r.excluded_since_previous:,}',ha='center',fontsize=9)
  ax.set_title('Study A · approximate replication' if analysis=='Calixte attempt' else 'Study B · insurance extension',pad=12)
  note='Ages 18–64; mean BP from readings 1–3 ≥130/80; no medication-only cases.' if analysis=='Calixte attempt' else 'Ages 20–64; measured ≥130/80 or reported current medication.\nMedication-confirmed cases can have missing BP; no skip imputation.'
  ax.text(.49,.025,note,ha='center',fontsize=9);save(fig,name)
 # Figure1 with scientifically separated outcome scales.
 fig,axes=plt.subplots(1,2,figsize=(10,4.5))
 for ax,analysis,outcome,groups,title in [
  (axes[0],'Calixte attempt','unawareness',['Routine non-emergency place','No routine non-emergency place'],'Study A · unawareness'),
  (axes[1],'Insurance extension','awareness',['Insured','Uninsured'],'Study B · awareness')]:
  rows=desc[(desc.analysis==analysis)&(desc.variable==outcome)].set_index('group').loc[groups]
  ax.errorbar([0,1],100*rows.estimate,yerr=np.vstack([100*(rows.estimate-rows.ci_low),100*(rows.ci_high-rows.estimate)]),fmt='o',markersize=7,capsize=4,color=COLOR)
  labels=['Non-emergency\nroutine place','Lacking non-emergency\nroutine place'] if analysis=='Calixte attempt' else groups
  ax.set_xticks([0,1],labels);ax.set_ylim(0,100);ax.set_ylabel('Survey-weighted percentage (95% CI)');ax.set_title(title);ax.grid(axis='y',alpha=.15)
  for i,(_,r) in enumerate(rows.iterrows()):ax.text(i,100*r.ci_high+4,f'n={r.n:,}',ha='center',fontsize=9)
 fig.tight_layout();save(fig,'weighted_outcomes')
 # Figure2 separates ratios that must not be treated as interchangeable.
 fig,axes=plt.subplots(1,2,figsize=(11,5))
 a=reg[(reg.term=='no_routine_non_emergency_care')&reg.model.isin(['A1','A2','A3','A4'])].set_index('model').loc[['A1','A2','A3','A4']]
 forest(axes[0],a,['Exposure only','Demographic','Add SES','Add obesity/smoking'],'Study A · unawareness prevalence ratios')
 b=reg[(reg.term=='uninsured')&reg.model.isin(['I3','I3_PR','J3'])].set_index('model').loc[['I3','I3_PR','J3']]
 forest(axes[1],b,['2011–2018 adjusted OR','2011–2018 adjusted PR','2017–2018 adjusted OR'],'Study B · uninsured vs insured awareness')
 fig.tight_layout();save(fig,'association_forest')
 # Figure3: selected declared sensitivities, not selected by significance.
 fig,axes=plt.subplots(1,2,figsize=(13,6))
 anames=['A4','A4_strict23','A4_no_place_only','A4_single_place','A4_exclude_ER','A4_household_income']
 a=reg[reg.model.isin(anames)&reg.term.isin(['no_routine_non_emergency_care','no_any_place','no_routine'])].set_index('model').loc[anames]
 forest(axes[0],a,['Main non-ER proxy','Strict readings2–3','No-place only','Single-place only','Exclude ER users','Grouped household income'],'Study A · reconstruction sensitivities')
 bnames=['I3','I3_measured','I3_140','I3_bp_complete','I3_cycle','I3_omit_PIR']
 b=reg[(reg.term=='uninsured')&reg.model.isin(bnames)].set_index('model').loc[bnames]
 forest(axes[1],b,['Main matched model','Measured-only130/80','Threshold140/90 + medicine','Require BP complete','Cycle adjustment','Omit PIR'],'Study B · adjusted OR sensitivities')
 fig.tight_layout();save(fig,'sensitivity_comparison')
 # Logistic probability standardization is included as a small optional fourth statistical panel.
 fig,ax=plt.subplots(figsize=(6,4));rows=marginal.iloc[:2]
 ax.errorbar([0,1],100*rows.estimate,yerr=np.vstack([100*(rows.estimate-rows.ci_low),100*(rows.ci_high-rows.estimate)]),fmt='o',capsize=4,color=COLOR)
 ax.set_xticks([0,1],rows.estimand);ax.set_ylim(0,100);ax.set_ylabel('Standardized awareness probability (%)');ax.set_title('Study B · logistic standardization');ax.grid(axis='y',alpha=.15);fig.tight_layout();save(fig,'adjusted_probabilities')
 (FIG/'CAPTIONS.md').write_text('''# Figure captions

Flow A/B: unweighted sequential domain counts. A requires measured BP; B admits current-medication cases without BP. A case and final model counts are distinct. No original figures were overwritten.

Weighted outcomes: A shows unawareness on the A4-complete reconstructed cohort; B shows awareness among insurance/outcome-complete cases. They have different exposures, outcomes, populations and denominators. Bounded beta/Korn–Graubard-type CI, NCHS screening in tables.

Association forest: model-specific survey Taylor intervals with residual design reference df. A PRs estimate unawareness; B ratios estimate awareness. OR and PR are different measures. Original single-cycle OR is a historical baseline, not an independent contemporaneous control.

Sensitivity comparison: specifications were declared in the final protocol before revised fitting; final plan followed preliminary exploration and is not preregistered. Case/response coding changes estimands; no closest-to-benchmark selection.

Adjusted probabilities: B3 logistic predictions standardized over the weighted B3 complete-case covariate distribution; joint Taylor model/distribution uncertainty, logit-transformed bounded intervals, residual model df. Independent JKn refits assess variance. These are associational model standardizations, not an insurance policy effect. Quasi-Poisson fitted means above1 are diagnosed and never presented as probabilities.
''')
 print('Generated separate flows and aggregate 300-DPI PNG/vector PDF figures')

if __name__=='__main__':run()
