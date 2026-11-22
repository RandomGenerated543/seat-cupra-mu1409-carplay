/* Dedicated wired /info wrapper. No wireless receiver, radio or service changes. */
#include <stdint.h>
#include <stdio.h>
#include <errno.h>
#include <dlfcn.h>

typedef const void *Ref;
typedef Ref (*CopyInfo)(void *, void *, void *, int *);
#ifdef CPMAP_TEST
extern void *cpmap_test_resolve(int next, const char *name);
#define RESOLVE(next,name) cpmap_test_resolve(next,name)
#else
#define RESOLVE(next,name) dlsym((next) ? RTLD_NEXT : RTLD_DEFAULT, name)
#endif
#ifndef CPMAP_LOG
#define CPMAP_LOG "/ramdisk/mu1447-wired-display.log"
#endif
static void report(int status, int count)
{
    FILE *f = fopen(CPMAP_LOG, "a");
    if (f) {
        fprintf(f, "WIRED_VC_ZOOM percent=70 result=%d auxiliary_displays=%d\n", status, count);
        fclose(f);
    }
}
__attribute__((visibility("default")))
Ref AirPlayCopyServerInfo(void *server, void *qualifier, void *peer, int *error)
{
    CopyInfo next = (CopyInfo)RESOLVE(1,"AirPlayCopyServerInfo");
    Ref result;
    int saved_errno, status=-1, count=0;
    Ref displays_key=0, type_key=0, zoom_key=0;
    Ref (*make_string)(Ref,const char *,unsigned);
    Ref (*get_value)(Ref,Ref);
    long (*array_count)(Ref);
    Ref (*array_item)(Ref,long);
    int64_t (*get_int)(Ref,Ref,int *);
    int (*set_int)(Ref,Ref,int64_t);
    void (*release)(Ref);
    if (!next || next == AirPlayCopyServerInfo) {
        if (error) *error=-1;
        return 0;
    }
    result=next(server,qualifier,peer,error);
    saved_errno=errno;
    if (!result) return result;
    make_string=(Ref (*)(Ref,const char *,unsigned))RESOLVE(0,"CFStringCreateWithCString");
    get_value=(Ref (*)(Ref,Ref))RESOLVE(0,"CFDictionaryGetValue");
    array_count=(long (*)(Ref))RESOLVE(0,"CFArrayGetCount");
    array_item=(Ref (*)(Ref,long))RESOLVE(0,"CFArrayGetValueAtIndex");
    get_int=(int64_t (*)(Ref,Ref,int *))RESOLVE(0,"CFDictionaryGetInt64");
    set_int=(int (*)(Ref,Ref,int64_t))RESOLVE(0,"CFDictionarySetInt64");
    release=(void (*)(Ref))RESOLVE(0,"CFRelease");
    if (!make_string || !get_value || !array_count || !array_item || !get_int || !set_int || !release)
        goto done;
    displays_key=make_string(0,"displays",0x08000100);
    type_key=make_string(0,"type",0x08000100);
    zoom_key=make_string(0,"zoomFactor",0x08000100);
    if (displays_key && type_key && zoom_key) {
        Ref displays=get_value(result,displays_key);
        if (displays) {
            long n=array_count(displays), i;
            if (n>=0 && n<=16) {
                for (i=0;i<n;++i) {
                    Ref display=array_item(displays,i);
                    int e=-1;
                    if (display && get_int(display,type_key,&e)==111 && e==0) {
                        int s=set_int(display,zoom_key,70);
                        ++count;
                        if (count==1 || s) status=s;
                    }
                }
            }
        }
    }
    if (displays_key) release(displays_key);
    if (type_key) release(type_key);
    if (zoom_key) release(zoom_key);
done:
    report(status,count);
    errno=saved_errno;
    return result;
}
