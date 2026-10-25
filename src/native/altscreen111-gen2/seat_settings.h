#ifndef SEAT_SETTINGS_H
#define SEAT_SETTINGS_H
#include <stdint.h>
#include <stddef.h>
#include "alt111_settings.h"
int seat_navigation_url(const struct alt111_settings *,char *,size_t);
void seat_settings_poll(uint64_t now,uint64_t session);
int seat_settings_url(char *,size_t);
uint64_t seat_settings_revision(void);
int seat_settings_query(void);
void seat_settings_ack(uint64_t session,uint64_t revision,int success,uint64_t request);
int seat_settings_view(void);
struct alt111_profile;
int seat_settings_geometry(struct alt111_profile *);
#endif
