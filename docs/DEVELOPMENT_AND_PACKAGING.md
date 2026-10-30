# Source, dependencies and packing a release

**Experimental software, no warranty.** Building successfully is not target acceptance. No build command should connect to or flash a vehicle/adapter.

## Source map

- src/native/altscreen111-gen2: target receiver, original compressed-video path, queue recovery, SEAT view/settings bridge and wheel adapter.
- src/native/alt111-settings and src/native/mibr-control: authoritative settings registry, versioned control broker, durable profile transactions and recovery.
- src/menu/java/de/mibr/hmi and settings/registry.json: native English HOME/menu source, popup/scroll work, cockpit zoom-factor selector.
- src/media-info: project media bridge/state model, original-bytecode hook transformer, build/package tools and tests for cockpit AudioSD title/artist/album.
- src/main-display-zoom and its release ZIP's source/: separate centre-display experiment, complete fixed/menu receiver variants and test harnesses.
- runtime/: startup/firewall/writer/ownership/settings scripts. Preserve existing internal runtime paths; do not rename them because an adapter's public label changed.
- deployment/full-install and scripts/assemble_consolidated_install.py: baseline-pinned fresh-stack assembly; not a universal firmware installer.
- adapters/source/*.zip: neutral-labelled adapter source-only snapshots. Full matching release ZIPs retain the stock build inputs and firmware images required by their build recipes.

## Dependencies

| Task | Dependencies |
|---|---|
| Install compiled car ZIP | Working authorized SSH, matching car baseline, readable/writable SD, stable power, backups/recovery. No SDK/compiler on the unit. |
| Flash compiled adapter ZIP | Matching model/system/protocol, computer, adapter Wi-Fi/web updater, Python 3.12+; model-specific shell wrapper optional. No car SSH. |
| Host checks | Python 3, workstation C compiler, JDK for Java tests; environment variables CC/JAVA/JAVAC as documented. |
| Native SEAT build | Legally obtained compatible QNX 6.5 ARMv7 compiler/sysroot, compatible Docker build environment where used, ARM softfp/VFPv3-D16 flags and pinned source dependencies. |
| Menu build | Exact local MU1409 API compile JAR and target-bound OEM hooks, ECJ 3.26.0, JDK; class format 46/Java 1.2 target. |
| Media build | Exact local target API and original Java class inputs, JDK/ECJ and bytecode transformer; see src/media-info/build.py. Set MU1409_WORKSPACE to a prepared build workspace. |
| AX adapter build | Per-package Zig/MIPS32r2/o32/glibc constraints, Python build/ELF tools and exact stock archive; full Mini5 build additionally uses the pinned SquashFS/LZO tooling/container. |
| HW301 build | Per-package ARM cross-build/Docker tools, exact vendor v129 app image and upstream shim sources. Read its source/build recipe; do not use MIPS outputs. |

QNX SDKs, recovered target API/JXE/JAR inputs, MFi keys/certificates, private runtime secrets and full firmware dumps are not supplied as general build dependencies. Do not upload them or another tester's backups/logs.

## Host checks and builds

```sh
python3 scripts/audit_publication.py
python3 scripts/test_host.py
```

Read BUILD.md for native/menu compiler setup. The source tree includes the cockpit-menu zoom extension; the historical foundation receiver-only artifact remains pinned to its original fixed-70% build. These are different versions. Reproducible hashes must match the component being built; never force a rebuilt receiver into an older guarded installer by editing its expected hash. The centre-screen candidate is a separate variant, not silently enabled for every build.

## Packing an installation ZIP

1. Assemble only the matching baseline using scripts/assemble_consolidated_install.py and its explicitly pinned local inputs. For feature updates use that feature's build/package script and target preimage checks. Keep fresh-install and existing-stack upgrade paths separate.
2. Include the complete named folder: installer/uploader, required payloads/images, target manifests, KIT.sha256 or equivalent, instructions, disclaimer, source/license material and the applicable rollback inputs. Never include a tester's original-backup/ or current secret/profile captures.
3. Generate SHA-256 manifests **after** finalizing public labels/docs. Do not change any candidate/rollback firmware byte merely to remove a document label. Verify ZIP integrity and every image hash after repacking.
4. Run the relevant host/ABI/installer/uploader tests. State exactly what was and was not tested on hardware.
5. Produce a release-level SHA256SUMS.txt and catalogue with model, vendor, system/protocol, scope (app-only/full image), version and source provenance. Do not name packages after owners/testers.
6. Upload runtime files as **GitHub Release assets**, especially large firmware ZIPs. Keep project source and dependency/build docs in Git. Mark the release pre-release/experimental. Download the published artifacts and verify their hashes before calling publication complete.

This handoff preserves the already-built guarded runtime layers instead of inventing a new combined installer during publication. The source-only release snapshot excludes the runtime downloads/build caches and does not contain the SDK or private firmware extraction inputs. Installer recovery remains tied to the exact original kit and stored before-images.

Receiver identity check: the legacy foundation payload is verified with the default profile; the current cockpit-menu source uses `python3 scripts/verify_receiver.py FILE --profile menu-zoom`. The Docker source builder selects that profile. This does not permit applying the new receiver alone to the old broker/menu.
