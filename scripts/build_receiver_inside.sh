#!/bin/bash
# Workstation/container build only. Does not connect to a vehicle.
set -euo pipefail
cd /work
A=private/development/mu1409-wp2-r57/src/native
V=/diag/source
C=arm-unknown-nto-qnx6.5.0eabi-gcc
F=(-include stddef.h -D_QNX_SOURCE -DMIBR_SHA256_LIBRARY_ONLY -DMIBR_SEAT_TARGET -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -mno-unaligned-access -O2 -g -std=gnu99)
I=(-I"$V/include" -I"$A/alt111-settings/include" -I"$A/altscreen111-gen2/include" -I"$A/mibr-control")
CORE=("$A/alt111-settings/settings_core.c" "$A/alt111-settings/settings_posix.c" "$A/altscreen111-gen2/src/alt111_policy.c" "$A/sha256sum-compat/sha256sum_compat.c")
mkdir -p /diag/payload
"$C" "${F[@]}" -shared -fPIC "${I[@]}" "$V/libaltscreen111_gen2.c" "$V/seat_settings.c" \
 "$V/src/alt111_profile.c" "$V/src/alt111_control.c" "$V/src/alt111_video.c" "$V/src/alt111_resync.c" \
 "$V/src/alt111_zoom.c" "$V/src/alt111_zoom_debugspi.c" "${CORE[@]}" \
 -Wl,-soname,libaltscreen111.so -lsocket -o /diag/receiver-debug.so
arm-unknown-nto-qnx6.5.0eabi-strip -o /diag/payload/libmibr_carplay111.so /diag/receiver-debug.so
arm-unknown-nto-qnx6.5.0eabi-readelf -h -d /diag/payload/libmibr_carplay111.so > /diag/LOADER-AUDIT.txt
