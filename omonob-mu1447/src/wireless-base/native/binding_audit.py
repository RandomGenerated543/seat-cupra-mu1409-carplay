from pathlib import Path
from hashlib import sha256
from struct import unpack_from
import json
W=Path(__file__).resolve().parents[2]
hook=Path('/path/to/inputs/manual-ssh-mu1447/payload/wireless/common/ota/libbtwcp.so').read_bytes()
target=Path('/path/to/SEAT-CUPRA-MU1409-AltScreen/work/p4709-mu1447-port/app/eso/bin/apps/btstack').read_bytes()
assert sha256(hook).hexdigest()=='95a75391792c7266eb8c759c20f3b35745d2cd890b74fad45e2c36a5406e9d4e'
assert sha256(target).hexdigest()=='a0276f0b8a0c9ba3a50578cba901db07250398a0d9aa61005df4c0290d99fea4'
def at(image,address,size):
 ph=unpack_from('<I',image,28)[0];es,n=unpack_from('<HH',image,42)
 for i in range(n):
  kind,off,base,_,length,*_=unpack_from('<8I',image,ph+i*es)
  if kind==1 and base<=address and address+size<=base+length:return image[off+address-base:off+address-base+size]
 raise ValueError(hex(address))
start=0x175e0;result=[]
checks=[(4,0x34,8),(8,0x3c,8),(0xc,0x44,8),(0x18,0x4c,8),(0x1c,0x54,8),(0x20,0x5c,8),(0x24,0x64,8),(0x28,0x6c,8),(0x2c,0x74,8),(0x30,0x7c,8),(0x90,0x98,12),(0x94,0xa4,12),(0xb0,0xb4,12)]
for off,sig,n in checks:
 addr=unpack_from('<I',hook,start+off)[0];expected=hook[start+sig:start+sig+n]
 actual=at(target,addr,n);assert actual==expected,(hex(addr),actual.hex(),expected.hex())
 result.append({'descriptor_offset':hex(off),'target_address':hex(addr),'fingerprint':expected.hex(),'match':True})
for off,sig in [(0x10,0x36db),(0x14,0x36e3)]:
 addr=unpack_from('<I',hook,start+off)[0];expected=at(hook,sig,8);actual=at(target,addr,8);assert expected==actual
 result.append({'descriptor_offset':hex(off),'target_address':hex(addr),'fingerprint':expected.hex(),'match':True})
out={'target':'MU1447 SEAT P4709 btstack','target_sha256':sha256(target).hexdigest(),'bridge_sha256':sha256(hook).hexdigest(),'profile':'existing +8 descriptor','entry_point_fingerprints':result,'count':len(result),'scope':'Static entry point compatibility only; no RF/session/structure ABI acceptance implied.'}
(W/'research/native-binding-audit.json').write_text(json.dumps(out,indent=2)+'\n')
print('NATIVE_ENTRY_FINGERPRINTS=PASS count='+str(len(result)))
