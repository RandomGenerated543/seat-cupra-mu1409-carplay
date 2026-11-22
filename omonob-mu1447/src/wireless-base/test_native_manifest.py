"""Execute the shipped native ARM manifest parser, with libc/file APIs stubbed.
This tests its real delimiter/path/duplicate handling rather than a permissive
host reimplementation. File hashes are supplied by the fixture.
"""
from pathlib import Path
from struct import unpack_from,pack
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm_const import *
W=Path(__file__).resolve().parent.parent
image=(W/'release/MU1447-Native-Wireless-v1.0-rc1.2/file-check').read_bytes()
H='a'*64

def run(text):
 vm=Uc(UC_ARCH_ARM,UC_MODE_ARM);vm.mem_map(0x100000,0x10000);vm.mem_map(0x300000,0x40000)
 ph=unpack_from('<I',image,28)[0];es,n=unpack_from('<HH',image,42)
 for i in range(n):
  typ,off,addr,_,size,*_=unpack_from('<8I',image,ph+i*es)
  if typ==1:vm.mem_write(addr,image[off:off+size])
 vm.mem_write(0x300000,b'/backup\0');vm.mem_write(0x300100,b'/seal\0')
 lines=text.splitlines(keepends=True);allocated=0x310000
 def string(addr):
  out=bytearray()
  while (b:=vm.mem_read(addr,1)[0]):out.append(b);addr+=1
  return out.decode()
 def fgets(dest,size,f,_):
  if not lines:return 0
  s=lines.pop(0).encode();assert len(s)<size;vm.mem_write(dest,s+b'\0');return dest
 def lstat(path,out,*_):
  s=string(path);mode=0o040755 if s in ('/backup','/backup/files') else 0o100644
  vm.mem_write(out,b'\0'*72);vm.mem_write(out+44,pack('<I',mode));return 0
 def snprintf(dest,size,fmt,root):
  extra=unpack_from('<I',vm.mem_read(vm.reg_read(UC_ARM_REG_SP),4))[0]
  s=(string(root)+'/'+string(extra)).encode();vm.mem_write(dest,s+b'\0');return len(s)
 def malloc(n,*_):
  nonlocal allocated
  p=allocated;allocated+=n+16;return p
 def memcpy(dst,src,n,*_):vm.mem_write(dst,bytes(vm.mem_read(src,n)));return dst
 def hash_file(path,out,*_):vm.mem_write(out,H.encode()+b'\0');return 0
 def strchr(addr,needle,*_):
  s=string(addr);i=s.find(chr(needle));return 0 if i<0 else addr+i
 functions={0x10099c:lambda *_:1,0x1008e8:fgets,0x100a14:lambda a,*_:len(string(a)),0x100960:lambda *_:0,0x1009b4:lambda *_:0,0x1009d8:lambda a,b,*_:int(string(a)!=string(b)),0x100954:lstat,0x1008c4:snprintf,0x10096c:lambda a,b,n,*_:int(vm.mem_read(a,n)!=vm.mem_read(b,n)),0x10090c:malloc,0x1008f4:memcpy,0x100a44:lambda *_:0,0x1008ac:lambda *_:0,0x100930:lambda *_:0,0x100a20:strchr,0x10101c:hash_file}
 regs=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)
 def hook(vm,addr,*_):
  if addr in functions:
   result=functions[addr](*(vm.reg_read(r) for r in regs));vm.reg_write(UC_ARM_REG_R0,result);vm.reg_write(UC_ARM_REG_PC,vm.reg_read(UC_ARM_REG_LR))
 vm.hook_add(UC_HOOK_CODE,hook)
 vm.reg_write(UC_ARM_REG_SP,0x33ff00);vm.reg_write(UC_ARM_REG_R0,0x300000);vm.reg_write(UC_ARM_REG_R1,0x300100);vm.reg_write(UC_ARM_REG_LR,0x300800)
 vm.emu_start(0x1011a0,0x300800,count=100000)
 assert vm.reg_read(UC_ARM_REG_PC)==0x300800
 return vm.reg_read(UC_ARM_REG_R0)
assert run(H+' files/001\n')==2
assert run(H+'  files/001\n')==0
assert run(H+'  targets.tsv\n'+H+'  before.tsv\n'+H+'  after.tsv\n')==0
assert run(H+'  files/001\n'+H+'  files/001\n')==2
assert run(H+'  ../outside\n')==2
assert run(H+'  files/001')==2
print('NATIVE_MANIFEST=PASS actual_ARM_parser single_space_rejected double_space_accepted metadata_paths duplicates_traversal_missing_newline')
