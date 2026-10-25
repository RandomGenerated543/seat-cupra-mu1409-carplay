#!/bin/ksh
# Exact WP2 receiver diagnostic swap. No Java, settings, media owner or PF edits.
set -u
case "$0" in */*) ROOT=${0%/*};; *) ROOT=.;; esac
ROOT=$(cd "$ROOT" && pwd) || exit 2
. "$ROOT/hashes.sh" || exit 2
BASE=/mnt/app/root/altscreen-u2
SHA=$BASE/bin/sha256sum
TARGET=/mnt/app/eso/lib/libmibr_carplay111.so
BACK=$BASE/backup/queue-recovery-v01
RECOVERY=$BASE/queue-recovery
RW=0
MODE=${1:---check}
fail(){ echo "QUEUE_RECOVERY_INSTALL=FAIL $*";exit 20; }
digest(){ LINE=$("$SHA" "$1") || return 1;echo "$LINE" | awk '{print $1}'; }
verify(){ [ -f "$1" ] && [ ! -L "$1" ] && [ "$(digest "$1")" = "$2" ] || fail "unexpected_bytes=$1"; }
finish(){ RC=$?;trap - 0;if [ "$RW" -eq 1 ];then sync;mount -ur /mnt/app || { echo QUEUE_RECOVERY_INSTALL=FAIL remount_readonly;RC=35; };fi;exit "$RC"; }
trap finish 0
trap 'exit 130' 1 2 15
case "$MODE" in --check|--apply|--restore) ;; *) fail usage_check_apply_restore;; esac
for C in awk cp chmod mv mkdir mount sync;do command -v "$C" >/dev/null 2>&1 || fail "missing=$C";done
verify "$SHA" 95d1e6e9611905d9f91f020d34b1bcd1236085c2862dee3faf0a91e790d37f3c
CURRENT=$(digest "$TARGET") || fail receiver_read
case "$CURRENT" in "$ORIGINAL"|"$DIAGNOSTIC") ;; *) fail unknown_receiver_preserved;; esac
if [ -e "$BACK" ];then verify "$BACK/receiver.before" "$ORIGINAL";fi
if [ "$MODE" != --restore ];then
 verify /mnt/app/eso/lib/libairplay.so 193a4fd9101ec2aa05e7159cfa307b96500810d379ca74a194f172adc13a46b5
 verify /mnt/app/eso/hmi/lsd/lsd.sh "$STARTUP"
 verify /mnt/app/root/mibr-carplay111-safearea.conf "$SAFEAREA"
 [ -r "$BASE/harman-r13/enabled" ] || fail r13_disabled
 verify "$ROOT/payload/libmibr_carplay111.so" "$DIAGNOSTIC"
 verify "$ROOT/install.sh" "$INSTALLER"
 if [ "$CURRENT" = "$DIAGNOSTIC" ];then verify "$BACK/receiver.before" "$ORIGINAL";fi
fi
if [ "$MODE" = --check ];then echo QUEUE_RECOVERY_PREFLIGHT=PASS writes=0 geometry_unchanged=1 zoomFactor=70 recovery_effect=UNTESTED;exit 0;fi
if [ "$MODE" = --restore ];then
 verify "$BACK/receiver.before" "$ORIGINAL"
 SOURCE=$BACK/receiver.before;EXPECTED=$ORIGINAL
else SOURCE=$ROOT/payload/libmibr_carplay111.so;EXPECTED=$DIAGNOSTIC;fi
[ ! -e "$TARGET.queuerecovery-new" ] && [ ! -L "$TARGET.queuerecovery-new" ] || fail partial_stage_preserved
mount -uw /mnt/app || fail app_writable
RW=1
if [ "$MODE" = --apply ];then
 if [ ! -e "$BACK" ];then
  [ ! -e "$BACK.preparing" ] || fail partial_backup_preserved
  mkdir "$BACK.preparing" || fail backup_directory
  cp "$TARGET" "$BACK.preparing/receiver.before" || fail backup_copy
  verify "$BACK.preparing/receiver.before" "$ORIGINAL"
  sync
  mv "$BACK.preparing" "$BACK" || fail backup_commit
 fi
 mkdir -p "$RECOVERY" || fail recovery_directory
 cp "$ROOT/install.sh" "$RECOVERY/install.sh.new" && cp "$ROOT/hashes.sh" "$RECOVERY/hashes.sh.new" || fail recovery_copy
 verify "$RECOVERY/install.sh.new" "$INSTALLER"
 chmod 644 "$RECOVERY/install.sh.new" "$RECOVERY/hashes.sh.new" || fail recovery_permissions
 mv "$RECOVERY/install.sh.new" "$RECOVERY/install.sh" && mv "$RECOVERY/hashes.sh.new" "$RECOVERY/hashes.sh" || fail recovery_commit
fi
cp "$SOURCE" "$TARGET.queuerecovery-new" || fail stage_copy
verify "$TARGET.queuerecovery-new" "$EXPECTED"
chmod 755 "$TARGET.queuerecovery-new" || fail stage_permissions
sync
mv "$TARGET.queuerecovery-new" "$TARGET" || fail receiver_commit
verify "$TARGET" "$EXPECTED"
echo "QUEUE_RECOVERY_INSTALL=PASS mode=$MODE RESTART_REQUIRED=YES geometry_unchanged=1 zoomFactor=70 recovery_effect=UNTESTED"
