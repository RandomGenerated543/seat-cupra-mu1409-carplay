/* Exact storage primitives required by R57's guarded profile transaction.
 * Only fixed, exclusively created project probe files are ever modified. */
#define _POSIX_C_SOURCE 200809L
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
int main(int argc,char **argv){
    const char *dir="/mnt/app/root/altscreen-u2/wp2";
    const char *before="/mnt/app/root/altscreen-u2/wp2/.storage-probe-new";
    const char *after="/mnt/app/root/altscreen-u2/wp2/.storage-probe-ready";
    const char *step="mount_identity";const char value[]="SEAT-WP2-STORAGE-PROBE\n";
    struct stat root,owned,st;struct statvfs fs;char data[sizeof(value)];
    int fd=-1,parent=-1,created=0,renamed=0,rc=1,saved;
    if(lstat("/mnt/app",&root)||lstat(dir,&owned)||!S_ISDIR(owned.st_mode)||
       root.st_dev!=owned.st_dev||statvfs("/mnt/app",&fs))goto done;
    if(argc==2&&!strcmp(argv[1],"--readonly")){
        if(fs.f_flag&ST_RDONLY){puts("WP2_STORAGE_STATE=READONLY");return 0;}
        return 1;
    }
    if(argc!=1||(fs.f_flag&ST_RDONLY))goto done;
    step="exclusive_paths";
    if(!lstat(after,&st)||errno!=ENOENT)goto done;
    fd=open(before,O_WRONLY|O_CREAT|O_EXCL,0600);if(fd<0)goto done;created=1;
    step="write_fsync";
    if(write(fd,value,sizeof(value)-1)!=(ssize_t)(sizeof(value)-1)||fsync(fd))goto done;
    if(close(fd)){fd=-1;goto done;}fd=-1;
    step="native_rename";
    if(rename(before,after))goto done;renamed=1;
    step="directory_fsync";
    parent=open(dir,O_RDONLY);if(parent<0||fsync(parent))goto done;
    step="readback";
    fd=open(after,O_RDONLY);if(fd<0||fstat(fd,&st)||!S_ISREG(st.st_mode)||
       st.st_dev!=root.st_dev||st.st_size!=(off_t)(sizeof(value)-1)||
       read(fd,data,sizeof(data))!=(ssize_t)(sizeof(value)-1)||
       memcmp(data,value,sizeof(value)-1))goto done;
    if(close(fd)){fd=-1;goto done;}fd=-1;
    step="cleanup_fsync";
    if(unlink(after))goto done;renamed=0;created=0;
    if(fsync(parent))goto done;
    rc=0;
done:
    saved=errno;
    if(fd>=0)close(fd);
    if(created)unlink(renamed?after:before);
    if(parent>=0)close(parent);
    if(rc)printf("WP2_STORAGE_PROBE=FAIL step=%s errno=%d production_files_changed=0\n",step,saved);
    else puts("WP2_STORAGE_PROBE=PASS native_rename=1 file_fsync=1 directory_fsync=1 readback=1");
    return rc;
}
