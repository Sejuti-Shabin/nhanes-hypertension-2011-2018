"""Download authentic CDC four-cycle data and source codebooks; never synthetic replacements."""
from pathlib import Path
import urllib.request,hashlib,json,time,concurrent.futures
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'
CYCLES={'G':2011,'H':2013,'I':2015,'J':2017}
COMPONENTS=['DEMO','BPX','BPQ','HIQ','HUQ','BMX','SMQ']

def obtain(item):
 suffix,year,component,ext=item
 name=f'{component}_{suffix}.{ext}';p=RAW/name
 url=f'https://wwwn.cdc.gov/nchs/data/nhanes/public/{year}/datafiles/{name}'
 if not p.exists():
  for attempt in range(3):
   try:
    req=urllib.request.Request(url,headers={'User-Agent':'NHANES-reproducible-research/1.0'})
    payload=urllib.request.urlopen(req,timeout=60).read()
    if ext=='xpt' and not payload.startswith(b'HEADER RECORD'):raise ValueError('Not SAS XPORT')
    if ext=='htm' and b'Data Documentation' not in payload:raise ValueError('Not NHANES codebook')
    p.write_bytes(payload);break
   except Exception:
    if attempt==2:raise
    time.sleep(attempt+1)
 return name,{'url':url,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'cycle':f'{year}–{year+1}','suffix':suffix,'origin':'official CDC; J core inherited and checksum-preserved'}

def run():
 RAW.mkdir(parents=True,exist_ok=True)
 jobs=[(s,y,c,e) for s,y in CYCLES.items() for c in COMPONENTS for e in ['xpt','htm']]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  result=dict(pool.map(obtain,jobs))
 manifest=ROOT/'data/source_manifest.json'
 if manifest.exists():
  old=json.loads(manifest.read_text())
  if any(k not in result or v['sha256']!=result[k]['sha256'] for k,v in old.items()):raise ValueError('Source snapshot changed; protocol review required')
  if set(result)!=set(old):manifest.write_text(json.dumps(result,indent=2,sort_keys=True))
 else:manifest.write_text(json.dumps(result,indent=2,sort_keys=True))
 print('Authentic source files ready:',len(result))
 return result

if __name__=='__main__':run()
