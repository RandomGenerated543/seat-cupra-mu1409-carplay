#include <stdio.h>
#include <string.h>
#include <dlfcn.h>
static int same(const char *a,const char *b) {
 unsigned char x[4096],y[4096];size_t nx,ny;int result=1;
 FILE *fa=fopen(a,"rb"),*fb=fopen(b,"rb");
 if(!fa||!fb)goto done;
 do {nx=fread(x,1,sizeof(x),fa);ny=fread(y,1,sizeof(y),fb);if(nx!=ny||memcmp(x,y,nx))goto done;}while(nx);
 if(!ferror(fa)&&!ferror(fb))result=0;
done:if(fa)fclose(fa);if(fb)fclose(fb);return result;
}
int main(int argc,char **argv) {
 if(argc==4&&!strcmp(argv[1],"--same"))return same(argv[2],argv[3]);
 if(argc==3&&!strcmp(argv[1],"--load")) {
  void *h=dlopen(argv[2],RTLD_NOW|RTLD_LOCAL),*fn;
  if(!h){fprintf(stderr,"WIRED_DISPLAY_LOAD=FAIL %s\n",dlerror());return 1;}
  fn=dlsym(h,"AirPlayCopyServerInfo");dlclose(h);
  if(!fn)return 1;
  puts("WIRED_DISPLAY_LOAD=PASS activators_invoked=0");return 0;
 }
 return 2;
}
