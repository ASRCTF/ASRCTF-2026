// gcc -o chal chal.c -Wl,-z,relro,-z,now -fPIE -pie -fstack-protector-all
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define MAX 8
#define MAGIC 0x1337133713371337ULL

typedef struct note {
    uint64_t magic;
    size_t size;
    char *data;
    char title[8];
} note;

note *notes[MAX];
int writes;

unsigned long getnum() {
    char buf[0x20] = {};
    read(0, buf, sizeof(buf) - 1);
    return strtoul(buf, 0, 0);
}

int valid(note *n) {
    return n && n->magic == MAGIC && n->size <= 0x600 && n->data;
}

void add() {
    puts("idx?");
    unsigned long idx = getnum();
    if (idx >= MAX || notes[idx]) return;

    puts("size?");
    size_t size = getnum();
    if (size < 0x20 || size > 0x600) _exit(1);

    note *n = malloc(sizeof(note));
    if (!n) _exit(1);

    n->magic = MAGIC;
    n->size = size;
    n->data = malloc(size);
    if (!n->data) _exit(1);

    puts("title?");
    read(0, n->title, sizeof(n->title));
    notes[idx] = n;
    puts("ok");
}

void edit() {
    puts("idx?");
    unsigned long idx = getnum();
    if (idx >= MAX || !valid(notes[idx])) return;
    if (writes >= 3) _exit(0);
    writes++;

    puts("data?");
    read(0, notes[idx]->data, notes[idx]->size);
    puts("ok");
}

void show() {
    puts("idx?");
    unsigned long idx = getnum();
    if (idx >= MAX || !valid(notes[idx])) return;

    write(1, notes[idx]->data, notes[idx]->size);
    puts("");
}

void delete() {
    puts("idx?");
    unsigned long idx = getnum();
    if (idx >= MAX || !valid(notes[idx])) return;

    note *n = notes[idx];
    char *data = n->data;

    n->magic = 0;
    n->size = 0;
    free(n);
    free(data);

    puts("ok");
}

void menu() {
    puts("1.add");
    puts("2.edit");
    puts("3.show");
    puts("4.del");
    puts("5.quit");
    printf("> ");
}

int main() {
    setbuf(stdin, 0);
    setbuf(stdout, 0);

    while (1) {
        menu();
        switch (getnum()) {
            case 1: add(); break;
            case 2: edit(); break;
            case 3: show(); break;
            case 4: delete(); break;
            case 5: exit(0);
            default: break;
        }
    }
}
