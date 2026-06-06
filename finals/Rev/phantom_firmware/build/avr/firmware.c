/*
 * phantom_firmware - AVR VM Interpreter
 * 
 * Target: ATmega328P (8-bit AVR)
 * 
 * This firmware implements a custom stack-based virtual machine that
 * interprets bytecode stored in EEPROM. The VM includes cipher-specific
 * opcodes for the custom Feistel block cipher.
 * 
 * Build: avr-gcc -mmcu=atmega328p -Os -o firmware.elf firmware.c
 * 
 * Author: nmluan (challenge source, compiled binary distributed to players)
 */

#include <stdint.h>
#include <string.h>

/* ========================================================================
 * Hardware Abstraction (simplified for CTF - no real AVR headers needed)
 * We compile this as a standalone binary for analysis purposes.
 * The actual "hardware" is simulated.
 * ======================================================================== */

/* Memory layout */
#define VM_STACK_SIZE   256
#define VM_MEM_SIZE     4096
#define VM_CODE_SIZE    2048
#define DISPLAY_BASE    0x100   /* 16x16 display buffer at 0x100-0x1FF */
#define DISPLAY_SIZE    256
#define EEPROM_BASE     0x800   /* VM bytecode starts here */

/* ========================================================================
 * S-Box (the weak one with differential characteristic)
 * Input diff 0x0D -> Output diff 0x07 with probability 2^-4
 * ======================================================================== */
static const uint8_t SBOX[16] = {
    0x0C, 0x05, 0x06, 0x0B, 0x09, 0x00, 0x0A, 0x0D,
    0x03, 0x0E, 0x0F, 0x08, 0x04, 0x07, 0x01, 0x02
};

static const uint8_t SBOX_INV[16] = {
    0x05, 0x0E, 0x0F, 0x08, 0x0C, 0x01, 0x02, 0x0D,
    0x0B, 0x04, 0x06, 0x03, 0x00, 0x07, 0x09, 0x0A
};

/* ========================================================================
 * P-Box (bit permutation for 32-bit values)
 * ======================================================================== */
static const uint8_t PBOX[32] = {
     0,  8, 16, 24,  1,  9, 17, 25,
     2, 10, 18, 26,  3, 11, 19, 27,
     4, 12, 20, 28,  5, 13, 21, 29,
     6, 14, 22, 30,  7, 15, 23, 31
};

/* ========================================================================
 * VM Opcodes
 * ======================================================================== */

/* Stack operations (000-xxx) */
#define OP_PUSH     0x00    /* PUSH imm8  (2 bytes) */
#define OP_PUSH16   0x01    /* PUSH16 imm16 (3 bytes) */
#define OP_POP      0x02    /* POP (1 byte) */
#define OP_DUP      0x03    /* DUP (1 byte) */
#define OP_SWAP     0x04    /* SWAP (1 byte) */
#define OP_OVER     0x05    /* OVER (1 byte) */
#define OP_ROT      0x06    /* ROT (1 byte) */

/* Arithmetic (001-xxx) */
#define OP_ADD      0x08    /* ADD (1 byte) */
#define OP_SUB      0x09    /* SUB (1 byte) */
#define OP_MUL      0x0A    /* MUL (1 byte) */
#define OP_XOR      0x0B    /* XOR (1 byte) */
#define OP_AND      0x0C    /* AND (1 byte) */
#define OP_OR       0x0D    /* OR (1 byte) */
#define OP_NOT      0x0E    /* NOT (1 byte) */

/* Bitwise (010-xxx) */
#define OP_SHL      0x10    /* SHL (1 byte) */
#define OP_SHR      0x11    /* SHR (1 byte) */
#define OP_ROTL     0x12    /* ROTL (1 byte) */
#define OP_ROTR     0x13    /* ROTR (1 byte) */

/* Control flow (011-xxx) */
#define OP_JMP      0x18    /* JMP addr16 (3 bytes) */
#define OP_JZ       0x19    /* JZ addr16 (3 bytes) */
#define OP_JNZ      0x1A    /* JNZ addr16 (3 bytes) */
#define OP_CALL     0x1B    /* CALL addr16 (3 bytes) */
#define OP_RET      0x1C    /* RET (1 byte) */

/* Cipher operations (100-xxx) */
#define OP_SBOX     0x20    /* SBOX - apply S-box to low nibble of TOS (1 byte) */
#define OP_SBOXI    0x21    /* SBOXI - apply inverse S-box (1 byte) */
#define OP_PERM     0x22    /* PERM - apply P-box to top 4 bytes of stack (1 byte) */
#define OP_PERMI    0x23    /* PERMI - apply inverse P-box (1 byte) */
#define OP_MIX      0x24    /* MIX - one Feistel round function (1 byte) */
#define OP_RKEY     0x25    /* RKEY imm8 - load round key N onto stack (2 bytes) */

/* Memory (101-xxx) */
#define OP_LOAD     0x28    /* LOAD addr16 (3 bytes) */
#define OP_STORE    0x29    /* STORE addr16 (3 bytes) */
#define OP_MMOD     0x2A    /* MMOD addr16 - self-modify code at addr (3 bytes) */
#define OP_CRC      0x2B    /* CRC - compute CRC of TOS (1 byte) */

/* I/O (110-xxx) */
#define OP_IN       0x30    /* IN (1 byte) */
#define OP_OUT      0x31    /* OUT (1 byte) */
#define OP_HALT     0x32    /* HALT (1 byte) */
#define OP_NOP      0x33    /* NOP (1 byte) */

/* Traps (111-xxx) */
#define OP_TRAP     0x38    /* TRAP len (2+len bytes) - embed string */
#define OP_DBG      0x39    /* DBG (1 byte) */
#define OP_RND      0x3A    /* RND (1 byte) - push pseudo-random byte */
#define OP_ENV      0x3B    /* ENV (1 byte) - push environment byte */

/* ========================================================================
 * VM State
 * ======================================================================== */
typedef struct {
    uint8_t  stack[VM_STACK_SIZE];   /* Data stack */
    uint16_t sp;                     /* Stack pointer */
    uint16_t call_stack[64];         /* Return address stack */
    uint8_t  csp;                    /* Call stack pointer */
    uint8_t  code[VM_CODE_SIZE];     /* Bytecode */
    uint16_t pc;                     /* Program counter */
    uint8_t  mem[VM_MEM_SIZE];       /* Data memory */
    uint8_t  round_keys[16][4];      /* 16 round keys, 32-bits each */
    uint8_t  output_buf[256];        /* Output buffer */
    uint16_t output_pos;             /* Output position */
    uint8_t  halted;                 /* Halt flag */
    uint8_t  error;                  /* Error code */
    uint32_t rng_state;              /* PRNG state */
} vm_state_t;

/* ========================================================================
 * P-Box Application (32-bit)
 * ======================================================================== */
static uint32_t apply_pbox(uint32_t input) {
    uint32_t output = 0;
    for (int i = 0; i < 32; i++) {
        if (input & (1UL << i)) {
            output |= (1UL << PBOX[i]);
        }
    }
    return output;
}

static uint32_t apply_pbox_inv(uint32_t input) {
    uint32_t output = 0;
    for (int i = 0; i < 32; i++) {
        if (input & (1UL << PBOX[i])) {
            output |= (1UL << i);
        }
    }
    return output;
}

/* ========================================================================
 * Stack Operations
 * ======================================================================== */
static inline void vm_push(vm_state_t *vm, uint8_t val) {
    if (vm->sp >= VM_STACK_SIZE) {
        vm->error = 1; /* Stack overflow */
        vm->halted = 1;
        return;
    }
    vm->stack[vm->sp++] = val;
}

static inline uint8_t vm_pop(vm_state_t *vm) {
    if (vm->sp == 0) {
        vm->error = 2; /* Stack underflow */
        vm->halted = 1;
        return 0;
    }
    return vm->stack[--vm->sp];
}

static inline uint8_t vm_peek(vm_state_t *vm) {
    if (vm->sp == 0) {
        vm->error = 2;
        vm->halted = 1;
        return 0;
    }
    return vm->stack[vm->sp - 1];
}

/* ========================================================================
 * Feistel Round Function
 * Takes 4 bytes from stack (32-bit half-block), applies SPN, returns 4 bytes
 * ======================================================================== */
static void vm_feistel_round(vm_state_t *vm, uint8_t round_idx) {
    /* Pop 4 bytes from stack (big-endian 32-bit value) */
    uint8_t b3 = vm_pop(vm);
    uint8_t b2 = vm_pop(vm);
    uint8_t b1 = vm_pop(vm);
    uint8_t b0 = vm_pop(vm);
    
    if (vm->error) return;
    
    /* Apply S-box substitution to each nibble */
    b0 = (SBOX[(b0 >> 4) & 0xF] << 4) | SBOX[b0 & 0xF];
    b1 = (SBOX[(b1 >> 4) & 0xF] << 4) | SBOX[b1 & 0xF];
    b2 = (SBOX[(b2 >> 4) & 0xF] << 4) | SBOX[b2 & 0xF];
    b3 = (SBOX[(b3 >> 4) & 0xF] << 4) | SBOX[b3 & 0xF];
    
    /* Apply P-box permutation */
    uint32_t val = ((uint32_t)b0 << 24) | ((uint32_t)b1 << 16) | 
                   ((uint32_t)b2 << 8) | (uint32_t)b3;
    val = apply_pbox(val);
    
    /* XOR with round key */
    uint8_t *rk = vm->round_keys[round_idx & 0xF];
    b0 = ((val >> 24) & 0xFF) ^ rk[0];
    b1 = ((val >> 16) & 0xFF) ^ rk[1];
    b2 = ((val >> 8) & 0xFF) ^ rk[2];
    b3 = (val & 0xFF) ^ rk[3];
    
    /* Push result back */
    vm_push(vm, b0);
    vm_push(vm, b1);
    vm_push(vm, b2);
    vm_push(vm, b3);
}

/* ========================================================================
 * VM Execution
 * ======================================================================== */
static void vm_step(vm_state_t *vm) {
    if (vm->halted || vm->pc >= VM_CODE_SIZE) {
        vm->halted = 1;
        return;
    }
    
    uint8_t opcode = vm->code[vm->pc];
    uint8_t a, b, c;
    uint16_t addr;
    uint32_t val32;
    
    switch (opcode) {
        /* Stack operations */
        case OP_PUSH:
            vm->pc++;
            vm_push(vm, vm->code[vm->pc]);
            vm->pc++;
            break;
            
        case OP_PUSH16:
            vm->pc++;
            addr = ((uint16_t)vm->code[vm->pc] << 8) | vm->code[vm->pc + 1];
            vm_push(vm, (addr >> 8) & 0xFF);
            vm_push(vm, addr & 0xFF);
            vm->pc += 2;
            break;
            
        case OP_POP:
            vm_pop(vm);
            vm->pc++;
            break;
            
        case OP_DUP:
            a = vm_peek(vm);
            vm_push(vm, a);
            vm->pc++;
            break;
            
        case OP_SWAP:
            a = vm_pop(vm);
            b = vm_pop(vm);
            vm_push(vm, a);
            vm_push(vm, b);
            vm->pc++;
            break;
            
        case OP_OVER:
            if (vm->sp < 2) { vm->error = 2; vm->halted = 1; break; }
            a = vm->stack[vm->sp - 2];
            vm_push(vm, a);
            vm->pc++;
            break;
            
        case OP_ROT:
            c = vm_pop(vm);
            b = vm_pop(vm);
            a = vm_pop(vm);
            vm_push(vm, b);
            vm_push(vm, c);
            vm_push(vm, a);
            vm->pc++;
            break;
        
        /* Arithmetic */
        case OP_ADD:
            a = vm_pop(vm);
            b = vm_pop(vm);
            vm_push(vm, (b + a) & 0xFF);
            vm->pc++;
            break;
            
        case OP_SUB:
            a = vm_pop(vm);
            b = vm_pop(vm);
            vm_push(vm, (b - a) & 0xFF);
            vm->pc++;
            break;
            
        case OP_MUL:
            a = vm_pop(vm);
            b = vm_pop(vm);
            vm_push(vm, (b * a) & 0xFF);
            vm->pc++;
            break;
            
        case OP_XOR:
            a = vm_pop(vm);
            b = vm_pop(vm);
            vm_push(vm, b ^ a);
            vm->pc++;
            break;
            
        case OP_AND:
            a = vm_pop(vm);
            b = vm_pop(vm);
            vm_push(vm, b & a);
            vm->pc++;
            break;
            
        case OP_OR:
            a = vm_pop(vm);
            b = vm_pop(vm);
            vm_push(vm, b | a);
            vm->pc++;
            break;
            
        case OP_NOT:
            a = vm_pop(vm);
            vm_push(vm, ~a);
            vm->pc++;
            break;
        
        /* Bitwise */
        case OP_SHL:
            a = vm_pop(vm);  /* shift amount */
            b = vm_pop(vm);  /* value */
            vm_push(vm, (b << (a & 7)) & 0xFF);
            vm->pc++;
            break;
            
        case OP_SHR:
            a = vm_pop(vm);
            b = vm_pop(vm);
            vm_push(vm, (b >> (a & 7)) & 0xFF);
            vm->pc++;
            break;
            
        case OP_ROTL:
            a = vm_pop(vm);
            b = vm_pop(vm);
            a &= 7;
            vm_push(vm, ((b << a) | (b >> (8 - a))) & 0xFF);
            vm->pc++;
            break;
            
        case OP_ROTR:
            a = vm_pop(vm);
            b = vm_pop(vm);
            a &= 7;
            vm_push(vm, ((b >> a) | (b << (8 - a))) & 0xFF);
            vm->pc++;
            break;
        
        /* Control flow */
        case OP_JMP:
            vm->pc++;
            addr = ((uint16_t)vm->code[vm->pc] << 8) | vm->code[vm->pc + 1];
            vm->pc = addr;
            break;
            
        case OP_JZ:
            vm->pc++;
            addr = ((uint16_t)vm->code[vm->pc] << 8) | vm->code[vm->pc + 1];
            a = vm_pop(vm);
            if (a == 0) {
                vm->pc = addr;
            } else {
                vm->pc += 2;
            }
            break;
            
        case OP_JNZ:
            vm->pc++;
            addr = ((uint16_t)vm->code[vm->pc] << 8) | vm->code[vm->pc + 1];
            a = vm_pop(vm);
            if (a != 0) {
                vm->pc = addr;
            } else {
                vm->pc += 2;
            }
            break;
            
        case OP_CALL:
            vm->pc++;
            addr = ((uint16_t)vm->code[vm->pc] << 8) | vm->code[vm->pc + 1];
            if (vm->csp >= 64) { vm->error = 3; vm->halted = 1; break; }
            vm->call_stack[vm->csp++] = vm->pc + 2;
            vm->pc = addr;
            break;
            
        case OP_RET:
            if (vm->csp == 0) { vm->error = 4; vm->halted = 1; break; }
            vm->pc = vm->call_stack[--vm->csp];
            break;
        
        /* Cipher operations */
        case OP_SBOX:
            a = vm_pop(vm);
            vm_push(vm, (SBOX[(a >> 4) & 0xF] << 4) | SBOX[a & 0xF]);
            vm->pc++;
            break;
        
        case OP_SBOXI:
            a = vm_pop(vm);
            vm_push(vm, (SBOX_INV[(a >> 4) & 0xF] << 4) | SBOX_INV[a & 0xF]);
            vm->pc++;
            break;
            
        case OP_PERM:
            /* Apply P-box to top 4 bytes of stack as 32-bit value */
            if (vm->sp < 4) { vm->error = 2; vm->halted = 1; break; }
            {
                uint8_t p3 = vm_pop(vm);
                uint8_t p2 = vm_pop(vm);
                uint8_t p1 = vm_pop(vm);
                uint8_t p0 = vm_pop(vm);
                val32 = ((uint32_t)p0 << 24) | ((uint32_t)p1 << 16) |
                        ((uint32_t)p2 << 8) | (uint32_t)p3;
                val32 = apply_pbox(val32);
                vm_push(vm, (val32 >> 24) & 0xFF);
                vm_push(vm, (val32 >> 16) & 0xFF);
                vm_push(vm, (val32 >> 8) & 0xFF);
                vm_push(vm, val32 & 0xFF);
            }
            vm->pc++;
            break;
        
        case OP_PERMI:
            if (vm->sp < 4) { vm->error = 2; vm->halted = 1; break; }
            {
                uint8_t p3 = vm_pop(vm);
                uint8_t p2 = vm_pop(vm);
                uint8_t p1 = vm_pop(vm);
                uint8_t p0 = vm_pop(vm);
                val32 = ((uint32_t)p0 << 24) | ((uint32_t)p1 << 16) |
                        ((uint32_t)p2 << 8) | (uint32_t)p3;
                val32 = apply_pbox_inv(val32);
                vm_push(vm, (val32 >> 24) & 0xFF);
                vm_push(vm, (val32 >> 16) & 0xFF);
                vm_push(vm, (val32 >> 8) & 0xFF);
                vm_push(vm, val32 & 0xFF);
            }
            vm->pc++;
            break;
            
        case OP_MIX:
            /* Full Feistel round - uses round index from TOS */
            a = vm_pop(vm);  /* round index */
            vm_feistel_round(vm, a);
            vm->pc++;
            break;
            
        case OP_RKEY:
            /* Load round key N (4 bytes) onto stack */
            vm->pc++;
            a = vm->code[vm->pc] & 0xF;
            vm_push(vm, vm->round_keys[a][0]);
            vm_push(vm, vm->round_keys[a][1]);
            vm_push(vm, vm->round_keys[a][2]);
            vm_push(vm, vm->round_keys[a][3]);
            vm->pc++;
            break;
        
        /* Memory operations */
        case OP_LOAD:
            vm->pc++;
            addr = ((uint16_t)vm->code[vm->pc] << 8) | vm->code[vm->pc + 1];
            vm->pc += 2;
            if (addr < VM_MEM_SIZE) {
                vm_push(vm, vm->mem[addr]);
            } else {
                vm_push(vm, 0);
            }
            break;
            
        case OP_STORE:
            vm->pc++;
            addr = ((uint16_t)vm->code[vm->pc] << 8) | vm->code[vm->pc + 1];
            vm->pc += 2;
            a = vm_pop(vm);
            if (addr < VM_MEM_SIZE) {
                vm->mem[addr] = a;
            }
            break;
            
        case OP_MMOD:
            /* Self-modify: write TOS byte to code at addr */
            vm->pc++;
            addr = ((uint16_t)vm->code[vm->pc] << 8) | vm->code[vm->pc + 1];
            vm->pc += 2;
            a = vm_pop(vm);
            if (addr < VM_CODE_SIZE) {
                vm->code[addr] = a;
            }
            break;
            
        case OP_CRC:
            /* Compute a simple CRC-like checksum of TOS */
            a = vm_pop(vm);
            vm_push(vm, (a * 0x9E + 0x37) & 0xFF);
            vm->pc++;
            break;
        
        /* I/O */
        case OP_IN:
            /* Read from input (stubbed - returns 0) */
            vm_push(vm, 0);
            vm->pc++;
            break;
            
        case OP_OUT:
            a = vm_pop(vm);
            if (vm->output_pos < 256) {
                vm->output_buf[vm->output_pos++] = a;
            }
            vm->pc++;
            break;
            
        case OP_HALT:
            vm->halted = 1;
            vm->pc++;
            break;
            
        case OP_NOP:
            vm->pc++;
            break;
        
        /* Traps & Debug */
        case OP_TRAP:
            /* TRAP: skip over embedded string (len byte + string data) */
            vm->pc++;
            a = vm->code[vm->pc]; /* length byte */
            vm->pc += 1 + a;      /* skip length + string data */
            break;
            
        case OP_DBG:
            /* Debug breakpoint - no-op in release */
            vm->pc++;
            break;
            
        case OP_RND:
            /* Push pseudo-random byte (LCG) */
            vm->rng_state = vm->rng_state * 1103515245 + 12345;
            vm_push(vm, (vm->rng_state >> 16) & 0xFF);
            vm->pc++;
            break;
            
        case OP_ENV:
            /* Push environment byte (returns 0 in standalone mode) */
            vm_push(vm, 0);
            vm->pc++;
            break;
            
        default:
            /* Unknown opcode - halt with error */
            vm->error = 5;
            vm->halted = 1;
            break;
    }
}

/* ========================================================================
 * VM Initialization and Run
 * ======================================================================== */
static void vm_init(vm_state_t *vm) {
    memset(vm, 0, sizeof(vm_state_t));
    vm->rng_state = 0xDEADBEEF;
}

static void vm_load_code(vm_state_t *vm, const uint8_t *bytecode, uint16_t len) {
    if (len > VM_CODE_SIZE) len = VM_CODE_SIZE;
    memcpy(vm->code, bytecode, len);
}

static void vm_set_round_keys(vm_state_t *vm, const uint8_t keys[16][4]) {
    memcpy(vm->round_keys, keys, 16 * 4);
}

static void vm_run(vm_state_t *vm, uint32_t max_steps) {
    uint32_t steps = 0;
    while (!vm->halted && steps < max_steps) {
        vm_step(vm);
        steps++;
    }
}

/* ========================================================================
 * Main Entry Point
 * For the CTF, this is compiled to an AVR ELF that players must reverse.
 * The bytecode and round keys are embedded in the binary.
 * ======================================================================== */

/* Placeholder: these will be filled by the build script */
/* The actual bytecode will be generated by assembler.py */
static const uint8_t VM_BYTECODE[] = {
    /* Will be replaced by build/vm/assembler.py output */
    OP_NOP, OP_HALT
};

static const uint16_t VM_BYTECODE_LEN = sizeof(VM_BYTECODE);

/* Entry point */
int main(void) {
    vm_state_t vm;
    vm_init(&vm);
    vm_load_code(&vm, VM_BYTECODE, VM_BYTECODE_LEN);
    
    /* Round keys will be loaded by the VM program itself via RKEY instructions */
    /* or populated from environment data */
    
    vm_run(&vm, 1000000); /* Max 1M steps */
    
    /* Output buffer contains the decrypted result */
    /* In the real firmware, this would be written to a UART or display */
    
    return vm.error;
}
