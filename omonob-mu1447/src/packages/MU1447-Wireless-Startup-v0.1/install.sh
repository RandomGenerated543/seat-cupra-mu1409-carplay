#!/bin/ksh
# One-file startup wake correction for the installed Runtime v0.1.
case "$0" in */*) KIT=$(cd "${0%/*}" && pwd);;*) KIT=$PWD;;esac
ACTION=${1:---check}
B=/mnt/app/.mu1447-wireless-startup-v01
S=/ramdisk/mu1447-startup-$$
LOCK=/ramdisk/mu1447-startup-install.lock
T=/mnt/app/eso/hmi/lsd/jars/CarPlayWireless-CP-55915411.jar
STAGED=0;LOCKED=0;WRITING=0
cleanup(){ [ "$STAGED" = 0 ] || rm -rf "$S";[ "$LOCKED" = 0 ] || rm -f "$LOCK";:; }
trap cleanup 0
file_hash(){ "$S/file-check" --hash "$1"; }
same(){ x=$(file_hash "$1") && y=$(file_hash "$2") && [ "$x" = "$y" ]; }
rollback(){
 cp -p "$B/CP.jar" "$T.mu1447-startup-restore" && same "$B/CP.jar" "$T.mu1447-startup-restore" &&
 mv -f "$T.mu1447-startup-restore" "$T" && same "$B/CP.jar" "$T" && sync
}
fail(){
 echo "MU1447_STARTUP=FAIL reason=$1"
 if [ "$WRITING" = 1 ];then
  WRITING=0
  if rollback;then echo 'MU1447_STARTUP_AUTO_ROLLBACK=PASS restart_manually=1';else echo 'MU1447_STARTUP_AUTO_ROLLBACK=FAIL retain_backup';fi
 fi
 exit 1
}
trap 'fail interrupted' 1 2 15
[ "$#" -le 1 ] || fail arguments
case "$ACTION" in --check|--apply|--restore|--status);;*)fail use_check_apply_restore_status;;esac
for cmd in cp chmod mkdir rm mv cat mount sync awk;do command -v "$cmd" >/dev/null 2>&1 || fail missing_command_$cmd;done
[ ! -e "$S" ] && mkdir "$S" || fail stage
STAGED=1
cp "$KIT/file-check" "$S/file-check" && chmod 755 "$S/file-check" || fail checker
"$S/file-check" --self-test && "$S/file-check" --manifest "$KIT" "$KIT/SHA256SUMS.txt" || fail package_integrity
(umask 077;set -C;: > "$LOCK") 2>/dev/null || fail management_lock
LOCKED=1
[ ! -L "$B" ] && [ ! -L "$T" ] && [ -f "$T" ] || fail target_type
if [ -e "$B" ];then
 [ -f "$B/complete" ] && "$S/file-check" --manifest "$B" "$B/SEAL.sha256" && [ "$(file_hash "$B/CP.jar")" = "$(cat "$KIT/BEFORE.sha256")" ] || fail backup_integrity
fi
before=$(cat "$KIT/BEFORE.sha256");after=$(file_hash "$KIT/payload/CP.jar");live=$(file_hash "$T") || fail current_archive
if [ "$ACTION" = --restore ];then
 [ -d "$B" ] || fail no_backup
 [ "$live" = "$before" ] || [ "$live" = "$after" ] || fail later_edit
 mount -uw /mnt/app || fail writable_volume
 rollback || fail restore
 echo 'MU1447_STARTUP=RESTORED runtime_v01_retained=1 restart_manually=1'
 exit 0
fi
[ "$live" = "$before" ] || [ "$live" = "$after" ] || fail CP_archive_not_recognized
if [ "$live" = "$after" ];then
 [ -d "$B" ] || fail installed_without_backup
 echo 'MU1447_STARTUP=ALREADY_INSTALLED';exit 0
fi
[ "$ACTION" != --status ] || { echo 'MU1447_STARTUP=ORIGINAL';exit 0; }
[ "$(cat /mnt/app/carplaymaps/PROFILE)" = MU1447/790 ] || fail wrong_profile
[ "$(file_hash /ifs/lsd.jxe)" = "$(cat "$KIT/JXE.sha256")" ] || fail wrong_firmware
while read -r wanted target;do
 [ ! -L "$target" ] && [ "$(file_hash "$target")" = "$wanted" ] || fail Runtime_v01_dependency_changed
done < "$KIT/DEPENDENCIES.tsv"
for part in /ramdisk /mnt/app;do
 free=$("$S/file-check" --free-bytes "$part") || fail free_space
 awk -v f="$free" 'BEGIN {exit !(f+0>=1000000)}' || fail insufficient_space
done
cp "$KIT/payload/CP.jar" "$S/CP.jar" || fail stage_CP
JARS="$KIT/payload/link-check.jar:$S/CP.jar:/mnt/app/eso/hmi/lsd/jars/CarPlayWireless-Touch-55915411.jar:/mnt/app/eso/hmi/lsd/jars/WirelessMapsBootstrap.jar:/mnt/app/eso/hmi/lsd/jars/VCMenu.jar:/mnt/app/eso/hmi/lsd/jars/CarPlayWireless-SI-55915411.jar"
(
 unset LD_PRELOAD
 export LD_LIBRARY_PATH=/ifs/jre/bin:/mnt/app/root/lib-target:/mnt/app/armle/lib:/mnt/app/armle/usr/lib:/mnt/app/armle/lib/dll:/mnt/app/eso/lib:/navigation:/navigation/lib
 /ifs/jre/bin/j9 -jcl:foun11 -verify -Xmx16m -Xbootclasspath/a:/ifs/lsd.jxe "-Xbootclasspath/p:$JARS" RuntimeLinkCheck
) || fail java_linkage
if [ "$ACTION" = --check ];then echo 'MU1447_STARTUP_CHECK=PASS persistent_writes=0';exit 0;fi
mount -uw /mnt/app || fail writable_volume
if [ ! -d "$B" ];then
 mkdir "$B" || fail backup_create
 cp -p "$T" "$B/CP.jar" && same "$T" "$B/CP.jar" || fail backup_copy
 echo "$(file_hash "$B/CP.jar")  CP.jar" > "$B/SEAL.sha256"
 "$S/file-check" --manifest "$B" "$B/SEAL.sha256" || fail backup_seal
 : > "$B/complete"
 sync
fi
WRITING=1
[ ! -e "$T.mu1447-startup-new" ] || fail existing_stage
cp "$KIT/payload/CP.jar" "$T.mu1447-startup-new" && chmod 644 "$T.mu1447-startup-new" &&
same "$KIT/payload/CP.jar" "$T.mu1447-startup-new" && mv -f "$T.mu1447-startup-new" "$T" &&
same "$KIT/payload/CP.jar" "$T" || fail replace_CP
WRITING=0
sync
echo 'MU1447_STARTUP=INSTALLED persistent=1 restart_manually=1'
