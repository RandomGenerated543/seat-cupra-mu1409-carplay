#include "alt111.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static const unsigned char cfg[]={1,0x42,0,31,0xff,0xe1,0,4,0x67,0x42,0,31,1,0,2,0x68,0xce};
static const unsigned char idr[]={0,0,0,2,0x65,0x88};
static const unsigned char dep[]={0,0,0,2,0x41,0x88};
static uint64_t setup(struct alt111_video *v){
 uint64_t s;alt111_video_init(v);s=alt111_video_begin(v,1);
 assert(alt111_video_config(v,s,cfg,sizeof cfg)==ALT111_OK);
 assert(alt111_video_attach(v)==ALT111_OK);return s;
}
static void consume(struct alt111_video *v){
 struct alt111_output_ticket t;const uint8_t *p;size_t n;
 assert(alt111_video_peek(v,&p,&n,&t)==ALT111_OK);
 assert(alt111_video_advance(v,&t,n)==ALT111_OK);
}
static void recover(unsigned partial){
 struct alt111_video v;uint64_t s=setup(&v),consumer=v.consumer;
 struct alt111_output_ticket t;const uint8_t *p;size_t n;unsigned i;
 assert(alt111_video_submit(&v,s,idr,sizeof idr,1)==ALT111_OK);
 if(partial){
  assert(alt111_video_peek(&v,&p,&n,&t)==ALT111_OK);
  assert(alt111_video_advance(&v,&t,1)==ALT111_OK);
 }else consume(&v);
 for(i=v.count;i<ALT111_QUEUE_CAP;i++)
  assert(alt111_video_submit(&v,s,dep,sizeof dep,1)==ALT111_OK);
 assert(alt111_video_submit(&v,s,dep,sizeof dep,1)==ALT111_SOFT_RESYNC);
 assert(v.attached && v.consumer==consumer && v.count==partial && v.recovery_wait_idr);
 assert(v.recovery_draining==partial && v.recovery_request_due==!partial);
 assert(alt111_video_submit(&v,s,dep,sizeof dep,1)==ALT111_WAIT);
 if(partial){
  assert(alt111_video_submit(&v,s,idr,sizeof idr,1)==ALT111_WAIT);
  assert(alt111_video_peek(&v,&p,&n,&t)==ALT111_OK && t.offset==1);
  assert(alt111_video_advance(&v,&t,n)==ALT111_OK);
  assert(!v.count && !v.recovery_draining && v.recovery_request_due);
 }
 assert(!v.consumer_primed);
 assert(alt111_video_submit(&v,s,idr,sizeof idr,1)==ALT111_OK);
 assert(!v.recovery_wait_idr && !v.recovery_request_due);
 assert(alt111_video_peek(&v,&p,&n,&t)==ALT111_OK && t.idr && n>sizeof idr);
 assert(p[4]==0x67); /* SPS/PPS prefix before the recovery IDR */
 consume(&v);assert(v.consumer_primed && v.consumer==consumer);
 assert(alt111_video_submit(&v,s,dep,sizeof dep,1)==ALT111_OK);consume(&v);
 assert(v.queued_bytes==0);
 assert(alt111_video_end(&v,s)==ALT111_OK && !v.attached);
 assert(alt111_video_submit(&v,s,dep,sizeof dep,1)==ALT111_STALE);
 alt111_video_destroy(&v);
}
static void byte_budget(void){
 struct alt111_video v;uint64_t s=setup(&v),consumer=v.consumer;
 size_t size=1024u*1024u+4u;unsigned char *p=malloc(size);unsigned i;
 assert(p);memset(p,0x88,size);p[0]=0;p[1]=0x10;p[2]=0;p[3]=0;p[4]=0x41;
 assert(alt111_video_submit(&v,s,idr,sizeof idr,1)==ALT111_OK);consume(&v);
 for(i=0;i<3;i++)assert(alt111_video_submit(&v,s,p,size,1)==ALT111_OK);
 assert(v.count<ALT111_QUEUE_CAP);
 assert(alt111_video_submit(&v,s,p,size,1)==ALT111_SOFT_RESYNC);
 assert(v.attached && v.consumer==consumer && v.queued_bytes==0);
 free(p);alt111_video_destroy(&v);
}
static void hard_failures(void){
 struct alt111_video v;uint64_t s=setup(&v);unsigned char changed[sizeof cfg];
 assert(alt111_video_submit(&v,s,idr,sizeof idr,1)==ALT111_OK);
 assert(alt111_video_submit(&v,s,dep,1,1)==ALT111_INVALID && !v.attached);
 assert(alt111_video_attach(&v)==ALT111_OK);
 memcpy(changed,cfg,sizeof cfg);changed[10]=30;
 assert(alt111_video_config(&v,s,changed,sizeof changed)==ALT111_RESTART_CONSUMER);
 assert(!v.attached);
 alt111_video_destroy(&v);
}
int main(void){
 unsigned i;for(i=0;i<200;i++){recover(0);recover(1);}
 byte_budget();hard_failures();
 assert(ALT111_QUEUE_CAP==16 && ALT111_QUEUE_BYTES==4u*1024u*1024u);
 puts("QUEUE_TEST=PASS 400_recoveries partial_AU_integrity fresh_IDR same_consumer byte_limit malformed_codec_teardown");return 0;
}
