/* SPDX-License-Identifier: GPL-3.0-or-later
 * Cooperative ownership shared by the MU1409 DisplayManager gate and remux.
 * Never unlink the lock file: a replaced inode would create two lock domains.
 * POSIX record locks are process scoped; callers serialize their own threads.
 */
#ifndef MIBR_MOST_OWNER_H
#define MIBR_MOST_OWNER_H
#include <errno.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#define MIBR_OWNER_PROTOCOL 2
#define MIBR_OWNER_PATH "/fs/tmpfs/mibr-isotx2-owner.lock"
#define MIBR_DIRECT_MARKER "/tmp/mibr-isotx2-gate.direct"
static inline int mibr_owner_set(int fd, short type)
{
    struct flock fl;
    memset(&fl, 0, sizeof(fl));
    fl.l_type = type;
    fl.l_whence = SEEK_SET;
    /* Whole file, with no blocking syscall: policy owns the bounded retry. */
    return fcntl(fd, F_SETLK, &fl);
}
static inline int mibr_owner_direct(int fd)
{
    unsigned n;
    for (n = 0; n < 500; ++n) {
        if (access(MIBR_DIRECT_MARKER, F_OK) != 0) {
            errno = ECANCELED;
            return -1;
        }
        if (mibr_owner_set(fd, F_WRLCK) == 0) return 0;
        if (errno != EACCES && errno != EAGAIN && errno != EINTR) return -1;
        usleep(10000);
    }
    errno = ETIMEDOUT;
    return -1;
}
#endif
