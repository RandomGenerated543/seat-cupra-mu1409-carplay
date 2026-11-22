# Exact MU1447 SD packages

**Highly experimental; install at your own risk.** Read [the required starting point and installation order](../docs/INSTALL.md) before downloading. These are add-ons for the exact omonob MU1447/790 setup. They are not firmware updates, MU1409 packages or a stock-to-wireless installer.

Download the versioned ZIPs using each file's **Raw / Download raw file** control. Keep the names intact. Extract the entire versioned folder to the SD root and read the README inside it. Install/check/restore commands run in the car's root SSH terminal, not on the computer.

| Order | Package |
|---:|---|
| 1 | [Wired Display v0.1.1](MU1447-Wired-Display-v0.1.1.zip) |
| 2 | [Wired Layout v0.2](MU1447-Wired-Layout-v0.2.zip) |
| 3 | [Center Down v0.1](MU1447-Center-Down-v0.1.zip) |
| 4 | [Native Wireless v1.0-rc1.3](MU1447-Native-Wireless-v1.0-rc1.3.zip) |
| 5 | [Wireless Network v0.1](MU1447-Wireless-Network-v0.1.zip) |
| 6 | [Wireless Layout v0.1](MU1447-Wireless-Layout-v0.1.zip) |
| 7 | [Wireless Runtime v0.1](MU1447-Wireless-Runtime-v0.1.zip) |
| 8 | [Wireless Startup v0.1](MU1447-Wireless-Startup-v0.1.zip) |

The order shows prerequisites, not a request to reinstall layers that are already applied. Restore in [reverse order](../docs/RECOVERY.md). Do not run earlier restorers over later changed files.

All eight ZIPs are the original delivered archives, not regenerated builds. The later observed result is in [status](../docs/STATUS.md). Original “untested” package text remains as written at build time.

## Verify on your computer

Download [SHA256SUMS.txt](SHA256SUMS.txt) beside the ZIPs. On macOS/Linux:

```sh
shasum -a 256 -c SHA256SUMS.txt
```

On Windows PowerShell, calculate one archive and compare its value with the matching manifest row:

```powershell
Get-FileHash .\MU1447-Wireless-Runtime-v0.1.zip -Algorithm SHA256
```

[PACKAGES.json](PACKAGES.json) also records archive sizes and identities. A checksum verifies file identity; it does not establish compatibility with a different unit or guarantee successful recovery.
