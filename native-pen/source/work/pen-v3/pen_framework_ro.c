#include <sys/mount.h>
#include <stdio.h>
#include <string.h>
int main(int argc,char**argv){if(argc!=2||strcmp(argv[1],"/system/framework/services.jar"))return 2;if(mount(NULL,argv[1],NULL,MS_BIND|MS_REMOUNT|MS_RDONLY|MS_NOSUID|MS_NODEV,NULL)){perror("pen framework readonly");return 1;}return 0;}
