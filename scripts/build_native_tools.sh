#!/bin/bash
# Host cross-build; source only. Never runs target executables.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
C="${QCC:-arm-unknown-nto-qnx6.5.0eabi-gcc}"
OUT="${OUT:-$ROOT/build/native-tools}"
mkdir -p "$OUT"
A=src/native
F=(-include stddef.h -D_QNX_SOURCE -DMIBR_SHA256_LIBRARY_ONLY -DMIBR_SEAT_TARGET -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -mno-unaligned-access -O2 -g -std=gnu99)
I=(-I"$A/alt111-settings/include" -I"$A/altscreen111-gen2/include" -I"$A/mibr-control")
CORE=("$A/alt111-settings/settings_core.c" "$A/alt111-settings/settings_posix.c" "$A/altscreen111-gen2/src/alt111_policy.c" "$A/sha256sum-compat/sha256sum_compat.c")
SERVICE=("$A/mibr-control/mibr_v3_readonly.c" "$A/mibr-control/mibr_v3_profile_store.c" "$A/mibr-control/mibr_v3_recovery_gate.c" "$A/mibr-control/mibr_v3_runtime_observer.c" "$A/mibr-control/mibr_v3_service.c" "$A/mibr-control/mibr_v3_key40.c" "$A/mibr-control/mibr_v3_input_bridge.c" "$A/mibr-control/mibr_v3_route_gateway.c" "$A/mibr-control/mibr_v3_owner_lifecycle.c")
"$C" "${F[@]}" "${I[@]}" "$A/alt111-settings/settings_cli.c" "${CORE[@]}" -lsocket -o "$OUT/alt111-settings"
"$C" "${F[@]}" -DMIBR_V3_TARGET_STORAGE_QUALIFIED "${I[@]}" "${SERVICE[@]}" "$A/mibr-control/mibr_v3_qnx_mount.c" "${CORE[@]}" -lsocket -o "$OUT/mibr-seat-service"
"$C" "${F[@]}" "${I[@]}" "$A/seat-tools/profile-tool.c" "${CORE[@]}" -lsocket -o "$OUT/profile-tool"
"$C" "${F[@]}" "$A/seat-tools/storage_probe.c" -o "$OUT/seat-storage-probe"
"$C" "${F[@]}" "$A/mibr-control/mibr_v3_genkey.c" -o "$OUT/mibr-v3-genkey"
"$C" "${F[@]}" -shared -fPIC "$A/isotx2-gate/isotx2_gate.c" -lsocket -o "$OUT/libmibr_isotx2_gate.so"
for name in owner_probe owner_unlock; do
 "$C" "${F[@]}" "$A/isotx2-gate/$name.c" -o "$OUT/${name//_/-}"
done
"$C" "${F[@]}" -UMIBR_SHA256_LIBRARY_ONLY "$A/sha256sum-compat/sha256sum_compat.c" -o "$OUT/sha256sum"
"$C" "${F[@]}" "$A/tee-compat/tee_compat.c" -o "$OUT/tee"
echo NATIVE_TOOLS=BUILT_TARGET_EXECUTION_UNTESTED
