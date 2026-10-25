# Build from source

**Highly experimental; [use at your own risk](../DISCLAIMER.md).**
No build script connects to the car.

## Source boundaries

The exact latest tested receiver is src/native/altscreen111-gen2, including
the target settings/view bridge, automatic wheel adapter, zoomFactor=70 and
bounded raw-Annex-B recovery. Corresponding public settings/policy/hash sources
and the authorized R13 broker are in src/native. Source origins are recorded.

Menu source in src/menu/java/de/mibr/hmi contains the project-owned R13 classes
plus the dropdown/red-scrollbar changes. Vendor Activator/WidgetFactory source,
firmware/API classes and SDKs must be supplied locally and are not redistributed.

## Workstation checks

Use Python 3, a C compiler and a JDK (JAVAC/JAVA may select non-default paths):

```sh
python3 scripts/audit_publication.py
python3 scripts/test_host.py
```

## Exact receiver with the existing validated compiler image

Provision a compatible/legally obtained QNX 6.5 ARMv7 compiler/sysroot yourself.
The tested local image name was mhi2-qnx65-armv7-public:4.9; this repository does
not distribute the image, SDK or sysroot and does not download it automatically.
With that validated local image and Docker running:

```sh
bash scripts/build_receiver_docker.sh
```

The builder maps historical **container-only** source paths to reproduce the
original compile/debug identity, with no dependency on the author's workspace.
scripts/verify_receiver.py refuses a differing receiver hash for substitution
into the guarded update. Toolchain differences can change output bytes; do not
silently replace the pinned payload or relax the guard after a mismatch.

## Other native tools and TS remuxer

Inside the validated cross-build environment, run scripts/build_native_tools.sh
with QCC set if needed. It builds the R13-compatible broker/settings/tools and
owner-protocol-2 support from source; it does not install them. Executing a
compiler successfully is not proof of a new target's compatibility.

The retained tools/build_direct_ts_remux.sh builds FFmpeg 6.1.5 from its pinned
source download and hash, then the original-H264 TS remuxer. It needs normal host
build dependencies/network access and a compatible compiler. No FFmpeg-linked
binary, transcoder or x264 experiment is shipped in this handoff.

## Local menu build

Set JAVA to a workstation Java executable, ECJ_JAR to ECJ 3.26.0,
SEAT_API_JAR to the locally recovered exact MU1409 API compile JAR, and
OEM_HOOKS_DIR to target-bound local source containing:
- de/vw/mib/cio/internal/Activator.java
- generated/de/vw/mib/global/view/internal/WidgetFactoryImpl.java

These must be the correct per-target hooks invoking the project menu adapter,
not arbitrary stock/Skoda classes. Obtaining/binding them is a target integration
step; this repository cannot supply redistribution rights to OEM code.

```sh
python3 scripts/build_menu.py
```

The output is build/menu/LOCAL-ONLY-menu.jar, class major 46. It includes the
locally supplied OEM-derived hooks and is deliberately ignored by Git.
Keep it local. A compiled JAR is not vehicle/menu/Back/focus acceptance.

## Consolidated final-stack bundle

See CONSOLIDATED_INSTALL.md. `scripts/assemble_consolidated_install.py` assembles
the final components supplied locally, verifies pinned input hashes, and produces
a local-only ZIP under build/. It does not recompile missing inputs, download
OEM files or synthesize compatibility approval for another baseline.

## Installation boundary

No universal fresh installation is claimed. Building source does not create a
generic supported SD installer. The separate receiver upgrade works only on the exact
already-matching project baseline. For another unit, perform exact firmware,
loader, startup, media-owner, Java and recovery qualification first.
