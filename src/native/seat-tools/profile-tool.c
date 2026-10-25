/* Validate and merge only view geometry; preserve current navigation preferences. */
#include "alt111_settings.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int managed(const char *k){return !strncmp(k,"viewarea.",9)||!strncmp(k,"viewareas.",10);}
static int read_profile(const char *path,struct alt111_settings *s,unsigned *seen){
 FILE *f;char *buf,*line,*end;size_t n;int id,rc=-1;
 if(alt111_settings_defaults(s,"mibr_legacy"))return -1;
 buf=malloc(ALT111_SETTING_BATCH_CAP+2);if(!buf)return -1;
 f=fopen(path,"rb");if(!f){free(buf);return -1;}
 n=fread(buf,1,ALT111_SETTING_BATCH_CAP+1,f);
 if(ferror(f)||!n||n>ALT111_SETTING_BATCH_CAP||buf[n-1]!='\n'||memchr(buf,0,n)){fclose(f);free(buf);return -1;}
 fclose(f);buf[n]=0;line=buf;
 while(*line){
  end=strchr(line,'\n');if(!end)goto done;*end=0;
  {char *eq=strchr(line,'=');if(!eq)goto done;*eq++=0;
   id=alt111_setting_find(line);if(id<0||seen[id]++||alt111_settings_set(s,(unsigned)id,eq,ALT111_TEMP))goto done;}
  line=end+1;
 }
 {char error[160];if(alt111_settings_validate(s,error,sizeof(error))){fprintf(stderr,"PROFILE_TOOL invalid=%s\n",error);goto done;}}
 rc=0;
done:free(buf);return rc;
}
int main(int argc,char **argv){
 struct alt111_settings *current=NULL,*before=NULL,*live=NULL;
 struct alt111_settings_paths paths={"/tmp","/mnt/app/root"};
 unsigned seen[ALTSET_COUNT]={0},oldseen[ALTSET_COUNT]={0};unsigned i;int restore,rc=1;
 char error[160];int old_count=0,old_selection=0;
 static const struct {const char *key,*value;} geometry[]={
  {"viewarea.selected","0"},{"viewareas.enabled","1"},{"viewareas.count","3"},{"viewareas.initial","0"},{"viewareas.transition_ms","0"},
  {"viewarea.0.x","0"},{"viewarea.0.y","0"},{"viewarea.0.w","1010"},{"viewarea.0.h","376"},
  {"viewarea.0.safe.x","151"},{"viewarea.0.safe.y","56"},{"viewarea.0.safe.w","708"},{"viewarea.0.safe.h","244"},{"viewarea.0.adjacent","1"},
  {"viewarea.1.x","0"},{"viewarea.1.y","0"},{"viewarea.1.w","1010"},{"viewarea.1.h","376"},
  {"viewarea.1.safe.x","264"},{"viewarea.1.safe.y","56"},{"viewarea.1.safe.w","482"},{"viewarea.1.safe.h","244"},{"viewarea.1.adjacent","0"}
 };
 if(argc<3||argc>4)return 2;
 restore=!strcmp(argv[1],"--restore");
 if((!restore&&strcmp(argv[1],"--upgrade")) || (restore&&argc!=4))return 2;
#ifdef ALT111_SETTINGS_TEST
 paths.temp=getenv("ALT111_SETTINGS_TEMP_ROOT");paths.persistent=getenv("ALT111_SETTINGS_PERSISTENT_ROOT");
 if(!paths.temp||!paths.persistent)return 2;
#endif
 current=calloc(1,sizeof(*current));before=calloc(1,sizeof(*before));live=calloc(1,sizeof(*live));
 if(!current||!before||!live)goto done;
 if(read_profile(argv[2],current,seen))goto done;
 old_count=(int)alt111_setting_integer(current,ALTSET_VIEWAREAS_COUNT);old_selection=(int)alt111_setting_integer(current,ALTSET_VIEWAREA_SELECTED);
 if(!restore && alt111_settings_load(&paths,live,error,sizeof(error)))goto done;
 /* No profile overwrite if the old broker failed to persist a recent edit. */
 for(i=0;!restore && i<ALTSET_COUNT;++i)if(seen[i] && strcmp(current->value[i],live->value[i])){
  fprintf(stderr,"PROFILE_TOOL unsaved_or_foreign_temp=%s\n",alt111_setting(i)->key);goto done;}
 if(restore){
  if(read_profile(argv[3],before,oldseen))goto done;
  for(i=0;i<ALTSET_COUNT;++i)if(managed(alt111_setting(i)->key)){
   if(!oldseen[i])goto done;
   strcpy(current->value[i],before->value[i]);seen[i]=1;}
 }else{
  if(strcmp(current->value[ALTSET_VIEWAREAS_COUNT],"1") && strcmp(current->value[ALTSET_VIEWAREAS_COUNT],"2"))goto done;
  for(i=0;i<sizeof(geometry)/sizeof(geometry[0]);++i){int id=alt111_setting_find(geometry[i].key);
   if(id<0||alt111_settings_set(current,(unsigned)id,geometry[i].value,ALT111_TEMP))goto done;
   seen[id]=1;}
 }
 if(!restore && old_count==2 && old_selection==1)strcpy(current->value[ALTSET_VIEWAREA_SELECTED],"2");
 if(alt111_settings_validate(current,error,sizeof(error))){fprintf(stderr,"PROFILE_TOOL candidate_invalid=%s\n",error);goto done;}
 for(i=0;i<ALTSET_COUNT;++i)if(seen[i])if(printf("%s=%s\n",alt111_setting(i)->key,current->value[i])<0)goto done;
 if(fflush(stdout))goto done;
 rc=0;
done:free(current);free(before);free(live);return rc;
}
