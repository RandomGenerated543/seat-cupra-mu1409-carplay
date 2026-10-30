/* Host-only regression for the exact canonical validator/profile serializer. */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../src/native/mibr-control/mibr_v3_profile_store.c"
int main(int argc,char **argv){
 char profile[8193],next[8193],again[8193],parse[8193];size_t n,nn,an;
 struct alt111_settings s;FILE *f;char *line;int id;
 assert(argc==2);f=fopen(argv[1],"rb");assert(f);
 n=fread(profile,1,8192,f);assert(!ferror(f)&&n&&n<8192);fclose(f);profile[n]=0;
 assert(!alt111_settings_defaults(&s,"mibr_legacy"));
 assert(!strcmp(s.value[ALTSET_DISPLAY_ZOOMFACTOR],"70"));
 assert(!alt111_setting_validate(ALTSET_DISPLAY_ZOOMFACTOR,"0"));
 assert(!alt111_setting_validate(ALTSET_DISPLAY_ZOOMFACTOR,"70"));
 assert(!alt111_setting_validate(ALTSET_DISPLAY_ZOOMFACTOR,"150"));
 assert(alt111_setting_validate(ALTSET_DISPLAY_ZOOMFACTOR,"20"));
 assert(alt111_setting_validate(ALTSET_DISPLAY_ZOOMFACTOR,"69"));
 assert(alt111_setting_validate(ALTSET_DISPLAY_ZOOMFACTOR,"151"));
 assert(alt111_setting_validate(ALTSET_DISPLAY_ZOOMFACTOR,"70%"));
 assert(alt111_setting_validate(ALTSET_DISPLAY_ZOOMFACTOR,"070"));
 strcpy(parse,profile);line=strtok(parse,"\n");
 while(line){char *eq=strchr(line,'=');assert(eq);*eq++=0;id=alt111_setting_find(line);assert(id>=0);
  assert(!alt111_settings_set(&s,(unsigned)id,eq,ALT111_TEMP));line=strtok(NULL,"\n");}
 assert(!profile_candidate(profile,n,&s,ALTSET_DISPLAY_ZOOMFACTOR,"100",1,next,&nn));
 assert(nn==n+strlen("display.zoomFactor=100\n"));
 assert(!memcmp(profile,next,n));assert(!strcmp(next+n,"display.zoomFactor=100\n"));
 strcpy(s.value[ALTSET_DISPLAY_ZOOMFACTOR],"100");
 assert(!profile_candidate(next,nn,&s,ALTSET_DISPLAY_ZOOMFACTOR,"70",1,again,&an));
 assert(!memcmp(profile,again,n));assert(!strcmp(again+n,"display.zoomFactor=70\n"));
 assert(!profile_candidate(again,an,&s,ALTSET_NAVIGATION_ETA,"no",0,next,&nn));
 assert(strstr(next,"display.zoomFactor=70\n"));
 puts("ZOOM_PROFILE=PASS defaults bounds old45_upgrade new46_edit unrelated_preferences_preserved");return 0;
}
