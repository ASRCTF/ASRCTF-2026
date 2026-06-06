//gcc chal.c -o chal -fno-stack-protector -z relro -z now -z noexecstack -no-pie
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char flag_buf[0x500];
int son; 


void setup(){
    son = 0xDEADDEAD;
    setbuf(stdin, NULL);
    setbuf(stdout, NULL);
}

void win(){
    printf("You may have won, but did you save my son?\n");
    if (son != 0xAAAAAAAA){
        printf("How dare you win without saving my son, how self-centered of you\n");
        exit(0);
    }
    printf("You did it! You saved my son\n");
    printf("Maybe you should make him stop screaming though...\n");
    FILE *p = fopen("flag.txt", "r");
    if (p == NULL){
        printf("Flag file not found please open a ticket if on remote server.\n");
        exit(0);
    }
    fgets(flag_buf, 0x250, p);
    flag_buf[strcspn(flag_buf, "\n")] = '\0';
    puts(flag_buf);
    fclose(p);

}


int main(){
    setup();
    printf("Make a choice, revive my son or enter the win function...\n>");
    char buffer[10];
    fgets(buffer, 0x20, stdin);
    return 0;
}
