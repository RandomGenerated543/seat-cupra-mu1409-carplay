/* Match the existing wired card preference at wireless descriptor construction. */
#define _QNX_SOURCE 1
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>
#include <sys/stat.h>
#include <stdlib.h>
#include <dlfcn.h>
#undef ferror
static int host_lstat(const char *path,struct stat *st){
 int (*fn)(const char *,struct stat *)=(int (*)(const char *,struct stat *))dlsym(RTLD_DEFAULT,"lstat");
 if(!fn){errno=ENOSYS;return -1;}return fn(path,st);
}
static int host_ferror(FILE *file){
 int (*fn)(FILE *)=(int (*)(FILE *))dlsym(RTLD_DEFAULT,"ferror");
 return fn?fn(file):1;
}
#define lstat host_lstat
#define ferror host_ferror
#include "cpmap_card_preferences.h"
typedef const void *Ref;typedef void *Object;
#define FN(a,t) ((t)(unsigned long)(a))
#define set_number FN(0x5ada0,int (*)(Object,Ref,long long))
#define string_new FN(0x52220,Object (*)(Ref,const char *,unsigned))
#define release FN(0x51ce8,void (*)(Ref))
static char *host_getenv(const char *name){
 char *(*fn)(const char *)=(char *(*)(const char *))dlsym(RTLD_DEFAULT,"getenv");
 return fn?fn(name):0;
}
static int position(void){
 struct cpmap_card_preference p;const char *root=host_getenv("CPMAP_CARD_STATE_DIR");
 if(!root||!root[0])root="/mnt/icab/persistent/cpmap-ui";
 return cpmap_card_read(root,&p)>=0?p.position:CPMAP_CARD_RIGHT;
}
__attribute__((section(".entry")))
int auxiliary_layout(Object alt,Ref initial,long long previous){
 int pos=position(),view=pos==CPMAP_CARD_CENTER?3:0;
 int result=set_number(alt,initial,view),status=-1;
 Object key=string_new(0,"zoomFactor",0x08000100);
 if(key){status=set_number(alt,key,70);release(key);}
 {
  FILE *out=fopen("/dev/shmem/mu1447-wireless-layout.status","w");
  if(out){fprintf(out,"revision=mu1447_layout_v01\nposition=%d\ninitial_view=%d\nzoom=70\nzoom_result=%d\n",pos,view,status);fclose(out);}
 }
 (void)previous;return result;
}
__attribute__((section(".url_entry")))
void auxiliary_url(char *out,size_t size){
 const char *url;
 switch(position()){
 case CPMAP_CARD_CENTER:url="maps:/car/instrumentcluster?showETA=yes&maneuverLayout=topAligned&showSpeedLimit=no";break;
 case CPMAP_CARD_LEFT:url="maps:/car/instrumentcluster?showETA=yes&maneuverLayout=leftAligned";break;
 case CPMAP_CARD_OFF:url="maps:/car/instrumentcluster/map?showETA=yes&maneuverLayout=no&showSpeedLimit=no";break;
 default:url="maps:/car/instrumentcluster?showETA=yes&maneuverLayout=rightAligned&showSpeedLimit=no";
 }
 if(out&&size)snprintf(out,size,"%s",url);
}
