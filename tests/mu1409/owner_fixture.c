/* SPDX-License-Identifier: GPL-3.0-or-later; HOST fixture, never ship to vehicle. */
#include <stdio.h>
#include <stdlib.h>
#include <sys/uio.h>
#include "../../src/native/common/most_owner.h"
int main(int argc,char **argv)
{
 int fd,lockfd=-1,n;
 const char *v;
 struct iovec iov;
 if(argc!=3)return 64;
 if(strcmp(argv[1],"contend")==0) {
  lockfd=open(MIBR_OWNER_PATH,O_RDWR);
  if(lockfd<0)return 10;
  n=mibr_owner_set(lockfd,F_WRLCK);
  close(lockfd);
  return n<0 && (errno==EACCES||errno==EAGAIN)?0:11;
 }
 if(strcmp(argv[1],"direct")==0) {
  lockfd=open(MIBR_OWNER_PATH,O_RDWR|O_CREAT,0600);
  if(lockfd<0 || mibr_owner_direct(lockfd)<0)return 12;
  v="D\n";
 } else v="S\n";
 fd=open(argv[2],O_WRONLY|O_CREAT|O_APPEND,0600);
 if(fd<0)return 13;
 iov.iov_base=(void*)v;iov.iov_len=2;
 for(n=0;n<2000;n++) {
  if(writev(fd,&iov,1)!=2)return 14;
  usleep(5000);
 }
 close(fd);if(lockfd>=0)close(lockfd);
 return 0;
}
