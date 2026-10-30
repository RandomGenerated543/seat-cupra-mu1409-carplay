# MU1409 CarPlay AudioSD metadata bridge

Experimental source candidate for song title, artist and album on the cockpit Audio/Media page. Host-built and tested; **vehicle acceptance outstanding**. This does not add text to the map page or implement artwork/progress/shuffle.

Reference architecture: [xPaiiN/mst2-carplay-vc](https://github.com/xPaiiN/mst2-carplay-vc), pinned at `f1ac169d1ce40b291d9a2ab6a0d97fe53474754f`. No MST2 source or installer is copied into this module. MHI2 uses its existing DSI metadata callbacks and OEM AudioSD output, rather than MST2 PPS polling.

## Build

Requires the owner's exact converted MU1409 `lsd.jar`, compile-only target API JAR, ECJ 3.26.0 and JDK 21 in the existing project workspace. Those OEM inputs are deliberately excluded. `BUILD.json` records the input/output hashes and the six patched methods. An ASM patch inserts fail-open hooks; all 148 untouched methods retain their original bytes. Classes target format 46.

Set `MU1409_WORKSPACE` to the absolute path of the existing SEAT-CUPRA-MU1409-AltScreen workspace, then run from this module:

```sh
python3 build.py
python3 package.py
python3 tests/test_installer.py
```

`package.py` additionally requires the exact consolidated R13 startup baseline at `work/seat-public-handoff/repo/build/SEAT-MU1409-final-stack-candidate-v0.2.1/payload/hmi-startup.sh` inside that workspace. It refuses an unknown baseline. It generates owner-only deployment scripts/payloads from those local inputs. It does not make the package suitable for another firmware.

## Scope and evidence

- DSI listener lifecycle follows the existing CarPlay target; invalid/disconnected metadata clears the cached track.
- Only the CarPlay branch of CurrentStationInfo receives metadata. Refresh is queued on its existing BAP task.
- Independent priority JAR; existing menu and native receiver binaries are not replaced.
- Host verification: 12 model assertions, 15 bridge assertions and eight installer fixture cases passed. See `BUILD.json` and `INSTALLER-TESTS.json`.
- Target J9 loader, actual DSI registration, cockpit field support, visible output, wireless metadata forwarding and OEM source transitions still require on-unit acceptance.

Installation and rollback instructions are in `package/README.md`. Use the generated complete SD package, not these source files. Unknown startup hashes are refused; preserve the failure output instead of bypassing the check.

Project-owned source follows the parent repository license. Target-derived OEM classes/startup files are not supplied in this source module. See the parent disclaimer; this is not an accepted release.
