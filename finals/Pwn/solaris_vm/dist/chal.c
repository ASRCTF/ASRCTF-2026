#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>

#define MAX_INSTRUCTIONS 512
#define MEM_SIZE 256

// VM Opcodes
typedef enum {
    OP_ADD = 0,
    OP_SUB = 1,
    OP_MUL = 2,
    OP_LI  = 3,
    OP_LOAD = 4,
    OP_STORE = 5,
    OP_JMP  = 6,
    OP_JEQ  = 7,
    OP_JLT  = 8,
    OP_INPUT = 9,
    OP_HALT  = 10
} Opcode;

// Instruction Representation (Packed to avoid compilation alignment discrepancies)
typedef struct {
    uint8_t op;
    uint8_t dst;
    uint8_t src1;
    uint8_t src2;
    int64_t imm;
} __attribute__((packed)) VMInstruction;

// Range Struct for JIT Range Analysis
typedef struct {
    int64_t min;
    int64_t max;
} Range;

// Global range state for each instruction to handle control flow merges
Range reg_ranges[MAX_INSTRUCTIONS][6];
uint8_t optimized[MAX_INSTRUCTIONS];

void setup() {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
}

void win() {
    char flag[128];
    FILE *f = fopen("flag.txt", "r");
    if (f == NULL) {
        puts("ORS-9: [ERROR] Flag file 'flag.txt' not found! Contact telemetry command.");
        exit(1);
    }
    if (fgets(flag, sizeof(flag), f)) {
        printf("ORS-9: [TELEMETRY KEY ACCEPTED] %s\n", flag);
    }
    fclose(f);
    exit(0);
}

// Merge incoming range state with existing target instruction state
void merge_ranges(int target, Range* incoming, int count) {
    if (target < 0 || target >= count) return;
    for (int r = 0; r < 6; r++) {
        Range* existing = &reg_ranges[target][r];
        if (existing->min > existing->max) {
            // Unvisited state (represented by min > max)
            *existing = incoming[r];
        } else {
            // Merge states: expand the bounds
            if (incoming[r].min < existing->min) {
                existing->min = incoming[r].min;
            }
            if (incoming[r].max > existing->max) {
                existing->max = incoming[r].max;
            }
        }
    }
}

// Perform forward range-analysis pass to optimize bounds checking
void optimize_vm(VMInstruction* code, int count) {
    // Initialize all range states to unvisited: min = 1, max = 0
    for (int i = 0; i < count; i++) {
        for (int r = 0; r < 6; r++) {
            reg_ranges[i][r] = (Range){1, 0};
        }
        optimized[i] = 0;
    }

    // Program entry point range state (all registers initialized to [0, 0])
    for (int r = 0; r < 6; r++) {
        reg_ranges[0][r] = (Range){0, 0};
    }

    for (int pc = 0; pc < count; pc++) {
        Range* current = reg_ranges[pc];
        
        // If this PC is unreachable, skip range analysis for it
        if (current[0].min > current[0].max) {
            continue;
        }

        VMInstruction inst = code[pc];
        Range next_ranges[6];
        memcpy(next_ranges, current, sizeof(next_ranges));

        switch (inst.op) {
            case OP_INPUT:
                if (inst.dst < 6) {
                    // Sensor telemetry range limit
                    next_ranges[inst.dst] = (Range){0, 100000};
                }
                break;
            case OP_LI:
                if (inst.dst < 6) {
                    next_ranges[inst.dst] = (Range){inst.imm, inst.imm};
                }
                break;
            case OP_ADD:
                if (inst.dst < 6 && inst.src1 < 6 && inst.src2 < 6) {
                    next_ranges[inst.dst] = (Range){
                        current[inst.src1].min + current[inst.src2].min,
                        current[inst.src1].max + current[inst.src2].max
                    };
                }
                break;
            case OP_SUB:
                if (inst.dst < 6 && inst.src1 < 6 && inst.src2 < 6) {
                    next_ranges[inst.dst] = (Range){
                        current[inst.src1].min - current[inst.src2].max,
                        current[inst.src1].max - current[inst.src2].min
                    };
                }
                break;
            case OP_MUL:
                if (inst.dst < 6 && inst.src1 < 6 && inst.src2 < 6) {
                    int64_t v1 = current[inst.src1].min * current[inst.src2].min;
                    int64_t v2 = current[inst.src1].min * current[inst.src2].max;
                    int64_t v3 = current[inst.src1].max * current[inst.src2].min;
                    int64_t v4 = current[inst.src1].max * current[inst.src2].max;
                    
                    int64_t min_val = v1;
                    if (v2 < min_val) min_val = v2;
                    if (v3 < min_val) min_val = v3;
                    if (v4 < min_val) min_val = v4;

                    int64_t max_val = v1;
                    if (v2 > max_val) max_val = v2;
                    if (v3 > max_val) max_val = v3;
                    if (v4 > max_val) max_val = v4;

                    next_ranges[inst.dst] = (Range){min_val, max_val};
                }
                break;
            case OP_LOAD:
                if (inst.dst < 6 && inst.src1 < 6) {
                    // Accessing mem clears the range since memory is dynamic
                    next_ranges[inst.dst] = (Range){-9223372036854775807LL, 9223372036854775807LL};
                    
                    // Static safety check for bounds-check elimination
                    if (current[inst.src1].min >= 0 && current[inst.src1].max < MEM_SIZE) {
                        optimized[pc] = 1; // Mark as optimized (eliminate check)
                    }
                }
                break;
            case OP_STORE:
                if (inst.dst < 6 && inst.src1 < 6) {
                    // Static safety check for bounds-check elimination
                    if (current[inst.dst].min >= 0 && current[inst.dst].max < MEM_SIZE) {
                        optimized[pc] = 1; // Mark as optimized (eliminate check)
                    }
                }
                break;
            case OP_JMP:
                merge_ranges(inst.imm, next_ranges, count);
                break;
            case OP_JEQ:
                merge_ranges(pc + 1, next_ranges, count);
                merge_ranges(inst.imm, next_ranges, count);
                break;
            case OP_JLT:
                if (inst.dst < 6 && inst.src1 < 6) {
                    Range taken_ranges[6];
                    Range fallthrough_ranges[6];
                    memcpy(taken_ranges, next_ranges, sizeof(taken_ranges));
                    memcpy(fallthrough_ranges, next_ranges, sizeof(fallthrough_ranges));

                    // If comparing with a constant register value
                    if (current[inst.src1].min == current[inst.src1].max) {
                        int64_t K = current[inst.src1].min;

                        /* 
                         * JIT OPTIMIZATION VULNERABILITY (Range Refinement Bug):
                         * The developer swapped the Taken and Fallthrough branch logic constraints.
                         * 
                         * Taken path (reg < K): Should constrain reg.max to K - 1.
                         * Fallthrough path (reg >= K): Should constrain reg.min to K.
                         * 
                         * Swapped behavior implemented below:
                         */
                        // [Taken Path Buggy Refinement]
                        if (taken_ranges[inst.dst].min < K) {
                            taken_ranges[inst.dst].min = K; 
                        }

                        // [Fallthrough Path Buggy Refinement]
                        if (fallthrough_ranges[inst.dst].max > K - 1) {
                            fallthrough_ranges[inst.dst].max = K - 1;
                        }
                    }

                    merge_ranges(inst.imm, taken_ranges, count);
                    merge_ranges(pc + 1, fallthrough_ranges, count);
                }
                break;
            case OP_HALT:
            default:
                break;
        }

        // Standard fallthrough propagation (except for jumps/branches/halts)
        if (inst.op != OP_JMP && inst.op != OP_JEQ && inst.op != OP_JLT && inst.op != OP_HALT) {
            merge_ranges(pc + 1, next_ranges, count);
        }
    }
}

// Main execution loop for the virtual machine
void run_vm(VMInstruction* code, int count) {
    int64_t regs[6] = {0};
    int64_t data_mem[MEM_SIZE] = {0};
    int pc = 0;

    printf("ORS-9: [TELEMETRY INITIATING] Running optimized bytecode...\n");

    while (pc < count) {
        VMInstruction inst = code[pc];
        switch (inst.op) {
            case OP_INPUT:
                if (inst.dst < 6) {
                    int64_t val = 0;
                    printf("INPUT> ");
                    if (scanf("%ld", &val) <= 0) {
                        printf("ORS-9: [ERROR] Invalid sensor value read.\n");
                        exit(1);
                    }
                    regs[inst.dst] = val;
                }
                pc++;
                break;
            case OP_LI:
                if (inst.dst < 6) {
                    regs[inst.dst] = inst.imm;
                }
                pc++;
                break;
            case OP_ADD:
                if (inst.dst < 6 && inst.src1 < 6 && inst.src2 < 6) {
                    regs[inst.dst] = regs[inst.src1] + regs[inst.src2];
                }
                pc++;
                break;
            case OP_SUB:
                if (inst.dst < 6 && inst.src1 < 6 && inst.src2 < 6) {
                    regs[inst.dst] = regs[inst.src1] - regs[inst.src2];
                }
                pc++;
                break;
            case OP_MUL:
                if (inst.dst < 6 && inst.src1 < 6 && inst.src2 < 6) {
                    regs[inst.dst] = regs[inst.src1] * regs[inst.src2];
                }
                pc++;
                break;
            case OP_LOAD:
                if (inst.dst < 6 && inst.src1 < 6) {
                    int64_t idx = regs[inst.src1];
                    if (!optimized[pc]) {
                        // Safe bounds check
                        if (idx < 0 || idx >= MEM_SIZE) {
                            printf("ORS-9: [TELEMETRY SEGV] Buffer index %ld out of bounds! Hardware shutdown.\n", idx);
                            exit(1);
                        }
                    }
                    regs[inst.dst] = data_mem[idx];
                }
                pc++;
                break;
            case OP_STORE:
                if (inst.dst < 6 && inst.src1 < 6) {
                    int64_t idx = regs[inst.dst];
                    int64_t val = regs[inst.src1];
                    if (!optimized[pc]) {
                        // Safe bounds check
                        if (idx < 0 || idx >= MEM_SIZE) {
                            printf("ORS-9: [TELEMETRY SEGV] Buffer index %ld out of bounds! Hardware shutdown.\n", idx);
                            exit(1);
                        }
                    }
                    data_mem[idx] = val;
                }
                pc++;
                break;
            case OP_JMP:
                pc = inst.imm;
                break;
            case OP_JEQ:
                if (inst.dst < 6 && inst.src1 < 6) {
                    if (regs[inst.dst] == regs[inst.src1]) {
                        pc = inst.imm;
                    } else {
                        pc++;
                    }
                } else {
                    pc++;
                }
                break;
            case OP_JLT:
                if (inst.dst < 6 && inst.src1 < 6) {
                    if (regs[inst.dst] < regs[inst.src1]) {
                        pc = inst.imm;
                    } else {
                        pc++;
                    }
                } else {
                    pc++;
                }
                break;
            case OP_HALT:
                printf("ORS-9: [SUCCESS] Telemetry routine executed successfully.\n");
                printf("Register State:\n");
                for (int r = 0; r < 6; r++) {
                    printf("r%d: 0x%016llx (%lld)\n", r, (unsigned long long)regs[r], (long long)regs[r]);
                }
                return;
            default:
                printf("ORS-9: [ERROR] Unknown instruction opcode: %d\n", inst.op);
                exit(1);
        }
    }
}

int main(int argc, char** argv) {
    setup();

    printf("==================================================\n");
    printf("   Solaris Space Station Telemetry Subsystem JIT  \n");
    printf("==================================================\n");

    uint32_t count = 0;
    printf("Enter Telemetry Bytecode count: ");
    if (scanf("%u", &count) <= 0 || count == 0 || count > MAX_INSTRUCTIONS) {
        printf("ORS-9: [ERROR] Invalid instruction size.\n");
        return 1;
    }

    VMInstruction* code = calloc(count, sizeof(VMInstruction));
    if (!code) {
        printf("ORS-9: [ERROR] Allocation failure.\n");
        return 1;
    }

    printf("Send %lu bytes of bytecode payload:\n", count * sizeof(VMInstruction));
    
    // Read raw bytecode instructions
    uint8_t* code_ptr = (uint8_t*)code;
    uint32_t bytes_to_read = count * sizeof(VMInstruction);
    uint32_t bytes_read = 0;
    while (bytes_read < bytes_to_read) {
        int r = read(0, code_ptr + bytes_read, bytes_to_read - bytes_read);
        if (r <= 0) {
            printf("ORS-9: [ERROR] Bytecode transmission interrupted.\n");
            free(code);
            return 1;
        }
        bytes_read += r;
    }

    // Run custom jumps validation (Forward Jumps only to allow single-pass JIT Range Analysis)
    for (int i = 0; i < count; i++) {
        VMInstruction inst = code[i];
        if (inst.op == OP_JMP || inst.op == OP_JEQ || inst.op == OP_JLT) {
            if (inst.imm <= i || inst.imm >= count) {
                printf("ORS-9: [JIT REJECT] Backward or out-of-bounds jumps are prohibited.\n");
                free(code);
                return 1;
            }
        }
    }

    // Run the buggy Range Analysis Optimizer
    optimize_vm(code, count);

    // Execute
    run_vm(code, count);

    free(code);
    return 0;
}
