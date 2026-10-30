> **2026-10-30 publication:** Start with [the beginner guide](NEWBIE_INSTALL.md) and [versioned downloads](../downloads/README.md). Older filenames/hashes below describe the retained foundation build; do not mix them with newer feature payloads.

# Final-stack installation candidate v0.2.1

**HIGHLY EXPERIMENTAL. USE AT YOUR OWN RISK. NO WARRANTY.** Read DISCLAIMER.md.

This is a new consolidated installer, not an already vehicle-qualified release.
It installs the retained **final** video, writer/gate, firewall/startup, wheel,
R13 menu and control components together. It does not install historical
intermediate receivers or require manually replaying WP1 and WP2 updates.
The component bytes were retained from the target development path; the fresh
installation/restore orchestration still needs its first parked vehicle test.

WP2 alone is not standalone: its menu needs the WP1 receiver, original-H.264 TS
writer, owner-protocol-2 gate, firewall and boot integration. This bundle includes
those foundations in their intended final configuration.

## Prerequisites

- Matching P4708 / MU1409 or compared P4708_1 baseline and fitted 790-family
  cockpit. The preflight compares exact native/Java/M.I.B./configuration bytes.
- Remove omonob **using its own matching uninstaller**, normally restart and
  confirm OEM infotainment/navigation and wired CarPlay work first. No omonob
  uninstaller is bundled, and this installer does not delete unknown mods.
- Preserve the separately installed M.I.B. NavActiveIgnore prerequisite. Its
  exact JAR and Java startup are checked. A differing patch needs review.
- Existing SSH access, stable power, parked vehicle, writable SD/USB, off-unit
  original backups and an independently accessible recovery method.
- Use the **assembled v0.2.1 bundle**, not GitHub's source Download ZIP or the
  receiver-only updater. No compiler/SDK is required on the unit.

If uncertain, use scripts/collect_install_baseline.py on the host first, then
scripts/compare_install_baseline.py. This only reads the car. Keep its OEM files
and runtime output private. A comparable omonob success is useful interoperability
evidence; it does not override a failed fresh-install baseline check.

## Prepare and install

Unzip the whole folder `SEAT-MU1409-final-stack-candidate-v0.2.1` to the SD root.
Keep install.sh, payload/, KIT.sha256, TARGETS.txt and IMMUTABLES.txt together.
Keep the supplied source/license materials with the package when sharing it.
Unplug the phone. Do not use SWDL or an automatic-flashing menu.

In the unit's SSH terminal (adjust /fs/sda0 if the medium uses another path):

```sh
/bin/ksh /fs/sda0/SEAT-MU1409-final-stack-candidate-v0.2.1/install.sh --check
```

Expect the J9 probe to pass and `FULL_PREFLIGHT=PASS persistent_writes=0`.
Stop on any other result. Do not change expected hashes to make it pass.
This proves preflight conditions, not working visible output.

After a matching preflight and original backups/recovery review:

```sh
/bin/ksh /fs/sda0/SEAT-MU1409-final-stack-candidate-v0.2.1/install.sh --apply
```

The expected final line is `FULL_INSTALL=FINAL_STACK_FILES_VERIFIED` with
`RESTART_REQUIRED=YES`. It saves all five modified activation/configuration
before-images to `original-backup/` on the SD before production writes, then
verifies another copy internally. It stages final project files first and
changes original activation files last. There is no automatic reboot or live
firewall reload. Filesystems are returned read-only; any failure is reported.

Normally restart the infotainment unit, reconnect SSH, then start a fresh wired
CarPlay session. **Do not rerun the old WP1/WP2 upgrade installers afterwards.**
Copy the SD original-backup folder off the medium and retain it independently.

## First acceptance checks

1. Original center-screen CarPlay and infotainment behavior.
2. Automatic wired map output, stable startup and no repeated stock/Waze cycling.
3. English CarPlay settings in the **car's HOME menu**, OEM Back/focus/re-entry.
4. Arrival-time toggle: stored/readback, request/ack and actual cockpit effect.
5. Right-wheel roller in Apple Maps/Google Maps. Waze did not visibly respond to
   that zoom command in the prior observations.
6. Disconnect: visible stock return. Reconnect: fresh working output. Then verify
   another normal restart and exactly one media owner.

Status command:

```sh
/bin/ksh /mnt/app/root/altscreen-u2/harman-r13/control.sh --status
/bin/ksh /mnt/app/root/altscreen-u2/scripts/direct_ts_auto_status.sh
```

Final receiver SHA256 is
`6165f72974b4ebea8f4a3e27a0354f20df98e29350b810b4e0ac4d5efcf7fce5`.
Original H.264 forwarding, auxiliary zoomFactor=70 and queue recovery are used;
there is no software decoding/resizing/encoding. Wide SafeArea is 708x244@151,56.
Full/Center information placement is unresolved. Red-scrollbar vehicle appearance
and behavior remain explicitly unaccepted until the operator checks them.

## Restore this fresh installation

Unplug the phone, retain power and SSH access. Preflight restoration:

```sh
/bin/ksh /fs/sda0/SEAT-MU1409-final-stack-candidate-v0.2.1/install.sh --restore-check
```

Then restore only if the original backups and current activation files verify:

```sh
/bin/ksh /fs/sda0/SEAT-MU1409-final-stack-candidate-v0.2.1/install.sh --restore
```

The same restore script and payload are also retained persistently at:

```sh
/bin/ksh /mnt/app/root/seat-full-install-v02-backup/kit/install.sh --restore-check
/bin/ksh /mnt/app/root/seat-full-install-v02-backup/kit/install.sh --restore
```

Restoration quiesces the project writer and its exact owned broker, restores the
five original files with verified readback, and disables project boot markers.
It leaves project files/preferences inert and preserves the pre-project M.I.B.
NavActiveIgnore state. Normally restart and independently verify stock behavior.
This is not a factory reset. A failed/partial backup, unknown bytes or inaccessible
SSH requires review/recovery, not a blind overwrite or bypass.

## Local maintainer assembly

```sh
python3 scripts/assemble_consolidated_install.py --inputs /path/to/retained-package-folders --baseline /path/to/private-original-firewall-files
```

This is host-only. It verifies pinned retained inputs and original firewall
hashes, generates the final settings profile, fixes the fresh installation's
recovery entry, and writes a local-only ZIP under build/. Firmware-derived
menu/startup payloads and SDKs are not published in this repository.

## v0.2.1 startup directory correction

The consolidated installer now creates `altscreen-u2/wp2/` before changing
activation files. The retained storage probe requires this directory even though
the active settings service lives under `harman-r13/`. It does not enable the
retired WP2 service. Missing this directory caused `mount_identity errno=2`,
then `R13_BOOT=PREREQUISITE_TIMEOUT` and missing geometry/settings.
baseline-B confirmed the manual directory repair allowed the broker to start;
CarPlay and automatic restart acceptance are separate checks.
Existing installations repaired this way do not need reinstallation.
The v0.2 backup/recovery location remains unchanged. Retain the original kit
used for an existing installation; do not mix recovery manifests.
