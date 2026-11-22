# MU1447 Center down 20 pixels — experimental v0.1

Follow-up to the installed MU1447-Wired-Layout-v0.2 patch only.
Moves Center's safe rectangle from **628×185 @191,56** to **628×185 @191,76**.
Both top and bottom move down 20 source pixels. Off, Left, Right, 70% zoom,
ETA requests and all executable code remain unchanged. Exactly one data byte
changes at file offset 0x6f5c. The phone/app controls final rendered placement.

Experimental: not yet visually checked in the car. Use at your own risk.

Extract the whole MU1447-Center-Down-v0.1 folder to SD root. Disconnect USB CarPlay.
Run in the car's SSH terminal:

```sh
/bin/ksh /fs/sda0/MU1447-Center-Down-v0.1/install.sh --check
```

With WIRED_CENTER_CHECK=PASS state=BEFORE:

```sh
/bin/ksh /fs/sda0/MU1447-Center-Down-v0.1/install.sh --apply
```

Wait for WIRED_CENTER=INSTALLED, manually restart, reconnect by USB and select Center.

Undo this adjustment (then manually restart again):

```sh
/bin/ksh /fs/sda0/MU1447-Center-Down-v0.1/install.sh --restore
```

Backup: /mnt/app/.mu1447-center-down-v01/core-before.so .
Restore this adjustment before restoring/uninstalling older layout add-ons.
Unknown cores are refused. Original backups are retained.

Local checks: one-byte diff, shell syntax, check/apply/repeated apply and exact rollback
in a host fixture. Native comparator is inherited from the previous wired patch.
The original core derives from the supplied omonob MU1447 rc.7 package.
