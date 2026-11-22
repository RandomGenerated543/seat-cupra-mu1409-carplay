#define _QNX_SOURCE 1
#include <pthread.h>
#include <dlfcn.h>
#include <errno.h>
/* QNX tid=0 names the calling thread. Pass its real ID to the bookkeeping
 * bridge so subsequent pthread_equal() checks do not compare against zero. */
__attribute__((visibility("default")))
int pthread_setname_np(pthread_t tid,const char *name) {
 int (*next)(pthread_t,const char *)=(int (*)(pthread_t,const char *))dlsym(RTLD_NEXT,"pthread_setname_np");
 if(!next || next==pthread_setname_np)return ENOSYS;
 return next(tid ? tid : pthread_self(),name);
}
