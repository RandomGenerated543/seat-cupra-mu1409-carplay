#include "alt111.h"
#include <stdlib.h>
/* Registry owns Wide/Full; native Center has its own explicit target file,
 * matching R57's third-area boundary without inventing registry keys. */
int seat_settings_geometry(struct alt111_profile *profile)
{
    struct alt111_settings *s;struct alt111_settings_paths paths={"/tmp","/mnt/app/root"};
    char error[160],buf[192];int fd,n,x,y,w,h;unsigned i;struct alt111_profile candidate;
    if(!profile)return -1;
    candidate=*profile;
#ifdef ALT111_SETTINGS_TEST
    {const char *t=getenv("ALT111_SETTINGS_TEMP_ROOT"),*r=getenv("ALT111_SETTINGS_PERSISTENT_ROOT");if(t&&r){paths.temp=t;paths.persistent=r;}}
#endif
    s=calloc(1,sizeof(*s));if(!s)return -1;
    if(alt111_settings_load(&paths,s,error,sizeof(error)) || alt111_setting_integer(s,ALTSET_VIEWAREAS_COUNT)!=3){free(s);return -1;}
    for(i=0;i<2;i++){
        unsigned base=i?ALTSET_VIEWAREA_1_X:ALTSET_VIEWAREA_0_X;
        if(alt111_setting_integer(s,base)||alt111_setting_integer(s,base+1)||
           alt111_setting_integer(s,base+2)!=1010||alt111_setting_integer(s,base+3)!=376){free(s);return -1;}
        candidate.views[i].safe.x=alt111_setting_integer(s,base+4);
        candidate.views[i].safe.y=alt111_setting_integer(s,base+5);
        candidate.views[i].safe.width=alt111_setting_integer(s,base+6);
        candidate.views[i].safe.height=alt111_setting_integer(s,base+7);
    }
    free(s);
    {const char *file="/mnt/app/root/altscreen-u2/harman-r13/center.conf";
#ifdef ALT111_SETTINGS_TEST
     if(getenv("SEAT_CENTER_CONFIG"))file=getenv("SEAT_CENTER_CONFIG");
#endif
     fd=open(file,O_RDONLY);}
    if(fd<0)return -1;
    n=(int)read(fd,buf,sizeof(buf)-1);close(fd);if(n<=0 || n>=(int)sizeof(buf)-1)return -1;
    buf[n]=0;
    if(sscanf(buf,"x=%d\ny=%d\nw=%d\nh=%d",&x,&y,&w,&h)!=4||x<0||y<0||w<1||h<1)return -1;
    candidate.views[2].safe.x=(unsigned)x;candidate.views[2].safe.y=(unsigned)y;
    candidate.views[2].safe.width=(unsigned)w;candidate.views[2].safe.height=(unsigned)h;
    if(alt111_profile_validate(&candidate)!=ALT111_OK)return -1;
    *profile=candidate;return 0;
}
