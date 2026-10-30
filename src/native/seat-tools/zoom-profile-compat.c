/* Read-only converter for downgrade: remove only the new zoom setting,
 * retaining every original preference byte. Caller commits output separately. */
#define _POSIX_C_SOURCE 200809L
#include "alt111_settings.h"
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
int main(int argc,char **argv){
 char data[8193],out[8193],line[272],error[160];size_t n=0,p=0,used=0;
 unsigned seen[ALTSET_COUNT]={0},count=0;int fd,id;ssize_t got;
 struct stat a,b;struct alt111_settings *s;
 if(argc!=2||lstat(argv[1],&a)||!S_ISREG(a.st_mode)||a.st_size<1||a.st_size>8192)return 2;
 fd=open(argv[1],O_RDONLY);if(fd<0)return 2;
 if(fstat(fd,&b)||a.st_dev!=b.st_dev||a.st_ino!=b.st_ino){close(fd);return 2;}
 while(n<(size_t)a.st_size){got=read(fd,data+n,(size_t)a.st_size-n);if(got<=0){close(fd);return 2;}n+=(size_t)got;}
 if(close(fd)||data[n-1]!='\n'||memchr(data,0,n)||memchr(data,'\r',n))return 2;
 s=calloc(1,sizeof(*s));if(!s)return 2;
 if(alt111_settings_defaults(s,"mibr_legacy")){free(s);return 2;}
 while(p<n){char *end=memchr(data+p,'\n',n-p),*eq;size_t len;
  if(!end){free(s);return 2;}len=(size_t)(end-data-p);
  if(!len||len>=sizeof(line)){free(s);return 2;}
  memcpy(line,data+p,len);line[len]=0;eq=strchr(line,'=');if(!eq){free(s);return 2;}*eq++=0;
  id=alt111_setting_find(line);
  if(id<0||seen[id]++||alt111_settings_set(s,(unsigned)id,eq,ALT111_TEMP)){free(s);return 2;}
  if(id!=ALTSET_DISPLAY_ZOOMFACTOR){memcpy(out+used,data+p,len+1);used+=len+1;count++;}
  p+=len+1;
 }
 if(count!=45||alt111_settings_validate(s,error,sizeof(error))){free(s);return 2;}free(s);
 return fwrite(out,1,used,stdout)==used&&!fflush(stdout)?0:3;
}
