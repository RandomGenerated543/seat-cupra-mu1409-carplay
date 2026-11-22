# MU1447 wireless layout correction v0.1

Layout-only update for the installed MU1447 native wireless rc1–rc1.3 build, with the known wired display/layout adjustments. **Experimental; resulting appearance still requires an on-car check.** Use at your own risk, without warranty.

## What changes

- Read the existing, CRC-checked wired navigation-card preference at wireless descriptor construction. The reported `position=0`, generation46, CRC`1d4def3c` is Center: it now starts on view3 rather than unconditional view0.
- Select the matching initial Center/Left/Right/Off navigation URL, retaining `showETA=yes` and fixed70% zoom.
- Identify the installed wired core and copy all five corresponding safe rectangles. Both known versions are supported: Center628×185 at191,56 and the subsequent Center-down version at191,76. Left remains606×252 at202,45; Right606×272 at202,45; Off606×329 at202,1.
- Update the receiver integrity guard's expected hash to match the exact new receiver. No integrity check is disabled.
- Write a closed/flushed status file at `/dev/shmem/mu1447-wireless-layout.status` so startup selection can be inspected without relying on buffered stdout.

The existing wired core, menu, selected preference file, network correction, firewall scripts, Bluetooth bridge, touchscreen integration and pairing store are untouched. This does not fix or certify wireless disconnects or the parking return that needs one touch.

## Install

Extract the entire `MU1447-Wireless-Layout-v0.1` folder to the SD root. In the car SSH terminal:

```sh
cd /fs/sda0/MU1447-Wireless-Layout-v0.1
/bin/ksh ./install.sh --check
```

Require `MU1447_LAYOUT_CHECK=PASS`. The preceding `MU1447_LAYOUT_MATCH=PASS` reports the exact wired Center Y selected. Unknown wired layouts, modified receiver/guard/map-helper binaries, malformed packages and changed backups are refused. Check does not change persistent files or restart the session.

Then:

```sh
/bin/ksh ./install.sh --apply
```

Require `MU1447_LAYOUT=INSTALLED`, then restart the infotainment normally. The updated descriptor is used by the next wireless connection. No pairing reset or new menu is required. Leave the existing Center choice selected.

After connection, optional read-only confirmation:

```sh
cat /dev/shmem/mu1447-wireless-layout.status
```

For Center, expect `position=0`, `initial_view=3`, `zoom=70` and `zoom_result=0`. This confirms the requested descriptor, not the final Waze rendering.

## Restore

```sh
cd /fs/sda0/MU1447-Wireless-Layout-v0.1
/bin/ksh ./install.sh --restore
```

After `MU1447_LAYOUT=RESTORED`, restart normally. The exact previous receiver and guard are saved under `/mnt/app/.mu1447-wireless-layout-v01`; keep that backup. Unknown later edits are not overwritten. Reapplying after restore is deliberately refused pending review of the retained backup.

Before restoring the entire wireless build through its original installer, restore this layout add-on first. If the separate network correction is installed, restore that add-on too before restoring the base build. The two add-ons change different files and can be restored in either order.

## Validation and provenance

Actual patched ARM instructions passed32 preference/URL cases, including the exact reported Center record, all four card modes, CRC/generation failures, previous-record fallback, allocation failure, caller return and register preservation. Both guarded receiver variants were checked. Host installer fixtures passed for both wired cores: no persistent check writes, variant selection, installation/idempotence, sealed byte-exact restore and rollback after an injected second-write failure; the network correction and wired files remain unchanged. Native hash/mount/file APIs are fixture components in those tests. Vehicle appearance and stability are not established by these local tests.

The preference reader is the existing public project's canonical reader. The fixed receiver hook source, build script, binary deltas and test scripts are included. Full original upstream/OEM binaries are not represented as newly authored source. Upstream GPL text and source notices are retained; OEM inputs retain their own rights. No private keys or credentials are bundled.
