# Wireless adapter selector

**HIGHLY EXPERIMENTAL. USE AT YOUR OWN RISK. NO WARRANTY.** Incorrect firmware can disable an adapter. Keep the matching rollback; no recovery is guaranteed. These packages install nothing on the head unit or cockpit. First verify direct-cable cockpit maps with the correct vehicle-specific modification.

Labels below identify actual hardware and firmware, never a tester. A case/logo/product shop name alone is insufficient. The two AX1800M/suding systems use different packages. AX1800/yunlian is another target. HW301/CXZ521 is another target again.

| Target | Download |
|---|---|
| HW301 / CXZ521; original APP HW301_20250630126, system 20250320; candidate vendor v129 / HW301_20260122129 | [HW301-CXZ521-app20260122129-v0.1.zip](https://github.com/RandomGenerated543/seat-cupra-mu1409-carplay/releases/download/experimental-2026-10-30/HW301-CXZ521-app20260122129-v0.1.zip) |
| AX1800M / suding / v851se-yunlian-cp; system 202504180933CA; protocol 20261008165747 | [AX1800M-Suding-system202504180933CA-protocol20261008165747-v0.2.zip](https://github.com/RandomGenerated543/seat-cupra-mu1409-carplay/releases/download/experimental-2026-10-30/AX1800M-Suding-system202504180933CA-protocol20261008165747-v0.2.zip) |
| Mini 5 Pro / AX1800 / yunlian / v851se-yunlian-cp; original system 202504171406CA, protocol 20250415195209; full March base system 202603120932CA, protocol 20260109175612 | [Mini5Pro-AX1800-Yunlian-system202603120932CA-protocol20260109175612-v0.2.zip](https://github.com/RandomGenerated543/seat-cupra-mu1409-carplay/releases/download/experimental-2026-10-30/Mini5Pro-AX1800-Yunlian-system202603120932CA-protocol20260109175612-v0.2.zip) |
| AX1800M / suding / v851se-yunlian-cp; system 202603120956CA; original protocol 20260109175612, candidate October protocol 20261008165747 | [AX1800M-Suding-system202603120956CA-protocol20261008165747-v0.2.zip](https://github.com/RandomGenerated543/seat-cupra-mu1409-carplay/releases/download/experimental-2026-10-30/AX1800M-Suding-system202603120956CA-protocol20261008165747-v0.2.zip) |

The owner reports all four configurations working on 30 October 2026. The packaged host-test/qualification notes retain their original evidence boundaries; this is not a guarantee for another board, firmware or phone. Source and license notices are in each ZIP and [source-only archives](source).

## Before running a command

Extract the **whole matching folder**. Use a computer connected to the adapter Wi-Fi. These Python/shell commands run on the computer, not in the car SSH terminal. Install Python 3.12 or newer for a common supported environment. No Internet is required after all package files are downloaded. Probe uses the adapter web interface; no adapter SSH/root login is needed. Never mix uploaders, images or IMAGES.json from different packages.

### HW301 / CXZ521

Default observed address is 192.168.31.1. Follow its README if it changes. On macOS/Linux:

```sh
sh adapter.sh dry-run
sh adapter.sh probe
sh adapter.sh flash
```

After FLASH_REPORTED_COMPLETE=1 and the documented wait/power cycle:

```sh
sh adapter.sh verify
```

The custom build marker is more informative than the vendor UI version. Read RECOVERY.md for the matching app-image recovery process; it differs from the AX uploaders. The package includes Python implementations for Windows; use the commands accepted by `py adapter.py --help` and its README rather than assuming a shell exists.

### AX1800M / suding / system 202504180933CA

This is the October application package. On Windows:

```powershell
py adapter-october-r6.py dry-run
py adapter-october-r6.py probe
py adapter-october-r6.py flash
```

Recovery: `py adapter-october-r6.py rollback`. Logs: `py adapter-october-r6.py logs --out logs-adapter`. It changes application members; October stock is not a full flash backup.

### Mini 5 Pro / AX1800 / yunlian

```powershell
py adapter-mini5.py dry-run
py adapter-mini5.py probe
py adapter-mini5.py flash
```

Recovery: `py adapter-mini5.py rollback`. Logs: `py adapter-mini5.py logs --out logs-mini5`. This package writes a **full March kernel/rootfs image**; it is not an app-only change. Included stock fallback is March, **not the original April image**. The v0.2 address-port guard remains enabled.

### AX1800M / suding / system 202603120956CA

```powershell
py adapter.py dry-run
py adapter.py probe
py adapter.py flash
```

Recovery: `py adapter.py rollback`. Logs: `py adapter.py logs --out logs-ax1800m`. This independent v0.2 uses October application binaries with a corrected final initial-SETUP enabledFeatures lookup; it does not recover the original January application. The included stock rollback is October application-only. The original January/October version strings alone cannot prove custom hook liveness.

## During and after flashing

Keep power connected until the uploader explicitly reports completion. UNKNOWN, timeout or a version string is not success; save output and do not automatically retry or interrupt power. Follow the model-specific reboot/power-cycle instructions. Allow roughly 3–10 minutes depending on image size/connection; do not unplug because an estimate elapsed.

In the parked car, check centre-screen CarPlay/audio first, then cockpit maps, supported app zoom, disconnect/reconnect, a normal restart and OEM return. If connection fails, collect the version text, extracted altscreen log and full bundle before rollback/restart. The vendor bundle can contain identifiers; review it privately before posting publicly.

Mac/Linux equivalents use `python3` instead of Windows `py` where the package requires Python. The iPhone may need an old pairing removed and a fresh pairing; that is not proof the firmware is compatible. Never use a guessed IP/password or override a failed hardware/firmware guard.

## Required vehicle test and fresh phone pairing

A bench/computer may be used for upload and build verification. Functional acceptance MUST be tested in the actual compatible car, with its working head unit and Virtual Cockpit. A bench unit without the cockpit can produce misleading black-screen/no-map results.

After flashing reports completion and the documented reboot/power cycle is finished, remove the OLD adapter pairing from the iPhone: Settings > Bluetooth > the adapter > Forget This Device; also Settings > General > CarPlay > the matching adapter/car entry > Forget This Car if that entry exists. Do not erase unrelated pairings. Then connect the adapter in the parked car and pair it again as a new connection, with Bluetooth and Wi-Fi enabled, approving CarPlay. Old pairing/cache state can prevent correct connection after an update.

Verify centre-screen video/audio first, then cockpit maps, app-supported zoom, disconnect/reconnect and OEM return. A version string or retained build marker alone is not a car test. Fresh pairing does not cure wrong hardware/firmware. Collect logs before a restart/rollback if it fails.


See [open issues](../docs/OPEN_ISSUES.md) for known limits.
