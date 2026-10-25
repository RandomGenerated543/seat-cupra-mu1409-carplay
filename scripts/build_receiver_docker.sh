#!/bin/bash
# Host-only: use a separately provisioned/validated QNX toolchain image.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
OUT="${OUT:-$ROOT/build/receiver}"
IMAGE="${IMAGE:-mhi2-qnx65-armv7-public:4.9}"
mkdir -p "$OUT"
# Historical in-container aliases preserve the original compile/debug identity;
# these are container paths, not host/private workspace dependencies.
docker run --rm --platform linux/amd64 \
 -v "$ROOT:/repo:ro" \
 -v "$ROOT/src/native:/work/private/development/mu1409-wp2-r57/src/native:ro" \
 -v "$OUT:/diag" -v "$ROOT/src/native/altscreen111-gen2:/diag/source:ro" \
 -w /work "$IMAGE" bash /repo/scripts/build_receiver_inside.sh
python3 "$ROOT/scripts/verify_receiver.py" "$OUT/payload/libmibr_carplay111.so"
