# Prerequisites

**Highly experimental; [read the disclaimer](../DISCLAIMER.md).**

The recorded target is MHI2_ER_SEG11_P4708_1 / MU1409 with the fitted 790-family
cockpit. A similar firmware name, MU number or brand is insufficient.

Before vehicle testing, establish exact hashes of libairplay.so, dio_manager,
displaymanager, smartphone_integrator, lsd.jxe and live startup/configuration.
The historical reference hashes are in config/mu1409-reference-hashes.sh;
they are evidence, not permission to overwrite a differing unit.

The guarded receiver upgrade requires the matching existing project stack:
owner protocol 2, its /dev/mlb/isoTX2 exclusive-writer gate, matching original
H264/TS transport, compatible settings broker/menu and exact startup/SafeArea
preimages. It is not an omonob or stock-to-project migration installer.
Unexpected existing bytes must stop the operation.

Use a parked vehicle, adequate stable power, a verified read-only inventory and
independent copies of original files plus an accessible recovery method.
Preserve independently installed M.I.B. prerequisites such as NavActiveIgnore;
they are not bundled or automatically replaced here.

For building, supply a validated QNX 6.5 ARMv7 compiler/sysroot, a workstation
C compiler, Python 3 and a JDK. Menu build additionally requires ECJ 3.26.0,
the exact target API compile JAR and two locally prepared OEM hooks. Do not
upload SDKs, firmware or generated vendor-hook classes to this public repository.

Credentials are provisioned per unit into RAM by the existing boot/control
flow. Never reuse another owner's secret/token or paste it into an issue.
