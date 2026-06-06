#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(){
    int i;
    char enc_msg[] = {'P', 'H', 'O', 'S', 'G', 'O', 'F', 'P', 'E', 'F', 'Y', 'F', 'F', 'G', 'F', 'K', 'J', 'O', 'F', 'G', 'O'};
    char input[0x100];
    int len = sizeof(enc_msg);
    int key = 0x6f;

    printf(">");
    if (fgets(input, sizeof(input), stdin) == NULL) return 0;
    input[strcspn(input, "\n")] = '\0';
    
    if (strlen(input) != len){
        return 0;
    }

    for (i=0; i<sizeof(enc_msg); i++){ 
        int res = (int)input[i] ^ key;
        char enc_char = (char)((res + 4) % 26 + 'A');
        if (enc_char != enc_msg[i]){
            return 0;
        }
    }
    printf("Please actually don't");
    return 0;
}
