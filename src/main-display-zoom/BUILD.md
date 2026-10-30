Use the existing local image mhi2-qnx65-armv7-public:4.9 (QNX SDK not redistributed).
Mount either source/menu-native or source/legacy-native as
/work/private/development/mu1409-wp2-r57/src/native (read-only), and its
altscreen111-gen2 subdirectory as /diag/source (read-only). Mount a writable
output directory as /diag; run the included build_receiver_inside.sh.
Build each variant separately. Both keep their own matching settings registry.
The original shared library is not included. The installer saves exact originals.
