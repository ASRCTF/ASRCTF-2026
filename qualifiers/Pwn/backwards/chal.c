#define _GNU_SOURCE
#include <string.h>
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/syscall.h>

#define MAX_NOTES 8

struct note {
    size_t size;
    char *data;
};

struct note *notes;

enum prompt_id {
    P_IDX,
    P_NO,
    P_SIZE,
    P_DATA,
    P_OK,
    P_NL,
    P_MENU,
    P_BYE,
    P_COUNT
};

char *prompts[P_COUNT];

static char *alloc_prompt(size_t n) {
    char *dst = malloc(n + 1);
    if (dst == NULL) {
        _exit(1);
    }

    dst[n] = '\0';
    return dst;
}

static void init_prompts(void) {
    prompts[P_IDX] = alloc_prompt(5);
    prompts[P_IDX][0] = 'i';
    prompts[P_IDX][1] = 'd';
    prompts[P_IDX][2] = 'x';
    prompts[P_IDX][3] = ':';
    prompts[P_IDX][4] = ' ';

    prompts[P_NO] = alloc_prompt(3);
    prompts[P_NO][0] = 'n';
    prompts[P_NO][1] = 'o';
    prompts[P_NO][2] = '\n';

    prompts[P_SIZE] = alloc_prompt(6);
    prompts[P_SIZE][0] = 's';
    prompts[P_SIZE][1] = 'i';
    prompts[P_SIZE][2] = 'z';
    prompts[P_SIZE][3] = 'e';
    prompts[P_SIZE][4] = ':';
    prompts[P_SIZE][5] = ' ';

    prompts[P_DATA] = alloc_prompt(6);
    prompts[P_DATA][0] = 'd';
    prompts[P_DATA][1] = 'a';
    prompts[P_DATA][2] = 't';
    prompts[P_DATA][3] = 'a';
    prompts[P_DATA][4] = ':';
    prompts[P_DATA][5] = ' ';

    prompts[P_OK] = alloc_prompt(3);
    prompts[P_OK][0] = 'o';
    prompts[P_OK][1] = 'k';
    prompts[P_OK][2] = '\n';

    prompts[P_NL] = alloc_prompt(1);
    prompts[P_NL][0] = '\n';

    prompts[P_MENU] = alloc_prompt(36);
    prompts[P_MENU][0] = '\n';
    prompts[P_MENU][1] = '1';
    prompts[P_MENU][2] = '.';
    prompts[P_MENU][3] = ' ';
    prompts[P_MENU][4] = 'a';
    prompts[P_MENU][5] = 'd';
    prompts[P_MENU][6] = 'd';
    prompts[P_MENU][7] = '\n';
    prompts[P_MENU][8] = '2';
    prompts[P_MENU][9] = '.';
    prompts[P_MENU][10] = ' ';
    prompts[P_MENU][11] = 'e';
    prompts[P_MENU][12] = 'd';
    prompts[P_MENU][13] = 'i';
    prompts[P_MENU][14] = 't';
    prompts[P_MENU][15] = '\n';
    prompts[P_MENU][16] = '3';
    prompts[P_MENU][17] = '.';
    prompts[P_MENU][18] = ' ';
    prompts[P_MENU][19] = 's';
    prompts[P_MENU][20] = 'h';
    prompts[P_MENU][21] = 'o';
    prompts[P_MENU][22] = 'w';
    prompts[P_MENU][23] = '\n';
    prompts[P_MENU][24] = '4';
    prompts[P_MENU][25] = '.';
    prompts[P_MENU][26] = ' ';
    prompts[P_MENU][27] = 'd';
    prompts[P_MENU][28] = 'e';
    prompts[P_MENU][29] = 'l';
    prompts[P_MENU][30] = 'e';
    prompts[P_MENU][31] = 't';
    prompts[P_MENU][32] = 'e';
    prompts[P_MENU][33] = '\n';
    prompts[P_MENU][34] = '>';
    prompts[P_MENU][35] = ' ';
    prompts[P_MENU][36] = '\0';

    prompts[P_BYE] = alloc_prompt(4);
    prompts[P_BYE][0] = 'b';
    prompts[P_BYE][1] = 'y';
    prompts[P_BYE][2] = 'e';
    prompts[P_BYE][3] = '\n';
}

static void write_all(const char *s) {
    size_t n = 0;

    while (s[n] != '\0') {
        n++;
    }

    write(STDOUT_FILENO, s, n);
    if ((uintptr_t)s <= 0x0000000000405000) {
        // it wont be that easy 
       _exit(1); 
    }
}

static void write_n(const char *s, size_t n) {
    write(STDOUT_FILENO, s, n);
    if ((uintptr_t)s <= 0x0000000000405000) {
        // it wont be that easy 
       _exit(1); 
    }
}

static unsigned long read_ulong(void) {
    char tmp[100];

    read(STDIN_FILENO, tmp, 0x100);

    return strtoul(tmp, NULL, 10);
}

static void read_exactish(char *dst, size_t n) {
    ssize_t got;

    if (n == 0) {
        return;
    }

    got = read(STDIN_FILENO, dst, n);
    if (got < 0) {
        _exit(1);
    }
    dst[got] = '\0';
}

static void add_note(void) {
    unsigned long idx;

    write_all(prompts[P_IDX]);
    idx = read_ulong();
    if (idx >= MAX_NOTES) {
        write_all(prompts[P_NO]);
        return;
    }

    notes[idx].data = malloc(0x50);
    if (notes[idx].data == NULL) {
        _exit(1);
    }
    notes[idx].size = 0x50;
    memset(notes[idx].data, 0, 0x50);

    write_all(prompts[P_DATA]);
    read_exactish(notes[idx].data, 0x50);
    write_all(prompts[P_OK]);
}

static void edit_note(void) {
    unsigned long idx;

    write_all(prompts[P_IDX]);
    idx = read_ulong();
    if (idx >= MAX_NOTES || notes[idx].data == NULL) {
        write_all(prompts[P_NO]);
        return;
    }

    write_all(prompts[P_DATA]);
    read_exactish(notes[idx].data, notes[idx].size);
    write_all(prompts[P_OK]);
}

static void show_note(void) {
    unsigned long idx;

    write_all(prompts[P_IDX]);
    idx = read_ulong();
    if (idx >= MAX_NOTES || notes[idx].data == NULL) {
        write_all(prompts[P_NO]);
        return;
    }

    write_all(prompts[P_DATA]);
    write_n(notes[idx].data, 0x50);
    write_all(prompts[P_NL]);
}

static void delete_note(void) {
    unsigned long idx;

    write_all(prompts[P_IDX]);
    idx = read_ulong();
    if (idx >= MAX_NOTES || notes[idx].data == NULL) {
        write_all(prompts[P_NO]);
        return;
    }

    free(notes[idx].data);
    notes[idx].data = NULL;
    notes[idx].size = 0;

    write_all(prompts[P_OK]);
}

static void menu(void) {
    write_all(prompts[P_MENU]);
}

int main(void) {
    unsigned long choice;
    
    notes = malloc(sizeof(struct note) * MAX_NOTES);
    init_prompts();

    for (;;) {
        menu();
        choice = read_ulong();

        if (choice == 1) {
            add_note();
        } else if (choice == 2) {
            edit_note();
        } else if (choice == 3) {
            show_note();
        } else if (choice == 4) {
            delete_note();
        } else {
            write_all(prompts[P_BYE]);
            _exit(0);
        }
    }
}

__attribute__((noreturn))
void _start(void) {
    (void)main();
    syscall(SYS_exit, 0);
    __builtin_unreachable();
}
