#define _GNU_SOURCE
#include <sys/system_properties.h>
#include <sys/utsname.h>
#include <sys/file.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <signal.h>
#include <stdlib.h>
#include <pthread.h>
#include <sys/ioctl.h>
#include <sound/asound.h>
#ifndef R94_CLI
#include <jni.h>
#endif
#define STATE "/data/adb/r94-speaker-direction-v19"
static int fd=-1,lockfd=-1;
static volatile sig_atomic_t stopping;
static pthread_mutex_t mutex=PTHREAD_MUTEX_INITIALIZER;
static void stop(int n){(void)n;stopping=1;}
static int ctl(const char *name,int write,long *values,int count){
 struct snd_ctl_elem_value v;memset(&v,0,sizeof(v));v.id.iface=SNDRV_CTL_ELEM_IFACE_MIXER;
 snprintf((char*)v.id.name,sizeof(v.id.name),"%s",name);
 if(write)for(int i=0;i<count;i++)v.value.integer.value[i]=values[i];
 if(ioctl(fd,write?SNDRV_CTL_IOCTL_ELEM_WRITE:SNDRV_CTL_IOCTL_ELEM_READ,&v)<0)return -1;
 if(!write)for(int i=0;i<count;i++)values[i]=v.value.integer.value[i];return 0;
}
static int initialize(void){
 if(fd>=0)return 0;
 char board[PROP_VALUE_MAX];struct utsname u;
 if(getuid()!=0||__system_property_get("ro.product.board",board)<=0||strcmp(board,"spinel")||
    uname(&u)||!strstr(u.version,"#35 SMP PREEMPT "))return -20;
 lockfd=open(STATE "/route.lock",O_CREAT|O_RDWR|O_CLOEXEC|O_NOFOLLOW,0600);
 if(lockfd<0 || flock(lockfd,LOCK_EX|LOCK_NB)){if(lockfd>=0)close(lockfd);lockfd=-1;return -24;}
 fd=open("/dev/snd/controlC0",O_RDWR|O_CLOEXEC);
 long s[22];if(fd<0||ctl("TB371FC Route State",0,s,22)||s[0]!=19){if(fd>=0)close(fd);fd=-1;close(lockfd);lockfd=-1;return -20;}
 return 0;
}
static int complete(long s[22],long req[5]){
 static const int factory[]={0,1,0,1};
 for(int n=0;n<4;n++){
  int b=2+n*5;
  if(s[b]!=s[1])return 0;
  if(s[b+2])return -1;
  if(req[0]){if(s[b+1]!=(req[n+1]==factory[n]?0x410:0x401)||(s[b+4]&2))return -1;}
  else if(s[b+4])return -1;
 }
 return 1;
}
static void report(long s[22],int rc){
 printf("NATIVE_API19 gen=%ld result=%d",s[1],rc);
 for(int n=0;n<4;n++){int b=2+n*5;printf(" chip%d_ack=%ld_word=%04lx_err=%ld_epoch=%ld_flags=%ld",n,s[b],s[b+1],s[b+2],s[b+3],s[b+4]);}
 printf("\n");fflush(stdout);
}
static int request(long req[5],int force){
 int rc=initialize();if(rc)return rc;
 long s[22]={0},old[5];
 if(ctl("TB371FC Route State",0,s,22)||ctl("TB371FC Route Request",0,old,5))return -22;
 if(!force&&!memcmp(req,old,sizeof(old))&&complete(s,req)==1)return req[0]?4:0;
 if(ctl("TB371FC Route Request",1,req,5))return -22;
 for(int t=0;t<40;t++){
  if(ctl("TB371FC Route State",0,s,22))return -22;
  rc=complete(s,req);
  if(rc==1){report(s,req[0]?4:0);return req[0]?4:0;}
  if(rc<0){report(s,-21);return -21;}
  usleep(10000);
 }
 report(s,-21);return -21;
}
static int restore(void){long req[5]={0,0,1,0,1};return request(req,0);}
static int apply(int r,int swap){
 /* Candidate baseline: display1 is factory pairing. Physical calibration
  * is pending; the table is explicit and can be revised from listening. */
 static const int table[4][4]={{0,0,1,1},{0,1,0,1},{1,1,0,0},{1,0,1,0}};
 if(r<0||r>3||swap<0||swap>1)return -20;
 long req[5]={1,0,0,0,0};for(int n=0;n<4;n++)req[n+1]=table[r][n]^swap;
 return request(req,0);
}
#ifndef R94_CLI
JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM *v,void *r){(void)v;(void)r;signal(SIGTERM,stop);return JNI_VERSION_1_6;}
JNIEXPORT jboolean JNICALL Java_R94SpeakerDirection_stopRequested(JNIEnv *e,jclass c){(void)e;(void)c;return stopping||access(STATE "/stop",F_OK)==0;}
JNIEXPORT jint JNICALL Java_R94SpeakerDirection_apply(JNIEnv *e,jclass c,jint r,jint s){(void)e;(void)c;pthread_mutex_lock(&mutex);int rc=apply(r,s);pthread_mutex_unlock(&mutex);return rc;}
JNIEXPORT jint JNICALL Java_R94SpeakerDirection_restore(JNIEnv *e,jclass c){(void)e;(void)c;pthread_mutex_lock(&mutex);int rc=restore();pthread_mutex_unlock(&mutex);return rc;}
JNIEXPORT jint JNICALL Java_R94SpeakerDirection_swap(JNIEnv *e,jclass c){
 (void)e;(void)c;pthread_mutex_lock(&mutex);long v=0;int rc=initialize();
 if(!rc&&ctl("Swap channel",0,&v,1))rc=-1;
 pthread_mutex_unlock(&mutex);return rc?rc:(v==0||v==1?(int)v:-1);
}
#else
int main(int argc,char **argv){
 (void)mutex;(void)stop;(void)apply;
 if(argc!=2||strcmp(argv[1],"--restore"))return 20;
 int rc=restore();printf("RESTORE_RESULT=%d\n",rc);return rc?21:0;
}
#endif
