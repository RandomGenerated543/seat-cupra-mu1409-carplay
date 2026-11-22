# MU1447 wired cockpit display — experimental v0.1.1

Fixed **70% zoom**, **628×220 safe area at X=191, Y=56** for the two large-map
view definitions, and **showETA=yes** for the wired omonob MU1447/790 implementation.
**No added menu and no wireless receiver.**

Highly experimental; use at your own risk. No warranty or liability is accepted
to the extent permitted by applicable law. Not tested in a physical vehicle.
Retain all backups and a working SSH connection. Park with stable power.

## Compatibility and dependencies

v0.1 failed the owner's compatibility check before persistent writes. Do not use
that older ZIP for this installation. v0.1.1 prints separate core/runtime-launcher/
active-launcher match results so any remaining mismatch is identified.


Requires an already-working **wired CarPlay cockpit-map installation** for
P4709 / MU1447 and cluster 790 (1010×376). It does not install cockpit maps from
scratch. The exact original wired `core.so` and launcher must match the files
from the **public wired v2.1.0-rc.7 MU1447 package**. This version matches the
1,826-byte launcher shown by the owner, including its media/artwork startup block.
Other wired implementations may differ: the check will refuse it rather
than replace it with another implementation. No wireless kit is required or installed.

The check requires `/ifs/lsd.jxe` size 55,712,574 and byte-compares both launchers
and the core. It also stages and loads the small add-on on QNX, without invoking
its CarPlay entry point. A check PASS establishes file compatibility and library
loadability, not a visible CarPlay pass.

Original core SHA256:
`918f81fb43f49dacfb5e52c304e24ee3f9d00a0b6d6f66f85d6d3d87de8feaed`
Original launcher SHA256:
`5afe5b4564f09090e6e40ab4d8fb3dcb69bd204358f379ea9f8bad4ece3b592f`
Candidate core SHA256:
`31007f7efbf9e18fa427e1f06de6e84bfc1f95506652e1ba043523a859736d42`

## Install from SD

1. Extract the ZIP on the computer. Copy the **whole
   `MU1447-Wired-Display-v0.1.1` folder** to the SD root.
2. Insert SD1. Disconnect USB CarPlay. Keep the phone disconnected while installing.
3. Log into the car through your working SSH connection, then run:

```sh
/bin/ksh /fs/sda0/MU1447-Wired-Display-v0.1.1/install.sh --check
```

Expect `WIRED_DISPLAY_LOAD=PASS activators_invoked=0`, followed by
`WIRED_DISPLAY_CHECK=PASS state=ORIGINAL persistent_writes=0`.
If a mismatch, FAIL or PARTIAL state appears, save the output and stop.
No persistent files have been changed by this check. Temporary files are staged
individually into `/ramdisk`, avoiding the recursive SD-copy problem.

4. Apply the three display settings together:

```sh
/bin/ksh /fs/sda0/MU1447-Wired-Display-v0.1.1/install.sh --apply
```

Wait for:

```text
WIRED_DISPLAY=INSTALLED zoom=70 safe=628x220@191,56 showETA=yes restart_manually=1 visible=UNTESTED
```

5. Manually restart the infotainment fully. Then reconnect the iPhone **by USB**.
6. Open a map in the cockpit using omonob's existing controls. There is no new
   “Wide” menu to select. The safe-area change affects internal views **0 and 4**,
   the two existing large-map variants. The three other view rectangles remain exact.
7. Start an actual navigation route in Waze/Apple Maps and check ETA/directions.
   Check the centre-screen picture, sound and touch as well.

Status:

```sh
/bin/ksh /fs/sda0/MU1447-Wired-Display-v0.1.1/install.sh --status
grep 'WIRED_VC_ZOOM' /ramdisk/mu1447-wired-display.log | tail -10
```

Expected runtime marker: `WIRED_VC_ZOOM percent=70 result=0 auxiliary_displays=1`.
This reports successful local descriptor modification; it is not an independent
phone-side acknowledgement. This is display scaling, separate from steering-wheel
map zoom buttons.

## Why ETA was missing

All four map URL slots in the inspected wired core explicitly requested
`showETA=no`. The patch requests `showETA=yes` in each slot. It also leaves
`maneuverLayout=` empty so the phone chooses its default directions arrangement,
matching the previously used Waze URL style. The existing dedicated `/map` route
is preserved where present, and `showSpeedLimit=no` is retained.

This fixes a concrete request-side suppression. ETA still depends on an active
route and the phone/app's response; its appearance on every view/app is unverified.
The safe area is a layout hint to iOS; it does not crop the video, remove a cluster
mask or guarantee identical positioning in all navigation apps.

## Restore this add-on

Disconnect USB CarPlay, then:

```sh
/bin/ksh /fs/sda0/MU1447-Wired-Display-v0.1.1/install.sh --restore
```

Wait for `WIRED_DISPLAY=RESTORED restart_manually=1 backup_retained=1`, then
manually restart again. The original core and both launcher copies are restored
byte-for-byte and the added library is removed. The pre-existing wired cockpit-map
installation remains installed. Backup is retained at:
`/mnt/app/.mu1447-wired-display-v011`.
Restore this add-on before updating/uninstalling the underlying omonob installation.

## Files and implementation

Persistent changes are limited to:

- `/mnt/app/carplaymaps/core.so`: four URL slots and safe rectangles 0 and 4.
  Original ELF headers, executable code, relocations and symbol offsets are exact.
- `/mnt/app/carplaymaps/libmu1447-wired-display.so`: a new small native library.
  It wraps `AirPlayCopyServerInfo`, delegates to the existing core, then adds
  numeric `zoomFactor=70` only to display dictionaries with `type=111`.
- `/mnt/app/carplaymaps/dio_manager.wrapper.sh` and
  `/mnt/app/eso/bin/apps/dio_manager`: prepend that library to the existing
  preload chain. Every other launcher line is retained.

No wireless files, Bluetooth/Wi-Fi/firewall settings, MU1409 components, JARs,
menu entries, source video dimensions, source FPS, startup.sh or firmware are installed.
The add-on uses dynamically resolved existing CF APIs, not firmware-specific code
addresses. Missing APIs leave the existing info result untouched and emit a diagnostic.
The native check loads only the new library, never the AirPlay engine or an activator.

## Local validation

- Same C display logic compiled and executed on the host with fixture CF APIs:
  only type 111 changes; primary/other displays, returned info/error/errno preserved;
  missing APIs, allocation/setter failures, absent display, malformed count,
  repeat calls and key object cleanup checked.
- Exact binary patch boundaries checked: core byte length and all code/ELF layout
  unchanged; safe rectangles 0 and 4 changed; all four URLs request ETA.
- Host filesystem fixtures verify check without persistent writes, failed loader
  preflight without writes, original backups, repeated install, exact restore,
  partial-state recovery, unknown-file refusal, active-session and lock refusal,
  and refusal of a corrupt backup. The QNX loader is mocked in host fixtures;
  the real QNX loader check runs on the head unit before installation.
- Shell syntax and native build completed. **No physical MU1447 car acceptance yet.**

Source is included. `sh source/build.sh` requires Docker and the local
`mhi2-qnx65-armv7-public:4.9` GCC/binutils/QNX target build image (not bundled).
`python3 source/test_installer.py` runs host fixtures. To test display C logic:

```sh
clang -Wall -Wextra -Werror -DCPMAP_TEST -DCPMAP_LOG='"/dev/null"' \
  source/wired-display.c source/test_display.c -o test-display
./test-display
```

The core and launcher originate from the local public omonob v2.1.0-rc.7
MU1447 package. v0.1.1 corrects the earlier launcher mismatch: the core/add-on
are unchanged from v0.1, while the supported baseline is now the public wired
launcher rather than the manual wireless-kit launcher. Its media/artwork
startup block and its existing three-library preload chain are preserved; the
new wired display library is prepended to that chain.
Upstream: https://github.com/omonob/VW-MHI2-Wireless-Carplay-Maps . This experimental
add-on is separate and does not imply upstream approval. Preserve upstream notices
and licenses when sharing. Computer build tools are not required to install from SD.
