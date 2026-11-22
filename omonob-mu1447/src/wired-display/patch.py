from pathlib import Path
import re
from hashlib import sha256
from struct import unpack_from,pack_into
base=Path(__file__).resolve().parent.parent
p=base/'payload'
b=(p/'core-original.so').read_bytes()
assert sha256(b).hexdigest()=='918f81fb43f49dacfb5e52c304e24ee3f9d00a0b6d6f66f85d6d3d87de8feaed'
out=bytearray(b)
allowed=set()
for i in (0,4):
 off=0x6f28+i*16
 assert unpack_from('<4i',b,off)==(202,1,606,329)
 pack_into('<4i',out,off,191,56,628,220)
 allowed.update(range(off,off+16))
slots=[(0x7648,0x769c),(0x769c,0x76f0),(0x76f0,0x7740),(0x7740,0x7798)]
for start,end in slots:
 old=b[start:b.index(0,start)]
 assert old.startswith(b'maps:/car/instrumentcluster') and old.count(b'showETA=no')==1
 new=re.sub(rb'maneuverLayout=[^&]*',b'maneuverLayout=',old.replace(b'showETA=no',b'showETA=yes'))
 assert len(new)<end-start
 assert not any(b[start+len(old):end])
 out[start:end]=(new+b'\0').ljust(end-start,b'\0')
 allowed.update(range(start,end))
assert len(out)==len(b)
assert {i for i,(a,c) in enumerate(zip(b,out)) if a!=c}<=allowed
# ELF headers, code, relocations, symbols and exported interfaces remain exact.
assert out[:0x6f28]==b[:0x6f28]
(p/'core-display.so').write_bytes(out)
w=(p/'wrapper-original.sh').read_text()
needle='LD_PRELOAD="$ROOT/core.so:'
assert w.count(needle)==1
(p/'wrapper-display.sh').write_text(w.replace(needle,'LD_PRELOAD="$ROOT/libmu1447-wired-display.so:$ROOT/core.so:'))
print('CORE_PATCH=PASS same_ELF_layout=1 ETA_yes=4 safe_rectangles=0,4')
print('CORE_CANDIDATE_SHA256='+sha256(out).hexdigest())
