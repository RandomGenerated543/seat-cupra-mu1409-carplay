#!/bin/ksh
# Read-only snapshot; no activation, network configuration or key collection.
echo 'MU1447_WIRELESS_RUNTIME=SNAPSHOT visible=OPERATOR_CHECK_REQUIRED'
for F in /dev/shmem/wcp_autostart.log /dev/shmem/wcp_cp.log /dev/shmem/wcp_touch_hmi.log /dev/shmem/wcp_chansync.log /ramdisk/omonob-791-input.log;do
 echo "=== $F ==="
 if [ -r "$F" ];then tail -15 "$F";else echo MISSING;fi
done
if [ -r /dev/shmem/btwcp.log ];then
 echo '=== Bluetooth bridge (filtered) ==='
 grep -E 'resolved=|armed=|mismatch|skip-noapi' /dev/shmem/btwcp.log | tail -8
fi
echo 'A snapshot is not a visual, audio, touch or stability pass.'
