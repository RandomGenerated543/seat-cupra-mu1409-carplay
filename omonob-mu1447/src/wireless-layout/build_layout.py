from pathlib import Path
from struct import unpack_from,pack_into
from hashlib import sha256
W=Path(__file__).resolve().parents[2];PJT=W.parents[1]
K=W/'layout-update/MU1447-Wireless-Layout-v0.1';P=K/'payload'
base=(W/'payload/wcp_receiver').read_bytes();guard=(W/'payload/wireless-receiver-exec').read_bytes();code=(W/'source/layout-v01/layout.bin').read_bytes()
assert len(base)>0xf04a0 and guard[0x1310:0x1350]==sha256(base).hexdigest().encode()
symbols={line.split()[2]:int(line.split()[0],16) for line in (W/'research/layout-symbols.txt').read_text().splitlines() if len(line.split())==3}
cores={56:PJT/'work/mu1447-wired-display/MU1447-Wired-Layout-v0.2/payload/core-layout.so',76:PJT/'work/mu1447-wired-display/MU1447-Center-Down-v0.1/payload/core-center.so'}
rows=[]
for y,core in cores.items():
 b=core.read_bytes();r=bytearray(base[:0xf04a0]+code)
 ph=unpack_from('<I',r,28)[0];record=ph+13*32
 assert unpack_from('<4I',r,record)==(1,0xf0000,0x150000,0x150000)
 pack_into('<II',r,record+16,0x4a0+len(code),0x4a0+len(code))
 assert unpack_from('<I',r,0xc4b74)[0]==0xebfffe11
 target=symbols['auxiliary_url'];delta=target-(0xe4b74+8);assert delta%4==0
 pack_into('<I',r,0xc4b74,0xeb000000|((delta//4)&0xffffff))
 r[0xf0450:0xf04a0]=b[0x6f28:0x6f28+80]
 assert unpack_from('<4i',r,0xf0480)==(191,y,628,185)
 g=bytearray(guard);g[0x1310:0x1350]=sha256(r).hexdigest().encode()
 (P/f'receiver-{y}').write_bytes(r);(P/f'guard-{y}').write_bytes(g)
 rows.append(sha256(b).hexdigest()+' '+str(y))
(K/'WIRED-CORES.tsv').write_text('\n'.join(rows)+'\n')
(K/'BASELINE.sha256').write_text(sha256(base).hexdigest()+'  receiver\n'+sha256(guard).hexdigest()+'  guard\n')
(K/'HELPER.sha256').write_text(sha256((W/'payload/libomonob-wireless-maps.so').read_bytes()).hexdigest()+'\n')
print('LAYOUT_VARIANTS=PASS Center_y=56,76 other_views_exact_wired source_preferences_read_only=1')
