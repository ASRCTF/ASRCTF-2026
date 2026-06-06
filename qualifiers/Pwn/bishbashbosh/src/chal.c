#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/md5.h>

void setup() {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
}

const char *fetch =
"                     z z   z                     %s@%s\n"
" z       zz         z      z z z   z z           ------------------------\n"
"                  z         z  zzz    z          OS: fake os\n"
" zz    zz  z     z  z   z    z z z   zz    z     Kernel: real kernel\n"
"     zzz     z z                 z z    z        Shell: BishBashBosh\n"
"         z  z   zxtkcbgrx            z z z       \n"
" z            w2PPPQQQQONOUr  z      z  z        \n"
"    z  zz pb4ULLMNOOONNNOROMR20mz z  z     z     \n"
" zz zzzu1NQTRLTY1Z11ZXYZ1ZPVOPSROTp   zz         \n"
"z    vZRUWVTQSY3Z11ZZZ3ZVZ1ZTNWUWVRVq  z         \n"
"zz   dRPPPPRSPU4353533Z1VUUVPRTPPPPP7zz z        \n"
"   z tZRRTPPQYSSTTUVUUVVRRRSYTPPRSQVp  z         \n"
"z    zu3RPRQUUPQRRUVVVVVSRRPRVQQPQZmz  zzz       \n"
"  z    yl2TUSPQSPVUSTWSYUPRQPRWTYfx   z    z     \n"
" zz       uf1TRPPW6VUXTZPPPQSXar  z     z        \n"
" zz   z     vja59cba980ac059gsz   z    z z z     \n"
"z zz    z     z    vuuvzz  z         z  z        \n"
" z  zzz          z     z      zz z               \n"
"              z   zzzz   z     z  z      z z     \n"
"zz zz z  z       z             z    z  zz        \n"
"zz     z  z z          z                 z       \n"
"     z        z     zz        z      z  z        \n"
"   z   z  z    z z          z                    \n"
"  zz         zz        z      z                  \n";

typedef struct {
    char username[64];
    char passwd[64];
    void (*init_password)();
} BashProfile;

void init(BashProfile *bp, void (*init_password)(), char *username, char *passwd) {
    strcpy(bp->username, username);
    init_password(bp, passwd);
}

void compute_md5(char *str, unsigned char digest[16]) {
    MD5_CTX ctx;

    MD5_Init(&ctx);
    MD5_Update(&ctx, str, strlen(str));
    MD5_Final(digest, &ctx);
}

void hash_password(BashProfile *bp, char* passwd) {
    char hashed_pwd[16];
    compute_md5(passwd, hashed_pwd);
    strcpy(bp->passwd, hashed_pwd);
}

void whoami(BashProfile bp) {
    printf(bp.username);
}

int main() {
    setup();

    BashProfile bp;
    bp.init_password = hash_password;

    char username[64];
    char passwd[64];

start:

    printf("Welcome to BishBashBosh:\n");

    printf("Please enter a username:\n> ");
    gets(username);

    printf("Please enter a password:\n> ");
    gets(passwd);

    init(&bp, bp.init_password, username, passwd);

    while (1) {
        char command[64];
        printf("> ");
        fgets(command, sizeof(command), stdin);

        command[strcspn(command, "\n")] = 0;

        if (strlen(command) == 0) {
            continue;
        }

        if (strcmp(command, "whoami") == 0) {
            whoami(bp);
        }
        else if (strcmp(command, "passwd") == 0) {
            printf("No passwd for you!\n");
        }
        else if (strcmp(command, "fastfetch") == 0) {
            printf(fetch, bp.username, bp.passwd);
        }
        else if (strcmp(command, "help") == 0) {
            printf("Available Commands:\n");
            printf("1. whoami\n");
            printf("2. passwd\n");
            printf("3. fastfetch\n");
            printf("4. exit\n");
        }
        else if (strcmp(command, "exit") == 0) {
            printf("Exiting to login screen.\n");
            goto start;
        }
        else {
            printf("Invalid Command\n");
        }
    }

    return 0;
}