#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <seccomp.h>

#include <fcntl.h>
#include <unistd.h>

__attribute__((used, noinline))
void gadget() {
    asm volatile (
        "pop %rdi;"
        "ret;"
    );

    asm volatile (
        "pop %rsi;"
        "ret;"
    );
}

void setup_seccomp() {
    scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_KILL);

    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit_group), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(open), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(openat), 0);

    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(brk), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(mmap), 0);

    seccomp_load(ctx);
}

void setup() {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
    setup_seccomp();
}

const char* ascii = 
"      ⢀⣀⣀                     \n"
"     ⠰⣿⡉⠹⢧⣶⣦⣤⣀⣀               \n"
"     ⣴⠛⠻⣧⣼⡟⠿⠿⣿⣿⣿⣿⣿⣶⣶⣤⣤⣀⡀      \n"
"    ⢀⣿⢶⣄⢠⣿⣷⣶⣦⣤⣈⣉⠙⠛⠻⠿⣿⣿⣿⣿⣿⠁    \n"
"    ⢻⣇⡀⠛⣿⡟⠛⠿⢿⣿⣿⣿⣿⣿⣶⣦⣤⣄⣉⣿⡏  ⣄  \n"
"    ⣟⠉⠹⢶⣿⣿⣷⣶⣦⣤⣌⣉⣙⠛⠛⠻⠿⢿⡿⠋⣠⣴⣦⡈⠓ \n"
"   ⣰⠟⢻⣆⣾⣏⡉⠛⠛⠿⢿⣿⣿⣿⣿⣿⣶⡶ ⣠⣾⣿⣿⠟⠁  \n"
"  ⢀⣽⣦⣄⢹⣿⣿⣿⣿⣷⣶⣤⣤⣈⣉⠙⠛⠋⣠⣾⣿⣿⠟⠁    \n"
"  ⢸⣇ ⠻⣿⣏⣉⡉⠛⠻⠿⢿⣿⣿⣿⠋⠠⣾⣿⣿⠟⠁      \n"
" ⢠⣿⠉⠿⣼⣿⣿⣿⣿⣿⣷⣶⣦⣤⣬⡁⢠⡦⠈⠛⡁        \n"
" ⣴⠿⢶⣄⣿⣧⣤⣄⣉⡉⠛⠛⠿⢿⡟⣀⣠⣤⣶⣾⠇        \n"
" ⢿⣤⣌⣹⣿⣿⣿⣿⣿⣿⣿⣶⣶⣤⣤⣈⣉⠙⣻⡿         \n"
"   ⠉⠙⠿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇         \n"
"          ⠉⠉⠛⠛⠿⠿⣿⣿⣿⡟          \n"
"                 ⠈⠉⠁          \n";

typedef struct {
    char name[64];
    char content[1024];
} Note;


void notebookSM() {

    printf("Welcome to NotebookSM: \n\n");
    printf(ascii);

    char name[64];
    Note notesList[64];
    char content[1024];
    int index = 0;
    int buf;
    
    while (1) {
        printf("---------------------\n");
        printf("Enter an option:\n");
        printf("1. Create Notebook\n");
        printf("2. Edit Notebook\n");
        printf("3. Delete Notebook\n");
        printf("4. View Notebook\n");
        printf("5. Exit\n");
        printf("---------------------\n");

        printf("\n> ");

        scanf("%d%*c", &buf);

        switch (buf) {
            case 1: {
                printf("Name your Notebook:\n");
                printf("> ");
                fgets(name, 64, stdin);
                printf("Enter the contents of your Notebook:\n");
                printf("> ");
                fgets(content, 1024, stdin);
                memcpy(notesList[index].name, name, 64);
                memcpy(notesList[index].content, content, 1024);
                index++;
                break;
            }
            
            case 2: {
                printf("Enter the name of Notebook to edit:\n");
                
                printf("> ");
                fgets(name, 64, stdin);
                int found = 0;

                for (int i = 0; i < 64; i++) {
                    if (strcmp(notesList[i].name, name) == 0) {
                        printf("Enter the content to input: \n");  
                        printf("> ");
                        fgets(content, 1024, stdin);
                        strcpy(notesList[i].content, content);
                        found = 1;
                        break;
                    }
                }

                if (!found) printf("Notes not found!\n");
                break;
            }

            case 3: {
                printf("Enter the Name of the Notebook to Delete:\n");
                printf("> ");
                fgets(name, 64, stdin);
                int found = 0;

                for (int i = 0; i < 64; i++) {
                    if (strcmp(notesList[i].name, name) == 0) {
                        memset(notesList[i].name, 0, 64);
                        memset(notesList[i].content, 0, 1000);
                        found = 1;
                        break;
                    }
                }

                if (!found) printf("Notes not found!\n");
                index--;
                break;
            }
            
            case 4: {
                printf("Enter the Name of the Notebook to View:\n");
                printf("> ");
                fgets(name, 64, stdin);
                int found = 0;
                for (int i = 0; i < 64; i++) {
                    if (strcmp(notesList[i].name, name) == 0) {
                        printf("Notes Name: %s\n", notesList[i].name);
                        printf("Content:\n%s\n", notesList[i].content);
                        found = 1;
                        break;
                    }
                }

                if (!found) printf("Notes not found!\n");
                break;
            }

            case 5: {                
                printf("Exitting!\n");
                return;
            }

            default: {
                printf("Invalid Option!\n");
                break;
            }
        }
    }

    return;
}

int main() {
    setup();
    notebookSM();
    return 0;
}