#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(){
    char *a = "Whelp no flag";
    int size = 13;
    char guess[14];
    printf(">");
    fgets(guess, 14, stdin);
    guess[strcspn(guess, "\n")] = '\0';
    if (strcmp(guess, a) == 0){
        printf("yep, no flag");
        return 0;
    }
    return 0;
}
