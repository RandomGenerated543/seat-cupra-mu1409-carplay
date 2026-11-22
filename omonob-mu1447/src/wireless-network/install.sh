#!/bin/ksh
# Two-script network-only update. No receiver, Java, driver or persistent PF edits.
case "$0" in */*) KIT=$(cd "${0%/*}" && pwd);; *) KIT=$PWD;;esac
ACTION=${1:---check}
B=/mnt/app/.mu1447-wireless-network-v01
S=/ramdisk/mu1447-network-$$
LOCK=/ramdisk/mu1447-network.lock
LOCKED=0;WRITING=0;STAGED=0
cleanup(){ [ "$STAGED" = 0 ] || rm -rf "$S";[ "$LOCKED" = 0 ] || rm -f "$LOCK";:; }
trap cleanup 0
file_hash(){ "$S/file-check" --hash "$1"; }
same(){ a=$(file_hash "$1") && b=$(file_hash "$2") && [ "$a" = "$b" ]; }
rollback(){
 for name in wcp_pf.sh wcp_pfwatch.sh;do
  cp -p "$B/$name" "/mnt/ota/$name.mu1447-net-restore" &&
  same "$B/$name" "/mnt/ota/$name.mu1447-net-restore" &&
  mv -f "/mnt/ota/$name.mu1447-net-restore" "/mnt/ota/$name" || return 1
 done
 sync
}
fail(){
 echo "MU1447_NETWORK=FAIL reason=$1"
 if [ "$WRITING" = 1 ];then
  WRITING=0
  if rollback;then echo 'MU1447_NETWORK_AUTO_ROLLBACK=PASS restart_manually=1';else echo 'MU1447_NETWORK_AUTO_ROLLBACK=FAIL retain_backup';fi
 fi
 exit 1
}
trap 'fail interrupted' 1 2 15
[ "$#" -le 1 ] || fail arguments
case "$ACTION" in --check|--apply|--restore|--status);;*) fail use_check_apply_restore_status;;esac
for cmd in cp mkdir chmod rm mv cat mount sync awk grep;do command -v "$cmd" >/dev/null 2>&1 || fail missing_command_$cmd;done
[ ! -e "$S" ] && mkdir "$S" || fail ram_stage
STAGED=1
cp "$KIT/file-check" "$S/file-check" && chmod 755 "$S/file-check" || fail checker_stage
"$S/file-check" --self-test && "$S/file-check" --manifest "$KIT" "$KIT/SHA256SUMS.txt" || fail package_integrity
(umask 077;set -C;: > "$LOCK") 2>/dev/null || fail management_lock
LOCKED=1
for p in "$B" /mnt/ota/wcp_pf.sh /mnt/ota/wcp_pfwatch.sh;do [ ! -L "$p" ] || fail symlink_target;done
if [ -d "$B" ];then
 [ -f "$B/complete" ] && "$S/file-check" --manifest "$B" "$B/SEAL.sha256" || fail incomplete_or_changed_backup
fi
if [ "$ACTION" = --restore ];then
 [ -d "$B" ] || fail no_backup
 for name in wcp_pf.sh wcp_pfwatch.sh;do
  same "/mnt/ota/$name" "$KIT/payload/$name" || same "/mnt/ota/$name" "$B/$name" || fail later_edit_$name
 done
 mount -uw /mnt/ota || fail ota_mount
 rollback || fail restore
 echo 'MU1447_NETWORK=RESTORED restart_manually=1'
 exit 0
fi
if [ "$ACTION" = --status ];then
 if same /mnt/ota/wcp_pf.sh "$KIT/payload/wcp_pf.sh" && same /mnt/ota/wcp_pfwatch.sh "$KIT/payload/wcp_pfwatch.sh";then
  echo 'MU1447_NETWORK=INSTALLED runtime_requires_operator_check'
 else echo 'MU1447_NETWORK=NOT_INSTALLED_OR_RESTORED';fi
 exit 0
fi
if [ -d "$B" ];then
 if same /mnt/ota/wcp_pf.sh "$KIT/payload/wcp_pf.sh" && same /mnt/ota/wcp_pfwatch.sh "$KIT/payload/wcp_pfwatch.sh";then
  echo 'MU1447_NETWORK=ALREADY_INSTALLED restart_required_if_not_yet_restarted=1';exit 0
 fi
 fail retained_backup_requires_review
fi
[ "$(cat /mnt/app/carplaymaps/PROFILE)" = MU1447/790 ] || fail wrong_profile
while read -r wanted name;do
 [ "$(file_hash "/mnt/ota/$name")" = "$wanted" ] || fail installed_script_mismatch_$name
done < "$KIT/BASELINE.sha256"
# Separate RAM outputs: preflight does not overwrite the live generated policy.
MU1447_PF_RAM_DIR="$S" /bin/sh "$KIT/payload/wcp_pf.sh" check || fail native_firewall_preflight
if [ "$ACTION" = --check ];then
 echo 'MU1447_NETWORK_CHECK=PASS native_pf_syntax=PASS persistent_writes=0 active_rules_changed=0'
 exit 0
fi
mount -uw /mnt/app && mount -uw /mnt/ota || fail writable_volumes
mkdir "$B" || fail backup_create
: > "$B/SEAL.sha256"
for name in wcp_pf.sh wcp_pfwatch.sh;do
 cp -p "/mnt/ota/$name" "$B/$name" && same "/mnt/ota/$name" "$B/$name" || fail backup_copy_$name
 echo "$(file_hash "$B/$name")  $name" >> "$B/SEAL.sha256"
done
"$S/file-check" --manifest "$B" "$B/SEAL.sha256" || fail backup_integrity
: > "$B/complete"
sync
WRITING=1
for name in wcp_pf.sh wcp_pfwatch.sh;do
 [ ! -e "/mnt/ota/$name.mu1447-net-new" ] || fail existing_stage_$name
 cp "$KIT/payload/$name" "/mnt/ota/$name.mu1447-net-new" &&
 chmod 755 "/mnt/ota/$name.mu1447-net-new" &&
 same "$KIT/payload/$name" "/mnt/ota/$name.mu1447-net-new" &&
 mv -f "/mnt/ota/$name.mu1447-net-new" "/mnt/ota/$name" || fail install_$name
 same "$KIT/payload/$name" "/mnt/ota/$name" || fail final_readback_$name
done
WRITING=0
sync
echo 'MU1447_NETWORK=INSTALLED manual_restart_required=1 active_session_unchanged=1'
echo 'Factory control/audio/video queue classification added; connection stability UNTESTED.'
