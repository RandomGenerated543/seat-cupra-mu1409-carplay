#!/bin/ksh
# Read-only discovery for the exact MU1440 stock keypanel logging path.
# No mounts, writes, process signals or persistent changes.
set -u

echo "=== MU1440 KEYPANEL TRACE DISCOVERY ==="
echo "mode=READ_ONLY"
echo

echo "=== relevant processes ==="
pidin ar 2>/dev/null | grep '/eso/bin/traceserver' 2>/dev/null || true
pidin ar 2>/dev/null | grep '/ifs/jre/bin/j9' 2>/dev/null || true
echo

TPID=
set -- $(pidin ar 2>/dev/null | grep '/eso/bin/traceserver' 2>/dev/null)
[ "$#" -gt 0 ] && TPID=$1

echo "=== traceserver fds ==="
if [ -n "$TPID" ]; then
  echo "traceserver_pid=$TPID"
  pidin -p "$TPID" fds 2>/dev/null || echo "traceserver_fds=UNAVAILABLE"
else
  echo "traceserver_pid=NOT_FOUND"
fi
echo

echo "=== candidate trace utilities ==="
FOUND=0
for P in   /proc/boot/sloginfo   /bin/sloginfo   /usr/bin/sloginfo   /sbin/sloginfo   /proc/boot/traceprinter   /bin/traceprinter   /usr/bin/traceprinter   /proc/boot/tracelogger   /bin/tracelogger   /usr/bin/tracelogger   /eso/bin/traceprinter   /eso/bin/tracelogger
do
  if [ -x "$P" ]; then
    echo "trace_tool=$P"
    FOUND=1
  fi
done
[ "$FOUND" -eq 1 ] || echo "trace_tool=NONE_IN_KNOWN_PATHS"
echo

echo "=== logging configuration files ==="
for F in   /eso/hmi/lsd/config/logging.properties   /eso/hmi/lsd/traceConfig.properties   /mnt/app/eso/hmi/lsd/config/logging.properties   /mnt/app/eso/hmi/lsd/traceConfig.properties
do
  if [ -r "$F" ]; then
    echo "--- $F ---"
    cat "$F" 2>/dev/null
    echo "--- end $F ---"
  fi
done
echo

echo "=== obvious logger endpoints ==="
for P in /dev/slog /dev/slogger /dev/trace /dev/shmem/trace /tmp/esotrace /tmp/trace
do
  [ -e "$P" ] && ls -l "$P" 2>/dev/null
done
echo

echo "KEYPANEL_TRACE_DISCOVERY=COMPLETE"
echo "Next step: choose a reader only from the paths/endpoints proven above."
exit 0
