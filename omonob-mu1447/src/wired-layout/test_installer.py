from pathlib import Path
import tempfile,shutil,subprocess,os
kit=Path(__file__).resolve().parent.parent
for incoming in ['core-display-v011.so','core-eta-v01.so']:
 with tempfile.TemporaryDirectory() as td:
  t=Path(td);u=t/'unit';k=t/'kit';shutil.copytree(kit,k)
  root=u/'mnt/app/carplaymaps';root.mkdir(parents=True)
  (u/'mnt/app/eso/bin/apps').mkdir(parents=True)
  for d in ['ramdisk','dev/shmem']:(u/d).mkdir(parents=True)
  s=(kit/'install.sh').read_text()
  for prefix in ['/mnt/','/ramdisk/','/dev/']:s=s.replace(prefix,str(u)+prefix)
  (k/'install.sh').write_text(s)
  (k/'payload/file-check').write_text('#!/bin/sh\n[ "$1" = --same ] || exit 2\nexec cmp -s "$2" "$3"\n')
  original=(kit/'payload'/incoming).read_bytes();core=root/'core.so';core.write_bytes(original)
  for path,name in [(root/'dio_manager.wrapper.sh','wrapper-display.sh'),(u/'mnt/app/eso/bin/apps/dio_manager','wrapper-display.sh'),(root/'libmu1447-wired-display.so','libmu1447-wired-display.so')]:path.write_bytes((kit/'payload'/name).read_bytes())
  mock=t/'bin';mock.mkdir();(mock/'mount').write_text('#!/bin/sh\nexit 0\n');(mock/'mount').chmod(0o755)
  env=dict(os.environ,PATH=str(mock)+':'+os.environ['PATH'])
  def files():return {str(p.relative_to(u)):p.read_bytes() for p in (u/'mnt').rglob('*') if p.is_file()}
  before=files()
  def run(action,ok=True):
   r=subprocess.run(['/bin/sh',str(k/'install.sh'),action],env=env,capture_output=True,text=True)
   assert (r.returncode==0)==ok,(r.stdout,r.stderr)
  run('--check');assert files()==before
  for a in ['--apply','--apply','--restore']:run(a)
  assert core.read_bytes()==original
  after={key:val for key,val in files().items() if '/.mu1447-wired-layout-v02/' not in key};assert after==before
  core.write_bytes(b'unknown');run('--apply',False);assert core.read_bytes()==b'unknown'
print('INSTALL_RESTORE=PASS both_previous_versions read_only_check repeated_apply exact_undo other_files_unchanged unknown_refused')
