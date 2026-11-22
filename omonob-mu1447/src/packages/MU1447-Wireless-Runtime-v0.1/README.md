# MU1447 wireless runtime correction v0.1

For **SEAT/Cupra MHI2_ER_SEG11_P4709 / MU1447 / 790 cockpit**, with our **MU1447-Native-Wireless-v1.0-rc1.3** already installed. This is an update, not a standalone wireless installer. The earlier rc1.2 has the same runtime inputs, but this does not repair its installer or backups.

**Highly experimental. Use entirely at your own risk; no warranty or liability is accepted by the contributors, to the extent permitted by law. Local regression checks passed; this update has not yet been tested in a car.** Install and first check the controls while parked.

## What this changes

- Keep camera/popup ownership separate from a notification that the CarPlay canvas was hidden. Returning from the cameras can release touch correctly.
- Defer CarPlay screen claims while an OEM screen owns the display, including claims outside the canvas refresh path.
- Move UDP touch transmission off the HMI input callback. The queue is bounded, movement events can coalesce, and gestures do not cross between camera controls and CarPlay halfway through a press.
- Retry HMI readiness and observer setup during startup. Retain registration identity until cleanup succeeds, preventing duplicate observer/worker registration on retries.
- Observe the receiver's actual session separately from the main video stream. A main-screen video interruption does not itself end the phone session or cockpit grant. A real receiver-session change still releases the old session.
- Serialize receiver startup/staging and refuse an ambiguous process identity.

It replaces three wireless Java archives and two startup/controller scripts, and adds one small process-observation/startup guard. The guard opens receiver memory **read-only**, checks its code fingerprints, and reads one existing session pointer; it never writes receiver memory or prints pairing material. The separate preflight checks the necessary HMI methods without running activators.

The receiver, player, Bluetooth and OEM binaries, firewall and channel scripts, zoom, safe areas, navigation-card preferences, media support, public menu, pairing store and wired configuration are outside this update. The three recognized receiver versions are the base receiver and both delivered safe-area variants. Your existing layout is retained.

**Wi-Fi disconnect tuning is outside this fix.** Radio/transport disconnects may still occur. The earlier layout update was not proven to cause those disconnects, and this package neither installs nor removes it.

## Installation

1. Unzip `MU1447-Wireless-Runtime-v0.1.zip` on the computer. Copy the whole `MU1447-Wireless-Runtime-v0.1` folder to the SD root. Keep all files together. Do not copy the package recursively into the unit's small RAM disk.
2. Boot the infotainment normally with the existing wireless installation enabled. The receiver daemon must be running for the read-only compatibility check; an active iPhone session is not required.
3. Connect by SSH as usual. For the known home-network address on a Mac:

   ```sh
   ssh -o ConnectTimeout=10 -o ConnectionAttempts=1 -o ControlPath=none -o HostKeyAlgorithms=+ssh-rsa root@192.168.50.242
   ```

   Use the unit's current address if different. Enter its existing root password.
4. In the car's SSH terminal:

   ```sh
   /bin/ksh /fs/sda0/MU1447-Wireless-Runtime-v0.1/install.sh --check
   ```

   Continue only after `MU1447_RUNTIME_CHECK=PASS`. A refused baseline or unavailable receiver observation means **stop**; do not bypass it. Check writes only temporary files, not persistent configuration.
5. Install:

   ```sh
   /bin/ksh /fs/sda0/MU1447-Wireless-Runtime-v0.1/install.sh --apply
   ```

   Expect `MU1447_RUNTIME=INSTALLED persistent=1 restart_manually=1`. Perform a normal infotainment restart using the power knob. The script does not restart the unit or interrupt the current session automatically. The correction persists after restart.
6. While parked, verify startup touch, entering/leaving the cameras, OEM camera controls, returning to CarPlay, and an ordinary wired session. No new phone pairing or firmware flash is required by this update.

If the SD uses a different mount point, substitute it in the commands. Native dependencies (`file-check`, the QNX guard, Java metadata checker) are included; nothing needs installing on the computer to run this package.

## Restore only this update

```sh
/bin/ksh /fs/sda0/MU1447-Wireless-Runtime-v0.1/install.sh --restore
```

Expect `MU1447_RUNTIME=RESTORED`, then restart the infotainment normally. This restores the six runtime targets to the exact prior state; the newly added guard is removed. Wi-Fi and safe-area add-ons remain as they were. **Restore this update before using the base wireless package's uninstaller.**

The checksummed original backup is retained at `/mnt/app/.mu1447-wireless-runtime-v01`. Do not delete it. Later edits to a tracked target are refused instead of overwritten. A detected write failure attempts an immediate rollback and reports whether it succeeded. An interrupted power supply is not an atomic transaction across files; retain the SD and backup if installation is interrupted. Re-running `--apply` after a completed installation is harmless. `--status` reports the recognized file state.

## Validation and limits

See `TEST-RESULTS.json` and the included `source/` and `tests/`. Tests exercise the patched bytecode with simulated OEM/network boundaries, delayed startup and partial registration failures, camera/touch orderings, blocked touch transmission, real-session versus video-gap handling, native lock/PID/status code, and install/restore/failure transactions. They do not emulate the whole vehicle, GPU, Wi-Fi radio or QNX scheduler. The installer separately checks exact firmware identity, all package files, receiver fingerprints and Java linkage on the real unit before writes.

The underlying wireless integration uses omonob's receiver and Java service approach; this package supplies MU1447 runtime corrections to that existing installation. A local successful test is not a claim of bug-free operation on the car. Some apparent freezes may have a separate player or transport cause.
