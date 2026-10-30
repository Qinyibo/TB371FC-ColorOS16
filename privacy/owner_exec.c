// SPDX-License-Identifier: Apache-2.0
// Enter the final SELinux domain first, then arm parent-death protection and
// exec a same-domain, non-setuid/capability-bearing private service binary.
#include <errno.h>
#include <limits.h>
#include <signal.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <unistd.h>
#ifndef R94_BACKEND_PATH
#define R94_BACKEND_PATH "/data/adb/modules/r94_privacy_password_test/bin/pms-backing"
#endif
#ifndef R94_GATEWAY_PATH
#define R94_GATEWAY_PATH "/data/adb/modules/r94_privacy_password_test/bin/pms-gateway"
#endif
int main(int argc, char **argv) {
    if (getuid()!=0 || argc!=3) return 20;
    if (!argv[1][0]) return 20;
    for (const char *p=argv[1];*p;p++) if (*p<'0' || *p>'9') return 20;
    char *end=0;errno=0;long expected=strtol(argv[1],&end,10);
    if (errno || !end || *end || expected<=1 || expected>INT_MAX) return 20;
    if (strcmp(argv[2],R94_BACKEND_PATH) && strcmp(argv[2],R94_GATEWAY_PATH)) return 20;
    if (getppid()!=(pid_t)expected) return 21;
    if (prctl(PR_SET_PDEATHSIG,SIGTERM,0,0,0)) return 22;
    if (getppid()!=(pid_t)expected) return 21;
    char *args[]={argv[2],0};execv(argv[2],args);
    return 23;
}
