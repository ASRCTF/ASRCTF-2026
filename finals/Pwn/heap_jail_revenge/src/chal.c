//gcc chal.c -o chal -fno-stack-protector -fPIE -pie -z relro -z now


#include <stdio.h>
#include <stdlib.h>
#include <malloc.h>
#include <string.h>
#include <unistd.h>

#define TOTAL_CELLS 16
#define MAX_SIZE  0x1000
void *cells[TOTAL_CELLS];
int paywalled = 0;
int times = 0;

void setup(){
    setbuf(stdin, NULL);
    setbuf(stdout, NULL);
    setbuf(stderr, NULL);
    printf("Welcome to heap jail! Good luck breaking free!\n");
}

int get_index(){
    int idx;
    for (idx=0; idx<TOTAL_CELLS; idx++){
        if (!cells[idx]){
            break;
        }
    }
    return idx;
}

void locked(){
    if (paywalled == 0){
        printf("You want 'free()'dom? Just paynow the jail warden $50 SGD. Paynow accepted, 1 btc is also accepted!\n");
        printf("PM neko#4394 on discord for more info [but please don't spam the jail warden, he may be on staycation in a not so remote island\n");
        printf("Totally not a pay2win ctf lmao!");
        return;
    }
    printf("Thanks for the 50 smackeroonies, here's your 'free'dom");
    printf("free()\n");
    return;
}

void menu(){
    printf("You wander across the cells, what do you do?\n\n");
    printf("\t[1] Explore a new cell\n");
    printf("\t[2] Revisit an old cell\n");
    printf("\t[3] Scream for help\n");
    printf("\t[4] Get a chance a 'free'dom\n");
    printf(">");
}

void scream(){
    printf("You screamed as loud as you could.\n");
    sleep(1);
    printf("Nothing happens.\n");
    sleep(1);
    printf("And then it hits you.\n");
    sleep(1);
    printf("Nothing hits you.\n");
}

void explore(){
    int idx = get_index();
    int size;
    if (idx == TOTAL_CELLS){
        printf("No more cells to explore!\n");
        return;
    }
    printf("A cell which size you can customize... how interesting!\n");
    printf("How big do you want the cell to be?\n>");
    if (scanf("%d", &size) != 1) return;
    if (size < 0x0 || size > MAX_SIZE){
        printf("Unfortunately that is a maximum (and minimum) size to jail cells.\n");
        return;
    }
    cells[idx] = malloc(size);
    printf("Customize your cell, make it look pretty!\n");
    printf("You'll be stuck here for awhile after all...\n>");
    read(0, cells[idx], 200);
    return;
}

void revisit(){
    int idx;
    int choice;
    printf("Which cell would you like to revisit?\n>");
    if (scanf("%d", &idx) != 1) return;
    if (idx < 0x0 || idx > TOTAL_CELLS){
        printf("Cell ain't here kid.\n");
        return;
    }
    if (!cells[idx]){
        printf("You haven't even seen that cell yet!\n");
        return;
    }
    printf("Would you like to:\n");
    printf("\t[1] Mesmerize at the stunning view of your decorated cell\n");
    printf("\t[2] Redecorate the cell\n>");
    if (scanf("%d", &choice) != 1) return;
    switch(choice){
        case 1:
            printf("Here it is! Your self-decorated cell!\n");
            puts(cells[idx]);
            break;
        case 2:
            printf("Don't like your current cell? It's fine! This jail allows for customization!\n");
            printf("How would you like to redecorate your cell?\n>");
            read(0, cells[idx], MAX_SIZE);
            printf("Cell redecorated!\n");
            break;
    }
    return;
}

void secret(){
    if (times >= 1){
        printf("You've seen this before!\n");
        return;
    }
    printf("You walked down the corridor and notice certain numbers.\n");
    printf("A postal code? Your first thought, but jail cells won't need postal codes.\n");
    void *code = malloc(0x10);
    printf("Do what you will with this:%p\n", code);
    times++;
}

int main(){
    int choice;
    setup();
    while (1){
        menu();
        if (scanf("%d", &choice) != 1) return 0;
        switch (choice){
            case 1: 
                explore();
                break;
            case 2:
                revisit();
                break;
            case 3:
                scream();
                break;
            case 4:
                locked();
                break;
            case 1337:
                secret();
                break;
            default:
                printf("Invalid choice!\n");
        }
    }
}

