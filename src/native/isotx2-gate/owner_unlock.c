/* SPDX-License-Identifier: GPL-3.0-or-later
 * Remove only our empty startup lock directory, using QNX libc directly.
 * No recursive deletion and no caller-supplied path.
 */
#include <errno.h>
#include <stdio.h>
#include <unistd.h>
int main(void) {
    if (rmdir("/fs/tmpfs/mibr-direct-start.lock") == 0 || errno == ENOENT) return 0;
    perror("owner-unlock");
    return 1;
}
