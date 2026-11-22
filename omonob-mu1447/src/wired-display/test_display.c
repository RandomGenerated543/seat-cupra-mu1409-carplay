#include <assert.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef const void *Ref;
extern Ref AirPlayCopyServerInfo(void *,void *,void *,int *);
struct display {int64_t type,zoom; int type_error,write_error;};
static struct display main_display={110,123,0,0}, alt_display={111,0,0,0}, unrelated={222,321,0,0};
static Ref entries[3]; static long n=3;
static int key_allocations,key_releases,missing_api,allocation_fail,no_result,core_calls,writes,return_error;
static int displays_present=1;
static Ref fake_copy(void *a,void *b,void *c,int *error) {
 assert(a==(void*)10 && b==(void*)20 && c==(void*)30);++core_calls;
 if(error)*error=return_error;errno=17;return no_result?0:entries;
}
static Ref make_string(Ref allocator,const char *s,unsigned encoding) {
 assert(!allocator && encoding==0x08000100);
 if(allocation_fail)return 0;
 ++key_allocations;return strdup(s);
}
static Ref get_value(Ref obj,Ref key) {assert(obj==entries && !strcmp(key,"displays"));return displays_present?entries:0;}
static long get_count(Ref obj) {assert(obj==entries);return n;}
static Ref get_item(Ref obj,long i) {assert(obj==entries && i>=0 && i<3);return entries[i];}
static int64_t get_int(Ref obj,Ref key,int *error) {
 const struct display *d=obj;assert(!strcmp(key,"type"));*error=d->type_error;return d->type;
}
static int set_int(Ref obj,Ref key,int64_t value) {
 struct display *d=(struct display*)obj;assert(d==&alt_display && !strcmp(key,"zoomFactor") && value==70);
 ++writes;if(!d->write_error)d->zoom=value;return d->write_error;
}
static void release(Ref obj) {++key_releases;free((void*)obj);}
void *cpmap_test_resolve(int next,const char *name) {
 if(next){assert(!strcmp(name,"AirPlayCopyServerInfo"));return fake_copy;}
 if(missing_api)return 0;
 if(!strcmp(name,"CFStringCreateWithCString"))return make_string;
 if(!strcmp(name,"CFDictionaryGetValue"))return get_value;
 if(!strcmp(name,"CFArrayGetCount"))return get_count;
 if(!strcmp(name,"CFArrayGetValueAtIndex"))return get_item;
 if(!strcmp(name,"CFDictionaryGetInt64"))return get_int;
 if(!strcmp(name,"CFDictionarySetInt64"))return set_int;
 if(!strcmp(name,"CFRelease"))return release;
 assert(0);return 0;
}
static void invoke(void) {
 int error=-99,before=core_calls;
 Ref r=AirPlayCopyServerInfo((void*)10,(void*)20,(void*)30,&error);
 assert(r==(no_result?0:entries) && core_calls==before+1 && error==return_error && errno==17);
 assert(main_display.zoom==123 && unrelated.zoom==321 && key_allocations==key_releases);
}
int main(void) {
 entries[0]=&main_display;entries[1]=&alt_display;entries[2]=&unrelated;
 invoke();assert(alt_display.zoom==70 && writes==1);
 invoke();assert(writes==2);
 missing_api=1;invoke();assert(writes==2);missing_api=0;
 allocation_fail=1;invoke();assert(writes==2);allocation_fail=0;
 displays_present=0;invoke();assert(writes==2);displays_present=1;
 n=17;invoke();assert(writes==2);n=3;
 alt_display.type_error=1;invoke();assert(writes==2);alt_display.type_error=0;
 alt_display.write_error=1;alt_display.zoom=0;invoke();assert(writes==3 && alt_display.zoom==0);alt_display.write_error=0;
 no_result=1;return_error=-5;invoke();assert(writes==3);
 puts("WIRED_DISPLAY=PASS type111_only primary_unchanged original_result_error_errno_preserved missing_API allocation_failure missing_display bad_count type_error setter_failure repeat_calls resource_cleanup");
}
