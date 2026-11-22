from pathlib import Path
from hashlib import sha256
from struct import unpack_from,pack_into
p=Path(__file__).resolve().parent.parent/'payload'
b=(p/'core-stock-reference.so').read_bytes()
assert sha256(b).hexdigest()=='918f81fb43f49dacfb5e52c304e24ee3f9d00a0b6d6f66f85d6d3d87de8feaed'
out=bytearray(b);allowed=set()
# Java menu values: Center=0, Left=1, Right=2, Off=3.
# Native cpmap_card_view_for: Center ->3; active Left ->1; Off ->0/4.
expected=[(202,1,606,329),(202,45,606,252),(202,45,606,272),(191,56,628,185),(202,1,606,329)]
for i in [1,3]:
 off=0x6f28+i*16
 pack_into('<4i',out,off,*expected[i]);allowed.update(range(off,off+16))
for i,r in enumerate(expected):assert unpack_from('<4i',out,0x6f28+i*16)==r
slots=[(0x7648,0x769c),(0x769c,0x76f0),(0x76f0,0x7740),(0x7740,0x7798)]
for i,(start,end) in enumerate(slots):
 old=b[start:b.index(0,start)]
 assert old.count(b'showETA=no')==1
 new=old.replace(b'showETA=no',b'showETA=yes')
 if i==1:
  # Preserve leftAligned; this slot lacks one byte for the longer yes value.
  # Omit the optional speed-limit suppression rather than move any code/pointers.
  new=new.replace(b'&showSpeedLimit=no',b'')
 assert len(new)<end-start
 out[start:end]=(new+b'\0').ljust(end-start,b'\0')
 allowed.update(range(start,end))
assert len(out)==len(b)
assert {i for i,(x,y) in enumerate(zip(b,out)) if x!=y}<=allowed
assert out[:0x6f28]==b[:0x6f28]
assert b'maneuverLayout=no' in out[0x76f0:0x7740]
assert b'maneuverLayout=topAligned' in out[0x7648:0x769c]
assert b'maneuverLayout=leftAligned' in out[0x769c:0x76f0]
(p/'core-layout.so').write_bytes(out)
print('LAYOUT_PATCH=PASS center_view=3 left_view=1 off_original_views=0,4 showETA=yes original_ELF_and_code=exact')
print('CANDIDATE_SHA256='+sha256(out).hexdigest())
