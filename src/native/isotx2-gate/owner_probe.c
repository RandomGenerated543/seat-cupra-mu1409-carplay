/* SPDX-License-Identifier: GPL-3.0-or-later
 * Target runtime dependency check: QNX4 temporary filesystem only, never MOST.
 */
#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include "../common/most_owner.h"
int main(void)
{
    int fd, status, n;
    pid_t child;
    char dir[128];
    printf("OWNER_PROBE path=%s protocol=%d\n",MIBR_OWNER_PATH,MIBR_OWNER_PROTOCOL);
    fflush(stdout);
    snprintf(dir,sizeof(dir),"/fs/tmpfs/mibr-owner-probe.%ld",(long)getpid());
    if(mkdir(dir,0700)<0) {perror("owner probe mkdir");return 25;}
    if(rmdir(dir)<0) {perror("owner probe remove empty directory");return 26;}
    fd=open(MIBR_OWNER_PATH,O_RDWR|O_CREAT,0600);
    if(fd<0) {perror("owner probe open");return 20;}
    for(n=0;n<100;n++) {
        if(mibr_owner_set(fd,F_WRLCK)==0) break;
        if(errno!=EACCES && errno!=EAGAIN && errno!=EINTR) {perror("owner probe lock");close(fd);return 21;}
        usleep(10000);
    }
    if(n==100) {puts("OWNER_PROBE=BUSY");close(fd);return 22;}
    child=fork();
    if(child<0) {perror("owner probe fork");close(fd);return 23;}
    if(child==0) {
        int other=open(MIBR_OWNER_PATH,O_RDWR);
        int ok=other>=0 && mibr_owner_set(other,F_RDLCK)<0 && (errno==EACCES || errno==EAGAIN);
        if(other>=0) close(other);
        _exit(ok?0:1);
    }
    if(waitpid(child,&status,0)!=child || !WIFEXITED(status) || WEXITSTATUS(status)!=0) {
        puts("OWNER_PROBE=FAIL_CONFLICT_NOT_ENFORCED");close(fd);return 24;
    }
    close(fd);
    printf("OWNER_PROBE=PASS protocol=%d directories=PASS conflict=PASS\n",MIBR_OWNER_PROTOCOL);
    return 0;
}
