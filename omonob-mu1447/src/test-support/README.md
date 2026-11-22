# Host bytecode-test support

`JavaAudit.java` contains the child-first class loader, ASM replacement helper and reflection accessors used by Runtime/Startup tests. Compile it on the modern host alongside ASM/ASM-tree; it is not a class installed into the head unit.

Its `main` reproduces defects in the older pre-correction runtime. The current regression tests use its utility methods rather than treating that older-defect reproduction as a current acceptance test. Paths in the retained module test scripts must be adapted to include this compiled support directory and the exact OEM/menu dependency jars. See the build guide.
