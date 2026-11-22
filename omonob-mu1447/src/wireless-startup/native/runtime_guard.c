#define _QNX_SOURCE 1
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#ifdef __QNXNTO__
#include <devctl.h>
#include <sys/procfs.h>
#endif
/* Process identity and an existing receiver session pointer are read-only.
 * No socket, firmware/driver mutation, credentials or process-memory writes. */
static const unsigned char expected_set[16]=SET_FINGERPRINT;
static const unsigned char expected_clear[16]=CLEAR_FINGERPRINT;
#ifndef PIDFILE
#define PIDFILE "/dev/shmem/wcp_receiver.pid"
#endif
#ifndef STATUS
#define STATUS "/ramdisk/mu1447-wcp-session.status"
#endif
static int read_at(int fd,off_t at,void *out,size_t size){return lseek(fd,at,SEEK_SET)==at&&read(fd,out,size)==(ssize_t)size?0:-1;}
static int number_pid(pid_t *pid){char b[32],extra;long value;FILE *f=fopen(PIDFILE,"r");if(!f)return errno==ENOENT?1:3;if(!fgets(b,sizeof b,f)||ferror(f)){fclose(f);return 3;}fclose(f);if(sscanf(b,"%ld %c",&value,&extra)!=1||value<2||value>2147483647L)return 3;*pid=(pid_t)value;return 0;}
/* 0 verified receiver,1 absent/dead,2 wrong process,3 observation unavailable. */
static int receiver(pid_t *pid,uint32_t *session){
 char path[64];unsigned char data[16];int fd,r;uint32_t a,b;
 r=number_pid(pid);if(r)return r;
 if(kill(*pid,0)){return errno==ESRCH?1:3;}
 snprintf(path,sizeof path,"/proc/%ld/as",(long)*pid);fd=open(path,O_RDONLY);if(fd<0)return errno==ENOENT?1:3;
#ifdef __QNXNTO__
 {union {procfs_debuginfo aligned;char data[sizeof(procfs_debuginfo)+1024];} storage;char *info=storage.data;procfs_debuginfo *d=(procfs_debuginfo *)info;const char *base;memset(info,0,sizeof storage);
  r=devctl(fd,DCMD_PROC_MAPDEBUG_BASE,d,sizeof storage,0);if(r){close(fd);return 3;}
  info[sizeof storage-1]=0;base=strrchr(d->path,'/');base=base?base+1:d->path;
  if(strcmp(base,"wcp_receiver")){close(fd);return 2;}
 }
#else
 close(fd);return 3;
#endif
 if(read_at(fd,0xea050,data,16)||memcmp(data,expected_set,16)||read_at(fd,0xea080,data,16)||memcmp(data,expected_clear,16)){close(fd);return 3;}
 if(read_at(fd,0x112a6c,&a,4)||read_at(fd,0x112a6c,&b,4)||a!=b){close(fd);return 3;}
 close(fd);if(a&&(a<0x10000U||(a&3U)))return 3;*session=a;return 0;
}
static int lock_file(const char *path){struct flock lock;int fd=open(path,O_RDWR|O_CREAT,0600);if(fd<0)return -1;memset(&lock,0,sizeof lock);lock.l_type=F_WRLCK;lock.l_whence=SEEK_SET;if(fcntl(fd,F_SETLK,&lock)){close(fd);return -1;}fcntl(fd,F_SETFD,FD_CLOEXEC);return fd;}
static int run_script(const char *script,const char *arg){int lock=lock_file("/ramdisk/mu1447-wcp-start.lock"),status;pid_t child;
 if(lock<0){puts("MU1447_RUNTIME=START_ALREADY_MANAGED");return arg?1:0;}
 child=fork();if(child<0){close(lock);return 1;}
 if(child==0){setenv("MU1447_START_GUARDED","1",1);if(arg)execl("/bin/sh","sh",script,arg,(char *)0);else execl("/bin/sh","sh",script,(char *)0);_exit(127);}
 while(waitpid(child,&status,0)<0){if(errno!=EINTR){close(lock);return 1;}}
 close(lock);return WIFEXITED(status)?WEXITSTATUS(status):1;
}
static volatile sig_atomic_t done;
static void stop(int sig){(void)sig;done=1;}
static int publish(pid_t pid,unsigned gen,unsigned long long sample,const char *state){char stage[128];FILE *f;int result;
 snprintf(stage,sizeof stage,STATUS".new-%ld",(long)getpid());f=fopen(stage,"w");if(!f)return -1;
 result=fprintf(f,"format=1\nreceiver_pid=%ld\nmonitor_pid=%ld\ngeneration=%u\nsample=%llu\nstate=%s\nrevision=mu1447_session_v01\n",(long)pid,(long)getpid(),gen,sample,state);
 if(fclose(f)||result<0){unlink(stage);return -1;}if(rename(stage,STATUS)){unlink(stage);return -1;}return 0;
}
static int watch(void){int lock=lock_file("/ramdisk/mu1447-wcp-session.lock");pid_t pid=0,last_pid=-1;uint32_t ptr=0,last_ptr=0xffffffffU;unsigned generation=0;unsigned long long sample=0;struct timespec nap={0,250000000};
 if(lock<0)return 0;signal(SIGTERM,stop);signal(SIGINT,stop);
 while(!done){int rc;const char *state;
  pid=0;ptr=0;rc=receiver(&pid,&ptr);state=rc==0?(ptr?"active":"idle"):rc==1?"idle":"unknown";
  if(rc==0||rc==1){if(pid!=last_pid||ptr!=last_ptr){if(generation==2147483647U){state="unknown";}else{generation++;last_pid=pid;last_ptr=ptr;}}}
  if(publish(pid,generation,++sample,state)){close(lock);return 1;}
  if(access("/mnt/persist/wcp_autostart",F_OK)||!access("/mnt/persist/btwcp_off",F_OK))break;
  nanosleep(&nap,0);
 }
 publish(0,generation,++sample,"idle");close(lock);return 0;
}
int main(int argc,char **argv){pid_t pid=0;uint32_t session=0;int rc;
 if(argc==2&&!strcmp(argv[1],"--self-test")){if(sizeof(uint32_t)!=4)return 1;puts("MU1447_RUNTIME_SELF_TEST=PASS");return 0;}
 if(argc==2&&!strcmp(argv[1],"--run-startup"))return run_script("/mnt/ota/wcp_autostart.sh",0);
 if(argc==3&&!strcmp(argv[1],"--run-controller")&&(!strcmp(argv[2],"start")||!strcmp(argv[2],"stop")))return run_script("/dev/shmem/wcp_ctl.sh",argv[2]);
 if(argc==2&&!strcmp(argv[1],"--session-watch"))return watch();
 if(argc==2&&(!strcmp(argv[1],"--inspect")||!strcmp(argv[1],"--receiver-alive"))){rc=receiver(&pid,&session);if(!strcmp(argv[1],"--inspect"))printf("MU1447_RECEIVER_OBSERVATION rc=%d pid=%ld state=%s writes_to_receiver=0\n",rc,(long)pid,rc==0?(session?"active":"idle"):"unknown");return rc;}
 fputs("Usage: --self-test | --inspect | --receiver-alive | --run-startup | --run-controller start|stop | --session-watch\n",stderr);return 2;
}
