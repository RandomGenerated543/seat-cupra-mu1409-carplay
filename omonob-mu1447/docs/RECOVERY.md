# Restore order

Each installer has its own backup and exact before/after checks. Restoration is a supported file transaction, not a guarantee of recovery if SSH, storage or hardware has failed. Retain all backups and stable power.

For a complete stack installed in the documented order, restore in reverse order. Disconnect CarPlay first where the individual README requires it; run each command from the unit's SSH terminal and perform its requested normal restart.

```sh
/bin/ksh /fs/sda0/MU1447-Wireless-Startup-v0.1/install.sh --restore
/bin/ksh /fs/sda0/MU1447-Wireless-Runtime-v0.1/install.sh --restore
/bin/ksh /fs/sda0/MU1447-Wireless-Layout-v0.1/install.sh --restore
/bin/ksh /fs/sda0/MU1447-Wireless-Network-v0.1/install.sh --restore
/bin/ksh /fs/sda0/MU1447-Native-Wireless-v1.0-rc1.3/install.sh --restore
```

These are separate steps, **not a block to paste and run without checking each result**. Restore only packages that are actually installed. The base wireless restore returns to the wired setup it saved and retains phone pairing data. Stop after that if you want to keep the wired display/layout improvements.

To remove the wired add-ons as well:

```sh
/bin/ksh /fs/sda0/MU1447-Center-Down-v0.1/install.sh --restore
/bin/ksh /fs/sda0/MU1447-Wired-Layout-v0.2/install.sh --restore
/bin/ksh /fs/sda0/MU1447-Wired-Display-v0.1.1/install.sh --restore
```

If the superseded ETA-only v0.1 add-on was installed before Wired Layout v0.2, restoring that layout may return its core to the ETA-only state. Restore the original ETA-only package at that point, before Wired Display. The ETA-only add-on is not required for new installations; retain your historical package if your backups depend on it.

Restore Startup before Runtime: Startup changes the CP archive and the older Runtime installer correctly refuses that later archive. Likewise, restore Runtime, Wireless Layout and Network before the base wireless restore. Do not force another installer's backup into place.

## Backup locations

| Package | Unit backup |
|---|---|
| Wired Display | `/mnt/app/.mu1447-wired-display-v011` |
| Wired Layout | `/mnt/app/.mu1447-wired-layout-v02` |
| Center Down | `/mnt/app/.mu1447-center-down-v01` |
| Wireless base | `/mnt/app/.mu1447-native-wireless-v1-backup` |
| Network | See its original README/installer |
| Wireless Layout | `/mnt/app/.mu1447-wireless-layout-v01` |
| Runtime | `/mnt/app/.mu1447-wireless-runtime-v01` |
| Startup | `/mnt/app/.mu1447-wireless-startup-v01` |

A backup being present is not proof that the corresponding correction is still installed: successful restores retain backups. Use the installer status/check output and actual identities. Do not remove locks or backups blindly after a failure. Save the full output; unknown later edits are intentionally refused.

A restore to a wired baseline is not a firmware-upgrade guide. Do not run MU1409 restore packages on MU1447 or restore a different vehicle's files.
