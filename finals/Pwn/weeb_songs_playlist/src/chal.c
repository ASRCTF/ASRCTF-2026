//gcc -Wl,-z,now -Wl,-z,relro -fstack-protector-all -D_FORTIFY_SOURCE=2 -O2 -pie -fPIE -s -o chal chal.c
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <sys/ioctl.h>

#define RED     "\033[38;5;160m"
#define BOLDRED "\033[1;38;5;160m"
#define ORANGE  "\033[38;5;208m"
#define YELLOW  "\033[38;5;220m"
#define GREEN   "\033[38;5;82m"
#define BLUE    "\033[38;5;39m"
#define PURPLE  "\033[38;5;93m"
#define PINK    "\033[38;5;201m"
#define RESET   "\033[0m"

#define MAX_SONGS 32
#define MAX_SONG_SIZE 600
size_t Song_Sizes[MAX_SONGS];
void *Playlist[MAX_SONGS];

void spacing(){
    struct winsize w;
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &w) == 0) {
        for (int i = 0; i < w.ws_row; i++) {
            printf("\n");
        }
    } else {
        for (int i = 0; i < 40; i++) {
            printf("\n");
        }
    }
}

void print_banner() {
    spacing();
    const char* rainbow[] = {RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE};
    
    char *lines[] = {
        " __        __        _       ____  _             _ _     _     _  ___   ___   ",
        " ╲ ╲      ╱ ╱__  ___│ │__   │  _ ╲│ │ __ _ _   _│ (_)___│ │_  ╱ │╱ _ ╲ ╱ _ ╲  ",
        "  ╲ ╲ ╱╲ ╱ ╱ _ ╲╱ _ ╲ '_ ╲  │ │_) │ │╱ _` │ │ │ │ │ ╱ __│ __│ │ │ │ │ │ │ │ │ ",
        "   ╲ V  V ╱  __╱  __╱ │_) │ │  __╱│ │ (_│ │ │_│ │ │ ╲__ ╲ │_  │ │ │_│ │ │_│ │ ",
        "    ╲_╱╲_╱ ╲___│╲___│_.__╱  │_│   │_│╲__,_│╲__, │_│_│___╱╲__│ │_│╲___╱ ╲___╱  ",
        "                                           │___╱                              "
    };

    int num_lines = 6;
    int visible_width = 79; 
    
    // TOP BORDER
    printf("╔");
    for(int i = 0; i < visible_width; i++) printf("═");
    printf("╗\n");
    
    for (int i = 0; i < num_lines; i++) {
        printf("║ ");                    
        printf("%s", rainbow[i % 6]);    
        printf("%s", lines[i]);          
        printf("%s", RESET);             

        int printed_len = 2 + strlen(lines[i]); 
        int padding = visible_width - printed_len;
        
        if (padding > 0) {
            for (int j = 0; j < padding; j++) printf(" ");
        }
        
        printf("║\n");   // Right border
    }
    
    // BOTTOM BORDER
    printf("╚");
    for(int i = 0; i < visible_width; i++) printf("═");
    printf("╝\n");
}


void acknowledge(){
    char *msg = GREEN "[*] Press ENTER to return" RESET "\n" PINK ">" RESET;
    write(1, msg, strlen(msg));
    
    int c;
    while ((c = getchar()) != '\n' && c != EOF);
}

int get_idx(){
    int idx;
    for (idx=0; idx<MAX_SONGS; idx++){
        if (Playlist[idx] == NULL){
            return idx;
        }
    }
    return -1;
}



void add_song(){
    spacing();
    unsigned int size;
    int idx;
    char *entry_txt = PINK "[*] Adding a song? Finding available space..." RESET "\n";
    char *size_txt = PINK "[*] How big is your song?\n>" RESET;
    char *max_size_txt = BOLDRED "[*] Your song is too big!\n" RESET;
    char *song_txt = PINK "Enter the contents of your song!\n>" RESET;
    char *full_txt = BOLDRED "[!] Playlist full! Upgrade to the pro version to get 128 more playlist slots!" RESET "\n";
    char *success = GREEN "[*] New song has been addded!" RESET "\n";
    idx = get_idx();
    write(1, entry_txt, strlen(entry_txt));
    if (idx == -1){
        write(1, full_txt, strlen(full_txt));
        acknowledge();
        return;
    }
    write(1, size_txt, strlen(size_txt));
    if (scanf("%u", &size) != 1) return;
    int c;
    while ((c = getchar()) != '\n' && c != EOF);
    if (size > MAX_SONG_SIZE){
        write(1, max_size_txt, strlen(max_size_txt));
        return;
    }
    void *raw_chunk = malloc(size);
    if (raw_chunk == NULL) exit(1);
    Song_Sizes[idx] = size;
    Playlist[idx] = raw_chunk;
    write(1, success, strlen(success));
    acknowledge();
}

void edit_song(){
    spacing();
    int user_idx;
    char *entry_txt = PINK "[*] Editing a song? Provide the index" RESET "\n";
    char *idx_txt = PINK "[*] Enter idx of the song you want to edit\n>" RESET;
    char *edit_txt = PINK "[*] Enter the new contents of the song\n>" RESET;
    char *success = GREEN "[*] Song has been edited\n" RESET;
    char *no_song = BOLDRED "[!] Song entry not found!\n";
    write(1, entry_txt, strlen(entry_txt));
    write(1, idx_txt, strlen(idx_txt));
    scanf("%d", &user_idx);
    int c;
    while ((c = getchar()) != '\n' && c != EOF);
    if (user_idx < 0 || user_idx >= MAX_SONGS || Playlist[user_idx] == NULL){
        write(1, no_song, strlen(no_song));
        acknowledge();
        return;
    }
    void *data_ptr = Playlist[user_idx];
    size_t original_size = Song_Sizes[user_idx];
    write(1, edit_txt, strlen(edit_txt));
    int bytes_read = read(0, Playlist[user_idx], original_size);
    if (bytes_read >= 0){
        ((char*)data_ptr)[bytes_read] = '\0';
    }
    write(1, success, strlen(success));
    acknowledge();
}

void delete_song(){
    spacing();
    int user_idx;
    char *entry_txt = PINK "[*] Deleting a song? Provide the index" RESET "\n";
    char *delete_txt = PINK "[*] Enter idx of the song you want to delete\n>" RESET;
    char *no_song = BOLDRED "[!] Song entry not found!\n";
    char *success = GREEN "[*] Song has been deleted\n" RESET;
    write(1, entry_txt, strlen(entry_txt));
    write(1, delete_txt, strlen(delete_txt));
    scanf("%d", &user_idx);
    int c;
    while ((c = getchar()) != '\n' && c != EOF);
    if (user_idx >= MAX_SONGS || Playlist[user_idx] == NULL){
        write(1, no_song, strlen(no_song));
        acknowledge();
        return;
    }
    free(Playlist[user_idx]);
    Playlist[user_idx] = NULL;
    Song_Sizes[user_idx] = 0;
    write(1, success, strlen(success));
    acknowledge();
}

void view_a_song(){
    spacing();
    int user_idx;
    char *entry_txt = PINK "[*] Viewing the contents of a song? Provide the index" RESET "\n";
    char *view_a_song_txt = PINK "[*] Enter index of the song you want to view\n>" RESET;
    char *desc_header = PINK "[*] Contents of song:" RESET "\n";
    char *max_songs = BOLDRED "[*] Song entry not found!" RESET "\n";
    
    write(1, entry_txt, strlen(entry_txt));
    write(1, view_a_song_txt, strlen(view_a_song_txt));
    if (scanf("%d", &user_idx) != 1) return;
    int c;
    while ((c = getchar()) != '\n' && c != EOF);
    if (user_idx >= MAX_SONGS || Playlist[user_idx] == NULL){
        write(1, max_songs, strlen(max_songs));
        acknowledge();
        return;
    }
    
    write(1, desc_header, strlen(desc_header));
    write(1, Playlist[user_idx], 600);
    write(1, "\n", 1);
    acknowledge();
}

void view_all_songs() {
    spacing();
    char *list_header = PINK "[*] Printing all tracks in the playlist:" RESET "\n";
    char *empty_msg = BOLDRED "[!] The playlist is currently empty!" RESET "\n";
    char *desc_lbl = PINK "  Contents: " RESET;
    char *idx_fmt = "\nTrack [%d]\n";
    char buffer[32];
    int found = 0;

    write(1, list_header, strlen(list_header));

    for (int i = 0; i < MAX_SONGS; i++) {
        if (Playlist[i] != NULL) {
            found = 1;
            void *data_ptr = Playlist[i];
            
            // CHANGE: Pull the track size directly from your new global size tracker array
            size_t original_size = Song_Sizes[i];
            
            int len = snprintf(buffer, sizeof(buffer), idx_fmt, i);
            if (len > 0 && len < (int)sizeof(buffer)) {
                write(1, buffer, len);
            }

            write(1, desc_lbl, strlen(desc_lbl));
            write(1, data_ptr, strnlen((char*)data_ptr, original_size));
            write(1, "\n", 1);
        }
    }

    if (!found) {
        write(1, empty_msg, strlen(empty_msg));
    }

    acknowledge();
}

void menu(){
    char *welcome = PINK "[*] Thanks for using Weeb Playlist 100" RESET "\n\n";
    char *ass_msg = "\t" RED "[!] Note that this is the free version only!" RESET "\n\n";
    char *qn = PINK "[?] What would you like to do?" RESET "\n\n";
    char *opt1 = PURPLE "[1] Add a song\n" RESET;
    char *opt2 = PURPLE "[2] Edit a song\n" RESET;
    char *opt3 = PURPLE "[3] Delete a song\n" RESET;
    char *opt4 = PURPLE "[4] View a song\n" RESET;
    char *opt5 = PURPLE "[5] View all songs\n" RESET;
    char *opt6 = PURPLE "[6] Exit\n" RESET;
    char *marker = PINK ">" RESET;
    write(1, welcome, strlen(welcome));
    write(1, ass_msg, strlen(ass_msg));
    write(1, qn, strlen(qn));
    write(1, opt1, strlen(opt1));
    write(1, opt2, strlen(opt2));
    write(1, opt3, strlen(opt3));
    write(1, opt4, strlen(opt4));
    write(1, opt5, strlen(opt5));
    write(1, opt6, strlen(opt6));
    write(1, marker, strlen(marker));
}   

void quit(){
    char *exit_msg = PINK "Thanks for using Weeb Playlist\n" RESET;
    write(1, exit_msg, strlen(exit_msg));
    exit(1);
}

void setup(){
    setbuf(stdin, NULL);
	setbuf(stdout, NULL);
	setbuf(stderr, NULL);
}

int main(){
    setup();
    int option;
    char *error = BOLDRED "[!] That's not a valid option!\n" RESET;
    while (1){
        print_banner();
        menu();
        // Overly complicated code for better ui experience ig 
        
        if (scanf("%d", &option) != 1) return 0;
        getchar();
        switch (option){
            case 1:
                add_song();
                break;
            case 2:
                edit_song();
                break;
            case 3:
                delete_song();
                break;
            case 4:
                view_a_song();
                break;
            case 5:
                view_all_songs();
                break;
            case 6:
                quit();
                break;
            default:
                write(1, error, strlen(error));
                acknowledge();
        }
    }
}
