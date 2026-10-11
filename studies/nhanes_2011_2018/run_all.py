#!/usr/bin/env python3
"""Complete fail-closed reproducibility command; all outputs are derived from authentic data."""
import argparse,importlib.metadata,json,os,re,subprocess,sys,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def run():
 parser=argparse.ArgumentParser();parser.add_argument('--check-only',action='store_true');parser.add_argument('--offline',action='store_true',help='Do not fetch missing sources; cached source files must exist');args=parser.parse_args()
 out=ROOT/'outputs';out.mkdir(exist_ok=True);logs=out/'logs';logs.mkdir(exist_ok=True)
 state={'run_id':str(uuid.uuid4()),'status':'running','stages':[]}
 def save():
  (out/'run_state.json').write_text(json.dumps(state,indent=2));(out/'execution.json').write_text(json.dumps(state['stages'],indent=2))
 for name in ['validation.json','validation_provenance.json','tests.json','clean_copy_validation.json']:(out/name).unlink(missing_ok=True)
 save();env=os.environ.copy();env['PYTHONHASHSEED']='0';env['TZ']='America/Chicago'
 local=Path.home()/'R/library'
 if local.exists():env['R_LIBS_USER']=str(local)+(':'+env['R_LIBS_USER'] if env.get('R_LIBS_USER') else '')
 commands=[]
 if not args.check_only:
  if not args.offline:commands.append(('download',[sys.executable,'src/download.py']))
  commands += [('prepare',[sys.executable,'src/pipeline.py']),('R_reference',['Rscript','r/analysis.R',str(ROOT)]),('R_robustness',['Rscript','r/robustness.R',str(ROOT)])]
 commands += [('validate',[sys.executable,'src/validate.py']),('baseline_tests',[sys.executable,'src/audit_baseline.py']),('tests',[sys.executable,'-m','unittest','discover','-s','tests','-v'])]
 if not args.check_only:commands += [('figures',[sys.executable,'src/figures.py']),('report',[sys.executable,'src/report.py']),('QA',[sys.executable,'src/qa.py'])]
 for name,cmd in commands:
  print('Running',name,flush=True);start=time.monotonic()
  try:
   p=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True);rc=p.returncode;output=p.stdout+p.stderr
  except OSError as e:rc=127;output=str(e)
  (logs/(name+'.log')).write_text(output)
  state['stages'].append({'stage':name,'returncode':rc,'seconds':round(time.monotonic()-start,3)});save()
  if name=='tests':
   match=re.search(r'Ran (\d+) tests',output);fail=re.search(r'failures=(\d+)',output);error=re.search(r'errors=(\d+)',output);skipped=re.search(r'skipped=(\d+)',output)
   (out/'tests.json').write_text(json.dumps({'tests':int(match.group(1)) if match else None,'passed':rc==0,'failures':int(fail.group(1)) if fail else 0,'errors':int(error.group(1)) if error else 0,'skipped':int(skipped.group(1)) if skipped else 0,'passed_count':(int(match.group(1)) if match else 0)-(int(fail.group(1)) if fail else 0)-(int(error.group(1)) if error else 0)-(int(skipped.group(1)) if skipped else 0)},indent=2))
  if rc:
   state['status']='failed';state['failed_stage']=name;save()
   (out/'validation.json').unlink(missing_ok=True);(out/'validation_provenance.json').unlink(missing_ok=True)
   print(output);raise SystemExit(name+' failed; prior success invalidated')
  print(p.stdout.strip() if 'p' in locals() else output,flush=True)
 environment={'python':sys.version,'random_seed':20261010,'stochastic_estimation':False}
 for name in ['numpy','pandas','scipy','statsmodels','matplotlib','beautifulsoup4']:environment[name]=importlib.metadata.version(name)
 (out/'python_environment.json').write_text(json.dumps(environment,indent=2))
 state['status']='complete';save();print('Complete workflow passed')

if __name__=='__main__':run()
