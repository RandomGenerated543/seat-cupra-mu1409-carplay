from pathlib import Path
from hashlib import sha256
import tempfile,subprocess,os,shutil,json
K=Path(__file__).resolve().parent.parent
PROJECT=K.parents[3]
FW=PROJECT/'work/p4709-mu1447-port/system-extracted/filesystems/efs-system.img/etc'
BASE=PROJECT/'work/mu1447-wireless-integration/payload/ota'
h=lambda p:sha256(Path(p).read_bytes()).hexdigest()
checks=[]
with tempfile.TemporaryDirectory(prefix='mu1447-qos-') as tmp:
 t=Path(tmp).resolve();ram=t/'ram';ram.mkdir();pf=t/'pfctl';calls=t/'calls'
 pf.write_text('''#!/bin/sh
printf '%s\\n' "$*" >> "$MOCK_CALLS"
if [ "$1 $2" = '-s nat' ];then
 case "$MOCK_PROFILE" in mlan0) echo 'nat pass on mlan0 all tagged WLAN -> 1';;ecm0)echo 'nat pass on ecm0 all tagged WLAN -> 1';;ppp0)echo 'nat pass on ppp0 all tagged WLAN -> 1';echo 'nat pass on en0 all tagged WLAN -> 1';;*)echo 'nat pass on ppp0 all tagged WLAN -> 1';echo 'nat pass on ecm0 all tagged WLAN -> 1';;esac
fi
if [ "$1" = -n ] && [ "${MOCK_NATIVE_PF_FAIL:-0}" = 1 ];then exit 1;fi
exit 0
''');pf.chmod(0o755)
 env=dict(os.environ,MU1447_PFCTL=str(pf),MU1447_PF_CONFIG_DIR=str(FW),MU1447_PF_RAM_DIR=str(ram),MOCK_CALLS=str(calls))
 for profile,file in [('default','pf.conf'),('mlan0','pf.mlan0.conf'),('ecm0','pf.ecm0.conf'),('ppp0','pf.ppp0.conf')]:
  calls.write_text('')
  r=subprocess.run(['/bin/sh',str(K/'payload/wcp_pf.sh'),'check'],env=dict(env,MOCK_PROFILE=profile),capture_output=True,text=True);assert r.returncode==0,(r.stdout,r.stderr)
  generated=(ram/'wcp_pf.conf').read_text();original=(FW/file).read_text()
  additions=[l for l in generated.splitlines() if l not in original.splitlines()]
  assert len(additions)==6,additions
  assert ''.join(l+'\n' for l in generated.splitlines() if l in original.splitlines())==original
  assert '6030, 6031' in generated and 'queue(video_out, video_ack)' in generated
  assert 'label "MU1447_WCP_QOS_v1" queue(control_out, control_ack)' in generated
  assert not any(l.startswith('-f ') for l in calls.read_text().splitlines())
 checks.append('all four exact MU1447 OEM policies preserve every original line/NAT/SSH rule and add only queue classification')
 # Missing factory queues must fail before any load.
 bad=t/'badcfg';shutil.copytree(FW,bad)
 p=bad/'pf.conf';p.write_text(p.read_text().replace('queue control_out','queue removed_control'))
 r=subprocess.run(['/bin/sh',str(K/'payload/wcp_pf.sh'),'check'],env=dict(env,MOCK_PROFILE='default',MU1447_PF_CONFIG_DIR=str(bad)),capture_output=True,text=True);assert r.returncode!=0 and 'missing_queue' in r.stdout
 checks.append('missing factory queue refuses policy generation')
 # Isolated installer with native checker and mount stubs. Never touches live files.
 unit=t/'unit';kit=t/'kit';shutil.copytree(K,kit)
 for d in ['mnt/app/carplaymaps','mnt/ota','ramdisk']:(unit/d).mkdir(parents=True)
 (unit/'mnt/app/carplaymaps/PROFILE').write_text('MU1447/790\n')
 for name in ['wcp_pf.sh','wcp_pfwatch.sh']:shutil.copyfile(BASE/name,unit/'mnt/ota'/name)
 s=(kit/'install.sh').read_text()
 for name in ['/mnt/','/ramdisk/']:s=s.replace(name,str(unit)+name)
 (kit/'install.sh').write_text(s)
 helper='''#!/usr/bin/env python3
import pathlib,sys,hashlib
h=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
a=sys.argv
if a[1]=='--self-test':pass
elif a[1]=='--hash':print(h(a[2]))
elif a[1]=='--manifest':
 for l in pathlib.Path(a[3]).read_text().splitlines(keepends=True):
  if l[64:66]!='  ' or not l.endswith('\\n'):sys.exit(2)
  if h(pathlib.Path(a[2])/l[66:-1])!=l[:64]:sys.exit(1)
else:sys.exit(2)
'''
 (kit/'file-check').write_text(helper)
 (kit/'SHA256SUMS.txt').write_text(''.join(h(p)+'  '+str(p.relative_to(kit))+'\n' for p in sorted(kit.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt'))
 b=t/'bin';b.mkdir();m=b/'mount';m.write_text('#!/bin/sh\nexit 0\n');m.chmod(0o755)
 e=dict(env,PATH=str(b)+':'+os.environ['PATH'],MOCK_PROFILE='default')
 def run(action,ok=True,**extra):
  r=subprocess.run(['/bin/ksh',str(kit/'install.sh'),action],env=dict(e,**extra),capture_output=True,text=True,timeout=30)
  assert (r.returncode==0)==ok,(action,r.stdout,r.stderr)
  return r.stdout
 originals={n:(unit/'mnt/ota'/n).read_bytes() for n in ['wcp_pf.sh','wcp_pfwatch.sh']}
 assert 'NETWORK_CHECK=PASS' in run('--check') and not (unit/'mnt/app/.mu1447-wireless-network-v01').exists()
 assert 'native_firewall_preflight' in run('--apply',False,MOCK_NATIVE_PF_FAIL='1') and not (unit/'mnt/app/.mu1447-wireless-network-v01').exists()
 checks.append('installer check and rejected native PF syntax do not change persistent files')
 assert 'NETWORK=INSTALLED' in run('--apply')
 assert 'ALREADY_INSTALLED' in run('--apply')
 assert 'NETWORK=RESTORED' in run('--restore')
 assert all((unit/'mnt/ota'/n).read_bytes()==v for n,v in originals.items())
 checks.append('install, sealed backup, idempotence and byte-exact restore')
print('NETWORK_TESTS=PASS cases='+str(len(checks))+' native_pf_parser=ON_UNIT_GATE_REQUIRED')
(K/'source/TEST-RESULTS.json').write_text(json.dumps({'result':'PASS','scope':'host fixtures; native PF syntax is a mandatory on-unit gate, not host-validated','cases':checks},indent=2)+'\n')
