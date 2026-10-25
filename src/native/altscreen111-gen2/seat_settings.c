/* Private SEAT adapter to Harman's sole canonical settings core. No media I/O. */
#include "seat_settings.h"
#include <pthread.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <inttypes.h>

static pthread_mutex_t lock=PTHREAD_MUTEX_INITIALIZER;
static char current_url[384];
static uint64_t revision,session,requested,acknowledged,next_poll,completed_show_request;
static int valid,query_enabled,ack_status=-1,view_selected=-1;
int seat_navigation_url(const struct alt111_settings *s,char *out,size_t cap){
    const char *base,*surface,*maneuver;int n;
    if(!s||!out||!cap)return -1;
    surface=s->value[ALTSET_NAVIGATION_SURFACE];
    base=!strcmp(surface,"map")?"maps:/car/instrumentcluster/map":
         !strcmp(surface,"instructioncard")?"maps:/car/instrumentcluster/instructioncard":
         "maps:/car/instrumentcluster";
    if(strcmp(s->value[ALTSET_NAVIGATION_URL],"auto"))base=s->value[ALTSET_NAVIGATION_URL];
    if(!strcmp(s->value[ALTSET_NAVIGATION_QUERY],"0")||
       strstr(base,"instructioncard"))n=snprintf(out,cap,"%s",base);
    else{
        maneuver=s->value[ALTSET_NAVIGATION_MANEUVER];
        if(!strcmp(maneuver,"none"))maneuver="";
        n=snprintf(out,cap,"%s?showSpeedLimit=%s&showCompass=%s&showETA=%s&maneuverLayout=%s",base,
            s->value[ALTSET_NAVIGATION_SPEEDLIMIT],s->value[ALTSET_NAVIGATION_COMPASS],
            s->value[ALTSET_NAVIGATION_ETA],maneuver);
    }
    return n<0||(size_t)n>=cap?-1:0;
}
static void publish(void){
    char text[1024];int fd,n;
    n=snprintf(text,sizeof(text),"revision=seat_wp2_v1\nsettings_valid=%d\ncontrol_session=%" PRIu64
        "\ndesired_revision=%" PRIu64 "\nrequested_revision=%" PRIu64
        "\ncompleted_show_request=%" PRIu64 "\nacknowledged_revision=%" PRIu64 "\nphone_ack_status=%d\nvisible=UNKNOWN\nnav_url=%s\n",
        valid,session,revision,requested,completed_show_request,acknowledged,ack_status,current_url);
    if(n<=0||(size_t)n>=sizeof(text))return;
    fd=open("/tmp/mibr-seat-settings.status",O_WRONLY|O_CREAT|O_TRUNC,0600);
    if(fd>=0){(void)write(fd,text,(size_t)n);(void)close(fd);}
}
void seat_settings_poll(uint64_t now,uint64_t current_session){
    struct alt111_settings desired;struct alt111_settings_paths paths={"/tmp","/mnt/app/root"};
    char error[128],url[384];int okay;
    if(now<next_poll)return;
    next_poll=now+250;
    okay=access("/mnt/app/root/altscreen-u2/harman-r13/enabled",F_OK)==0 &&
         !alt111_settings_load(&paths,&desired,error,sizeof(error))&&
         !seat_navigation_url(&desired,url,sizeof(url));
    pthread_mutex_lock(&lock);
    if(session!=current_session){session=current_session;acknowledged=0;requested=0;ack_status=-1;completed_show_request=0;}
    if(okay){
        if(revision!=desired.revision){acknowledged=0;ack_status=-1;completed_show_request=0;}
        revision=desired.revision;strcpy(current_url,url);valid=1;
        query_enabled=!strcmp(desired.value[ALTSET_NAVIGATION_QUERY],"1");
        view_selected=!strcmp(desired.value[ALTSET_VIEWAREA_SELECTED],"0")?0:!strcmp(desired.value[ALTSET_VIEWAREA_SELECTED],"1")?1:!strcmp(desired.value[ALTSET_VIEWAREA_SELECTED],"2")?2:-1;
    }else{valid=0;acknowledged=0;ack_status=-1;view_selected=-1;}
    publish();pthread_mutex_unlock(&lock);
}
int seat_settings_url(char *out,size_t cap){
    int okay;pthread_mutex_lock(&lock);okay=valid;
    if(okay){size_t n=strlen(current_url);if(n>=cap)okay=0;else memcpy(out,current_url,n+1);}
    pthread_mutex_unlock(&lock);return okay;
}
uint64_t seat_settings_revision(void){
    uint64_t r;pthread_mutex_lock(&lock);r=valid?revision:0;requested=r;pthread_mutex_unlock(&lock);return r;
}
int seat_settings_query(void){
    int q;pthread_mutex_lock(&lock);q=valid?query_enabled:-1;pthread_mutex_unlock(&lock);return q;
}
void seat_settings_ack(uint64_t s,uint64_t r,int success,uint64_t request){
    pthread_mutex_lock(&lock);
    if(valid&&s&&s==session&&r&&r==revision){ack_status=success?0:1;acknowledged=success?r:0;completed_show_request=request;publish();}
    pthread_mutex_unlock(&lock);
}

int seat_settings_view(void){int v;pthread_mutex_lock(&lock);v=valid?view_selected:-1;pthread_mutex_unlock(&lock);return v;}

#include "seat_geometry.inc"
