# Installation and prerequisites

Highly experimental; at your own risk. This guide describes the supported sequence, not a universal upgrade or an automated all-in-one installer.

## Required starting point

- **MHI2_ER_SEG11_P4709 / MU1447**, 790-family cockpit, 1010×376 auxiliary surface.
- A working **omonob public wired v2.1.0-rc.7 MU1447/790** installation, including its original core and 1,826-byte launcher. The base wired installation is an upstream dependency; these add-ons do not install it from stock.
- Working root SSH access, adequate storage, a readable SD card and stable power. The installers preserve existing SSH credentials and do not install SSH.
- Wired cockpit maps must already work before adding wireless. Restore conflicting/older wireless implementations using their own verified backups first.
- Keep the original packages and all unit backups. Never skip a failed identity, space, backup or Java check.

The checks pin exact native inputs or before/after hashes. A matching model name is insufficient. Do not flash another car's full firmware or manually replace a refused input.

## Download and prepare

Download the ZIPs from [downloads](../downloads/README.md), verify their SHA-256 values, and extract each entire versioned folder to the SD root. Keep folder names and contents intact. Use the QNX paths below, not the Mac/Windows drive path. SD1 is normally `/fs/sda0`; substitute the verified mount point if different.

The SD install needs no Python, JDK or QNX compiler. Native helpers are included. Do not recursively copy these packages into the small `/ramdisk`; their installers stage individual files themselves. `/dev/shmem` does not support normal subdirectory workflows on this target.

## Recommended order for a fresh supported wired baseline

| Order | ZIP | Purpose |
|---:|---|---|
| 1 | `MU1447-Wired-Display-v0.1.1.zip` | Fixed 70% cockpit scaling and ETA request |
| 2 | `MU1447-Wired-Layout-v0.2.zip` | Correct actual Off/Left/Right/Center card mapping |
| 3 | `MU1447-Center-Down-v0.1.zip` | Final Center Y=76 placement |
| 4 | `MU1447-Native-Wireless-v1.0-rc1.3.zip` | Persistent native wireless base |
| 5 | `MU1447-Wireless-Network-v0.1.zip` | Existing-queue firewall/QoS correction |
| 6 | `MU1447-Wireless-Layout-v0.1.zip` | Wireless placement matches recognized wired core |
| 7 | `MU1447-Wireless-Runtime-v0.1.zip` | Camera/touch/session/startup corrections |
| 8 | `MU1447-Wireless-Startup-v0.1.zip` | One-file touch-readiness wake correction |

If an item is already installed successfully, do not restore it just to repeat this sequence. Apply only the missing supported layers, checking each. The exact installed state determines what its checker accepts.

For every package:

1. Read that ZIP's README. Disconnect an active CarPlay session when its instructions require it.
2. Run `--check` in the car SSH terminal.
3. Continue only on its documented PASS. Save failure output and stop on a mismatch.
4. Run `--apply`.
5. Wait for the documented installed result, then perform the normal manual infotainment restart requested by that package. Recheck basic operation before moving to the next layer.

Example for the final correction:

```sh
/bin/ksh /fs/sda0/MU1447-Wireless-Startup-v0.1/install.sh --check &&
/bin/ksh /fs/sda0/MU1447-Wireless-Startup-v0.1/install.sh --apply
```

Normal restarts are required to load the changed Java/native runtime. No automatic reboot is performed. The wireless installation and runtime corrections are persistent after successful installation; the SD is not needed for ordinary automatic startup, but retain it for restoration.

The original rc1/rc1.1/rc1.2 wireless installer failures are superseded by rc1.3. If rc1.2 left an unfinished `baseline_seal` backup, use rc1.3's documented `--recover-backup` before proceeding. This verifies and preserves that backup. Do not delete it or bypass the seal.

## Wi-Fi configuration used in the successful test

In the car's regular settings, disable its **internet-client/uplink connection and automatic search/join**, while keeping the **WLAN hotspot enabled** for the iPhone. This is a manual setting, not a change silently applied by any package. It avoids joining the home Wi-Fi during startup. See [status](STATUS.md) for the limits of the result.

For SSH with this configuration, connect the computer to the car hotspot. The established car-hotspot address on the tested unit is `10.173.189.1`:

```sh
ssh -o ConnectTimeout=10 -o ConnectionAttempts=1 -o ControlPath=none \
  -o HostKeyAlgorithms=+ssh-rsa root@10.173.189.1
```

Use the unit's existing password or your own already-authorized SSH key. None is included. A home-network IP stops being usable when the car no longer joins that network. Other units may use another hotspot address; verify it rather than assuming the example applies.

## First parked checks

Check centre-screen video, touch and audio; camera-screen controls and return; cockpit map and ETA on an active route; app switching; a phone call; a wired session; then a later startup after full vehicle sleep. The current report does not certify every one of these scenarios.

If pairing is stuck, follow upstream pairing guidance and the package README. Do not delete the unit's identity or phone pairing-store files. No pairing reset is required by the runtime or startup corrections themselves.
