#!/bin/ksh
# MIBR MU1440 native keypanel SD-safe v1.3. Never alters OEM flash or video.
set -u
MEDIA=/net/mmx/fs/sda0
MEDIA_ALIAS=/net/mmx.mibhigh.net/fs/sda0
DIR=$(pwd) || exit 2
case "$DIR" in
  "$MEDIA"/*|"$MEDIA_ALIAS"/*) ;;
  *) echo "KEYPANEL_PREFLIGHT=FAIL wrong_directory=$DIR"; echo 'Expected SD root /net/mmx/fs/sda0 (or QNX alias)'; exit 2 ;;
esac
[ -x ./mibr-keypanel-native ] || { echo 'KEYPANEL_PREFLIGHT=FAIL binary_missing_or_not_executable'; exit 2; }
DURATION=${1:-120}
case "$DURATION" in
  *[!0-9]*|'') echo "KEYPANEL_PREFLIGHT=FAIL invalid_seconds=$DURATION"; exit 2 ;;
esac
[ "$DURATION" -ge 10 ] && [ "$DURATION" -le 1800 ] || { echo 'KEYPANEL_PREFLIGHT=FAIL seconds_must_be_10_to_1800'; exit 2; }
SDTEST="$DIR/.mibr-keypanel-rw-test.$$"
if ( : > "$SDTEST" ) 2>/dev/null; then
  rm -f "$SDTEST" || { echo 'KEYPANEL_PREFLIGHT=FAIL sd_probe_cleanup'; exit 2; }
  echo 'sd_mount=ALREADY_WRITABLE'
else
  echo "sd_mount=READ_ONLY_OR_UNWRITABLE attempting_mount_uw=$MEDIA"
  if mount -uw "$MEDIA"; then
    echo "sd_mount=REMOUNTED path=$MEDIA"
  elif mount -uw "$MEDIA_ALIAS"; then
    echo "sd_mount=REMOUNTED path=$MEDIA_ALIAS"
  else
    echo 'KEYPANEL_PREFLIGHT=FAIL sd_remount'
    exit 2
  fi
  if ! ( : > "$SDTEST" ) 2>/dev/null; then
    echo 'KEYPANEL_PREFLIGHT=FAIL sd_still_not_writable'
    exit 2
  fi
  rm -f "$SDTEST" || { echo 'KEYPANEL_PREFLIGHT=FAIL sd_probe_cleanup'; exit 2; }
  echo 'sd_mount=WRITE_PROBE_PASS'
fi
POINTER=./mibr-keypanel-native-current
if [ -e "$POINTER" ]; then
  echo 'KEYPANEL_PREFLIGHT=FAIL active_or_stale_sd_pointer'
  echo 'Inspect ./mibr-keypanel-native-current and active processes; do not auto-delete.'
  exit 2
fi
echo 'sd_flat_pointer=READY; tmp_writes=NONE; rename_syscall=NONE'
echo "recording_directory=$DIR/native-<PID>"
echo 'sd_output=YES; tmp_writes=NONE; tmp_subdirectories=NO; tmp_video=NO'
trap 'sync 2>/dev/null || true' 0
./mibr-keypanel-native --capture --out . --seconds "$DURATION"
RC=$?
echo "KEYPANEL_WRAPPER_EXIT=$RC"
exit "$RC"
