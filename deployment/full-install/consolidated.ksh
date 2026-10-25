#!/bin/ksh
# Exact-baseline consolidated candidate. Never flashes or restarts the unit.
set -u
unset LD_PRELOAD
case "$0" in */*) ROOT=${0%/*};; *) ROOT=.;; esac
ROOT=$(cd "$ROOT" && pwd) || exit 2
SHA=$ROOT/payload/sha256sum
BASE=/mnt/app/root/altscreen-u2
BACK=/mnt/app/root/seat-full-install-v02-backup
MEDIA_BACK=$ROOT/original-backup
RW_APP=0;RW_SYS=0;CHANGING=0;STAGE=;STAGE_HASH=
MODE=${1:---check}
fail(){ echo "FULL_INSTALL=FAIL $*";exit 20; }
digest(){ LINE=$("$SHA" "$1") || return 1;echo "$LINE" | awk '{print $1}'; }
verify(){ [ -f "$1" ] && [ ! -L "$1" ] && [ "$(digest "$1")" = "$2" ] || fail "unexpected_bytes=$1"; }
parent(){ case "$1" in */*) PARENT=${1%/*};; *) fail parent_path;;esac; }
atomic(){
 SRC=$1;DEST=$2;HASH=$3;PERM=$4
 verify "$SRC" "$HASH"
 if [ -f "$DEST" ] && [ ! -L "$DEST" ] && [ "$(digest "$DEST")" = "$HASH" ];then return 0;fi
 [ ! -e "$DEST.full-new" ] && [ ! -L "$DEST.full-new" ] || fail "partial_file=$DEST.full-new"
 parent "$DEST";mkdir -p "$PARENT" || fail parent_directory
 STAGE=$DEST.full-new;STAGE_HASH=$HASH
 cp "$SRC" "$DEST.full-new" || fail stage_copy
 verify "$DEST.full-new" "$HASH"
 chmod "$PERM" "$DEST.full-new" && mv "$DEST.full-new" "$DEST" || fail commit
 verify "$DEST" "$HASH"
 STAGE=;STAGE_HASH=
}
verify_kit(){
 [ -x "$SHA" ] || fail missing_executable_hash_helper
 verify "$SHA" 95d1e6e9611905d9f91f020d34b1bcd1236085c2862dee3faf0a91e790d37f3c
 [ -f "$ROOT/KIT.sha256" ] && [ -f "$ROOT/TARGETS.txt" ] && [ -f "$ROOT/IMMUTABLES.txt" ] || fail incomplete_kit
 while read HASH FILE;do
  case "$FILE" in /*|*..*|"") fail kit_path;;esac
  verify "$ROOT/$FILE" "$HASH"
 done < "$ROOT/KIT.sha256"
}
backup_valid(){
 while read KIND ID SRC TARGET BEFORE AFTER PERM;do
  [ "$KIND" = replace ] || continue
  verify "$BACK/original/$ID" "$BEFORE"
 done < "$ROOT/TARGETS.txt"
 [ "$(cat "$BACK/targets.sha256")" = "$(digest "$ROOT/TARGETS.txt")" ] || fail backup_target_manifest_changed
}
check_identity(){
 while read HASH FILE;do verify "$FILE" "$HASH";done < "$ROOT/IMMUTABLES.txt"
}
check_targets(){
 while read KIND ID SRC TARGET BEFORE AFTER PERM;do
  case "$TARGET" in /mnt/app/root/altscreen-u2/*|/mnt/app/root/mibr-carplay111-safearea.conf|/mnt/app/root/mibr-seat-zoom-auto.conf|/mnt/app/eso/lib/libmibr_carplay111.so|/mnt/app/eso/lib/libmibr_isotx2_gate.so|/mnt/app/eso/hmi/lsd/mibr/icons/mibr_seat_home_gears_rgba_150x150-v2.png|/mnt/app/eso/hmi/lsd/lsd.sh|/mnt/system/etc/boot/startup.sh|/mnt/system/etc/eso/production/smartphone_integrator.json|/mnt/system/etc/pf.conf|/mnt/system/etc/pf.mlan0.conf) ;;*) fail target_path;;esac
  case "$SRC" in payload/*) ;;*) fail source_path;;esac
  case "$SRC$TARGET" in *..*) fail traversal;;esac
  parent "$TARGET";ANCESTOR=$PARENT
  while [ "$ANCESTOR" != /mnt/app ] && [ "$ANCESTOR" != /mnt/system ];do
   [ ! -L "$ANCESTOR" ] || fail "symlink_parent=$ANCESTOR"
   ANCESTOR=${ANCESTOR%/*}
  done
  [ ! -L "$TARGET" ] && [ ! -e "$TARGET.full-new" ] && [ ! -L "$TARGET.full-new" ] || fail "symlink_or_partial=$TARGET"
  [ ! -e "$TARGET.full-rollback" ] && [ ! -L "$TARGET.full-rollback" ] || fail "rollback_fragment=$TARGET"
  if [ "$KIND" = replace ];then
   CURRENT=$(digest "$TARGET") || fail target_read
   case "$TARGET" in /mnt/system/*) verify "${TARGET#/mnt/system}" "$CURRENT";;esac
   if [ -d "$BACK/original" ];then
    [ "$CURRENT" = "$BEFORE" ] || [ "$CURRENT" = "$AFTER" ] || fail "foreign_file=$TARGET"
   else [ "$CURRENT" = "$BEFORE" ] || fail "baseline=$TARGET";fi
  elif [ "$KIND" = new ];then
   if [ "$MODE" != --restore ] && [ "$MODE" != --restore-check ] && [ -e "$TARGET" ];then
    [ -d "$BACK/original" ] || fail "preexisting_project_file=$TARGET"
    verify "$TARGET" "$AFTER"
   fi
  else fail invalid_target_kind;fi
 done < "$ROOT/TARGETS.txt"
}
rw(){
 mount -uw /mnt/app || fail app_writable;RW_APP=1
 mount -uw /mnt/system || fail system_writable;RW_SYS=1
}
rollback_files(){
 OK=1
 while read KIND ID SRC TARGET BEFORE AFTER PERM;do
  [ "$KIND" = replace ] || continue
  # Backups were independently verified before any activation write.
  cp "$BACK/original/$ID" "$TARGET.full-rollback" && chmod "$PERM" "$TARGET.full-rollback" && mv "$TARGET.full-rollback" "$TARGET" || OK=0
  [ "$(digest "$TARGET")" = "$BEFORE" ] || OK=0
 done < "$ROOT/TARGETS.txt"
 [ "$OK" -eq 1 ]
}
finish(){
 RC=$?;trap - 0
 if [ -n "$STAGE" ] && [ -f "$STAGE" ] && [ ! -L "$STAGE" ] && [ "$(digest "$STAGE")" = "$STAGE_HASH" ];then
  rm -f "$STAGE" || { echo FULL_INSTALL=FAIL verified_stage_cleanup;RC=34; }
 fi
 if [ "$RC" -ne 0 ] && [ "$CHANGING" -eq 1 ];then
  if rollback_files;then echo FULL_INSTALL=ACTIVATION_FILES_ROLLED_BACK RESTART_REQUIRED=YES;else echo FULL_INSTALL=ROLLBACK_FAILED independently_review_backups=1;RC=31;fi
 fi
 if [ "$RW_SYS" -eq 1 ];then sync;mount -ur /mnt/system || { echo FULL_INSTALL=FAIL system_readonly;RC=32; };fi
 if [ "$RW_APP" -eq 1 ];then sync;mount -ur /mnt/app || { echo FULL_INSTALL=FAIL app_readonly;RC=33; };fi
 exit "$RC"
}
trap finish 0
trap 'exit 130' 1 2 15
case "$MODE" in --check|--apply|--restore-check|--restore) ;;*) fail usage_check_apply_restore-check_restore;;esac
for C in awk cp mv chmod mkdir rm mount sync cat grep pidin sleep;do command -v "$C" >/dev/null 2>&1 || fail "missing_command=$C";done
verify_kit
check_identity
if [ -d "$BACK" ];then backup_valid;else
 case "$MODE" in --restore*) fail missing_original_backup;;esac
 [ ! -e "$BASE" ] && [ ! -L "$BASE" ] || fail existing_project_tree_use_migration_not_fresh_install
fi
check_targets
if [ "$MODE" = --check ] || [ "$MODE" = --apply ];then
 INVENTORY=$(pidin ar) || fail process_inventory
 for NAME in direct-ts-remux most-ts-writer stream-player altscreen-capture mibr-seat-service;do
  if echo "$INVENTORY" | awk -v n="$NAME" '$1 ~ /^[0-9]+$/ {e=$2;sub(/^.*\//,"",e);if(e==n)f=1} END{exit !f}';then fail "active_project_process=$NAME";fi
 done
 for F in /mnt/app/root/mibr-carplay111-fps /mnt/app/root/mibr-direct-output-fps /mnt/app/root/mibr-alt111-keyframe-policy.enabled /mnt/app/root/mibr-isotx2-gate-disable;do
  [ ! -e "$F" ] || fail "foreign_override=$F"
 done
 /armle/sbin/pfctl -n -f "$ROOT/payload/pf.conf" && /armle/sbin/pfctl -n -f "$ROOT/payload/pf.mlan0.conf" || fail firewall_syntax
 (unset LD_PRELOAD
  export LD_LIBRARY_PATH=/ifs/jre/bin:/mnt/app/root/lib-target:/mnt/app/armle/lib:/mnt/app/armle/usr/lib:/mnt/app/armle/lib/dll:/mnt/app/eso/lib:/navigation:/navigation/lib
  /ifs/jre/bin/j9 -jcl:foun11 -verify -Xmx12m -Xbootclasspath/a:/ifs/lsd.jxe -Xbootclasspath/p:"$ROOT/payload/probe.jar:$ROOT/payload/menu.jar" de.mibr.hmi.MibrR13MigrationProbe --oem-link) || fail target_j9_probe
fi
case "$MODE" in
 --check) echo FULL_PREFLIGHT=PASS persistent_writes=0 fresh_final_stack=1 visible_effect=UNTESTED;exit 0;;
 --restore-check) echo FULL_RESTORE_CHECK=PASS original_backups_verified=1 persistent_writes=0;exit 0;;
 --restore)
  # Quiesce only this project's writer and broker before restoring activation.
  if [ -r /tmp/mibr-isotx2-gate.stats ] && grep -q '^loaded=1$' /tmp/mibr-isotx2-gate.stats;then
   STOP=$BASE/scripts/direct_ts_auto_stop.sh
   EXPECTED=$(awk -v f="$STOP" '$4==f {print $6}' "$ROOT/TARGETS.txt")
   verify "$STOP" "$EXPECTED"
   /bin/ksh "$STOP" || fail writer_quiescence
  fi
  INVENTORY=$(pidin ar) || fail process_inventory
  PIDS=$(echo "$INVENTORY" | awk -v p="$BASE/harman-r13/bin/mibr-seat-service" '$1 ~ /^[0-9]+$/ && $2==p {print $1}')
  case "$PIDS" in *[!0-9]*) fail ambiguous_owned_broker;;esac
  if [ -n "$PIDS" ];then
   [ "$PIDS" -gt 1 ] || fail broker_pid
   kill -TERM "$PIDS" || fail broker_stop
   N=0;while kill -0 "$PIDS" 2>/dev/null;do N=$((N+1));[ "$N" -lt 30 ] || fail broker_stop_timeout;sleep 1;done
  fi
  INVENTORY=$(pidin ar) || fail process_inventory
  for NAME in direct-ts-remux most-ts-writer stream-player altscreen-capture;do
   if echo "$INVENTORY" | awk -v n="$NAME" '$1 ~ /^[0-9]+$/ {e=$2;sub(/^.*\//,"",e);if(e==n)f=1} END{exit !f}';then fail "writer_still_running=$NAME";fi
  done
  rw
  CHANGING=1
  rollback_files || fail restore_write_or_readback
  CHANGING=0
  # Retain project data/backups inert. OEM startup and classpath are restored.
  rm -f "$BASE/config/autostart.enabled" "$BASE/harman-r13/enabled" || fail disable_markers
  echo FULL_RESTORE=PASS original_activation_files_verified=1 RESTART_REQUIRED=YES
  echo 'Project files/preferences retained inert; original M.I.B./NavActiveIgnore preserved. Verify stock behavior after restart.'
  exit 0;;
esac
"$ROOT/payload/owner-probe" || fail target_owner_lock_probe
# Save all before-images to writable external media BEFORE production writes.
mkdir -p "$MEDIA_BACK" || fail media_not_writable
while read KIND ID SRC TARGET BEFORE AFTER PERM;do
 [ "$KIND" = replace ] || continue
 if [ -e "$MEDIA_BACK/$ID" ];then verify "$MEDIA_BACK/$ID" "$BEFORE";else
  verify "$TARGET" "$BEFORE"
  cp "$TARGET" "$MEDIA_BACK/$ID" || fail external_backup
  verify "$MEDIA_BACK/$ID" "$BEFORE"
 fi
done < "$ROOT/TARGETS.txt"
sync
rw
if [ ! -d "$BACK" ];then
 mkdir -p "$BACK/original" || fail internal_backup_directory
 while read KIND ID SRC TARGET BEFORE AFTER PERM;do
  [ "$KIND" = replace ] || continue
  cp "$MEDIA_BACK/$ID" "$BACK/original/$ID" || fail internal_backup
  verify "$BACK/original/$ID" "$BEFORE"
 done < "$ROOT/TARGETS.txt"
 digest "$ROOT/TARGETS.txt" > "$BACK/targets.sha256" || fail backup_record
fi
backup_valid
# Keep a self-contained restore route on the application filesystem too.
while read HASH FILE;do atomic "$ROOT/$FILE" "$BACK/kit/$FILE" "$HASH" 755;done < "$ROOT/KIT.sha256"
atomic "$ROOT/KIT.sha256" "$BACK/kit/KIT.sha256" "$(digest "$ROOT/KIT.sha256")" 644
# Stage final project files first; original activation files remain intact.
while read KIND ID SRC TARGET BEFORE AFTER PERM;do
 [ "$KIND" = new ] || continue
 atomic "$ROOT/$SRC" "$TARGET" "$AFTER" "$PERM"
done < "$ROOT/TARGETS.txt"
CHANGING=1
while read KIND ID SRC TARGET BEFORE AFTER PERM;do
 [ "$KIND" = replace ] || continue
 atomic "$ROOT/$SRC" "$TARGET" "$AFTER" "$PERM"
done < "$ROOT/TARGETS.txt"
CHANGING=0
echo FULL_INSTALL=FINAL_STACK_FILES_VERIFIED RESTART_REQUIRED=YES visible_effect=UNTESTED
echo 'Normal restart, fresh wired CarPlay session, then independent video/menu/zoom/stock-return checks. No reboot was performed.'
