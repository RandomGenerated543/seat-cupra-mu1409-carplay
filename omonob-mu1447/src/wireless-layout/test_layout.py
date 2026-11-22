"""Run the actual patched ARM helper with file/CF/libc fixture APIs."""
from pathlib import Path
from struct import pack,unpack_from
import re,zlib,json
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm_const import *
W=Path(__file__).resolve().parents[2];K=W/'layout-update/MU1447-Wireless-Layout-v0.1'
API=json.loads((W/'source/receiver/plt-bindings.json').read_text())
ROOT='/mnt/icab/persistent/cpmap-ui'
def state(pos,gen=46):
 body=f'format=1\nposition={pos}\ngeneration={gen}\n';return body+f'crc32={zlib.crc32(body.encode()):x}\n'
assert state(0).endswith('crc32=1d4def3c\n')
def run(y,files,url=False,allocation=True,original_result=0):
 image=(K/f'payload/receiver-{y}').read_bytes();vm=Uc(UC_ARCH_ARM,UC_MODE_ARM)
 vm.mem_map(0x10000,0x160000);vm.mem_map(0x300000,0x20000)
 ph=unpack_from('<I',image,28)[0];es,n=unpack_from('<HH',image,42)
 for i in range(n):
  typ,off,base,_,size,*_=unpack_from('<8I',image,ph+i*es)
  if typ==1:vm.mem_write(base,image[off:off+size])
 objects={1:{}};opened={};logs=[];calls=[];live=set()
 def cstr(addr):
  out=bytearray()
  while (b:=vm.mem_read(addr,1)[0]):out.append(b);addr+=1
  return out.decode()
 def stack(i=0):return unpack_from('<I',vm.mem_read(vm.reg_read(UC_ARM_REG_SP)+i*4,4))[0]
 def newobj(x):n=len(objects)+2;objects[n]=x;live.add(n);return n
 def setnum(dst,key,lo,hi):
  assert hi==0;k=objects[key] if key in objects else cstr(key+8);calls.append((k,lo));objects[dst][k]=lo;return original_result if k=='initialViewArea' else 0
 def release(addr,*_):live.remove(addr);return 0
 def fopen(path,mode,*_):
  p=cstr(path)
  if cstr(mode)=='w':opened[9000]=p;return 9000
  if p not in files:return 0
  n=8000+len(opened);opened[n]=p;return n
 def lstat(path,out,*_):
  p=cstr(path)
  if p not in files:vm.mem_write(0x31e000,pack('<I',2));return 0xffffffff
  vm.mem_write(out,b'\0'*72);vm.mem_write(out+8,pack('<Q',len(files[p].encode())));vm.mem_write(out+44,pack('<I',0o100600));return 0
 def fread(out,size,count,f):
  data=files[opened[f]].encode()[:size*count];vm.mem_write(out,data);return len(data)//size
 def memcmp(a,b,n,*_):return int(bytes(vm.mem_read(a,n))!=bytes(vm.mem_read(b,n)))
 def memchr(a,b,n,*_):
  data=bytes(vm.mem_read(a,n));i=data.find(bytes([b]));return 0 if i<0 else a+i
 def sscanf(data,fmt,pos,gen):
  m=re.fullmatch(r'format=1\nposition=([+-]?\d+)\ngeneration=(\d+)\ncrc32=([0-9a-fA-F]+)\n',cstr(data))
  if not m:return 0
  vm.mem_write(pos,pack('<i',int(m[1])));vm.mem_write(gen,pack('<Q',int(m[2])&0xffffffffffffffff));vm.mem_write(stack(),pack('<I',int(m[3],16)));vm.mem_write(stack(1),pack('<I',len(cstr(data))));return 3
 def snprintf(out,size,fmt,arg):
  f=cstr(fmt)
  if f=='%s':s=cstr(arg)
  elif f in ('%s/navigation-card.state','%s/navigation-card.previous'):s=f.replace('%s',cstr(arg))
  elif f=='format=1\nposition=%d\ngeneration=%llu\n':s=f'format=1\nposition={arg}\ngeneration={stack()+(stack(1)<<32)}\n'
  elif f=='%scrc32=%x\n':s=cstr(arg)+f'crc32={stack():x}\n'
  else:raise AssertionError(f)
  if size:vm.mem_write(out,s.encode()[:size-1]+b'\0')
  return len(s)
 def fprintf(f,fmt,pos,view):logs.append((opened[f],cstr(fmt),pos,view,stack()));return 1
 def dlsym(handle,name,*_):return {'lstat':0x302000,'ferror':0x302004,'getenv':0x302008}[cstr(name)]
 functions={API['fopen']:fopen,API['fclose']:lambda *_:0,API['fread']:fread,API['fprintf']:fprintf,API['snprintf']:snprintf,API['sscanf']:sscanf,API['memcmp']:memcmp,API['memchr']:memchr,API['dlsym']:dlsym,API['__get_errno_ptr']:lambda *_:0x31e000,0x302000:lstat,0x302004:lambda *_:0,0x302008:lambda *_:0,0x5ada0:setnum,0x52220:lambda allocator,a,*unused:(newobj(cstr(a)) if allocation else 0),0x51ce8:release}
 regs=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)
 saved={r:v for r,v in zip((UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_SP),(*range(904,912),0x31d000))}
 def dispatch(vm,addr,*_):
  if addr in functions:
   assert vm.reg_read(UC_ARM_REG_SP)%8==0
   result=functions[addr](*(vm.reg_read(r) for r in regs));vm.reg_write(UC_ARM_REG_R0,result);vm.reg_write(UC_ARM_REG_PC,vm.reg_read(UC_ARM_REG_LR))
 vm.hook_add(UC_HOOK_CODE,dispatch)
 for r,v in saved.items():vm.reg_write(r,v)
 if url:
  vm.reg_write(UC_ARM_REG_R0,0x310000);vm.reg_write(UC_ARM_REG_R1,512);vm.emu_start(0xe4b74,0xe4b78,count=100000);result=cstr(0x310000)
 else:
  for r,v in zip(regs,(1,0x3fc58,0,0)):vm.reg_write(r,v)
  vm.emu_start(0xe4b64,0xe4b68,count=100000);assert vm.reg_read(UC_ARM_REG_R0)==original_result
  assert len(logs)==1 and not live
  result=objects[1]
 assert all(vm.reg_read(r)==v for r,v in saved.items())
 return result
cases=0
for y in [56,76]:
 for pos,alignment in enumerate(['topAligned','leftAligned','rightAligned','no']):
  f={ROOT+'/navigation-card.state':state(pos)}
  assert run(y,f)=={'initialViewArea':3 if pos==0 else 0,'zoomFactor':70}
  u=run(y,f,url=True);assert 'showETA=yes' in u and f'maneuverLayout={alignment}' in u
  cases+=1
 for bad in ['',state(0).replace('1d4def3c','deadbeef'),state(0,0),state(0,1<<63),state(9),state(0)+'extra\n']:
  f={ROOT+'/navigation-card.state':bad}
  assert run(y,f)['initialViewArea']==0
  f[ROOT+'/navigation-card.previous']=state(0)
  assert run(y,f)['initialViewArea']==3
  cases+=2
 assert run(y,{})['initialViewArea']==0
 assert run(y,{ROOT+'/navigation-card.state':state(0)},allocation=False)=={'initialViewArea':3}
 assert run(y,{ROOT+'/navigation-card.state':state(0)},original_result=7)['initialViewArea']==3
 guard=(K/f'payload/guard-{y}').read_bytes()
 from hashlib import sha256
 assert guard[0x1310:0x1350]==sha256((K/f'payload/receiver-{y}').read_bytes()).hexdigest().encode()
print('ARM_LAYOUT=PASS cases='+str(cases)+' exact_user_preference all_card_modes CRC_previous_fallback missing_invalid_generation original_return allocation_failure ABI guarded_variants')
