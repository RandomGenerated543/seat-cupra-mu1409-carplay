from pathlib import Path
from hashlib import sha256
import tempfile,shutil,subprocess,os,ast
R=Path(__file__).resolve().parent;W=R.parent;P=W.parents[1];K=R/'package/MU1447-Wireless-Startup-v0.1';old=W/'runtime-fix-v01/package/MU1447-Wireless-Runtime-v0.1';h=lambda p:sha256(Path(p).read_bytes()).hexdigest()
module=ast.parse((W/'source/test_transaction.py').read_text());helper=next(ast.literal_eval(n.value) for n in ast.walk(module) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='helper' for x in n.targets) and isinstance(n.value,ast.Constant))
with tempfile.TemporaryDirectory(prefix='mu1447-startup-install-') as temp:
 t=Path(temp);u=t/'unit';k=t/'kit';shutil.copytree(K,k)
 for name in ['mnt/app','mnt/ota','ifs/jre/bin','ramdisk']:(u/name).mkdir(parents=True,exist_ok=True)
 def put(path,src=None,text=None):
  p=u/path.lstrip('/');p.parent.mkdir(parents=True,exist_ok=True)
  if src:shutil.copyfile(src,p)
  else:p.write_text(text or '')
  return p
 target=put('/mnt/app/eso/hmi/lsd/jars/CarPlayWireless-CP-55915411.jar',old/'payload/CP.jar')
 names=['Touch.jar','Bootstrap.jar','wcp_autostart.sh','wcp_ctl.sh','mu1447-runtime-guard']
 for row,name in zip((K/'DEPENDENCIES.tsv').read_text().splitlines(),names):put(row.split()[1],old/'payload'/name)
 put('/mnt/app/carplaymaps/PROFILE',text='MU1447/790\n');put('/mnt/persist/settings',text='settings sentinel\n');put('/mnt/ota/wcp_pf.sh',text='network sentinel\n')
 os.link(P/'work/p4709-mu1447-port/stage2/ifs/lsd.jxe',u/'ifs/lsd.jxe')
 j9=put('/ifs/jre/bin/j9',text='#!/bin/sh\necho J9_BOUNDARY_STUB=PASS\n');j9.chmod(0o755)
 for name in ['install.sh','DEPENDENCIES.tsv']:
  text=(k/name).read_text()
  for p in ['/mnt/','/ifs/','/ramdisk']:text=text.replace(p,str(u)+p)
  (k/name).write_text(text)
 (k/'file-check').write_text(helper.replace('print(1000000 if', 'print(100000 if'))
 (k/'SHA256SUMS.txt').write_text(''.join(h(p)+'  '+str(p.relative_to(k))+'\n' for p in sorted(k.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt'))
 b=t/'bin';b.mkdir()
 for name,body in [('mount','exit 0'),('cp','case "${MOCK_FAIL_REPLACE:-0}:$2" in 1:*.mu1447-startup-new)exit 1;;esac\nexec /bin/cp "$@"')]:
  f=b/name;f.write_text('#!/bin/sh\n'+body+'\n');f.chmod(0o755)
 env=dict(os.environ,PATH=str(b)+':'+os.environ['PATH'])
 def run(action,ok=True,**extra):
  p=subprocess.run(['/bin/ksh',str(k/'install.sh'),action],capture_output=True,text=True,timeout=30,env=dict(env,**extra));assert (p.returncode==0)==ok,(action,p.stdout,p.stderr);return p.stdout
 def snapshot():return {str(p.relative_to(u)):h(p) for p in (u/'mnt').rglob('*') if p.is_file() and '.mu1447-wireless-startup-v01/' not in str(p)}
 before=snapshot();assert 'CHECK=PASS' in run('--check');assert snapshot()==before
 assert 'insufficient_space' in run('--check',False,MOCK_LOW_RAM='1');assert snapshot()==before
 saved=target.read_bytes();target.write_bytes(b'unknown CP');assert 'not_recognized' in run('--check',False);target.write_bytes(saved)
 dep=u/'mnt/ota/wcp_ctl.sh';saved=dep.read_bytes();dep.write_bytes(b'unknown controller');assert 'dependency_changed' in run('--check',False);dep.write_bytes(saved)
 assert 'INSTALLED persistent=1' in run('--apply');after=snapshot();assert set(n for n in before if before[n]!=after[n])=={str(target.relative_to(u))}
 assert 'ALREADY_INSTALLED' in run('--apply');assert snapshot()==after
 saved=target.read_bytes();target.write_bytes(b'later edit');assert 'later_edit' in run('--restore',False);target.write_bytes(saved)
 assert 'RESTORED' in run('--restore');assert snapshot()==before
 assert 'AUTO_ROLLBACK=PASS' in run('--apply',False,MOCK_FAIL_REPLACE='1');assert snapshot()==before
 assert 'INSTALLED persistent=1' in run('--apply');assert 'RESTORED' in run('--restore');assert snapshot()==before
result='STARTUP_INSTALLER=PASS readonly_check low_space_refusal exact_runtime_dependencies one_file_only idempotence sealed_restore later_edit_refusal replacement_failure_rollback\n'
(R/'build/startup-installer-tests.log').write_text(result);print(result,end='')
