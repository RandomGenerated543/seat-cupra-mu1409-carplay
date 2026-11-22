from pathlib import Path
from hashlib import sha256
import ast,shutil,tempfile,subprocess,os,json
W=Path(__file__).resolve().parents[2];PJT=W.parents[1];K=W/'layout-update/MU1447-Wireless-Layout-v0.1'
h=lambda p:sha256(Path(p).read_bytes()).hexdigest()
module=ast.parse((W/'source/test_transaction.py').read_text())
helper=next(ast.literal_eval(n.value) for n in ast.walk(module) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='helper' for x in n.targets) and isinstance(n.value,ast.Constant))
cores={56:PJT/'work/mu1447-wired-display/MU1447-Wired-Layout-v0.2/payload/core-layout.so',76:PJT/'work/mu1447-wired-display/MU1447-Center-Down-v0.1/payload/core-center.so'}
checks=[]
for variant,core in cores.items():
 with tempfile.TemporaryDirectory(prefix='mu1447-layout-') as tmp:
  t=Path(tmp).resolve();u=t/'unit';k=t/'kit';shutil.copytree(K,k)
  for d in ['mnt/app/carplaymaps','mnt/ota','ramdisk']:(u/d).mkdir(parents=True)
  def put(name,src=None,text=None):
   p=u/name.lstrip('/');p.parent.mkdir(parents=True,exist_ok=True)
   if src:shutil.copyfile(src,p)
   else:p.write_text(text or '')
  put('/mnt/app/carplaymaps/core.so',core)
  put('/mnt/app/carplaymaps/PROFILE',text='MU1447/790\n')
  put('/mnt/ota/wcp_receiver',W/'payload/wcp_receiver')
  put('/mnt/app/carplaymaps/wireless-receiver-exec',W/'payload/wireless-receiver-exec')
  put('/mnt/app/carplaymaps/libomonob-wireless-maps.so',W/'payload/libomonob-wireless-maps.so')
  put('/mnt/ota/wcp_pf.sh',W/'network-qos-v01/MU1447-Wireless-Network-v0.1/payload/wcp_pf.sh')
  source=(k/'install.sh').read_text()
  for p in ['/mnt/','/ramdisk/']:source=source.replace(p,str(u)+p)
  (k/'install.sh').write_text(source)
  (k/'file-check').write_text(helper)
  (k/'SHA256SUMS.txt').write_text(''.join(h(p)+'  '+str(p.relative_to(k))+'\n' for p in sorted(k.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt'))
  b=t/'bin';b.mkdir()
  for n,s in [('mount','exit 0'),('cp','case "${MOCK_FAIL_SECOND:-0}:$2" in 1:*wireless-receiver-exec.mu1447-layout-new)exit 1;;esac\nexec /bin/cp "$@"')]:
   p=b/n;p.write_text('#!/bin/sh\n'+s+'\n');p.chmod(0o755)
  env=dict(os.environ,PATH=str(b)+':'+os.environ['PATH'])
  def snapshot():return {str(p.relative_to(u)):h(p) for p in (u/'mnt').rglob('*') if p.is_file()}
  def run(action,ok=True,**extra):
   r=subprocess.run(['/bin/ksh',str(k/'install.sh'),action],env=dict(env,**extra),capture_output=True,text=True,timeout=30)
   assert (r.returncode==0)==ok,(action,r.stdout,r.stderr)
   return r.stdout
  before=snapshot()
  assert f'191,{variant}' in run('--check') and before==snapshot()
  assert 'LAYOUT=INSTALLED' in run('--apply')
  assert (u/'mnt/ota/wcp_receiver').read_bytes()==(K/f'payload/receiver-{variant}').read_bytes()
  assert 'ALREADY_INSTALLED' in run('--apply')
  assert 'LAYOUT=RESTORED' in run('--restore')
  bk=u/'mnt/app/.mu1447-wireless-layout-v01'
  assert {p:v for p,v in snapshot().items() if not p.startswith('mnt/app/.mu1447-wireless-layout-v01/')}==before
  shutil.rmtree(bk)
  assert 'AUTO_ROLLBACK=PASS' in run('--apply',False,MOCK_FAIL_SECOND='1')
  assert {p:v for p,v in snapshot().items() if not p.startswith('mnt/app/.mu1447-wireless-layout-v01/')}==before
  checks.append(f'CenterY{variant}: check readonly, correct variant installed, idempotence, sealed restore, second-write failure rollback, QoS retained')
print('LAYOUT_INSTALLER=PASS variants=2 rollback=PASS network_and_wired_unchanged=1')
(K/'source/TEST-RESULTS.json').write_text(json.dumps({'result':'PASS','scope':'host transaction; native hash checker/mount calls stubbed','cases':checks,'arm_helper_cases':32,'car_acceptance':'UNTESTED'},indent=2)+'\n')
