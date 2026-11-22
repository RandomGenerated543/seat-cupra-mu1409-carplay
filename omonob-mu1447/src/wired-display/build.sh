#!/bin/sh
set -eu
cd "${0%/*}"
docker run --rm --platform linux/amd64 -v "$PWD:/work" -w /work mhi2-qnx65-armv7-public:4.9 sh -ec '
t=arm-unknown-nto-qnx6.5.0eabi
"$t-gcc" -shared -fPIC -Os -Wall -Wextra -Werror -fvisibility=hidden -march=armv7-a -marm -mfloat-abi=softfp -Wl,-soname,libmu1447-wired-display.so -o libmu1447-wired-display.so wired-display.c
"$t-gcc" -Os -Wall -Wextra -Werror -march=armv7-a -marm -mfloat-abi=softfp -o file-check checker.c
"$t-readelf" -d libmu1447-wired-display.so
'
cp libmu1447-wired-display.so ../payload/libmu1447-wired-display.so
cp file-check ../payload/file-check
python3 patch.py
