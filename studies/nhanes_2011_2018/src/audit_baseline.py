"""Run historical tests only in an isolated copy; keep baseline code/results immutable."""
import hashlib,json,shutil,subprocess,sys,tempfile,re
from data import ROOT,OUT

def verify_preservation():
 baseline=ROOT.parent/'nhanes_2017_2018'
 if not baseline.exists():return None
 manifest=json.loads((ROOT/'reference/original_sha256.json').read_text())
 for path,sha in manifest.items():
  file=baseline/path
  if not file.exists() or hashlib.sha256(file.read_bytes()).hexdigest()!=sha:raise AssertionError('Historical baseline changed: '+path)
 return len(manifest)

def run():
 count=verify_preservation();baseline=ROOT.parent/'nhanes_2017_2018'
 if count is None:
  (OUT/'baseline_audit.json').write_text(json.dumps({'baseline_present':False,'tests_returncode':None,'execution':'Historical working tree not included in portable checkout; aggregate baseline comparisons executed separately'},indent=2))
  print('Historical working tree absent; original-test rerun not claimed. Aggregate baseline comparison remains available.')
  return
 with tempfile.TemporaryDirectory(prefix='nhanes_baseline_audit_') as temp:
  copy=__import__('pathlib').Path(temp)/'baseline'
  shutil.copytree(baseline,copy,ignore=shutil.ignore_patterns('__pycache__','.build-libs'))
  result=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=copy,capture_output=True,text=True)
  (OUT/'logs').mkdir(exist_ok=True)
  (OUT/'logs/historical_suite.log').write_text(result.stdout+result.stderr)
  match=re.search(r'Ran (\d+) tests',result.stderr)
  (OUT/'baseline_audit.json').write_text(json.dumps({'files_unchanged':count,'tests_returncode':result.returncode,'test_count':int(match.group(1)) if match else None,'execution':'Historical tests ran in isolated copy; baseline not rerun in place'},indent=2))
  if result.returncode:print(result.stdout+result.stderr);raise SystemExit(result.returncode)
 verify_preservation();print('Historical tests passed in isolated copy;',count,'baseline files unchanged')

if __name__=='__main__':run()
