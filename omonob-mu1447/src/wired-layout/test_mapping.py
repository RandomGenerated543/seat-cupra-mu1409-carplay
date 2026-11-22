"""Execute the original/patched native selector at two load addresses."""
from pathlib import Path
from struct import unpack_from
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_ARM
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR
p=Path(__file__).resolve().parent.parent/'payload'
b=(p/'core-layout.so').read_bytes()
expected={0:(3,3),1:(0,1),2:(0,2),3:(0,4)}
for base in [0x10000,0x500000]:
 vm=Uc(UC_ARCH_ARM,UC_MODE_ARM);vm.mem_map(base,0x20000);vm.mem_write(base,b)
 end=base+0x18000
 for position,views in expected.items():
  for route,view in enumerate(views):
   vm.reg_write(UC_ARM_REG_R0,position);vm.reg_write(UC_ARM_REG_R1,route);vm.reg_write(UC_ARM_REG_LR,end)
   vm.emu_start(base+0x1cb0,end,count=1000)
   assert vm.reg_read(UC_ARM_REG_R0)==view
rects=[unpack_from('<4i',b,0x6f28+i*16) for i in range(5)]
assert rects[3]==(191,56,628,185)
assert rects[1]==(202,45,606,252) and 45+272-(45+252)==20
assert rects[0]==rects[4]==(202,1,606,329)
assert rects[2]==(202,45,606,272)
print('ARM_MENU_MAPPING=PASS Center_view3 Left_active_view1 Off_views0_4 both_route_states multiple_load_addresses geometry')
