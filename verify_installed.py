import hashlib,json,pathlib,subprocess,sys,tempfile
ROOT=pathlib.Path(__file__).resolve().parent
REPO=ROOT.name
PY=pathlib.Path(sys.argv[1]).absolute()
CMD=PY.parent/REPO

def check(args,expected,cwd):
 r=subprocess.run([str(CMD),*map(str,args)],cwd=cwd,text=True,capture_output=True,timeout=20)
 if r.returncode!=expected:raise AssertionError((args,expected,r.returncode,r.stdout,r.stderr))
 if expected==2 and (not r.stderr or r.stdout):raise AssertionError('failure must have stderr and no partial report')
 return json.loads(r.stdout) if r.stdout else None

with tempfile.TemporaryDirectory(prefix='installed-example-') as tmp:
 t=pathlib.Path(tmp)
 if REPO=='cut-stock-proof':
  source=t/'input.json';source.write_bytes((ROOT/'example.json').read_bytes());raw=source.read_bytes()
  r=check([source],0,t);assert r['bar_count']==2 and r['first_fit_bar_count']==3
  check([source,'--budget','1'],2,t)
  fail=t/'oversized.json';fail.write_text('{"stock_length":10,"kerf":0,"pieces":[{"id":"x","length":11}]}');assert check([fail],1,t)['status']=='infeasible'
 elif REPO=='rup-proof-trace':
  source=t/'input.cnf';source.write_bytes((ROOT/'example.cnf').read_bytes());raw=source.read_bytes()
  proof=t/'proof.drup';proof.write_bytes((ROOT/'example.drup').read_bytes());assert check([source,proof],0,t)['status']=='verified'
  proof.write_text('1 0');assert check([source,proof],1,t)['status']=='incomplete'
  proof.write_text('999 0');check([source,proof],2,t)
 else:
  ext={'fits-hdu-map':'fits','elf-page-permissions':'elf','tiff-strip-map':'tiff'}[REPO]
  source=t/('invented.'+ext);check(['--make-example',source],0,t);raw=source.read_bytes()
  check(['--make-example',source],2,t)
  r=check([source],1 if REPO=='elf-page-permissions' else 0,t)
  if REPO=='fits-hdu-map':
   assert r['hdus'][1]['data_range']==[5760,5764]
   f=t/'padding.fits';b=bytearray(raw);b[-1]=1;f.write_bytes(b);assert check([f],1,t)['findings']
  elif REPO=='elf-page-permissions':
   assert r['page_intervals'][0]['flags_union']==7
  else:
   assert r['pages'][0]['strips'][0]['range']==[122,126]
 assert source.read_bytes()==raw
 bad=t/'malformed';bad.write_bytes(b'bad input')
 check([bad,t/'proof.drup'] if REPO=='rup-proof-trace' else [bad],2,t)
 print(json.dumps({'installed_console':True,'outside_checkout':True,'expected_results':True,'failure_case':True,'source_sha256':hashlib.sha256(raw).hexdigest(),'source_unchanged':True}))
