from pathlib import Path
import tempfile,subprocess,os,json
W=Path(__file__).resolve().parent.parent
with tempfile.TemporaryDirectory(prefix='mu1447-channel-') as temp:
 t=Path(temp);flag=t/'autostart';flag.touch();counter=t/'ticks';counter.write_text('0');cfg=t/'uaputl.cfg';cfg.write_text('Channel=4\nWpaPassphrase=fixture-secret\n')
 stable=t/'stable';pid=t/'watch.pid';log=t/'log'
 code=(W/'payload/ota/wcp_chansync.sh').read_text().replace('CFG=/tmp/uaputl.cfg','CFG='+str(cfg)).replace('/dev/shmem/mu1447-wcp-chansync.pid',str(pid)).replace('/mnt/persist/btwcp_off',str(t/'off')).replace('/mnt/persist/wcp_autostart',str(flag))
 script=t/'wcp_chansync.sh';script.write_text(code)
 b=t/'bin';b.mkdir()
 def exe(name,code):p=b/name;p.write_text('#!/bin/sh\n'+code);p.chmod(0o755);return str(p)
 iface=exe('ifconfig',f'''n=$(cat '{counter}')
if [ "$1" = uap0 ];then
 if [ "$n" -lt 124 ];then echo 'uap0 RUNNING chan 9';else echo 'uap0 RUNNING chan 11';fi
else echo 'mlan0 RUNNING status: active';fi
''')
 exe('sleep',f'''n=$(cat '{counter}');n=$((n+1));echo "$n" > '{counter}'
[ "$n" -lt 145 ] || rm -f '{flag}'
exit 0
''')
 exe('pidin',"echo '123 /dev/shmem/wcp_chansync.sh watch'\n")
 env=dict(os.environ,PATH=str(b)+':'+os.environ['PATH'],WCP_IFCONFIG=iface,WCP_CHAN_STABLE=str(stable),WCP_CHANSYNC_LOG=str(log),WCP_CHANSYNC_NAP='2')
 subprocess.run(['/bin/sh',str(script),'watch'],env=env,check=True,timeout=15)
 assert counter.read_text().strip()=='145'
 assert cfg.read_text()=='Channel=11\nWpaPassphrase=fixture-secret\n'
 assert stable.read_text().strip()=='11' and not pid.exists()
 assert 'channel moved 9 -> 11' in log.read_text() and 'fixture-secret' not in log.read_text()
 # Simulate a second start while the real previous watcher remains alive.
 pid.write_text(str(os.getpid()));flag.touch()
 subprocess.run(['/bin/sh',str(script),'watch'],env=env,check=True,timeout=3)
 assert pid.read_text()==str(os.getpid()) and counter.read_text().strip()=='145'
 print('CHANNEL_WATCH=PASS survives_240_seconds late_channel_change stable_recovery singleton credentials_unchanged')
