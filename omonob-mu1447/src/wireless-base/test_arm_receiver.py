"""Execute actual patched ARM instructions with fixture CF and file APIs."""
from pathlib import Path
from struct import unpack_from
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm_const import *
p=Path(__file__).resolve().parent.parent/'payload'
image=(p/'wcp_receiver').read_bytes()

def run(config=None, view=None, allocate=True, original_status=0, zoom_status=0):
    vm=Uc(UC_ARCH_ARM, UC_MODE_ARM)
    vm.mem_map(0x10000,0x150000); vm.mem_map(0x300000,0x10000)
    ph=unpack_from('<I',image,28)[0]
    for i in range(14):
        kind,off,base,_,length,*_=unpack_from('<8I',image,ph+i*32)
        if kind==1: vm.mem_write(base,image[off:off+length])
    alt={'viewAreas':'donor','widthPixels':1010,'heightPixels':376,'type':111}
    objects={1:alt}; live=set(); calls=[]; files={}; logs=[]
    def new(obj):
        n=len(objects)+1; objects[n]=obj; live.add(n); return n
    def string(addr):
        b=bytearray()
        while (c:=vm.mem_read(addr,1)[0]): b.append(c);addr+=1
        return b.decode()
    def key(addr):return objects[addr] if addr in objects else string(addr+8)
    def setnum(dest,k,lo,hi):
        assert hi==0
        k=key(k); calls.append((k,lo))
        status=zoom_status if k=='zoomFactor' else original_status if k=='initialViewArea' else 0
        if not status:objects[dest][k]=lo
        return status
    def setval(dest,k,value,_):objects[dest][key(k)]=objects[value];return 0
    def append(dest,value,*_):objects[dest].append(objects[value]);return 0
    def release(addr,*_):live.remove(addr);return 0
    def fopen(path,mode,*_):
        assert string(path)=='/mnt/persist/cpmap-vc-zoom.conf' and string(mode)=='r'
        if config is None:return 0
        n=new('file');files[n]=config;return n
    def fgets(buf,size,f,_):
        data=files[f]
        if not data:return 0
        n=min(len(data),size-1)
        nl=data.find('\n',0,n)
        if nl>=0:n=nl+1
        vm.mem_write(buf,data[:n].encode()+b'\0');files[f]=data[n:];return buf
    targets={
        0x5ada0:setnum,0x520d0:setval,0x51db4:append,
        0x58fb0:lambda lo,hi,*_:new(lo),
        0x52060:lambda *_:new({}),0x51d1c:lambda *_:new([]),
        0x52220:lambda _,addr,encoding,__:(new(string(addr)) if allocate else 0),
        0x51ce8:release,0xefb30:fopen,0xf01c0:fgets,
        0xefb50:lambda f,*_:(live.remove(f) or 0),
        0xef8e0:lambda addr,*_:(logs.append(string(addr)) or 0),
    }
    regs=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)
    saved={r:v for r,v in zip((UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_SP),(*range(9004,9012),0x30ff00))}
    def dispatch(vm,addr,*_):
        if addr in targets:
            assert vm.reg_read(UC_ARM_REG_SP)%8==0
            result=targets[addr](*(vm.reg_read(r) for r in regs))
            vm.reg_write(UC_ARM_REG_R0,result);vm.reg_write(UC_ARM_REG_PC,vm.reg_read(UC_ARM_REG_LR))
    vm.hook_add(UC_HOOK_CODE,dispatch)
    for r,v in saved.items():vm.reg_write(r,v)
    if view is None:
        for r,v in zip(regs,(1,0x3fc58,0,0)):vm.reg_write(r,v)
        vm.emu_start(0xe4b64,0xe4b68,count=100000)
        assert vm.reg_read(UC_ARM_REG_PC)==0xe4b68
        assert vm.reg_read(UC_ARM_REG_R0)==original_status
        assert live==set(),live
        assert calls[0]==('initialViewArea',0)
        assert sum(k=='initialViewArea' for k,v in calls)==1
        result=alt
    else:
        for r,v in zip(regs,(1010,376,view,0)):vm.reg_write(r,v)
        vm.reg_write(UC_ARM_REG_LR,0x301000)
        vm.emu_start(0xe5988,0x301000,count=100000)
        assert vm.reg_read(UC_ARM_REG_PC)==0x301000
        addr=vm.reg_read(UC_ARM_REG_R0);result=objects[addr] if addr else None
        assert live==({addr} if addr else set()),live
    assert all(vm.reg_read(r)==v for r,v in saved.items())
    return result


assert run()['zoomFactor']==70
assert 'zoomFactor' not in run(allocate=False)
assert 'zoomFactor' not in run(zoom_status=1)
assert run(original_status=7)['zoomFactor']==70
expected=[(202,1,606,329),(202,45,606,252),(202,45,606,272),(191,76,628,185),(202,1,606,329)]
for i,rect in enumerate(expected):
 d=run(view=i)
 assert (d['widthPixels'],d['heightPixels'],d['originXPixels'],d['originYPixels'])==(1010,376,0,0)
 safe=d['safeArea']
 assert tuple(safe[k] for k in ['originXPixels','originYPixels','widthPixels','heightPixels'])==rect
 assert d['adjacentViewAreas']==[j for j in range(5) if j!=i]
assert run(view=5) is None
print('ARM_RECEIVER=PASS fixed70 original_return ABI allocation_failure setter_failure resource_release five_SEAT_rectangles adjacency')
