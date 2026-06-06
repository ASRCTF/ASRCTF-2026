/*
 * tetris_time
 *
 * Controls: a/d  move left/right
 *           s    soft drop
 *           w    rotate
 *           q    quit
 */

#include <curses.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define BOARD_W  10
#define BOARD_H  20
#define BOARD_X   2
#define BOARD_Y   1

static int board[BOARD_H][BOARD_W];

static const int PIECES[7][4][4][2] = {
    {{{0,0},{0,1},{0,2},{0,3}},{{0,2},{1,2},{2,2},{3,2}},
     {{3,0},{3,1},{3,2},{3,3}},{{0,1},{1,1},{2,1},{3,1}}},
    {{{0,0},{0,1},{1,0},{1,1}},{{0,0},{0,1},{1,0},{1,1}},
     {{0,0},{0,1},{1,0},{1,1}},{{0,0},{0,1},{1,0},{1,1}}},
    {{{0,1},{1,0},{1,1},{1,2}},{{0,1},{1,1},{1,2},{2,1}},
     {{1,0},{1,1},{1,2},{2,1}},{{0,1},{1,0},{1,1},{2,1}}},
    {{{0,1},{0,2},{1,0},{1,1}},{{0,1},{1,1},{1,2},{2,2}},
     {{1,1},{1,2},{2,0},{2,1}},{{0,0},{1,0},{1,1},{2,1}}},
    {{{0,0},{0,1},{1,1},{1,2}},{{0,2},{1,1},{1,2},{2,1}},
     {{1,0},{1,1},{2,1},{2,2}},{{0,1},{1,0},{1,1},{2,0}}},
    {{{0,0},{1,0},{1,1},{1,2}},{{0,1},{0,2},{1,1},{2,1}},
     {{1,0},{1,1},{1,2},{2,2}},{{0,1},{1,1},{2,0},{2,1}}},
    {{{0,2},{1,0},{1,1},{1,2}},{{0,1},{1,1},{2,1},{2,2}},
     {{1,0},{1,1},{1,2},{2,0}},{{0,0},{0,1},{1,1},{2,1}}},
};

static const int PIECE_COLOR[7] = {1,2,3,4,5,6,7};

static int cur_type, cur_rot, cur_row, cur_col;
static int next_type;

static int score       = 0;
static int level       = 0;
static int lines_total = 0;

static int cond_tetris_l3  = 0;
static int cond_keybind_l4 = 0;

static const unsigned char FLAG_BLOB[FLAG_LEN] = { FLAG_BYTES };

static void lfsr_stream(unsigned char *out, int n)
{
    unsigned short reg = 0xACE1u;
    for (int i = 0; i < n; i++) {
        unsigned char byte = 0;
        for (int b = 0; b < 8; b++) {
            int lsb = reg & 1;
            reg >>= 1;
            if (lsb) reg ^= 0xB400u;
            byte = (unsigned char)((byte >> 1) | (lsb << 7));
        }
        out[i] = byte;
    }
}

static void check_and_reveal(void)
{
    if (!cond_tetris_l3 || !cond_keybind_l4)
        return;

    unsigned char key[FLAG_LEN];
    lfsr_stream(key, FLAG_LEN);

    char flag[FLAG_LEN + 1];
    for (int i = 0; i < FLAG_LEN; i++)
        flag[i] = (char)(FLAG_BLOB[i] ^ key[i]);
    flag[FLAG_LEN] = '\0';

    int wy, wx;
    getmaxyx(stdscr, wy, wx);
    int row = wy / 2;
    int col = (wx - FLAG_LEN) / 2;

    attron(A_BOLD | COLOR_PAIR(3));
    mvprintw(row - 1, col, "*** FLAG ***");
    mvprintw(row,     col, "%s", flag);
    attroff(A_BOLD | COLOR_PAIR(3));
    refresh();
    sleep(30);
}

static int valid(int type, int rot, int row, int col)
{
    for (int i = 0; i < 4; i++) {
        int r = row + PIECES[type][rot][i][0];
        int c = col + PIECES[type][rot][i][1];
        if (r < 0 || r >= BOARD_H || c < 0 || c >= BOARD_W) return 0;
        if (board[r][c]) return 0;
    }
    return 1;
}

static void lock_piece(void)
{
    for (int i = 0; i < 4; i++)
        board[cur_row + PIECES[cur_type][cur_rot][i][0]]
             [cur_col + PIECES[cur_type][cur_rot][i][1]] = cur_type + 1;
}

static int clear_lines(void)
{
    int cleared = 0;
    for (int r = BOARD_H - 1; r >= 0; ) {
        int full = 1;
        for (int c = 0; c < BOARD_W; c++)
            if (!board[r][c]) { full = 0; break; }
        if (full) {
            for (int rr = r; rr > 0; rr--)
                memcpy(board[rr], board[rr-1], sizeof(board[0]));
            memset(board[0], 0, sizeof(board[0]));
            cleared++;
        } else {
            r--;
        }
    }
    return cleared;
}

static const int LINE_SCORES[5] = {0, 100, 300, 500, 800};

static void update_score(int n)
{
    int level_before = level;

    score       += LINE_SCORES[n] * (level + 1);
    lines_total += n;
    level        = lines_total / 10;

    if (n == 4 && level_before == 3)
        cond_tetris_l3 = 1;

    check_and_reveal();
}

static void spawn_piece(void)
{
    cur_type  = next_type;
    cur_rot   = 0;
    cur_row   = 0;
    cur_col   = BOARD_W / 2 - 2;
    next_type = rand() % 7;
}

static void draw_board(void)
{
    for (int r = 0; r < BOARD_H; r++) {
        mvaddch(BOARD_Y + r, BOARD_X - 1,      '|');
        mvaddch(BOARD_Y + r, BOARD_X + BOARD_W, '|');
    }
    mvhline(BOARD_Y + BOARD_H, BOARD_X - 1, '-', BOARD_W + 2);

    for (int r = 0; r < BOARD_H; r++) {
        for (int c = 0; c < BOARD_W; c++) {
            int v = board[r][c];
            if (v) {
                attron(COLOR_PAIR(PIECE_COLOR[v-1]));
                mvaddch(BOARD_Y + r, BOARD_X + c, '#');
                attroff(COLOR_PAIR(PIECE_COLOR[v-1]));
            } else {
                mvaddch(BOARD_Y + r, BOARD_X + c, '.');
            }
        }
    }

    attron(COLOR_PAIR(PIECE_COLOR[cur_type]));
    for (int i = 0; i < 4; i++) {
        int r = cur_row + PIECES[cur_type][cur_rot][i][0];
        int c = cur_col + PIECES[cur_type][cur_rot][i][1];
        if (r >= 0)
            mvaddch(BOARD_Y + r, BOARD_X + c, '@');
    }
    attroff(COLOR_PAIR(PIECE_COLOR[cur_type]));
}

static void draw_sidebar(void)
{
    int sx = BOARD_X + BOARD_W + 3;
    mvprintw(BOARD_Y + 1,  sx, "SCORE : %d", score);
    mvprintw(BOARD_Y + 2,  sx, "LINES : %d", lines_total);
    mvprintw(BOARD_Y + 3,  sx, "LEVEL : %d", level);
    mvprintw(BOARD_Y + 5,  sx, "NEXT:");
    for (int i = 0; i < 4; i++) {
        int r = PIECES[next_type][0][i][0];
        int c = PIECES[next_type][0][i][1];
        attron(COLOR_PAIR(PIECE_COLOR[next_type]));
        mvaddch(BOARD_Y + 7 + r, sx + c, '#');
        attroff(COLOR_PAIR(PIECE_COLOR[next_type]));
    }
    mvprintw(BOARD_Y + 12, sx, "a/d : move");
    mvprintw(BOARD_Y + 13, sx, "w   : rotate");
    mvprintw(BOARD_Y + 14, sx, "s   : drop");
    mvprintw(BOARD_Y + 15, sx, "q   : quit");
}

int main(void)
{
    srand((unsigned)time(NULL));

    initscr();
    cbreak();
    noecho();
    keypad(stdscr, TRUE);
    curs_set(0);
    nodelay(stdscr, TRUE);

    if (has_colors()) {
        start_color();
        init_pair(1, COLOR_CYAN,    COLOR_BLACK);
        init_pair(2, COLOR_YELLOW,  COLOR_BLACK);
        init_pair(3, COLOR_MAGENTA, COLOR_BLACK);
        init_pair(4, COLOR_GREEN,   COLOR_BLACK);
        init_pair(5, COLOR_RED,     COLOR_BLACK);
        init_pair(6, COLOR_BLUE,    COLOR_BLACK);
        init_pair(7, COLOR_WHITE,   COLOR_BLACK);
    }

    memset(board, 0, sizeof(board));
    next_type = rand() % 7;
    spawn_piece();

    int gravity_ticks = 30;
    int tick          = 0;
    int game_over     = 0;

    while (!game_over) {
        int ch = getch();
        switch (ch) {
        case 'q':
            game_over = 1;
            break;
        case 'a':
            if (valid(cur_type, cur_rot, cur_row, cur_col - 1)) cur_col--;
            break;
        case 'd':
            if (valid(cur_type, cur_rot, cur_row, cur_col + 1)) cur_col++;
            break;
        case 'w': {
            int nr = (cur_rot + 1) % 4;
            if (valid(cur_type, nr, cur_row, cur_col)) cur_rot = nr;
            break;
        }
        case 's':
            if (valid(cur_type, cur_rot, cur_row + 1, cur_col)) cur_row++;
            break;
        case 'f':
            if (level == 4) {
                cond_keybind_l4 = 1;
                check_and_reveal();
            }
            break;
        }

        tick++;
        if (tick >= gravity_ticks) {
            tick          = 0;
            gravity_ticks = 30 - level * 2;
            if (gravity_ticks < 5) gravity_ticks = 5;

            if (valid(cur_type, cur_rot, cur_row + 1, cur_col)) {
                cur_row++;
            } else {
                lock_piece();
                int n = clear_lines();
                if (n) update_score(n);
                spawn_piece();
                if (!valid(cur_type, cur_rot, cur_row, cur_col))
                    game_over = 1;
            }
        }

        erase();
        draw_board();
        draw_sidebar();
        refresh();

        struct timespec ts = {0, 16666667};
        nanosleep(&ts, NULL);
    }

    endwin();
    printf("Game over!  Score: %d  Lines: %d\n", score, lines_total);
    return 0;
}
