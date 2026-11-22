from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile,ZIP_DEFLATED
import shutil,json
R=Path(__file__).resolve().parent;W=R.parent;P=W.parents[1];K=R/'package/MU1447-Wireless-Runtime-v0.1';D=K/'payload';D.mkdir(parents=True,exist_ok=True)
h=lambda p:sha256(p.read_bytes()).hexdigest()
items=[('CP-fixed.jar','CP.jar',W/'payload/CarPlayWireless-CP-MU1447.jar'),('Touch-runtime.jar','Touch.jar',W/'payload/CarPlayWireless-Touch-MU1447.jar'),('Bootstrap-runtime.jar','Bootstrap.jar',W/'payload/WirelessMapsBootstrap-MU1447.jar'),('wcp_autostart.sh','wcp_autostart.sh',W/'payload/ota/wcp_autostart.sh'),('wcp_ctl.sh','wcp_ctl.sh',W/'payload/ota/wcp_ctl.sh'),('mu1447-runtime-guard','mu1447-runtime-guard',None)]
for src,dst,_ in items:shutil.copyfile(R/'build'/src,D/dst)
for name in ['BEFORE.tsv','AFTER.tsv']:
 (K/name).write_text(''.join(f'{i:03d} '+(h(old) if old else 'MISSING' if name=='BEFORE.tsv' else h(D/dst))+'\n' for i,(src,dst,old) in enumerate(items,1)) if name=='BEFORE.tsv' else ''.join(f'{i:03d} {h(D/dst)}\n' for i,(_,dst,_) in enumerate(items,1)))
shutil.copyfile(W/'release/MU1447-Native-Wireless-v1.0-rc1.3/file-check',K/'file-check')
shutil.copyfile(R/'build/link-check.jar',D/'link-check.jar')
(K/'JXE.sha256').write_text(h(P/'work/p4709-mu1447-port/stage2/ifs/lsd.jxe')+'\n')
(K/'MAPS.sha256').write_text(h(W/'payload/libomonob-wireless-maps.so')+'\n')
(K/'RECEIVERS.tsv').write_text(h(W/'payload/wcp_receiver')+' '+h(W/'payload/wireless-receiver-exec')+'\n'+''.join(h(W/f'layout-update/MU1447-Wireless-Layout-v0.1/payload/receiver-{v}')+' '+h(W/f'layout-update/MU1447-Wireless-Layout-v0.1/payload/guard-{v}')+'\n' for v in [56,76]))
for n in ['source','tests']:
 out=K/n
 if out.exists():shutil.rmtree(out)
 shutil.copytree(R/n,out,ignore=shutil.ignore_patterns('*.class','__pycache__'))
for f in ['build.py','test_java.py','test_native.py','test_installer.py','package.py']:
 if (R/f).exists():shutil.copyfile(R/f,K/'source'/f)
logs={p.name:p.read_text() for p in [R/'build/runtime-tests.log',R/'build/native-tests.log',R/'build/link-check-host.log',R/'build/installer-tests.log',R/'build/abi-tests.log'] if p.exists()}
(K/'TEST-RESULTS.json').write_text(json.dumps({'date':'2026-11-21','local_results':logs,'hardware_acceptance':'NOT_PERFORMED','preflight_on_unit':'Required before any persistent write','network_scope':'unchanged','native_guard_sha256':h(D/'mu1447-runtime-guard'),'baseline':'MU1447 wireless rc1.3; recognized base/56/76 receiver variants; existing Wi-Fi and layout add-ons preserved'},indent=2)+'\n')
(K/'BUILD.json').write_text(json.dumps({'name':K.name,'native_target':'QNX 6.5 ARMv7 softfp','changed_existing_files':5,'new_file':'/mnt/ota/mu1447-runtime-guard','donor_CP_sha256':h(Path('/path/to/inputs/manual-ssh-mu1447/payload/wireless/common/jars/CarPlayWireless-CP-55915411.jar')),'source_working_directory':str(R),'build_notes':'build.py assembles Java delta against the retained MU1447/OEM inputs; QNX compiler command in source/BUILDING.txt'},indent=2)+'\n')
(K/'SHA256SUMS.txt').write_text(''.join(h(p)+'  '+str(p.relative_to(K))+'\n' for p in sorted(K.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt'))
zip_path=R/'package'/f'{K.name}.zip'
with ZipFile(zip_path,'w',ZIP_DEFLATED) as z:
 for p in sorted(K.rglob('*')):
  if p.is_file():z.write(p,str(p.relative_to(K.parent)))
print('PACKAGE='+str(zip_path)+' bytes='+str(zip_path.stat().st_size)+' sha256='+h(zip_path))
