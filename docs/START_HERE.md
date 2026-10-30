# Choose the correct installation

**Highly experimental. Use at your own risk. No warranty or liability to the extent permitted by law. Read ../DISCLAIMER.md.**

There are two independent products: software installed on the car's MHI2 unit, and firmware installed on a USB wireless adapter. An adapter does not install cockpit-map support on an unmodified head unit.

| Your situation | Correct path |
|---|---|
| Matching SEAT MU1409, no project installed | Use a matching final-stack baseline A or B, after the matching existing mod's uninstaller and normal restart. Follow NEWBIE_INSTALL.md. |
| Existing working project stack | Do not reinstall WP1/final-stack. Use only the applicable feature updates whose checks pass. |
| P4709/MU1447, MHI2Q, Skoda/Audi/VW or another Java image | Do not use the SEAT MU1409 installer. An already-working wired cockpit mod for that target can be used with a separately qualified adapter. |
| Wired cockpit maps already work; want wireless | Choose by the adapter's actual identity/firmware in ../adapters/README.md. Do not choose by vehicle owner or housing shape. |

Installing the consolidated final stack already includes the WP1 video/writer/ownership/firewall/startup foundations and WP2 menu/control. Do not replay historical WP1 then WP2 upgrade kits on top. The source download is not the assembled installation kit.

On the car, installers run through SSH from an SD card. On an adapter, uploaders run on a computer connected to the adapter's Wi-Fi. Commands for one are not commands for the other.

## Required vehicle test and fresh phone pairing

A bench/computer may be used for upload and build verification. Functional acceptance MUST be tested in the actual compatible car, with its working head unit and Virtual Cockpit. A bench unit without the cockpit can produce misleading black-screen/no-map results.

After flashing reports completion and the documented reboot/power cycle is finished, remove the OLD adapter pairing from the iPhone: Settings > Bluetooth > the adapter > Forget This Device; also Settings > General > CarPlay > the matching adapter/car entry > Forget This Car if that entry exists. Do not erase unrelated pairings. Then connect the adapter in the parked car and pair it again as a new connection, with Bluetooth and Wi-Fi enabled, approving CarPlay. Old pairing/cache state can prevent correct connection after an update.

Verify centre-screen video/audio first, then cockpit maps, app-supported zoom, disconnect/reconnect and OEM return. A version string or retained build marker alone is not a car test. Fresh pairing does not cure wrong hardware/firmware. Collect logs before a restart/rollback if it fails.


See [open issues](OPEN_ISSUES.md) for known limits.
