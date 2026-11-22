#!/bin/ksh
# One persistent MU1447 add-on transaction. No service starts or radio changes.
case "$0" in */*) KIT=$(cd "${0%/*}" && pwd) ;; *) KIT=$PWD ;; esac
ACTION=${1:---status}
BACKUP=/mnt/app/.mu1447-native-wireless-v1-backup
S=/ramdisk/mu1447-wireless-stage-$$
CHECK=/ramdisk/mu1447-wireless-check-$$
LOCK=/ramdisk/mu1447-native-wireless.lock
LOCKED=0; STAGED=0; WRITING=0; RESTORING=0
P=$KIT/payload
restore_files(){
 for category in activation remaining;do
  while read -r before path id;do
   case "$path" in /mnt/system/etc/eso/production/connectivity.json|/mnt/app/eso/hmi/lsd/lsd.sh|/mnt/app/eso/hmi/lsd/config/bundles.properties) kind=activation;; *)kind=remaining;;esac
   [ "$kind" = "$category" ] || continue
   if [ "$before" = MISSING ];then rm -f "$path" || return 1;
   else
    cp -p "$BACKUP/files/$id" "$path.mu1447-restore" || return 1
    same "$BACKUP/files/$id" "$path.mu1447-restore" || return 1
    mv -f "$path.mu1447-restore" "$path" || return 1
   fi
   current_matches "$before" "$path" || return 1
   rm -f "$path.mu1447-new" || return 1
  done < "$BACKUP/before.tsv"
 done
 sync
}
fail(){
 echo "MU1447_WIRELESS=FAIL reason=$1"
 if [ "$WRITING" = 1 ] && [ "$RESTORING" = 0 ];then
  RESTORING=1
  if restore_files;then echo 'MU1447_WIRELESS_AUTO_ROLLBACK=PASS restart_manually=1';
  else echo 'MU1447_WIRELESS_AUTO_ROLLBACK=FAIL preserve_backup_do_not_retry';fi
 fi
 exit 1
}
cleanup(){
 rm -f "$CHECK" "$CHECK.seal"
 [ "$STAGED" = 0 ] || rm -rf "$S"
 [ "$LOCKED" = 0 ] || rm -f "$LOCK"
 :
}
trap cleanup 0
trap 'fail interrupted_preserve_backup' 1 2 15
[ "$#" -le 1 ] || fail too_many_arguments
case "$ACTION" in --check|--apply|--restore|--status|--recover-backup) ;; *) fail use_check_apply_restore_status_or_recover_backup ;; esac
for tool in cp chmod cat ls mkdir mv rm awk grep mount sync wc; do command -v "$tool" >/dev/null 2>&1 || fail missing_command_$tool; done
cp "$KIT/file-check" "$CHECK" || fail stage_checker
chmod 755 "$CHECK" || fail checker_permissions
file_hash(){ "$CHECK" --hash "$1"; }
same(){ a=$(file_hash "$1") && b=$(file_hash "$2") && [ "$a" = "$b" ]; }
"$CHECK" --self-test || fail native_checker_self_test
"$CHECK" --manifest "$KIT" "$KIT/SHA256SUMS.txt" || fail package_integrity
safe_target(){
 case "$1" in *..*|*' '*|*'|'*)return 1;; esac
 case "$1" in
 /mnt/ota/*|/mnt/app/carplaymaps/*|/mnt/app/eso/hmi/lsd/lsd.sh|/mnt/app/eso/hmi/lsd/config/bundles.properties|/mnt/app/eso/hmi/lsd/jars/*.jar|/mnt/persist/*|/mnt/system/etc/eso/production/connectivity.json) ;;
 *)return 1;; esac
 ancestor=$1
 while [ "$ancestor" != / ] && [ -n "$ancestor" ]; do
  [ ! -L "$ancestor" ] || return 1
  ancestor=${ancestor%/*}
 done
}
for keyfile in "$BACKUP" "$S";do [ ! -L "$keyfile" ] || fail symlink_directory;done
validate_backup(){
 [ -f "$BACKUP/complete" ] && [ -s "$BACKUP/before.tsv" ] && [ -s "$BACKUP/after.tsv" ] || fail incomplete_backup_preserve_files
 "$CHECK" --manifest "$BACKUP" "$BACKUP/SEAL.sha256" || fail backup_integrity
 same "$KIT/targets.tsv" "$BACKUP/targets.tsv" || fail backup_different_package
 while read -r id path mode source;do
  safe_target "$path" || fail backup_scope
 done < "$BACKUP/targets.tsv"
}
current_matches(){
 wanted=$1;path=$2
 if [ "$wanted" = MISSING ];then [ ! -e "$path" ] && [ ! -L "$path" ];
 else [ -f "$path" ] && [ "$(file_hash "$path")" = "$wanted" ];fi
}
check_receipt(){
 while read -r wanted path;do
  safe_target "$path" || return 1
  current_matches "$wanted" "$path" || return 1
 done < "$BACKUP/after.tsv"
}
if [ -d "$BACKUP" ] && [ "$ACTION" != --recover-backup ];then validate_backup;fi
if [ "$ACTION" = --status ];then
 if [ -d "$BACKUP" ];then
  if check_receipt;then echo 'MU1447_WIRELESS_STATUS=INSTALLED file_receipt=PASS visible=OPERATOR_CHECK_REQUIRED';
  else echo 'MU1447_WIRELESS_STATUS=CHANGED_OR_RESTORED keep_backup=1';fi
 else echo 'MU1447_WIRELESS_STATUS=NOT_INSTALLED_BY_THIS_PACKAGE';fi
 exit 0
fi
(umask 077;set -C; : > "$LOCK") 2>/dev/null || fail management_lock_exists
LOCKED=1
[ ! -e /dev/ipod0 ] && [ ! -e /dev/shmem/wcp_cp_session ] || fail disconnect_usb_and_wireless_carplay_first
if [ "$ACTION" = --recover-backup ];then
 # Recovery is only for a pre-write backup whose completion marker was never set.
 [ -d "$BACKUP" ] && [ ! -e "$BACKUP/complete" ] || fail not_an_unfinished_backup
 [ ! -e "$BACKUP.preseal-rc12" ] && [ ! -L "$BACKUP.preseal-rc12" ] || fail saved_unfinished_backup_exists
 same "$KIT/targets.tsv" "$BACKUP/targets.tsv" || fail recovery_different_targets
 # Normalize only the legacy separator; the native verifier still checks all
 # original saved hashes, safe relative paths, file types and duplicate entries.
 awk 'NF != 2 || length($1) != 64 || $1 ~ /[^0-9a-f]/ {bad=1;next} {print $1 "  " $2} END {exit bad}' "$BACKUP/SEAL.sha256" > "$CHECK.seal" || fail recovery_seal_format
 "$CHECK" --manifest "$BACKUP" "$CHECK.seal" || fail recovery_backup_integrity
 awk 'NR==FNR {paths[$1]=$2;total++;next} {rows++;if(NF!=3 || !($3 in paths) || paths[$3]!=$2 || seen[$3]++)bad=1} END {exit (bad || rows!=total)}' "$KIT/targets.tsv" "$BACKUP/before.tsv" || fail recovery_baseline_scope
 while read -r before path id;do
  safe_target "$path" || fail recovery_path
  current_matches "$before" "$path" || fail recovery_live_file_changed_$id
  if [ "$before" != MISSING ];then
   current_matches "$before" "$BACKUP/files/$id" || fail recovery_saved_file_changed_$id
  fi
 done < "$BACKUP/before.tsv"
 mount -uw /mnt/app || fail recovery_mount
 mv "$BACKUP" "$BACKUP.preseal-rc12" || fail recovery_preserve_backup
 sync
 echo 'MU1447_BACKUP_RECOVERY=PASS live_baseline_verified=1 old_backup_preserved=1'
 exit 0
fi
if [ "$ACTION" = --restore ];then
 [ -d "$BACKUP" ] || fail no_backup
 # Each tracked file must still be either its saved baseline or this transaction's
 # planned result. Preserve unexpected later edits rather than overwrite them.
 while read -r before path id;do
  after=$(awk -v p="$path" '$2==p{print $1}' "$BACKUP/after.tsv")
  current_matches "$before" "$path" || current_matches "$after" "$path" || fail changed_since_install_$id
 done < "$BACKUP/before.tsv"
 for part in /mnt/app /mnt/ota /mnt/persist /mnt/system;do mount -uw "$part" || fail remount_$part;done
 RESTORING=1
 restore_files || fail restore_files
 echo 'MU1447_WIRELESS=RESTORED wired_baseline_verified=1 restart_manually=1 pairing_store_retained=1'
 exit 0
fi
if [ -d "$BACKUP" ];then
 if check_receipt;then
  echo 'MU1447_WIRELESS=ALREADY_INSTALLED file_receipt=PASS visible=OPERATOR_CHECK_REQUIRED';exit 0
 fi
 fail previous_transaction_requires_restore
fi
echo 'MU1447_WIRELESS=CHECKING_EXACT_NATIVE_INPUTS'
while read -r wanted path;do
 [ "$(file_hash "$path")" = "$wanted" ] || fail native_input_mismatch_${path##*/}
 echo "NATIVE_INPUT=PASS file=${path##*/}"
done < "$KIT/native-baselines.tsv"
CORE=$(file_hash /mnt/app/carplaymaps/core.so) || fail missing_wired_core
case "$CORE" in af791f8b63712a2986735d23d36b52a46b448789b3aa16717dcc450e469042b0|f97db08d50d05a75e3a98f5057f4dc9ff67cce95fded6b297755b4e3428e83b9) ;; *)fail current_wired_layout_not_supported;;esac
same /mnt/app/carplaymaps/dio_manager.wrapper.sh "$P/wired-launcher-reference.sh" || fail runtime_launcher_mismatch
same /mnt/app/eso/bin/apps/dio_manager "$P/wired-launcher-reference.sh" || fail active_launcher_mismatch
same /mnt/app/carplaymaps/libmu1447-wired-display.so "$P/wired-zoom-reference.so" || fail working_zoom_library_mismatch
same /mnt/app/eso/hmi/lsd/jars/VCMenu.jar "$P/VCMenu-reference.jar" || fail public_rc7_menu_mismatch
same /mnt/system/etc/eso/production/connectivity.json "$P/connectivity-reference.json" || fail connectivity_has_other_changes
# Reject active older wireless classpaths rather than layering implementations.
grep -E 'CarPlayWireless|WirelessMapsBootstrap' /mnt/app/eso/hmi/lsd/lsd.sh >/dev/null 2>&1 && fail existing_wireless_classpath
# This unit's /ramdisk is only 20 MiB. Budget actual flat staging files,
# duplicate JAR aliases and generated configuration files, plus 8 MiB reserve.
# Persistent application volumes keep their independent conservative floor.
ram_stage=0
while read -r id target mode source;do
 case "$source" in
  MISSING) continue;;
  GENERATE_*)
   bytes=$(wc -c < "$target") || fail staging_size_$id
   bytes=$((bytes + 65536));;
  *) bytes=$(wc -c < "$P/$source") || fail staging_size_$id;;
 esac
 bytes=$(( ((bytes + 4095) / 4096) * 4096 ))
 ram_stage=$((ram_stage + bytes))
 case "$target" in *.jar) ram_stage=$((ram_stage + bytes));; esac
done < "$KIT/targets.tsv"
ram_required=$((ram_stage + 8388608))
for part in /ramdisk /mnt/app /mnt/ota;do
 free=$("$CHECK" --free-bytes "$part") || fail free_space_query
 case "$part" in /ramdisk) required=$ram_required;; *) required=30000000;; esac
 echo "SPACE_CHECK path=$part available_bytes=$free required_bytes=$required"
 awk -v available="$free" -v needed="$required" 'BEGIN { if (available !~ /^[0-9]+$/ || needed !~ /^[0-9]+$/) exit 1; exit !(available + 0 >= needed + 0) }' || fail insufficient_free_space_$part
done
[ ! -e "$S" ] || fail ram_stage_exists
mkdir "$S" || fail ram_stage_create
STAGED=1
: > "$S/plan.tsv"
while read -r id target mode source;do
 safe_target "$target" || fail target_scope_$id
 case "$source" in
  MISSING) echo "MISSING $target" >> "$S/plan.tsv";continue;;
  GENERATE_LSD) sh "$P/merge-wireless.sh" lsd "$target" "$S/$id" || fail classpath_merge;;
  GENERATE_BUNDLES) sh "$P/merge-wireless.sh" bundles "$target" "$S/$id" || fail bundle_merge;;
  GENERATE_CONNECTIVITY) cp "$P/connectivity-wireless.json" "$S/$id" || fail connectivity_stage;;
  *) cp "$P/$source" "$S/$id" || fail stage_$id;same "$P/$source" "$S/$id" || fail stage_compare_$id;;
 esac
 chmod "$mode" "$S/$id" || fail stage_permissions_$id
 case "$target" in *.sh) /bin/ksh -n "$S/$id" || fail staged_shell_syntax_$id;; esac
 echo "$(file_hash "$S/$id") $target" >> "$S/plan.tsv"
done < "$KIT/targets.tsv"
# Link in a separate VM with no class initialization or activator invocation.
JARS="$P/link-check.jar"
while read -r id target mode source;do
 case "$target" in /mnt/app/eso/hmi/lsd/jars/*.jar) cp "$S/$id" "$S/$id.jar" || fail java_stage_alias; JARS="$JARS:$S/$id.jar";; esac
done < "$KIT/targets.tsv"
echo 'MU1447_WIRELESS=CHECKING_JAVA_LINKAGE'
(
 unset LD_PRELOAD
 export LD_LIBRARY_PATH=/ifs/jre/bin:/mnt/app/root/lib-target:/mnt/app/armle/lib:/mnt/app/armle/usr/lib:/mnt/app/armle/lib/dll:/mnt/app/eso/lib:/navigation:/navigation/lib
 /ifs/jre/bin/j9 -jcl:foun11 -verify -Xmx16m -Xbootclasspath/a:/ifs/lsd.jxe "-Xbootclasspath/p:$JARS" Wireless1447LinkCheck
) || fail java_link_check
if [ "$ACTION" = --check ];then
 echo 'MU1447_WIRELESS_CHECK=PASS persistent_writes=0 pairing=UNTESTED video_touch_audio=UNTESTED'
 exit 0
fi
for part in /mnt/app /mnt/ota /mnt/persist /mnt/system;do mount -uw "$part" || fail remount_$part;done
mkdir "$BACKUP" || fail backup_directory
mkdir "$BACKUP/files" || fail backup_files_directory
cp "$KIT/targets.tsv" "$BACKUP/targets.tsv" || fail backup_targets
cp "$S/plan.tsv" "$BACKUP/after.tsv" || fail backup_plan
: > "$BACKUP/before.tsv"
: > "$BACKUP/SEAL.sha256"
while read -r id target mode source;do
 if [ -e "$target" ];then
  [ -f "$target" ] && [ ! -L "$target" ] || fail baseline_not_regular_$id
  cp -p "$target" "$BACKUP/files/$id" || fail baseline_copy_$id
  same "$target" "$BACKUP/files/$id" || fail baseline_verify_$id
  wanted=$(file_hash "$target") || fail baseline_hash_$id
  echo "$wanted $target $id" >> "$BACKUP/before.tsv"
  echo "$wanted  files/$id" >> "$BACKUP/SEAL.sha256"
 else echo "MISSING $target $id" >> "$BACKUP/before.tsv";fi
done < "$KIT/targets.tsv"
for metadata in targets.tsv before.tsv after.tsv;do echo "$(file_hash "$BACKUP/$metadata")  $metadata" >> "$BACKUP/SEAL.sha256";done
"$CHECK" --manifest "$BACKUP" "$BACKUP/SEAL.sha256" || fail baseline_seal
: > "$BACKUP/complete"
sync
WRITING=1
while read -r id target mode source;do
 if [ "$source" = MISSING ];then rm -f "$target" || fail remove_disable_flag_$id;
 else
  mkdir -p "${target%/*}" || fail parent_directory_$id
  [ ! -e "$target.mu1447-new" ] || fail pending_stage_$id
  cp "$S/$id" "$target.mu1447-new" || fail install_copy_$id
  chmod "$mode" "$target.mu1447-new" || fail install_mode_$id
  same "$S/$id" "$target.mu1447-new" || fail install_readback_$id
  mv -f "$target.mu1447-new" "$target" || fail install_activate_$id
 fi
done < "$KIT/targets.tsv"
check_receipt || fail final_receipt_mismatch
/mnt/app/carplaymaps/wireless-receiver-exec --transport-status || fail receiver_library_pair_guard
WRITING=0
sync
echo 'MU1447_WIRELESS=INSTALLED persistent=1 manual_restart_required=1 visible=UNTESTED'
echo 'Firmware, native BT/connection-manager, working wired core and media startup retained.'
