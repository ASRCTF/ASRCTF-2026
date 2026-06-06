/*gcc -o chal chal.c -std=c89 -no-pie -fno-stack-protector -Wno-implicit-function-declaration*/
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

void setup(){
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
}

int vuln(){
    char input_buffer[0x30];
    printf("A single gets with no leak should be safe right?\n>");
    gets(input_buffer);
    return 0;
}

int main(){
    setup();
    vuln();
    return 0;
}
