from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile,ZIP_DEFLATED
import shutil,json,struct
W=Path(__file__).resolve().parent.parent
PROJECT=W.parents[1]
MAN=Path('/path/to/inputs/manual-ssh-mu1447/payload')
PUB=Path('/path/to/inputs/VW_SKODA_SEAT_CarPlay_Maps_VC_FULL_MQB_Toolbox_V4.2A_v2.1.0-rc.7/Custom/carplay_maps_vc/payload')
FW=PROJECT/'work/p4709-mu1447-port'
K=W/'release/MU1447-Native-Wireless-v1.0-rc1';P=K/'payload';P.mkdir(parents=True,exist_ok=True)
rows=[]
def add(src,target,mode=644,name=None):
 idx=f'{len(rows)+1:03d}';name=name or idx+'-'+target.rsplit('/',1)[-1]
 if src is not None:shutil.copyfile(src,P/name);kind=name
 else:kind='MISSING'
 rows.append((idx,target,str(mode),kind))
# Keep every public rc.7 menu class byte-exact and only add missing phone helpers.
menu=PUB/'profiles/MU1447/790/VCMenu.jar'
with ZipFile(menu) as z:classes={n:z.read(n) for n in z.namelist()}
with ZipFile(MAN/'profiles/MU1447/790/VCMenu.jar') as z:
 for n in z.namelist():
  if n.startswith('org/omonob/phone/') and n.endswith('.class'):
   assert n not in classes;classes[n]=z.read(n)
assert sum(n.startswith('org/omonob/phone/') for n in classes)==15
merged=W/'build/VCMenu-MU1447-Wireless.jar'
with ZipFile(merged,'w',ZIP_DEFLATED) as z:
 for n,b in sorted(classes.items()):z.writestr(n,b)
with ZipFile(menu) as z:
 for n in z.namelist():assert classes[n]==z.read(n)
add(merged,'/mnt/app/eso/hmi/lsd/jars/VCMenu.jar')
for src,name in [(W/'payload/CarPlayWireless-CP-MU1447.jar','CarPlayWireless-CP-55915411.jar'),(MAN/'wireless/common/jars/CarPlayWireless-SI-55915411.jar','CarPlayWireless-SI-55915411.jar'),(W/'payload/CarPlayWireless-Touch-MU1447.jar','CarPlayWireless-Touch-55915411.jar'),(W/'payload/WirelessMapsBootstrap-MU1447.jar','WirelessMapsBootstrap.jar')]:add(src,'/mnt/app/eso/hmi/lsd/jars/'+name)
for src in sorted((W/'payload/ota').iterdir()):
 if src.is_file():add(src,'/mnt/ota/'+src.name,755 if src.suffix=='.sh' or src.name=='wcp_video' else 644)
add(W/'payload/libmu1447-bt-normalize.so','/mnt/ota/libmu1447-bt-normalize.so',755)
add(W/'payload/wcp_receiver','/mnt/ota/wcp_receiver',755)
for name in ['wireless-receiver-exec','libomonob-wireless-maps.so']:
 add(W/'payload'/name,'/mnt/app/carplaymaps/'+name,755 if name.endswith('-exec') else 644)
add(MAN/'wireless/profiles/AID10.5-17PM/wireless-entry','/mnt/app/carplaymaps/wireless-entry',755)
for src in sorted((MAN/'wireless/common/runtime').iterdir()):
 if src.is_file():add(src,'/mnt/app/carplaymaps/'+src.name,755 if src.suffix=='.sh' or src.name.startswith(('wireless-','wcp_')) else 644)
for name in ['btwcp_enable','btwcp_present_target','wcp_autostart','wcp_cp_stage']:
 add(MAN/'wireless/common/config'/name,'/mnt/persist/'+name)
profile=MAN/'wireless/profiles/AID10.5-17PM'
for name in ['altscreen.geom','v75-wireless-display.conf','cluster-profile']:
 add(profile/name,'/mnt/persist/'+('omonob-phone/cluster-profile' if name=='cluster-profile' else name))
# Startup descriptor defaults until the existing card-preference worker runs.
conf=W/'build/altscreen.conf';conf.write_text('width=1010\nheight=376\nfps=30\nmaxfps=30\nsafex=191\nsafey=76\nsafew=628\nsafeh=185\nnsafex=202\nnsafey=1\nnsafew=606\nnsafeh=329\nalturl=maps:/car/instrumentcluster?showETA=yes&maneuverLayout=topAligned&showSpeedLimit=no\n')
add(conf,'/mnt/persist/altscreen.conf')
for name in ['btwcp_off','wcp_cp_off','wcp_si_off','wcp_touch_off','wcp_pfwatch_off','wcp_autofront_off']:
 add(None,'/mnt/persist/'+name)
for kind,target in [('LSD','/mnt/app/eso/hmi/lsd/lsd.sh'),('BUNDLES','/mnt/app/eso/hmi/lsd/config/bundles.properties'),('CONNECTIVITY','/mnt/system/etc/eso/production/connectivity.json')]:
 rows.append((f'{len(rows)+1:03d}',target,'755' if kind=='LSD' else '644','GENERATE_'+kind))
(K/'targets.tsv').write_text('\n'.join('\t'.join(r) for r in rows)+'\n')
shutil.copyfile(MAN/'common/merge-wireless.sh',P/'merge-wireless.sh')
shutil.copyfile(W/'payload/link-check.jar',P/'link-check.jar')
check=PROJECT/'work/omonob-mu1409-wireless-port/upstream/standalone/SD_ROOT/install/file-check';shutil.copyfile(check,K/'file-check')
# Native inputs are identified, not replaced. JXE exact identity also pins HMI ABI.
paths=[('/ifs/lsd.jxe',FW/'stage2/ifs/lsd.jxe'),('/mnt/app/eso/bin/apps/btstack',FW/'app/eso/bin/apps/btstack'),('/mnt/app/eso/bin/apps/connectionmanager',W/'research/firmware/connectionmanager'),('/mnt/app/eso/lib/libairplay.so',FW/'app/eso/lib/libairplay.so')]
(K/'native-baselines.tsv').write_text('\n'.join(sha256(p.read_bytes()).hexdigest()+'\t'+target for target,p in paths)+'\n')
shutil.copyfile(menu,P/'VCMenu-reference.jar')
shutil.copyfile(PROJECT/'work/mu1447-wired-display/MU1447-Wired-Display-v0.1.1/payload/wrapper-display.sh',P/'wired-launcher-reference.sh')
shutil.copyfile(PROJECT/'work/mu1447-wired-display/MU1447-Wired-Display-v0.1.1/payload/libmu1447-wired-display.so',P/'wired-zoom-reference.so')
# Pin the connectivity input. Existing SSH settings in other files are not touched.
stock=FW/'system-extracted/filesystems/efs-system.img/etc/eso/production/connectivity.json'
text=stock.read_text();assert text.count('"exec":"/eso/bin/apps/btstack"')==1
(P/'connectivity-reference.json').write_bytes(stock.read_bytes())
(P/'connectivity-wireless.json').write_text(text.replace('"exec":"/eso/bin/apps/btstack"','"exec":"/mnt/ota/btstack_wrap.sh"'))
assert len({r[1] for r in rows})==len(rows)
assert all('..' not in r[1] for r in rows)
(K/'BUILD.json').write_text(json.dumps({'name':K.name,'hardware_validation':'NOT_PERFORMED','baseline':'MU1447 wired public rc.7 + owner display patches','touch_fix':'independent screen take/borrow ownership','receiver_sha256':sha256((W/'payload/wcp_receiver').read_bytes()).hexdigest(),'entry_sha256':sha256((W/'payload/wireless-receiver-exec').read_bytes()).hexdigest(),'normalizer_sha256':sha256((W/'payload/libmu1447-bt-normalize.so').read_bytes()).hexdigest(),'target_count':len(rows),'source_date':'2026-11-19'},indent=2)+'\n')
shutil.copyfile(W/'source/install.sh',K/'install.sh')
print('ASSEMBLY=PASS targets='+str(len(rows))+' rc7_menu_classes_preserved=1 phone_helpers_added=15')
