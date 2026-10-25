#!/bin/ksh
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Shared SD-root logging/evidence helpers for the MU1440 developer deployment.
# Keep this file QNX/ksh friendly: no GNU-only shell features are required.

mibr_stamp(){
  if [ -x /net/rcc/usr/bin/date ]; then
    /net/rcc/usr/bin/date +%Y%m%d-%H%M%S 2>/dev/null && return 0
  fi
  echo "run-$$"
}

mibr_media_rw(){
  P=$1
  case "$P" in
    /net/mmx/fs/*)
      mount -uw "$P" 2>/dev/null || return 1
      ;;
  esac
  T="$P/.mibr-altscreen-session-write-test.$$"
  touch "$T" 2>/dev/null || return 1
  [ -f "$T" ] || return 1
  rm -f "$T" 2>/dev/null || return 1
  return 0
}

mibr_hash_file(){
  F=$1
  [ -r "$F" ] || return 1
  set -- $("$MIBR_SESSION_SHA" "$F" 2>/dev/null)
  [ -n "${1:-}" ] || return 1
  echo "$1"
}

mibr_hex_ascii(){
  awk '
    function hv(c, p) {
      p=index("0123456789abcdef",tolower(c))
      return p ? p-1 : -1
    }
    function byte(s, a,b) {
      a=hv(substr(s,1,1)); b=hv(substr(s,2,1))
      if (a<0 || b<0) return -1
      return a*16+b
    }
    {
      line=$0
      if (line !~ /^0x[0-9A-Fa-f]+/) next
      sub(/^0x[0-9A-Fa-f]+[^0-9A-Fa-f]+/,"",line)
      gsub(/[^0-9A-Fa-f]/,"",line)
      for (i=1; i+1<=length(line); i+=2) {
        n=byte(substr(line,i,2))
        if (n>=32 && n<=126) out=out sprintf("%c",n)
      }
    }
    END {
      gsub(/[^A-Za-z0-9_-]/,"",out)
      if (length(out)) print out
    }'
}

mibr_e2p_ascii(){
  ADDR=$1
  LEN=$2
  on -f rcc /net/rcc/usr/apps/modifyE2P r "$ADDR" "$LEN" 2>/dev/null | mibr_hex_ascii
}

mibr_prepare_session(){
  MIBR_SESSION_ACTION=$1
  MIBR_SESSION_ROOT=$2
  MIBR_SESSION_TEE=$3
  MIBR_SESSION_SHA=$4

  [ -x "$MIBR_SESSION_TEE" ] || return 2
  [ -x "$MIBR_SESSION_SHA" ] || return 3
  mibr_media_rw "$MIBR_SESSION_ROOT" || return 4

  MIBR_SESSION_STAMP=$(mibr_stamp)
  MIBR_SESSION_DIR="$MIBR_SESSION_ROOT/mhi2-altscreen-logs/$MIBR_SESSION_STAMP-$MIBR_SESSION_ACTION-$$"
  MIBR_LOG_FILE="$MIBR_SESSION_DIR/session.log"
  MIBR_ARCHIVE_DIR="$MIBR_SESSION_DIR/archive"

  mkdir -p "$MIBR_ARCHIVE_DIR" 2>/dev/null || return 5
  touch "$MIBR_LOG_FILE" 2>/dev/null || return 6

  export MIBR_SESSION_ACTION MIBR_SESSION_ROOT MIBR_SESSION_TEE MIBR_SESSION_SHA
  export MIBR_SESSION_STAMP MIBR_SESSION_DIR MIBR_LOG_FILE MIBR_ARCHIVE_DIR
  return 0
}

mibr_run_logged(){
  SCRIPT=$1
  shift
  RCFILE="/tmp/mibr-altscreen-session-rc.$$"

  MIBR_LOG_ACTIVE=1
  export MIBR_LOG_ACTIVE

  (
    "$SCRIPT" "$@"
    RC=$?
    echo "$RC" > "$RCFILE"
    exit "$RC"
  ) 2>&1 | "$MIBR_SESSION_TEE" -i -a "$MIBR_LOG_FILE"

  if [ -r "$RCFILE" ]; then
    RC=$(cat "$RCFILE" 2>/dev/null)
    rm -f "$RCFILE" 2>/dev/null || true
  else
    RC=99
  fi
  sync 2>/dev/null || true
  echo "Issue log: $MIBR_LOG_FILE"
  echo "Issue-safe summary: $MIBR_SESSION_DIR/vehicle-summary.txt"
  echo "Recovery archive: $MIBR_ARCHIVE_DIR"
  echo "NOTE: recovery archive may contain third-party/OEM JAR bytes; review before attaching it to a public issue."
  return "$RC"
}

mibr_vehicle_summary(){
  OUT="$MIBR_SESSION_DIR/vehicle-summary.txt"
  AIR=/mnt/app/eso/lib/libairplay.so
  LSDJXE=/mnt/app/eso/hmi/lsd/lsd.jxe
  [ -r /ifs/lsd.jxe ] && LSDJXE=/ifs/lsd.jxe
  LSD=/mnt/app/eso/hmi/lsd/lsd.sh
  SMART=/mnt/system/etc/eso/production/smartphone_integrator.json
  DIOCFG=/mnt/system/etc/eso/production/dio_manager.json
  DISPLAYCFG=""
  for P in /etc/eso/production/displaymanager.json /mnt/system/etc/eso/production/displaymanager.json /mnt/app/eso/production/displaymanager.json; do
    if [ -r "$P" ]; then
      DISPLAYCFG=$P
      break
    fi
  done
  JARDIR=/mnt/app/eso/hmi/lsd/jars

  TRAIN=$(mibr_e2p_ascii 3A0 19 2>/dev/null)
  MU=$(mibr_e2p_ascii 3B9 4 2>/dev/null)
  [ -n "$MU" ] && MU="MU$MU"

  {
    echo "=== MHI2 AltScreen issue summary ==="
    echo "session_action=$MIBR_SESSION_ACTION"
    echo "session_stamp=$MIBR_SESSION_STAMP"
    echo "deployment_media=$MIBR_SESSION_ROOT"
    echo "validated_reference_target=MHI2_ER_SKG13_P4526_MU1440"
    echo "validated_reference_cluster=AID10-class"
    echo "train=${TRAIN:-UNKNOWN}"
    echo "mu=${MU:-UNKNOWN}"

    if [ -r "$MIBR_SESSION_ROOT/RELEASE-MANIFEST.txt" ]; then
      echo "--- deployment release manifest ---"
      awk '{print "release: " $0}' "$MIBR_SESSION_ROOT/RELEASE-MANIFEST.txt" 2>/dev/null
    fi

    for P in /net/mmx/mnt/system/etc/project.txt /mnt/system/etc/project.txt; do
      if [ -r "$P" ]; then
        echo "project_file=$P"
        awk 'NR<=20 {print "project: " $0}' "$P" 2>/dev/null
        break
      fi
    done

    for P in /net/mmx/mnt/app/img_ver.txt /mnt/app/img_ver.txt; do
      if [ -r "$P" ]; then
        awk 'NR==1 {print "img_ver=" $0; exit}' "$P" 2>/dev/null
        break
      fi
    done

    for P in /net/mmx/mnt/app/version_info.txt /mnt/app/version_info.txt; do
      if [ -r "$P" ]; then
        echo "version_info_file=$P"
        awk '
          /Branch|Label|Framework|GraphicsServices|HMI|J9|DSI|Toolchain|PDK|MME/ {
            print "version_info: " $0
          }' "$P" 2>/dev/null
        break
      fi
    done

    if [ -r /net/rcc/etc/version/RCC-version.txt ]; then
      awk '/version |label / {print "rcc: " $0}' /net/rcc/etc/version/RCC-version.txt 2>/dev/null
    fi

    for P in /net/mmx/dev/nvsku/project /net/mmx/dev/nvsku/sku /net/mmx/dev/nvsku/rev /net/mmx/dev/nvsku/bom; do
      if [ -r "$P" ]; then
        N=${P##*/}
        V=$(cat "$P" 2>/dev/null)
        echo "board_$N=$V"
      fi
    done

    for P in "$AIR" "$LSDJXE" "$LSD" "$SMART" "$DIOCFG" "$DISPLAYCFG" \
             /mnt/app/eso/lib/factories/libdsicarplayproxy.so \
             /mnt/app/armle/usr/sbin/mm-ipod \
             /mnt/app/armle/usr/lib/libiap2client.so.1 \
             /mnt/app/eso/bin/apps/smartphone_integrator \
             /mnt/app/eso/bin/apps/dio_manager \
             /mnt/app/eso/bin/apps/displaymanager \
             /mnt/app/eso/lib/libmibr_carplay111.so \
             /mnt/app/eso/lib/libmibr_isotx2_gate.so \
             "$JARDIR/MIBR-NavIgnore.jar"; do
      [ -n "$P" ] || continue
      if [ -r "$P" ]; then
        H=$(mibr_hash_file "$P" 2>/dev/null)
        echo "sha256 ${H:-HASH_FAILED} $P"
      else
        echo "missing $P"
      fi
    done

    echo "--- display / MOST endpoint presence ---"
    for P in /dev/mlb/isoTX1 /dev/mlb/isoTX2 /net/rcc/dev/name/local/inic/isoTX1 /net/rcc/dev/name/local/inic/isoTX2; do
      [ -e "$P" ] && echo "present $P" || echo "missing $P"
    done

    echo "--- relevant running processes ---"
    pidin ar 2>/dev/null | awk '
      /displaymanager|dio_manager|smartphone_integrator|mm-ipod|lsd/ { print }
    ' || true

    echo "--- lsd custom bootclasspath lines ---"
    if [ -r "$LSD" ]; then
      awk 'index($0,"bootclasspath") || index($0,"BOOTCLASSPATH") || index($0,"MIBR") || index($0,"NavActiveIgnore") {print NR ":" $0}' "$LSD" 2>/dev/null
    fi

    echo "--- lsd jars ---"
    for P in "$JARDIR"/*.jar "$JARDIR"/*.zip; do
      [ -f "$P" ] || continue
      H=$(mibr_hash_file "$P" 2>/dev/null)
      echo "jar_sha256 ${H:-HASH_FAILED} $P"
    done

    echo "--- privacy / sharing note ---"
    echo "VIN, FAZIT and device serial numbers are intentionally not collected."
    echo "This vehicle-summary.txt and session.log are intended to be safe defaults for issue reports."
    echo "Do not upload files from archive/ blindly; it may contain third-party/OEM JAR bytes."
  } > "$OUT"

  cat "$OUT"
}

mibr_archive_java_state(){
  REASON=$1
  LSD=/mnt/app/eso/hmi/lsd/lsd.sh
  JARDIR=/mnt/app/eso/hmi/lsd/jars
  OUT="$MIBR_ARCHIVE_DIR/java-$REASON"
  mkdir -p "$OUT/jars" 2>/dev/null || return 1

  [ -r "$LSD" ] && cp "$LSD" "$OUT/lsd.sh" 2>/dev/null || true
  for B in "$LSD.bu" "$LSD.mibr-directvc-stock" "$LSD.mibr-most20fps-stock" "$LSD.mibr-navignore-stock"; do
    [ -r "$B" ] || continue
    N=${B##*/}
    cp "$B" "$OUT/$N" 2>/dev/null || true
  done

  for P in "$JARDIR"/*.jar "$JARDIR"/*.zip; do
    [ -f "$P" ] || continue
    N=${P##*/}
    cp "$P" "$OUT/jars/$N" 2>/dev/null || true
  done

  {
    echo "reason=$REASON"
    if [ -r "$LSD" ]; then
      H=$(mibr_hash_file "$LSD" 2>/dev/null)
      echo "lsd_sha256=${H:-HASH_FAILED}"
      echo "--- custom/classpath lines ---"
      awk 'index($0,"bootclasspath") || index($0,"BOOTCLASSPATH") || index($0,"MIBR") || index($0,"NavActiveIgnore") || index($0,"Append jar") {print NR ":" $0}' "$LSD" 2>/dev/null
    fi
    echo "--- archived jars ---"
    for P in "$OUT/jars"/*; do
      [ -f "$P" ] || continue
      H=$(mibr_hash_file "$P" 2>/dev/null)
      echo "sha256 ${H:-HASH_FAILED} ${P##*/}"
    done
  } > "$OUT/MANIFEST.txt"

  echo "JAVA_ARCHIVE=$OUT"
  return 0
}
