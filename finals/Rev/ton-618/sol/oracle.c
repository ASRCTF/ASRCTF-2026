#include <stdio.h>
#include <stdint.h> 

static const uint64_t N[20] = {
    1020544596ULL, 1355972289ULL, 1391647585ULL, 1405480800ULL,
    1423944875ULL, 1437982291ULL, 1457513853ULL, 1457942829ULL,
    1499394254ULL, 1504263996ULL, 1643476878ULL, 1657334267ULL,
    1674293055ULL, 1717735726ULL, 1746059110ULL, 1781248712ULL,
    1829341823ULL, 1959926481ULL, 1966240608ULL, 1999302076ULL
};
static const uint64_t T = 11744788681ULL;

static const unsigned char CT[30] = {
    0x55, 0x42, 0x55, 0x43, 0x54, 0x46, 0x7b, 0x77,
    0x7c, 0x68, 0x58, 0x31, 0x35, 0x5f, 0x74, 0x68,
    0x27, 0x4e, 0x75, 0x33, 0x76, 0x5f, 0x35, 0x30,
    0x4b, 0x77, 0x75, 0x33, 0x33, 0x7d
};

int main(void) {
    uint64_t mask = 0;
    if (scanf("%lu", &mask) != 1 || mask >= (1UL << 20)) return 1;
    uint64_t s = 0;
    for (int i = 0; i < 20; i++)
        if ((mask >> i) & 1) s += N[i];
    if (s != T) return 1;
    unsigned char key[8];
    for (int i = 0; i < 8; i++) key[i] = (mask >> (i * 8)) & 0xff;
    for (int i = 0; i < 30; i++) putchar(CT[i] ^ key[i % 8]);
    putchar('\n');
    return 0;
}
