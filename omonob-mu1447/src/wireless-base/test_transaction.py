"""Host simulation of the real installer; QNX programs and mounts are stubs.
No test mode is added to the shipped installer and no live unit is contacted.
"""
from pathlib import Path
from hashlib import sha256
import os,shutil,subprocess,tempfile,json
W=Path(__file__).resolve().parent.parent
PJT=W.parents[1]
KIT=W/'release/MU1447-Native-Wireless-v1.0-rc1.3'
OUT=W/'build/transaction-test.json'
def digest(p):return sha256(p.read_bytes()).hexdigest()
def seal(k):
 (k/'SHA256SUMS.txt').write_text(''.join(f'{digest(p)}  {p.relative_to(k)}\n' for p in sorted(k.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt'))
def snapshot(u):return {str(p.relative_to(u)):digest(p) for r in ('mnt','ifs') for p in (u/r).rglob('*') if p.is_file()}
helper='''#!/usr/bin/env python3
import sys,hashlib,pathlib
h=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
a=sys.argv
if a[1]=='--self-test':pass
elif a[1]=='--hash':print(h(a[2]))
elif a[1]=='--free-bytes':print(1000000 if __import__('os').environ.get('MOCK_LOW_RAM')=='1' and a[2].endswith('/ramdisk') else 20421632 if a[2].endswith('/ramdisk') else 3123281920 if a[2].endswith('/mnt/ota') else 211760128)
elif a[1]=='--manifest':
 for l in pathlib.Path(a[3]).read_text().splitlines(keepends=True):
  if len(l)<68 or l[64:66]!='  ' or not l.endswith('\\n'):sys.exit(2)
  x,p=l[:64],l[66:-1]
  if h(pathlib.Path(a[2])/p)!=x:sys.exit(1)
else:sys.exit(2)
'''
checks=[]
with tempfile.TemporaryDirectory(prefix='mu1447-transaction-') as temp:
 T=Path(temp).resolve();u=T/'unit';k=T/'kit';shutil.copytree(KIT,k)
 for name in ('mnt/app','mnt/ota','mnt/persist','mnt/system','ifs/jre/bin','ramdisk','dev/shmem'):(u/name).mkdir(parents=True,exist_ok=True)
 def put(target,source=None,text=None):
  p=u/target.lstrip('/');p.parent.mkdir(parents=True,exist_ok=True)
  if source:shutil.copyfile(source,p)
  else:p.write_text(text or '')
  return p
 fw=PJT/'work/p4709-mu1447-port'
 for l in (KIT/'native-baselines.tsv').read_text().splitlines():
  _,path=l.split();src={'/ifs/lsd.jxe':fw/'stage2/ifs/lsd.jxe','/mnt/app/eso/bin/apps/btstack':fw/'app/eso/bin/apps/btstack','/mnt/app/eso/bin/apps/connectionmanager':W/'research/firmware/connectionmanager','/mnt/app/eso/lib/libairplay.so':fw/'app/eso/lib/libairplay.so'}[path];put(path,src)
 put('/mnt/app/carplaymaps/core.so',PJT/'work/mu1447-wired-display/MU1447-Center-Down-v0.1/payload/core-center.so')
 for dst,src in [('/mnt/app/carplaymaps/dio_manager.wrapper.sh','wired-launcher-reference.sh'),('/mnt/app/eso/bin/apps/dio_manager','wired-launcher-reference.sh'),('/mnt/app/carplaymaps/libmu1447-wired-display.so','wired-zoom-reference.so'),('/mnt/app/eso/hmi/lsd/jars/VCMenu.jar','VCMenu-reference.jar'),('/mnt/system/etc/eso/production/connectivity.json','connectivity-reference.json')]:put(dst,k/'payload'/src)
 put('/mnt/app/eso/hmi/lsd/lsd.sh',W/'research/firmware/lsd.sh')
 put('/mnt/app/eso/hmi/lsd/config/bundles.properties',W/'research/firmware/bundles.properties')
 put('/mnt/persist/btwcp_off',text='prior disable state\n')
 put('/mnt/persist/altscreen.conf',text='prior config\n')
 put('/mnt/persist/wcp/pairing-preserved',text='fixture non-secret pairing sentinel\n')
 # Do not execute any ARM program on the host.
 j9=put('/ifs/jre/bin/j9',text='#!/bin/sh\necho HOST_JAVA_STUB=PASS\n');j9.chmod(0o755)
 b=T/'bin';b.mkdir();mount=b/'mount';mount.write_text('#!/bin/sh\nexit 0\n');mount.chmod(0o755)
 for fn in ('install.sh','targets.tsv','native-baselines.tsv'):
  s=(k/fn).read_text()
  for old in ('/mnt/','/ifs/','/ramdisk/'):
   s=s.replace(old,str(u)+old)
  s=s.replace('/dev/ipod0',str(u)+'/dev/ipod0').replace('/dev/shmem/',str(u)+'/dev/shmem/')
  if fn=='install.sh':
   old=str(u)+'/mnt/app/carplaymaps/wireless-receiver-exec --transport-status'
   assert old in s;s=s.replace(old,'[ "${MOCK_GUARD_FAIL:-0}" = 0 ]')
  (k/fn).write_text(s)
 (k/'file-check').write_text(helper);(k/'file-check').chmod(0o755);seal(k)
 env=dict(os.environ,PATH=str(b)+':'+os.environ['PATH'])
 def run(action,ok=True,**extra):
  r=subprocess.run(['/bin/ksh',str(k/'install.sh'),action],env=dict(env,**extra),capture_output=True,text=True,timeout=40)
  if (r.returncode==0)!=ok:raise AssertionError(f'{action}: rc={r.returncode}\n{r.stdout}\n{r.stderr}')
  return r.stdout
 before=snapshot(u)
 assert 'insufficient_free_space_' in run('--check',ok=False,MOCK_LOW_RAM='1');assert snapshot(u)==before
 checks.append('insufficient RAM refuses without persistent writes')
 assert 'CHECK=PASS' in run('--check');assert snapshot(u)==before
 checks.append('check writes no persistent files')
 assert 'INSTALLED persistent=1' in run('--apply')
 after=snapshot(u)
 assert 'ALREADY_INSTALLED' in run('--apply');assert snapshot(u)==after
 checks.append('apply, exact receipt, repeat is idempotent')
 assert 'STATUS=INSTALLED' in run('--status')
 assert 'RESTORED wired_baseline_verified=1' in run('--restore')
 restored=snapshot(u);backup='mnt/app/.mu1447-native-wireless-v1-backup/'
 assert {p:h for p,h in restored.items() if not p.startswith(backup)}==before
 checks.append('restore every original tracked file, retain pairing and wired baseline')
 shutil.rmtree(u/'mnt/app/.mu1447-native-wireless-v1-backup')
 assert 'AUTO_ROLLBACK=PASS' in run('--apply',ok=False,MOCK_GUARD_FAIL='1')
 restored=snapshot(u);assert {p:h for p,h in restored.items() if not p.startswith(backup)}==before
 checks.append('late runtime-library guard failure automatically rolls back all changes')
 # Emulate the exact old native-helper failure: every backup row had one space.
 bk=u/'mnt/app/.mu1447-native-wireless-v1-backup'
 (bk/'complete').unlink()
 sealfile=bk/'SEAL.sha256';sealfile.write_text(sealfile.read_text().replace('  ',' '))
 first=(k/'targets.tsv').read_text().splitlines()[0].split();live=Path(first[1]);saved=live.read_bytes();live.write_bytes(b'later unknown change')
 assert 'recovery_live_file_changed_' in run('--recover-backup',ok=False)
 assert bk.exists() and not Path(str(bk)+'.preseal-rc12').exists()
 live.write_bytes(saved)
 checks.append('unfinished backup recovery refuses any changed live baseline')
 assert 'BACKUP_RECOVERY=PASS' in run('--recover-backup')
 assert not bk.exists() and Path(str(bk)+'.preseal-rc12').exists()
 checks.append('legacy single-space unfinished backup verified and retained, live baseline unchanged')
 # Start another install then force rollback, recreating a complete mixed-state backup.
 assert 'AUTO_ROLLBACK=PASS' in run('--apply',ok=False,MOCK_GUARD_FAIL='1')
 # Exact rollback also works following an interrupted partial write.
 bk=u/'mnt/app/.mu1447-native-wireless-v1-backup'
 row=(k/'targets.tsv').read_text().splitlines()[0].split();target=Path(row[1]);shutil.copyfile(k/'payload'/row[3],target)
 assert 'RESTORED wired_baseline_verified=1' in run('--restore')
 checks.append('mixed before/after partial transaction restores')
 # Later unknown edits are never silently overwritten.
 target.write_bytes(b'unexpected later edit')
 assert 'changed_since_install' in run('--restore',ok=False)
 checks.append('unrecognized later edits refuse restore')
 shutil.rmtree(bk);put('/mnt/app/eso/hmi/lsd/jars/VCMenu.jar',k/'payload/VCMenu-reference.jar')
 lib=u/'mnt/app/eso/lib/libairplay.so';lib.write_bytes(b'wrong native baseline')
 prior=snapshot(u);assert 'native_input_mismatch' in run('--check',ok=False);assert snapshot(u)==prior
 checks.append('wrong firmware native input fails without persistent writes')
OUT.write_text(json.dumps({'result':'PASS','scope':'host transaction simulation; ARM runtime and Java linkage mocked here','checks':checks},indent=2)+'\n')
print('TRANSACTION_TEST=PASS cases='+str(len(checks)))
