#include <stdio.h>
#include <stdlib.h>

void win(void) {
    puts("\n_w4y");
}

void vuln(void) {
    char buf[32];
    printf("Enter access code: ");
    fflush(stdout);
    gets(buf);
}

int main(void) {
    printf("win() is at %p\n", (void *)win);
    setvbuf(stdout, NULL, _IONBF, 0);
    vuln();
    return 0;
}
