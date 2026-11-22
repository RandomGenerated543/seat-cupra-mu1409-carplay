from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile,ZIP_DEFLATED
import shutil,json
R=Path(__file__).resolve().parent;W=R.parent;K=R/'package/MU1447-Wireless-Startup-v0.1';old=W/'runtime-fix-v01/package/MU1447-Wireless-Runtime-v0.1';h=lambda p:sha256(p.read_bytes()).hexdigest()
for src,dst in [(R/'build/CP-fixed.jar',K/'payload/CP.jar'),(R/'build/link-check.jar',K/'payload/link-check.jar'),(old/'file-check',K/'file-check'),(old/'JXE.sha256',K/'JXE.sha256')]:shutil.copyfile(src,dst)
(K/'BEFORE.sha256').write_text(h(old/'payload/CP.jar')+'\n')
paths=['/mnt/app/eso/hmi/lsd/jars/CarPlayWireless-Touch-55915411.jar','/mnt/app/eso/hmi/lsd/jars/WirelessMapsBootstrap.jar','/mnt/ota/wcp_autostart.sh','/mnt/ota/wcp_ctl.sh','/mnt/ota/mu1447-runtime-guard'];files=['Touch.jar','Bootstrap.jar','wcp_autostart.sh','wcp_ctl.sh','mu1447-runtime-guard']
(K/'DEPENDENCIES.tsv').write_text(''.join(h(old/'payload'/name)+' '+path+'\n' for path,name in zip(paths,files)))
for name in ['source','tests']:
 if (K/name).exists():shutil.rmtree(K/name)
 shutil.copytree(R/name,K/name,ignore=shutil.ignore_patterns('*.class','__pycache__'))
for name in ['build.py','test_java.py','package_startup.py','test_startup_installer.py']:
 if (R/name).exists():shutil.copyfile(R/name,K/'source'/name)
logs={p.name:p.read_text() for p in [R/'build/runtime-tests.log',R/'build/abi-tests.log',R/'build/startup-tests.log',R/'build/startup-installer-tests.log'] if p.exists()}
(K/'TEST-RESULTS.json').write_text(json.dumps({'date':'2026-11-21','baseline':'Runtime v0.1 installed','hardware_acceptance':'PENDING','results':logs,'changed_unit_files':1,'network_scope':'unchanged'},indent=2)+'\n')
(K/'SHA256SUMS.txt').write_text(''.join(h(p)+'  '+str(p.relative_to(K))+'\n' for p in sorted(K.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt'))
p=R/'package'/f'{K.name}.zip'
with ZipFile(p,'w',ZIP_DEFLATED) as z:
 for f in sorted(K.rglob('*')):
  if f.is_file():z.write(f,str(f.relative_to(K.parent)))
print('PACKAGE='+str(p)+' bytes='+str(p.stat().st_size))
