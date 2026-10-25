#!/bin/ksh
set -u
unset LD_PRELOAD
export LD_LIBRARY_PATH=/ifs/jre/bin:/mnt/app/root/lib-target:/mnt/app/armle/lib:/mnt/app/armle/usr/lib:/mnt/app/armle/lib/dll:/mnt/app/eso/lib:/navigation:/navigation/lib
BASE=/mnt/app/root/altscreen-u2
B=$BASE/harman-r13
PROFILE=$BASE/config/cpvc-r5.profile
[ -r "$B/enabled" ] || exit 0
N=0
while [ "$N" -lt 120 ];do
 [ -r "$B/enabled" ] || exit 0
 if [ -d /fs/tmpfs ] && "$B/bin/seat-storage-probe" --readonly >/dev/null 2>&1;then
  if ERROR=$(mkdir /fs/tmpfs/mibr-seat-r13.boot.lock 2>&1);then break;fi
  [ ! -d /fs/tmpfs/mibr-seat-r13.boot.lock ] || { echo R13_BOOT=ALREADY_ATTEMPTED lock_present=1;exit 0; }
 fi
 N=$((N+1));sleep 1
done
[ "$N" -lt 120 ] || { echo "R13_BOOT=PREREQUISITE_TIMEOUT mkdir_error=${ERROR:-not_attempted}";exit 7; }
[ ! -e "$BASE/wp2/enabled" ] || { echo R13_BOOT=OLD_CONTROL_NOT_RETIRED;exit 8; }
SOCKETS=$(/usr/sbin/netstat -an) || exit 8
if echo "$SOCKETS" | awk '/19831|28743/ && /LISTEN/ {f=1} END {exit !f}';then echo R13_BOOT=CONTROL_PORT_BUSY;exit 8;fi
"$B/bin/alt111-settings" reconcile || { echo R13_BOOT=SETTINGS_RECOVERY_REQUIRED;exit 3; }
"$B/bin/alt111-settings" batch --input "$PROFILE" || { echo R13_BOOT=PROFILE_INVALID;exit 4; }
[ ! -e /tmp/mibr-seat-r13.secret ] || { echo R13_BOOT=EXISTING_SECRET_PRESERVED;exit 5; }
"$B/bin/mibr-v3-genkey" /tmp/mibr-seat-r13.secret || exit 6
export MIBR_V3_PERSIST_DELAY_MS=25000 MIBR_V3_PERSIST_MAX_MS=90000
"$B/bin/mibr-seat-service" --port 28743 --secret-file /tmp/mibr-seat-r13.secret --qualify-durable >> /tmp/mibr-seat-r13-service.log 2>&1 &
SERVICE_PID=$!
echo "$SERVICE_PID" > /tmp/mibr-seat-r13-service.pid
sleep 1
kill -0 "$SERVICE_PID" 2>/dev/null || { echo R13_BOOT=SERVICE_EXITED see_service_log=1;exit 9; }
echo 1 > /tmp/mibr-seat-r13.ready
echo request > /tmp/mibr-alt111-gen2-reacquire
echo R13_BOOT=SERVICE_RUNNING port=28743 old_control_retired=1 visible=UNCONFIRMED
