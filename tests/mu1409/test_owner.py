"""Host/Linux integration checks using the actual gate C and shared lock header."""
import os,pathlib,subprocess,time,signal,json
out=pathlib.Path('/out');target=out/'mock-most';marker=pathlib.Path('/tmp/mibr-isotx2-gate.direct')
for p in (target,marker):
 if p.exists():p.unlink()
env=dict(os.environ,LD_PRELOAD='/out/libgate-host.so',MIBR_ISOTX2_GATE_TARGET=str(target))
fs=pathlib.Path('/fs/tmpfs'); delayed=pathlib.Path('/fs/tmpfs.delayed'); fs.rename(delayed)
stock=subprocess.Popen(['/out/owner-fixture','stock',str(target)],env=env)
direct=None
checks=[]
def until(pred):
 deadline=time.monotonic()+5
 while time.monotonic()<deadline:
  if pred():return
  time.sleep(.01)
 raise AssertionError('timed out')
try:
 until(lambda:target.exists() and target.stat().st_size>=10)
 assert 'owner_lock_ready=0\n' in pathlib.Path('/tmp/mibr-isotx2-gate.stats').read_text()
 checks.append('stock passes before late-mounted temporary filesystem; Direct readiness stays0')
 delayed.rename(fs)
 until(lambda:'owner_lock_ready=1\n' in pathlib.Path('/tmp/mibr-isotx2-gate.stats').read_text())
 checks.append('gate lazily acquires lock and publishes readiness after mount')
 assert subprocess.run(['/out/owner-probe-host'],capture_output=True).returncode==0
 checks.append('probe observes cross-process record-lock conflict')
 marker.touch()
 direct=subprocess.Popen(['/out/owner-fixture','direct',str(target)])
 until(lambda:b'D\n' in target.read_bytes())
 # Simulate the old watchdog clearing its marker while a writer is still alive.
 marker.unlink()
 offset=target.stat().st_size
 time.sleep(.15)
 tail=target.read_bytes()[offset:]
 assert tail and b'S' not in tail and b'D' in tail
 checks.append('stock stays suppressed while direct lock held after marker removal')
 p=subprocess.run(['/out/owner-fixture','contend',str(target)])
 assert p.returncode==0
 checks.append('second direct writer rejected by same lock')
 direct.kill();direct.wait(timeout=3);direct=None
 offset=target.stat().st_size
 until(lambda:b'S\n' in target.read_bytes()[offset:])
 checks.append('stock resumes after forced writer death releases kernel lock')
 stats=pathlib.Path('/tmp/mibr-isotx2-gate.stats').read_text()
 assert 'owner_protocol=2\n' in stats and f'gate_pid={stock.pid}\n' in stats
 checks.append('gate reports protocol and actual process identity')
 print(json.dumps({'grade':'HOST_ONLY_LINUX_MOCK','result':'PASS','checks':checks},indent=2))
finally:
 if delayed.exists() and not fs.exists():delayed.rename(fs)
 if direct is not None:direct.kill();direct.wait()
 stock.terminate();stock.wait(timeout=3)
 if marker.exists():marker.unlink()
