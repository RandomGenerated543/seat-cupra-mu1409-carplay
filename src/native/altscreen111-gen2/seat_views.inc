/* Three SEAT safe rectangles; preserve the original full outer video canvas. */
static int seat_adjacent(CFMutableDictionaryRef d,unsigned self)
{
    typedef CFTypeRef (*create_fn)(void *,int,const void *);
    create_fn create=(create_fn)sym_next("CFNumberCreate");
    CFMutableArrayRef a=NULL;CFStringRef k=NULL;CFTypeRef n=NULL;unsigned i;int okay=0;
    if(!create)return 0;
    a=p_CFArrayCreateMutable(NULL,0,p_array_callbacks);k=s_cf("adjacentViewAreas");
    if(!a||!k)goto done;
    for(i=0;i<3;i++)if(i!=self){int64_t value=i;n=create(NULL,4,&value);if(!n)goto done;p_CFArrayAppendValue(a,n);p_CFRelease(n);n=NULL;}
    p_CFDictionarySetValue(d,k,a);okay=1;
done:if(n)p_CFRelease(n);if(k)p_CFRelease(k);if(a)p_CFRelease(a);return okay;
}
static int add_reference_viewarea(CFMutableDictionaryRef alt)
{
    CFMutableArrayRef areas=NULL;CFMutableDictionaryRef view=NULL,safe=NULL;
    CFStringRef key=NULL;struct alt111_profile snapshot=g2_profile;unsigned i;int complete=0;
    if(!alt || snapshot.view_count!=3 || seat_settings_geometry(&snapshot)){
        logf_u2("SEAT_VIEW geometry=NOT_READY stock_main_unchanged=1 reconnect_after_boot=1");return 0;
    }
    areas=p_CFArrayCreateMutable(NULL,0,p_array_callbacks);if(!areas)goto done;
    for(i=0;i<3;i++){
        const struct alt111_view *v=&snapshot.views[i];
        view=dict_new();safe=dict_new();if(!view||!safe)goto done;
        set_i64(view,"widthPixels",v->area.width);set_i64(view,"heightPixels",v->area.height);
        set_i64(view,"originXPixels",v->area.x);set_i64(view,"originYPixels",v->area.y);
        set_i64(safe,"widthPixels",v->safe.width);set_i64(safe,"heightPixels",v->safe.height);
        set_i64(safe,"originXPixels",v->safe.x);set_i64(safe,"originYPixels",v->safe.y);
        set_false(view,"drawUIOutsideSafeArea");set_false(view,"viewAreaTransitionControl");
        if(!seat_adjacent(view,i))goto done;
        key=s_cf("safeArea");if(!key)goto done;p_CFDictionarySetValue(view,key,safe);p_CFRelease(key);key=NULL;
        p_CFArrayAppendValue(areas,view);p_CFRelease(safe);safe=NULL;p_CFRelease(view);view=NULL;
        logf_u2("SEAT_VIEW preset=%u name=%s full=%ux%u safe=%ux%u@%u,%u",i,
            i==0?"Wide":i==1?"Full":"Center",v->area.width,v->area.height,v->safe.width,v->safe.height,v->safe.x,v->safe.y);
    }
    key=s_cf("viewAreas");if(!key)goto done;p_CFDictionarySetValue(alt,key,areas);p_CFRelease(key);key=NULL;
    set_i64(alt,"initialViewArea",0);complete=1;
done:if(key)p_CFRelease(key);if(safe)p_CFRelease(safe);if(view)p_CFRelease(view);if(areas)p_CFRelease(areas);
    if(!complete)logf_u2("SEAT_VIEW advertisement=FAILED no_partial_array_committed=1");
    return complete;
}
#ifndef SEAT_VIEW_DICTIONARY_TEST
static void seat_view_poll(void)
{
    static uint64_t next;uint64_t now=monotonic_ms(),session;int selected,requested=-1,ack=-1,exhausted=0,rc=ALT111_WAIT,changed=0;
    unsigned shown=0;char b[512];int n,fd;
    if(now<next)return;next=now+250;selected=seat_settings_view();
    pthread_mutex_lock(&g2_core_lock);session=g2_control_session;
    if(session&&g2_control.active&&g2_control.desired&&selected>=0&&selected<3){
        if(g2_control.desired_view!=(unsigned)selected){rc=alt111_control_intent(&g2_control,1,(unsigned)selected);changed=1;pthread_cond_broadcast(&g2_core_cv);}
        requested=(int)g2_control.desired_view;ack=g2_control.acknowledged_view;exhausted=(int)g2_control.exhausted;shown=g2_control.shown_ack;
    }
    pthread_mutex_unlock(&g2_core_lock);
    if(changed)logf_u2("SEAT_VIEW request selected=%d session=%llu core_rc=%d",selected,(unsigned long long)session,rc);
    n=snprintf(b,sizeof(b),"revision=seat_r13_three_views_v01\nconfigured_count=3\ngeometry_source=canonical_registry_and_center_conf\n"
        "stored_index=%d\nrequested_index=%d\nphone_acknowledged_index=%d\nshown_ack=%u\nretry_exhausted=%d\nsession=%llu\nvisible=UNKNOWN\n",
        selected,requested,ack,shown,exhausted,(unsigned long long)session);
    if(n>0&&(size_t)n<sizeof(b)){fd=open("/tmp/mibr-seat-views.status",O_WRONLY|O_CREAT|O_TRUNC,0600);if(fd>=0){(void)write(fd,b,(size_t)n);(void)close(fd);}}
}
#endif
