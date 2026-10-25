#include "alt111.h"
#include <assert.h>
#include <stdio.h>
int main(void){
 struct alt111_control c;struct alt111_command cmd;uint64_t s;unsigned long t=100;
 assert(alt111_control_init(&c,3)==ALT111_OK);s=alt111_control_begin(&c);
 assert(alt111_control_intent(&c,1,0)==ALT111_OK);
 assert(alt111_control_next(&c,t,&cmd)==ALT111_OK && cmd.type==ALT111_CMD_SHOW);
 assert(alt111_control_complete(&c,s,cmd.request,1,++t)==ALT111_OK);
 assert(alt111_control_next(&c,++t,&cmd)==ALT111_OK && cmd.type==ALT111_CMD_VIEW && cmd.view==0);
 assert(alt111_control_complete(&c,s,cmd.request,1,++t)==ALT111_OK && c.acknowledged_view==0);
 /* Drain keyframe before switching. */
 assert(alt111_control_next(&c,++t,&cmd)==ALT111_OK && cmd.type==ALT111_CMD_KEYFRAME);
 assert(alt111_control_complete(&c,s,cmd.request,1,++t)==ALT111_OK);
 assert(alt111_control_intent(&c,1,1)==ALT111_OK);
 assert(alt111_control_next(&c,++t,&cmd)==ALT111_OK && cmd.type==ALT111_CMD_VIEW && cmd.view==1);
 /* A quick Full selection coalesces behind the already in-flight Center. */
 assert(alt111_control_intent(&c,1,0)==ALT111_OK);
 assert(alt111_control_next(&c,++t,&cmd)==ALT111_WAIT);
 assert(alt111_control_complete(&c,s,c.pending.request,1,++t)==ALT111_OK && c.acknowledged_view==1);
 assert(alt111_control_next(&c,++t,&cmd)==ALT111_OK && cmd.type==ALT111_CMD_VIEW && cmd.view==0);
 assert(alt111_control_complete(&c,s,cmd.request,1,++t)==ALT111_OK && c.acknowledged_view==0);
 assert(alt111_control_intent(&c,1,3)==ALT111_INVALID);
 assert(alt111_control_intent(&c,1,1)==ALT111_OK);
 {unsigned i;for(i=0;i<ALT111_ATTEMPTS;++i){
  t+=ALT111_RETRY_MS+1;
  assert(alt111_control_next(&c,t,&cmd)==ALT111_OK && cmd.type==ALT111_CMD_VIEW);
  assert(alt111_control_complete(&c,s,cmd.request,0,++t)==ALT111_OK);
 }}
 assert(c.exhausted && c.acknowledged_view==0);
 assert(alt111_control_next(&c,t+10000,&cmd)==ALT111_WAIT);
 assert(alt111_control_intent(&c,1,0)==ALT111_OK && !c.exhausted);
 assert(alt111_control_end(&c,s)==ALT111_OK);
 assert(alt111_control_complete(&c,s,999,1,t)==ALT111_STALE);
 s=alt111_control_begin(&c);assert(c.acknowledged_view==-1);
 assert(alt111_control_intent(&c,1,1)==ALT111_OK);
 assert(alt111_control_next(&c,++t,&cmd)==ALT111_OK && cmd.type==ALT111_CMD_SHOW);
 puts("VIEW_CONTROLLER3=PASS full_center_full serialized coalesced bounded_failures invalid_index stale reconnect");return 0;
}
