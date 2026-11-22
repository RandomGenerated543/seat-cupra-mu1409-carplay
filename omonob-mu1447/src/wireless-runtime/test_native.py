from pathlib import Path
import subprocess,tempfile,json,struct
R=Path(__file__).resolve().parent;W=R.parent;B=R/'build'
# Execute production format/PID/locking functions on the host. /proc and QNX devctl
# remain an on-unit preflight requirement; no host result claims to validate them.
with tempfile.TemporaryDirectory() as d:
 t=Path(d);f=t/'test.c';source=(R/'source/native/runtime_guard.c').as_posix()
 f.write_text('#define main guard_program_main\n#define PIDFILE "'+str(t/'pid')+'"\n#define STATUS "'+str(t/'status')+'"\n#include "'+str(R/'source/native/fingerprints.h')+'"\n#include "'+source+'"\n#undef main\n#include <assert.h>\nint main(void){pid_t p=0;int fd,status;FILE *f;\nassert(number_pid(&p)==1);f=fopen(PIDFILE,"w");fputs("1234\\n",f);fclose(f);assert(number_pid(&p)==0&&p==1234);f=fopen(PIDFILE,"w");fputs("1234 extra\\n",f);fclose(f);assert(number_pid(&p)==3);\nassert(publish(1234,3,9,"active")==0);fd=lock_file("'+str(t/'lock')+'");assert(fd>=0);p=fork();assert(p>=0);if(p==0){int other=lock_file("'+str(t/'lock')+'");_exit(other<0?0:1);}assert(waitpid(p,&status,0)==p&&WEXITSTATUS(status)==0);close(fd);assert(lock_file("'+str(t/'lock')+'")>=0);return 0;}\n')
 subprocess.run(['cc','-std=c99','-D_POSIX_C_SOURCE=200809L',str(f),'-o',str(t/'test')],check=True,capture_output=True)
 subprocess.run([str(t/'test')],check=True)
 text=(t/'status').read_text();assert text.startswith('format=1\nreceiver_pid=1234\nmonitor_pid=') and text.endswith('generation=3\nsample=9\nstate=active\nrevision=mu1447_session_v01\n')
base=W/'payload/wcp_receiver';variants=[base,W/'layout-update/MU1447-Wireless-Layout-v0.1/payload/receiver-56',W/'layout-update/MU1447-Wireless-Layout-v0.1/payload/receiver-76']
def at(b,address,n):
 ph=struct.unpack_from('<I',b,28)[0];sz,count=struct.unpack_from('<HH',b,42)
 for i in range(count):
  typ,off,va,_,size,*_=struct.unpack_from('<8I',b,ph+i*sz)
  if typ==1 and va<=address and address+n<=va+size:return b[off+address-va:off+address-va+n]
 raise AssertionError(hex(address))
for p in variants:
 b=p.read_bytes();assert at(b,0xea050,16)==at(base.read_bytes(),0xea050,16);assert at(b,0xea080,16)==at(base.read_bytes(),0xea080,16)
 # All current helper variants keep the same session callback/set/clear globals.
 assert at(b,0xe2214,0x80)==at(base.read_bytes(),0xe2214,0x80)
result='NATIVE=PASS host_PID_validation atomic_status_format exclusive_process_lock receiver_callback_fingerprints_variants=3\nQNX_PROCFS=REQUIRES_ON_UNIT_READONLY_INSPECT\n'
(B/'native-tests.log').write_text(result);print(result,end='')
