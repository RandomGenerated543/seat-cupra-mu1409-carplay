from pathlib import Path
from zipfile import ZipFile
from hashlib import sha256
import struct,json,subprocess,sys
k=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent.parent/'release/MU1447-Native-Wireless-v1.0-rc1'
rows=[line.split() for line in (k/'targets.tsv').read_text().splitlines()]
assert len(rows)==41 and len({r[1] for r in rows})==41
payload=k/'payload';lookup={Path(r[1]).name:payload/r[3] for r in rows if r[3] not in ('MISSING','GENERATE_LSD','GENERATE_BUNDLES','GENERATE_CONNECTIVITY')}
for forbidden in ('core.so','dio_manager','dio_manager.wrapper.sh','libmu1447-wired-display.so','btstack','connectionmanager','libairplay.so','lsd.jxe','pf.conf','pf.mlan0.conf'):
 assert forbidden not in lookup,forbidden
r=lookup['wcp_receiver'].read_bytes();guard=lookup['wireless-receiver-exec'].read_bytes()
assert struct.unpack_from('<I',r,0xc4a98)[0]==0xe3a0201e
for name,off in [('wcp_receiver',0x1310),('libomonob-wireless-maps.so',0x1384),('libv75-transport.so',0x13f4)]:assert guard[off:off+64]==sha256(lookup[name].read_bytes()).hexdigest().encode()
rectangles=[(202,1,606,329),(202,45,606,252),(202,45,606,272),(191,76,628,185),(202,1,606,329)]
for i,rect in enumerate(rectangles):
 assert struct.unpack_from('<4i',r,0xf0450+i*16)==rect
 x,y,w,h=rect;assert 0<=x and 0<=y and x+w<=1010 and y+h<=376
with ZipFile(payload/'VCMenu-reference.jar') as original,ZipFile(lookup['VCMenu.jar']) as extended:
 for n in original.namelist():assert original.read(n)==extended.read(n)
 assert len([n for n in extended.namelist() if n.startswith('org/omonob/phone/') and n.endswith('.class')])==15
for name in ['CarPlayWireless-CP-55915411.jar','CarPlayWireless-Touch-55915411.jar','WirelessMapsBootstrap.jar']:
 with ZipFile(lookup[name]) as z:
  for n in z.namelist():
   if n.endswith('.class'):assert struct.unpack_from('>H',z.read(n),6)[0]==46,(name,n)
for r in rows:
 if r[1].endswith('.sh') and r[3].startswith(tuple('0123456789')):
  p=payload/r[3];out=subprocess.run(['/bin/ksh','-n',str(p)],capture_output=True)
  assert out.returncode==0,out.stderr.decode()
assert subprocess.run(['/bin/ksh','-n',str(k/'install.sh')],capture_output=True).returncode==0
assert b'pfctl -f /etc/pf.mlan0.conf' not in lookup['wcp_autostart.sh'].read_bytes()
assert b'libmu1447-bt-normalize.so' in lookup['btstack_wrap.sh'].read_bytes()
print('RELEASE_STATIC=PASS targets41 Java46 original_menu_preserved guarded_native_pair safe_areas fps30 shell_syntax wired_files_retained')
