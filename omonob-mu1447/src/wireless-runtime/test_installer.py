from pathlib import Path
from hashlib import sha256
import tempfile,subprocess,shutil,ast,os,json
R=Path(__file__).resolve().parent;W=R.parent;P=W.parents[1];K=R/'package/MU1447-Wireless-Runtime-v0.1';h=lambda p:sha256(Path(p).read_bytes()).hexdigest()
module=ast.parse((W/'source/test_transaction.py').read_text());helper=next(ast.literal_eval(n.value) for n in ast.walk(module) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='helper' for x in n.targets) and isinstance(n.value,ast.Constant))
checks=[]
for variant in ['base','56','76']:
 with tempfile.TemporaryDirectory(prefix='mu1447-runtime-transaction-') as temp:
  t=Path(temp);u=t/'unit';k=t/'kit';shutil.copytree(K,k)
  for name in ['mnt/app','mnt/ota','ramdisk','ifs/jre/bin','dev/shmem']:(u/name).mkdir(parents=True,exist_ok=True)
  def put(path,src=None,text=None):
   p=u/path.lstrip('/');p.parent.mkdir(parents=True,exist_ok=True)
   if src:shutil.copyfile(src,p)
   else:p.write_text(text or '')
   p.chmod(0o755 if p.suffix=='.sh' else 0o644);return p
  targets=['/mnt/app/eso/hmi/lsd/jars/CarPlayWireless-CP-55915411.jar','/mnt/app/eso/hmi/lsd/jars/CarPlayWireless-Touch-55915411.jar','/mnt/app/eso/hmi/lsd/jars/WirelessMapsBootstrap.jar','/mnt/ota/wcp_autostart.sh','/mnt/ota/wcp_ctl.sh','/mnt/ota/mu1447-runtime-guard']
  src=[W/'payload/CarPlayWireless-CP-MU1447.jar',W/'payload/CarPlayWireless-Touch-MU1447.jar',W/'payload/WirelessMapsBootstrap-MU1447.jar',W/'payload/ota/wcp_autostart.sh',W/'payload/ota/wcp_ctl.sh']
  for name,p in zip(targets,src):put(name,p)
  put('/mnt/app/carplaymaps/PROFILE',text='MU1447/790\n');put('/mnt/app/carplaymaps/libomonob-wireless-maps.so',W/'payload/libomonob-wireless-maps.so')
  put('/mnt/ota/wcp_receiver',W/'payload/wcp_receiver' if variant=='base' else W/f'layout-update/MU1447-Wireless-Layout-v0.1/payload/receiver-{variant}')
  put('/mnt/app/carplaymaps/wireless-receiver-exec',W/'payload/wireless-receiver-exec' if variant=='base' else W/f'layout-update/MU1447-Wireless-Layout-v0.1/payload/guard-{variant}')
  # Exact firmware baseline as immutable hardlink; installation cannot write it.
  os.link(P/'work/p4709-mu1447-port/stage2/ifs/lsd.jxe',u/'ifs/lsd.jxe')
  for name in ['wcp_pf.sh','wcp_pfwatch.sh','wcp_chansync.sh']:put('/mnt/ota/'+name,text='fixture existing '+name+'\n')
  put('/mnt/persist/altscreen.conf',text='safe-area sentinel\n');put('/mnt/persist/wcp/paired-phone',text='non-secret pairing sentinel\n');put('/mnt/app/carplaymaps/core.so',text='wired/media sentinel\n')
  j9=put('/ifs/jre/bin/j9',text='#!/bin/sh\necho JAVA_BOUNDARY_STUB=PASS\n');j9.chmod(0o755)
  script=(k/'install.sh').read_text()
  for p in ['/mnt/','/ifs/','/ramdisk','/dev/shmem/']:script=script.replace(p,str(u)+p)
  expected='"$S/runtime-guard" --self-test && "$S/runtime-guard" --inspect'
  assert expected in script;script=script.replace(expected,'[ "${MOCK_OBSERVE_FAIL:-0}" = 0 ]')
  (k/'install.sh').write_text(script);(k/'file-check').write_text(helper)
  (k/'SHA256SUMS.txt').write_text(''.join(h(p)+'  '+str(p.relative_to(k))+'\n' for p in sorted(k.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt'))
  b=t/'bin';b.mkdir()
  for name,body in [('mount','exit 0'),('cp','case "${MOCK_FAIL_LAST:-0}:$2" in 1:*mu1447-runtime-guard.mu1447-runtime-new)exit 1;;esac\nexec /bin/cp "$@"')]:
   p=b/name;p.write_text('#!/bin/sh\n'+body+'\n');p.chmod(0o755)
  env=dict(os.environ,PATH=str(b)+':'+os.environ['PATH'])
  def run(action,ok=True,**extra):
   x=subprocess.run(['/bin/ksh',str(k/'install.sh'),action],capture_output=True,text=True,env=dict(env,**extra),timeout=30)
   assert (x.returncode==0)==ok,(variant,action,x.returncode,x.stdout,x.stderr)
   return x.stdout
  def snapshot():return {str(p.relative_to(u)):h(p) for p in (u/'mnt').rglob('*') if p.is_file()}
  original=snapshot();assert 'CHECK=PASS' in run('--check');assert snapshot()==original
  assert 'requires_running_compatible_receiver' in run('--check',False,MOCK_OBSERVE_FAIL='1');assert snapshot()==original
  assert 'insufficient_space' in run('--check',False,MOCK_LOW_RAM='1');assert snapshot()==original
  assert 'INSTALLED persistent=1' in run('--apply');installed=snapshot();assert 'ALREADY_INSTALLED' in run('--apply');assert snapshot()==installed
  assert 'RESTORED' in run('--restore');backup='mnt/app/.mu1447-wireless-runtime-v01/'
  visible=lambda:{n:v for n,v in snapshot().items() if not n.startswith(backup)}
  assert visible()==original;assert not (u/targets[5].lstrip('/')).exists()
  # Retained, sealed backup supports a subsequent apply after restoration.
  assert 'INSTALLED persistent=1' in run('--apply');changed=u/targets[1].lstrip('/');saved=changed.read_bytes();changed.write_bytes(b'unknown later edit');assert 'later_edit_002' in run('--restore',False);changed.write_bytes(saved)
  assert 'RESTORED' in run('--restore');assert visible()==original
  assert 'AUTO_ROLLBACK=PASS' in run('--apply',False,MOCK_FAIL_LAST='1');assert visible()==original
  # Interrupted mixed state: five writes could have succeeded; restore recognizes each.
  shutil.copyfile(k/'payload/CP.jar',u/targets[0].lstrip('/'));assert 'RESTORED' in run('--restore');assert visible()==original
  saved=(u/targets[0].lstrip('/')).read_bytes();(u/targets[0].lstrip('/')).write_bytes(b'unknown runtime');assert 'not_recognized' in run('--check',False);(u/targets[0].lstrip('/')).write_bytes(saved)
  checks.append(variant+': readonly check, missing observation refusal, low RAM refusal, apply/reapply, restore/reapply, later-edit refusal, last-write rollback, interrupted mixed-state restore, unknown input refusal; receiver/layout/network/wired/media/pairing unchanged')
result='INSTALLER=PASS variants=3 readonly_checks sealed_restore late_failure_rollback interrupted_restore existing_addons_preserved\n'
(R/'build/installer-tests.log').write_text(result+'\n'.join(checks)+'\n');print(result,end='')
