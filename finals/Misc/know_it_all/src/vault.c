
#include <stdio.h>
#include <string.h>

static const char cipher[] = "NFEPGS{1yy5_l}";

static void rot13(const char *in, char *out) {
    for (int i = 0; in[i]; i++) {
        char c = in[i];
        if      (c >= 'A' && c <= 'Z') out[i] = 'A' + (c - 'A' + 13) % 26;
        else if (c >= 'a' && c <= 'z') out[i] = 'a' + (c - 'a' + 13) % 26;
        else                           out[i] = c;
    }
    out[strlen(in)] = '\0';
}

int main(void) {
    char flag[64];
    rot13(cipher, flag);
    printf("%s\n", flag);
    return 0;
}
