#include <stdio.h>
#include <unistd.h>

int win(){
    printf("Damn a win function? You lucky you don't gotta use /bin/sh\x00\n");
    printf("Anyways here's your flag\x00\n");
    sleep(4);
    printf("Maybe you won't get your flag after all\x00\n");
    return 0;
}

int main(){
    setbuf(stdout, NULL);
    char s[67];
    printf("67 this 67 that how bout I give you 67 space on the %p\n", s);
    fgets(s, 0x67, stdin);
    return 0;
}
