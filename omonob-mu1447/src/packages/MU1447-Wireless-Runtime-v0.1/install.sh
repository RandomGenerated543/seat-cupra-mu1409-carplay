#!/bin/ksh
# Runtime-only MU1447 transaction. No receiver, Wi-Fi, settings or OEM binary patch.
case "$0" in */*) KIT=$(cd "${0%/*}" && pwd);;*) KIT=$PWD;;esac
ACTION=${1:---check}
B=/mnt/app/.mu1447-wireless-runtime-v01
S=/ramdisk/mu1447-runtime-$$
LOCK=/ramdisk/mu1447-runtime-install.lock
LOCKED=0;STAGED=0;WRITING=0
cleanup(){ [ "$STAGED" = 0 ] || rm -rf "$S";[ "$LOCKED" = 0 ] || rm -f "$LOCK";:; }
trap cleanup 0
file_hash(){ "$S/file-check" --hash "$1"; }
same(){ a=$(file_hash "$1") && b=$(file_hash "$2") && [ "$a" = "$b" ]; }
select_target(){
 ID=$1
 case "$ID" in
  001) TARGET=/mnt/app/eso/hmi/lsd/jars/CarPlayWireless-CP-55915411.jar;MODE=644;SOURCE=CP.jar;;
  002) TARGET=/mnt/app/eso/hmi/lsd/jars/CarPlayWireless-Touch-55915411.jar;MODE=644;SOURCE=Touch.jar;;
  003) TARGET=/mnt/app/eso/hmi/lsd/jars/WirelessMapsBootstrap.jar;MODE=644;SOURCE=Bootstrap.jar;;
  004) TARGET=/mnt/ota/wcp_autostart.sh;MODE=755;SOURCE=wcp_autostart.sh;;
  005) TARGET=/mnt/ota/wcp_ctl.sh;MODE=755;SOURCE=wcp_ctl.sh;;
  006) TARGET=/mnt/ota/mu1447-runtime-guard;MODE=755;SOURCE=mu1447-runtime-guard;;
  *) return 1;;
 esac
}
state_of(){ [ ! -L "$1" ] || return 1;if [ -f "$1" ];then file_hash "$1";elif [ ! -e "$1" ];then echo MISSING;else return 1;fi; }
expected(){ awk -v id="$1" '$1==id {print $2}' "$2"; }
rollback(){
 for id in 001 002 003 004 005 006;do
  select_target "$id" || return 1
  wanted=$(expected "$id" "$B/before.tsv")
  if [ "$wanted" = MISSING ];then rm -f "$TARGET" || return 1
  else
   cp -p "$B/$id" "$TARGET.mu1447-runtime-restore" &&
   same "$B/$id" "$TARGET.mu1447-runtime-restore" &&
   mv -f "$TARGET.mu1447-runtime-restore" "$TARGET" || return 1
  fi
  [ "$(state_of "$TARGET")" = "$wanted" ] || return 1
 done
 sync
}
fail(){
 echo "MU1447_RUNTIME=FAIL reason=$1"
 if [ "$WRITING" = 1 ];then
  WRITING=0
  if rollback;then echo 'MU1447_RUNTIME_AUTO_ROLLBACK=PASS restart_manually=1';else echo 'MU1447_RUNTIME_AUTO_ROLLBACK=FAIL retain_backup';fi
 fi
 exit 1
}
trap 'fail interrupted' 1 2 15
[ "$#" -le 1 ] || fail arguments
case "$ACTION" in --check|--apply|--restore|--status);;*)fail use_check_apply_restore_status;;esac
for cmd in cp mkdir chmod rm mv cat mount sync awk;do command -v "$cmd" >/dev/null 2>&1 || fail missing_command_$cmd;done
[ ! -e "$S" ] && mkdir "$S" || fail ram_stage
STAGED=1
cp "$KIT/file-check" "$S/file-check" && chmod 755 "$S/file-check" || fail stage_checker
"$S/file-check" --self-test && "$S/file-check" --manifest "$KIT" "$KIT/SHA256SUMS.txt" || fail package_integrity
(umask 077;set -C;: > "$LOCK") 2>/dev/null || fail management_lock
LOCKED=1
[ ! -L "$B" ] || fail backup_symlink
if [ -e "$B" ];then
 [ -f "$B/complete" ] && "$S/file-check" --manifest "$B" "$B/SEAL.sha256" || fail incomplete_or_changed_backup
 same "$B/after.tsv" "$KIT/AFTER.tsv" && same "$B/before.tsv" "$KIT/BEFORE.tsv" || fail backup_version
fi
if [ "$ACTION" = --restore ];then
 [ -d "$B" ] || fail no_backup
 for id in 001 002 003 004 005 006;do
  select_target "$id" || fail target
  live=$(state_of "$TARGET") || fail invalid_target_$id
  [ "$live" = "$(expected "$id" "$B/before.tsv")" ] || [ "$live" = "$(expected "$id" "$B/after.tsv")" ] || fail later_edit_$id
 done
 mount -uw /mnt/app && mount -uw /mnt/ota || fail writable_volumes
 rollback || fail restore
 echo 'MU1447_RUNTIME=RESTORED restart_manually=1 network_and_layout_preserved=1'
 exit 0
fi
matched=1;original=1
for id in 001 002 003 004 005 006;do
 select_target "$id" || fail target
 live=$(state_of "$TARGET") || fail invalid_target_$id
 [ "$live" = "$(expected "$id" "$KIT/AFTER.tsv")" ] || matched=0
 [ "$live" = "$(expected "$id" "$KIT/BEFORE.tsv")" ] || original=0
done
if [ "$matched" = 1 ];then
 [ -d "$B" ] || fail installed_without_rollback_backup
 echo 'MU1447_RUNTIME=ALREADY_INSTALLED restart_required_after_apply=1';exit 0
fi
[ "$original" = 1 ] || fail installed_runtime_not_recognized
[ "$ACTION" != --status ] || { echo 'MU1447_RUNTIME=ORIGINAL';exit 0; }
[ "$(cat /mnt/app/carplaymaps/PROFILE)" = MU1447/790 ] || fail wrong_profile
[ "$(file_hash /ifs/lsd.jxe)" = "$(cat "$KIT/JXE.sha256")" ] || fail wrong_HMI_firmware
# Accept either original receiver or the two delivered layout variants; never replace them.
rh=$(file_hash /mnt/ota/wcp_receiver) || fail receiver_missing
gh=$(file_hash /mnt/app/carplaymaps/wireless-receiver-exec) || fail receiver_guard_missing
awk -v r="$rh" -v g="$gh" '$1==r && $2==g {found=1} END {exit !found}' "$KIT/RECEIVERS.tsv" || fail receiver_version_unknown
[ "$(file_hash /mnt/app/carplaymaps/libomonob-wireless-maps.so)" = "$(cat "$KIT/MAPS.sha256")" ] || fail map_helper_changed
for part in /ramdisk /mnt/app /mnt/ota;do
 free=$("$S/file-check" --free-bytes "$part") || fail free_space
 case "$part" in /ramdisk) need=1500000;;*) need=1500000;;esac
 awk -v f="$free" -v n="$need" 'BEGIN {exit !(f+0>=n+0)}' || fail insufficient_space
 done
cp "$KIT/payload/mu1447-runtime-guard" "$S/runtime-guard" && chmod 755 "$S/runtime-guard" || fail stage_guard
"$S/runtime-guard" --self-test && "$S/runtime-guard" --inspect || fail receiver_observation_requires_running_compatible_receiver
for name in CP Touch Bootstrap;do cp "$KIT/payload/$name.jar" "$S/$name.jar" || fail java_stage;done
JARS="$KIT/payload/link-check.jar:$S/CP.jar:$S/Touch.jar:$S/Bootstrap.jar:/mnt/app/eso/hmi/lsd/jars/VCMenu.jar:/mnt/app/eso/hmi/lsd/jars/CarPlayWireless-SI-55915411.jar"
(
 unset LD_PRELOAD
 export LD_LIBRARY_PATH=/ifs/jre/bin:/mnt/app/root/lib-target:/mnt/app/armle/lib:/mnt/app/armle/usr/lib:/mnt/app/armle/lib/dll:/mnt/app/eso/lib:/navigation:/navigation/lib
 /ifs/jre/bin/j9 -jcl:foun11 -verify -Xmx16m -Xbootclasspath/a:/ifs/lsd.jxe "-Xbootclasspath/p:$JARS" RuntimeLinkCheck
) || fail java_linkage
if [ "$ACTION" = --check ];then echo 'MU1447_RUNTIME_CHECK=PASS persistent_writes=0 car_behavior=UNTESTED';exit 0;fi
mount -uw /mnt/app && mount -uw /mnt/ota || fail writable_volumes
if [ ! -d "$B" ];then
 mkdir "$B" || fail backup_create
 : > "$B/SEAL.sha256"
 cp "$KIT/BEFORE.tsv" "$B/before.tsv" && cp "$KIT/AFTER.tsv" "$B/after.tsv" || fail backup_metadata
 for id in 001 002 003 004 005 006;do
  select_target "$id" || fail target
  if [ "$(expected "$id" "$KIT/BEFORE.tsv")" = MISSING ];then : > "$B/$id";else cp -p "$TARGET" "$B/$id" && same "$TARGET" "$B/$id" || fail backup_copy_$id;fi
  echo "$(file_hash "$B/$id")  $id" >> "$B/SEAL.sha256"
 done
 for name in before.tsv after.tsv;do echo "$(file_hash "$B/$name")  $name" >> "$B/SEAL.sha256";done
 "$S/file-check" --manifest "$B" "$B/SEAL.sha256" || fail backup_integrity
 : > "$B/complete"
 sync
fi
WRITING=1
for id in 001 002 003 004 005 006;do
 select_target "$id" || fail target
 [ ! -e "$TARGET.mu1447-runtime-new" ] || fail existing_stage_$id
 cp "$KIT/payload/$SOURCE" "$TARGET.mu1447-runtime-new" &&
 chmod "$MODE" "$TARGET.mu1447-runtime-new" &&
 same "$KIT/payload/$SOURCE" "$TARGET.mu1447-runtime-new" &&
 mv -f "$TARGET.mu1447-runtime-new" "$TARGET" || fail install_$id
 [ "$(state_of "$TARGET")" = "$(expected "$id" "$KIT/AFTER.tsv")" ] || fail readback_$id
done
WRITING=0
sync
echo 'MU1447_RUNTIME=INSTALLED persistent=1 restart_manually=1 network_and_layout_preserved=1'
