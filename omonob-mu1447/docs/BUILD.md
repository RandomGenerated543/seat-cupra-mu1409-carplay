# Source map and build dependencies

This branch publishes the adaptation and patch code. It does not contain the full OEM firmware source, Apple AirPlay SDK, QNX sysroot, MFi private material or complete implementation source of shared opaque upstream native dependencies.

| Directory | Content |
|---|---|
| `src/wired-display` | Type-111-only zoom wrapper, wired URL/safe-area patcher, comparator and tests |
| `src/wired-layout` | Correct card/view mapping, URL/rectangle patch and tests |
| `src/wireless-base` | MU1447 target touch adaptation, original ownership/bootstrap patchers, BT normalization shim, receiver scaling helper, exact binary deltas and base installer/tests |
| `src/wireless-network` | Runtime PF/QoS rules, watcher and transaction tests |
| `src/wireless-layout` | Receiver layout/URL helper and binary/installer tests |
| `src/wireless-runtime` | Runtime v0.1 helper source, QNX read-only session/startup guard, two corrected scripts and tests |
| `src/wireless-startup` | Subsequent CP event-wake patch and current helper/build/test sources; supersedes the runtime CP archive after installation |
| `src/packages` | Reviewable original installer/readme/baseline metadata for each exact ZIP |
| `downloads` | Original delivered SD archives, byte-exact |

Use the original source/build notes inside each ZIP and its module. Native patched outputs require exact input hashes. Newer startup helper sources include the preceding runtime changes; the sequence still uses the delivered Runtime and Startup installers, not a newly invented combined binary.

## Dependencies used in the retained workspace

- Python 3.
- JDK 21 for build-time tools; ASM and ASM-tree 9.7.
- Exact MU1447 firmware-derived `lsd.jar`/JXE and OEM input classes, plus the supplied original CP/Touch/bootstrap donor jars.
- The supported public wired v2.1.0-rc.7 MU1447/790 menu, core and launchers.
- The supplied manual MU1447 wireless runtime and its exact native receiver/helper input files.
- QNX 6.5 ARMv7 compiler/binutils/sysroot, used through the local Docker image `mhi2-qnx65-armv7-public:4.9`; ARMv7 soft-float ABI conventions.
- A host C compiler for fixture tests and Python `unicorn` for ARM instruction tests.

Runtime helper classes are normalized to class version 46 with unsupported newer bytecode rejected. Metadata/ABI tests and the real-unit J9 check are separate requirements. A modern host JVM pass alone does not certify the target runtime.

The historical builders are **workspace builders, not standalone one-command builds**. The browsable copy replaces personal development paths with `/path/to` placeholders. Several scripts also expect retained intermediate files and sibling projects. Adapt those locations using the exact donor inputs and each module's original notes. Do not silently substitute a different MU version. The original ZIP sources are kept unchanged for provenance.

## Validation and packaging

`tools/verify_publication.py` verifies all published ZIP identities and their internal manifests, scans the nested archives for disallowed private-file names, checks source/branch separation and confirms the documented correction chains. It requires only Python 3 and does not contact a car or execute a native payload.

```sh
python3 omonob-mu1447/tools/verify_publication.py
```

Sources and installers are already inside their corresponding SD ZIPs. The outer `downloads/SHA256SUMS.txt` verifies exact archives; each ZIP contains its own file manifest. Checksums detect changes, not publisher identity. The original installer refuses unknown live inputs and builds/seals its own unit backup.

The publication only adds documentation and source/archive copies. It does not modify or rebuild the delivered vehicle payloads. Never treat GitHub's repository source ZIP as the extracted SD installation folder.
