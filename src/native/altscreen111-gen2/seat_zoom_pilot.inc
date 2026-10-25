/* Local SEAT adapter for Harman's pure zoom policy and passive correlation
 * decoder. Runs only from the existing serialized UI worker. No writer,
 * input suppression, Java modification, or media ownership changes. Automatic eligibility requires the existing
 * DIRECT source and a fresh native-scale-associated wheel event. */
#include "alt111_zoom.h"
#include "alt111_zoom_debugspi.h"
#include <sys/select.h>
static struct alt111_zoom seat_zoom;
static struct alt111_spi_zoom *seat_spi;
static int seat_sock=-1,seat_connecting;
static uint64_t seat_token,seat_seen,seat_start,seat_expires,seat_flight,seat_publish_at;
static AirPlayReceiverSessionRef seat_session;
static const char *seat_reason="disabled";
static const char *seat_status="/tmp/mibr-seat-zoom.status";
static const char *seat_auto_config="/mnt/app/root/mibr-seat-zoom-auto.conf";
static const char *seat_pause="/tmp/mibr-seat-zoom.pause";
static uint64_t seat_auto_sequence,seat_offer_token,seat_offer_session,seat_retry_at;
static uint64_t seat_fault_session;
static unsigned seat_auto_enabled;
static int seat_automatic_config(void)
{
    char b[64];
    return read_trimmed_value(seat_auto_config,b,sizeof(b))==0 && !strcmp(b,"enabled=1");
}
static unsigned seat_requested(void)
{
    if(access(seat_pause,F_OK)==0)return 0;
    return seat_auto_enabled && seat_automatic_config();
}

static unsigned seat_visible_locked(void)
{
    return g2_command_ready && g2_control_session && g2_control.active &&
        g2_control.desired && g2_control.shown_ack && !g2_control.reacquiring &&
        g2_video.active && g2_video.session==g2_control_session &&
        g2_video.config_valid && g2_video.attached && g2_video.consumer_primed;
}
static unsigned seat_connection_locked(void)
{
    return g2_control_session && g2_control.active && g2_control.desired &&
        g2_video.active && g2_video.session==g2_control_session;
}
static unsigned seat_observe_ready_locked(void)
{
    return seat_visible_locked() && (g2_control.pending.type==ALT111_CMD_NONE ||
                                     g2_control.pending.type==ALT111_CMD_KEYFRAME);
}
static uint64_t seat_bound_stream,seat_bound_codec,seat_bound_consumer;
static int seat_read_arm(uint64_t *generation,uint64_t *token,int *polarity)
{
    if(!seat_auto_enabled || !seat_offer_token || access(seat_pause,F_OK)==0 ||
       !seat_automatic_config())return 0;
    *generation=seat_offer_session;*token=seat_offer_token;*polarity=1;return 1;
}
static void seat_publish(void)
{
    char b[1400];int n,fd;struct alt111_zoom z;uint64_t token;
    if(monotonic_ms()<seat_publish_at)return;
    seat_publish_at=monotonic_ms()+200;
    pthread_mutex_lock(&g2_core_lock);z=seat_zoom;token=seat_token;pthread_mutex_unlock(&g2_core_lock);
    n=snprintf(b,sizeof(b),"revision=seat_zoom_auto_v2_1\nautomatic_enabled=%u\npid=%ld\narmed=%u\ntoken=%llu\nreason=%s\n"
        "session=%llu\npositive_is_in=%d\npending=%d\nin_flight=%u\naccepted=%llu\nrejected=%llu\n"
        "completed=%llu\nfailed=%llu\nstale=%llu\nframes=%llu\nwheel_records=%llu\nscale_records=%llu\nmatched=%llu\n",
        seat_auto_enabled,(long)getpid(),token?1u:0u,(unsigned long long)token,seat_reason,
        (unsigned long long)z.session,z.positive_direction,z.pending,z.in_flight,
        (unsigned long long)z.accepted,(unsigned long long)z.rejected,
        (unsigned long long)z.completed,(unsigned long long)z.failed,(unsigned long long)z.stale,
        (unsigned long long)(seat_spi?seat_spi->frames:0),
        (unsigned long long)(seat_spi?seat_spi->wheel_count:0),
        (unsigned long long)(seat_spi?seat_spi->tag_count:0),
        (unsigned long long)(seat_spi?seat_spi->matches:0));
    if(n<=0 || (size_t)n>=sizeof(b))return;
    fd=open(seat_status,O_WRONLY|O_CREAT|O_TRUNC,0644);
    if(fd>=0){(void)write(fd,b,(size_t)n);close(fd);}
}
static void seat_disable(const char *reason)
{
    int active;
    pthread_mutex_lock(&g2_core_lock);
    active=seat_token!=0;
    if(active && (!strncmp(reason,"command_",8) || !strcmp(reason,"completion_timeout") || !strcmp(reason,"DebugSPI_framing_error")))
        seat_fault_session=seat_zoom.session;
    seat_token=0;alt111_zoom_end(&seat_zoom);
    pthread_mutex_unlock(&g2_core_lock);
    if(seat_sock>=0)close(seat_sock);
    seat_sock=-1;seat_connecting=0;
    if(seat_session)p_CFRelease(seat_session);
    seat_session=NULL;seat_reason=reason;
    if(active && !strncmp(reason,"DebugSPI_",9))seat_retry_at=monotonic_ms()+5000;
    if(active)logf_u2("SEAT ZOOM disabled reason=%s; OEM inputs unchanged",reason);
}
static void seat_pair(void *opaque,uint32_t source_ms,int detent)
{
    int rc=ALT111_ZOOM_WAIT,polarity=0;uint64_t generation=0,token=0;
    int32_t age=(int32_t)((uint32_t)monotonic_ms()-source_ms);
    (void)opaque;
    if(age < -40 || age > 500 || (int32_t)(source_ms-(uint32_t)seat_start)<0)return;
    if(!seat_read_arm(&generation,&token,&polarity) || token!=seat_token ||
       (seat_expires && monotonic_ms()>=seat_expires) || access("/tmp/mibr-isotx2-gate.direct",F_OK)!=0)return;
    pthread_mutex_lock(&g2_core_lock);
    if(seat_token && generation==g2_control_session && seat_visible_locked() &&
       seat_zoom.active && seat_zoom.session==generation &&
       seat_observe_ready_locked()){
        /* The transport is automatically eligible only in active DIRECT.
         * Each intent still requires the measured native scale-action pair;
         * no raw rotation, key press, menu action or volume event suffices.
         * Native listener fan-out and native map zoom remain unchanged. */
        (void)alt111_zoom_context(&seat_zoom,generation,1u,1u,1u);
        rc=alt111_zoom_encoder(&seat_zoom,generation,4,40,detent,0,1);
    }
    pthread_mutex_unlock(&g2_core_lock);
    if(rc==ALT111_ZOOM_OK)logf_u2("SEAT ZOOM matched source_ms=%u detent=%d",source_ms,detent);
}
struct seat_completion {uint64_t token,session,request;unsigned direction;AirPlayReceiverSessionRef retained;};
static void seat_complete(OSStatus status,CFDictionaryRef response,void *opaque)
{
    struct seat_completion *ctx=(struct seat_completion *)opaque;int rc=ALT111_ZOOM_STALE;
    (void)response;if(!ctx)return;
    pthread_mutex_lock(&g2_core_lock);
    if(ctx->token==seat_token && ctx->session==g2_control_session){
        rc=alt111_zoom_complete(&seat_zoom,ctx->session,ctx->request,status==K_NO_ERR,monotonic_ms());
        if(rc==ALT111_ZOOM_OK && status!=K_NO_ERR)seat_fault_session=ctx->session;
    }
    pthread_mutex_unlock(&g2_core_lock);
    logf_u2("SEAT ZOOM completion request=%llu direction=%u os=%d rc=%d acknowledgement_only=1",
        (unsigned long long)ctx->request,ctx->direction,(int)status,rc);
    if(ctx->retained)p_CFRelease(ctx->retained);
    free(ctx);
}
static void seat_zoom_tick(void)
{
    struct alt111_zoom_command cmd;struct seat_completion *ctx;
    CFMutableDictionaryRef req,params;CFStringRef k;
    int rc;uint64_t token;
    if(!seat_token || !seat_session || !seat_requested() ||
       access("/tmp/mibr-isotx2-gate.direct",F_OK)!=0 || (seat_expires && monotonic_ms()>=seat_expires))return;
    pthread_mutex_lock(&g2_core_lock);
    token=seat_token;
    rc=(seat_visible_locked() && g2_control.pending.type==ALT111_CMD_NONE)
       ?alt111_zoom_next(&seat_zoom,g2_control_session,monotonic_ms(),&cmd):ALT111_ZOOM_WAIT;
    pthread_mutex_unlock(&g2_core_lock);
    if(rc!=ALT111_ZOOM_OK)return;
    seat_flight=monotonic_ms();
    req=dict_new();params=dict_new();
    ctx=(struct seat_completion *)calloc(1,sizeof(*ctx));
    if(!req || !params || !ctx){
        if(req)p_CFRelease(req);if(params)p_CFRelease(params);free(ctx);
        seat_disable("command_allocation_failed");return;
    }
    set_str(req,"type","changeMapZoomLevel");
    set_str(params,"uuid",g_alt_uuid);set_i64(params,"zoomDirection",(int64_t)cmd.direction);
    k=s_cf("params");
    if(!k){p_CFRelease(req);p_CFRelease(params);free(ctx);seat_disable("dictionary_key_failed");return;}
    p_CFDictionarySetValue(req,k,params);p_CFRelease(k);p_CFRelease(params);
    ctx->token=token;ctx->session=cmd.session;ctx->request=cmd.request;ctx->direction=cmd.direction;
    ctx->retained=(AirPlayReceiverSessionRef)p_CFRetain(seat_session);
    /* Snapshot scalars before dispatch: completion may execute synchronously. */
    rc=g_sendcmd?g_sendcmd(seat_session,req,seat_complete,ctx):-1;
    p_CFRelease(req);
    logf_u2("SEAT ZOOM submit request=%llu direction=%u rc=%d",
        (unsigned long long)cmd.request,cmd.direction,rc);
    if(rc!=K_NO_ERR){
        p_CFRelease(ctx->retained);free(ctx);seat_disable("command_submit_failed");
    }
}
static void seat_zoom_poll(void)
{
    uint64_t generation=0,token=0,now=monotonic_ms();int polarity=0,ready,flight;
    char chunk[8192];int loops;
    seat_auto_enabled=seat_automatic_config();
    if(access(seat_pause,F_OK)==0){
        pthread_mutex_lock(&g2_core_lock);seat_fault_session=0;pthread_mutex_unlock(&g2_core_lock);
    }
    if(seat_auto_enabled){
        uint64_t current;unsigned eligible;
        pthread_mutex_lock(&g2_core_lock);
        current=g2_control_session;
        eligible=seat_connection_locked() && current && seat_fault_session!=current &&
            ((seat_token && seat_zoom.session==current) || seat_visible_locked());
        pthread_mutex_unlock(&g2_core_lock);
        eligible=eligible && access("/tmp/mibr-isotx2-gate.direct",F_OK)==0 &&
            access(seat_pause,F_OK)!=0 && now>=seat_retry_at;
        if(!eligible){seat_offer_token=0;seat_offer_session=0;}
        else if(!seat_offer_token || seat_offer_session!=current){
            /* Unique binding epoch: never carry a queue/completion across
             * a reconnect, consumer reacquire, pause or DIRECT->STOCK. */
            seat_offer_session=current;
            seat_offer_token=0x4000000000000000ULL+(++seat_auto_sequence);
        }
    }else{seat_offer_token=0;seat_offer_session=0;}
    if(!seat_read_arm(&generation,&token,&polarity)){
        if(seat_token)seat_disable("automatic_context_unavailable");
        if(!seat_auto_enabled)seat_reason="automatic_disabled";
        else if(access(seat_pause,F_OK)==0)seat_reason="paused";
        else if(now<seat_retry_at)seat_reason="transport_retry_backoff";
        else seat_reason="waiting_for_direct_map_or_new_session";
        seat_publish();return;
    }
    if(token!=seat_seen){
        seat_disable("new_arm");seat_seen=token;
        seat_start=now;seat_expires=0;
        pthread_mutex_lock(&g2_core_lock);
        ready=seat_visible_locked() && generation==g2_control_session;
        pthread_mutex_unlock(&g2_core_lock);
        if(!ready || access("/tmp/mibr-isotx2-gate.direct",F_OK)!=0){seat_reason="arm_rejected_not_ready";seat_publish();return;}
        seat_session=retain_active_session();
        if(!seat_session){seat_reason="arm_rejected_no_session";seat_publish();return;}
        if(!seat_spi)seat_spi=(struct alt111_spi_zoom *)calloc(1,sizeof(*seat_spi));
        if(!seat_spi){seat_disable("decoder_allocation_failed");seat_publish();return;}
        alt111_spi_zoom_init(seat_spi);
        pthread_mutex_lock(&g2_core_lock);
        ready=seat_visible_locked() && generation==g2_control_session;
        if(ready){seat_token=token;seat_bound_stream=g2_video.stream;seat_bound_codec=g2_video.codec;
            seat_bound_consumer=g2_video.consumer;alt111_zoom_begin(&seat_zoom,generation);(void)alt111_zoom_polarity(&seat_zoom,generation,polarity);}
        pthread_mutex_unlock(&g2_core_lock);
        if(!ready){seat_disable("session_changed_during_arm");seat_publish();return;}
        seat_reason="armed_connecting";
        seat_sock=socket(AF_INET,SOCK_STREAM,0);
        if(seat_sock<0 || fcntl(seat_sock,F_SETFL,O_NONBLOCK)<0){seat_disable("socket_setup_failed");seat_publish();return;}
        {struct sockaddr_in a;memset(&a,0,sizeof(a));a.sin_family=AF_INET;a.sin_port=htons(15001);a.sin_addr.s_addr=htonl(INADDR_LOOPBACK);
         if(connect(seat_sock,(struct sockaddr *)&a,sizeof(a))<0){
            if(errno==EINPROGRESS)seat_connecting=1;else{seat_disable("DebugSPI_connect_failed");seat_publish();return;}
         }}
        logf_u2("SEAT ZOOM binding token=%llu session=%llu automatic=%u mode=PARALLEL_OEM_UNCHANGED",
            (unsigned long long)token,(unsigned long long)generation,seat_auto_enabled);
    }
    if(!seat_token){seat_publish();return;}
    pthread_mutex_lock(&g2_core_lock);
    ready=seat_connection_locked() && generation==g2_control_session &&
        seat_zoom.active && seat_zoom.session==generation;
    if(ready){
        unsigned reset=seat_bound_stream!=g2_video.stream ||
            seat_bound_codec!=g2_video.codec || seat_bound_consumer!=g2_video.consumer;
        if(!seat_observe_ready_locked() || reset){
            (void)alt111_zoom_context(&seat_zoom,generation,0u,0u,0u);
            if(reset)seat_start=now;
        }
        seat_bound_stream=g2_video.stream;seat_bound_codec=g2_video.codec;
        seat_bound_consumer=g2_video.consumer;
    }
    flight=seat_zoom.in_flight;
    if(seat_auto_enabled && seat_fault_session==generation)ready=0;
    pthread_mutex_unlock(&g2_core_lock);
    if(!ready || (seat_expires && now>=seat_expires) || access("/tmp/mibr-isotx2-gate.direct",F_OK)!=0){seat_disable("context_lost_or_expired");seat_publish();return;}
    if(flight && now-seat_flight>2000){seat_disable("completion_timeout");seat_publish();return;}
    if(seat_connecting){
        fd_set wr;struct timeval tv={0,0};int error=0;socklen_t len=sizeof(error);
        FD_ZERO(&wr);FD_SET(seat_sock,&wr);
        if(select(seat_sock+1,NULL,&wr,NULL,&tv)>0){
            if(getsockopt(seat_sock,SOL_SOCKET,SO_ERROR,&error,&len)<0 || error){seat_disable("DebugSPI_connect_failed");seat_publish();return;}
            seat_connecting=0;
        }else{if(now-seat_start>1000)seat_disable("DebugSPI_connect_timeout");seat_publish();return;}
    }
    seat_reason="armed_listening";
    for(loops=0;loops<8;loops++){
        ssize_t n=recv(seat_sock,chunk,sizeof(chunk),0);
        if(n>0){alt111_spi_zoom_feed(seat_spi,chunk,(size_t)n,seat_pair,NULL);
            if(seat_spi->bad_frames){seat_disable("DebugSPI_framing_error");break;}}
        else if(!n){seat_disable("DebugSPI_disconnected");break;}
        else{if(errno!=EAGAIN && errno!=EWOULDBLOCK && errno!=EINTR)seat_disable("DebugSPI_read_failed");break;}
    }
    seat_publish();
}
