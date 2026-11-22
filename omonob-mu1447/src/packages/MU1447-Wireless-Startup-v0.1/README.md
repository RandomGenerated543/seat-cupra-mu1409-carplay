# MU1447 wireless startup wake correction

Apply **on top of MU1447-Wireless-Runtime-v0.1**, already installed on the car. This replaces only its wireless CP Java archive. It is not a standalone wireless installer.

The old CP worker could sleep for one second after a screen-entry event while its cached touch readiness remained false. In a test using the actual patched worker with simulated OEM/video boundaries, the old readiness delay was approximately 1,000 ms; the event-driven correction woke within a few milliseconds on the host. That measures readiness, not total input-to-picture latency on the car. Phone/video startup may still contribute delay.

The correction signals the existing worker after screen/service events, and uses a revision check to avoid losing a notification between sampling the canvas and entering the original wait. It retains the one-second idle wait; it does not increase polling, bypass camera ownership or change touch coordinates/protocols. The original runtime's camera, touch, startup, registration and session regression tests still pass.

**Highly experimental; use at your own risk. No warranty or liability is accepted by the contributors, to the extent permitted by law. The correction is locally tested; acceptance on the car is pending.**

## Install

Extract this folder to the SD root, alongside the previous package. From the car SSH terminal:

```sh
/bin/ksh /fs/sda0/MU1447-Wireless-Startup-v0.1/install.sh --check &&
/bin/ksh /fs/sda0/MU1447-Wireless-Startup-v0.1/install.sh --apply
```

Expect `MU1447_STARTUP=INSTALLED`, then restart the infotainment normally. No pairing reset or firmware update is required. Verify startup response and entering/leaving the cameras while parked.

The preflight requires the exact installed Runtime v0.1 archives, scripts and guard, plus the exact MU1447 HMI. It checks Java linkage without running activators. It leaves receiver/player/native binaries, Wi-Fi scripts, zoom, safe areas, media support and pairing data alone. It backs up the one changed file and can be reapplied safely.

## Restore this correction

```sh
/bin/ksh /fs/sda0/MU1447-Wireless-Startup-v0.1/install.sh --restore
```

Restart normally afterward. This returns to Runtime v0.1, retaining its other fixes. **Restore this correction before restoring/uninstalling Runtime v0.1**, because its installer correctly refuses this newer CP archive.

Backup: `/mnt/app/.mu1447-wireless-startup-v01`. Do not delete it. The existing Runtime v0.1 backup is not modified. Later unknown edits are refused. A detected copy/readback failure attempts rollback; retain the SD and backups if power is interrupted.

## Source and validation

`source/` includes the ASM patcher, helper source and build/test scripts. It is a delta build using the original omonob donor and the exact retained MU1447 firmware/API dependencies, which are not redistributed. The installation requires no computer-side Python or Java dependencies. The original runtime native guard remains unchanged.

See `TEST-RESULTS.json`. Host tests stub OEM services, network sends and mount operations where appropriate; they do not establish Wi-Fi or GPU performance. Installer tests cover apply, reapply, restore, dependency/unknown-edit refusal and replacement failure rollback.
