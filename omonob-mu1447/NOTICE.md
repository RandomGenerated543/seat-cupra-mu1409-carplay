# Attribution and dependency notice

This MU1447 integration builds on omonob’s public wired/wireless CarPlay Maps work, the supplied manual MU1447 materials, the public rc.7 SEAT profile and community contributions retained in `CREDITS.upstream.md`. Sources: [wired project](https://github.com/omonob/VW-MHI2-Carplay-Maps) and [wireless project](https://github.com/omonob/VW-MHI2-Wireless-Carplay-Maps). This package is a separate experimental local adaptation, not an upstream-endorsed release.

The GPL text for upstream public project code is retained as `LICENSE.upstream`. It does not automatically license OEM classes, Apple/QNX dependencies or opaque native binaries. Their owners retain all rights and existing notices. Do not treat this SD candidate as authorization to redistribute third-party proprietary dependencies. New patch logic and its tests are supplied under GPL-3.0-or-later, without warranty; this does not relicense the inputs. No full firmware image or private authentication keys are included.

QNX documents zero as the current thread for `pthread_setname_np`: [QNX reference](https://qnx.com/developers/docs/6.4.0/neutrino/lib_ref/p/pthread_setname_np.html). The added shim normalizes that argument for bookkeeping; on-device acceptance is still required.
