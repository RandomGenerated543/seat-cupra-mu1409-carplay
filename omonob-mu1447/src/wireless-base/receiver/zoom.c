/* Exact receiver auxiliary descriptor hook, fixed 70 percent. */
typedef const void *Ref;typedef void *Object;
#define FN(a,t) ((t)(unsigned long)(a))
#define set_number FN(0x5ada0,int (*)(Object,Ref,long long))
#define string_new FN(0x52220,Object (*)(Ref,const char *,unsigned))
#define release FN(0x51ce8,void (*)(Ref))
#define log_line FN(0xef8e0,int (*)(const char *,...))
__attribute__((section(".entry")))
int auxiliary_zoom(Object alt,Ref initial,long long value){
 int result=set_number(alt,initial,value);
 Object key=string_new(0,"zoomFactor",0x08000100);
 if(key){int status=set_number(alt,key,70);release(key);log_line("MU1447_WIRELESS_DISPLAY zoom=70 result=%d\n",status);}
 return result;
}
