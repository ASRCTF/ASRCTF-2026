/// Custom Stack-Based VM Interpreter
///
/// Implements the PhantomVM instruction set with ~30 opcodes.
/// This is the runtime that executes the bytecode payload decoded
/// from the invisible Unicode configuration file.
///
/// NOTE: The VM uses a CUSTOM ISA — this is NOT standard WASM, JVM, or CLR bytecode.

use crate::cipher::{SBOX, SBOX_INV, PBOX, apply_pbox_32};

const VM_STACK_SIZE: usize = 256;
const VM_MEM_SIZE: usize = 4096;
const VM_CODE_SIZE: usize = 2048;

// Opcodes
const OP_PUSH: u8 = 0x00;
const OP_PUSH16: u8 = 0x01;
const OP_POP: u8 = 0x02;
const OP_DUP: u8 = 0x03;
const OP_SWAP: u8 = 0x04;
const OP_OVER: u8 = 0x05;
const OP_ROT: u8 = 0x06;
const OP_ADD: u8 = 0x08;
const OP_SUB: u8 = 0x09;
const OP_MUL: u8 = 0x0A;
const OP_XOR: u8 = 0x0B;
const OP_AND: u8 = 0x0C;
const OP_OR: u8 = 0x0D;
const OP_NOT: u8 = 0x0E;
const OP_SHL: u8 = 0x10;
const OP_SHR: u8 = 0x11;
const OP_ROTL: u8 = 0x12;
const OP_ROTR: u8 = 0x13;
const OP_JMP: u8 = 0x18;
const OP_JZ: u8 = 0x19;
const OP_JNZ: u8 = 0x1A;
const OP_CALL: u8 = 0x1B;
const OP_RET: u8 = 0x1C;
const OP_SBOX: u8 = 0x20;
const OP_SBOXI: u8 = 0x21;
const OP_PERM: u8 = 0x22;
const OP_PERMI: u8 = 0x23;
const OP_MIX: u8 = 0x24;
const OP_RKEY: u8 = 0x25;
const OP_LOAD: u8 = 0x28;
const OP_STORE: u8 = 0x29;
const OP_MMOD: u8 = 0x2A;
const OP_CRC: u8 = 0x2B;
const OP_IN: u8 = 0x30;
const OP_OUT: u8 = 0x31;
const OP_HALT: u8 = 0x32;
const OP_NOP: u8 = 0x33;
const OP_TRAP: u8 = 0x38;
const OP_DBG: u8 = 0x39;
const OP_RND: u8 = 0x3A;
const OP_ENV: u8 = 0x3B;

/// VM State
pub struct VmState {
    stack: [u8; VM_STACK_SIZE],
    sp: usize,
    call_stack: [u16; 64],
    csp: usize,
    code: [u8; VM_CODE_SIZE],
    pc: usize,
    mem: [u8; VM_MEM_SIZE],
    round_keys: [[u8; 4]; 16],
    output: Vec<u8>,
    halted: bool,
    error: u8,
    rng_state: u32,
    steps: u32,
    max_steps: u32,
}

impl VmState {
    pub fn new(max_steps: u32) -> Self {
        VmState {
            stack: [0; VM_STACK_SIZE],
            sp: 0,
            call_stack: [0; 64],
            csp: 0,
            code: [0; VM_CODE_SIZE],
            pc: 0,
            mem: [0; VM_MEM_SIZE],
            round_keys: [[0; 4]; 16],
            output: Vec::new(),
            halted: false,
            error: 0,
            rng_state: 0xDEADBEEF,
            steps: 0,
            max_steps,
        }
    }

    pub fn load_code(&mut self, bytecode: &[u8]) {
        let len = bytecode.len().min(VM_CODE_SIZE);
        self.code[..len].copy_from_slice(&bytecode[..len]);
    }

    pub fn set_round_keys(&mut self, keys: &[[u8; 4]; 16]) {
        self.round_keys = *keys;
    }

    fn push(&mut self, val: u8) {
        if self.sp >= VM_STACK_SIZE {
            self.error = 1;
            self.halted = true;
            return;
        }
        self.stack[self.sp] = val;
        self.sp += 1;
    }

    fn pop(&mut self) -> u8 {
        if self.sp == 0 {
            self.error = 2;
            self.halted = true;
            return 0;
        }
        self.sp -= 1;
        self.stack[self.sp]
    }

    fn peek(&self) -> u8 {
        if self.sp == 0 { return 0; }
        self.stack[self.sp - 1]
    }

    fn read_u16_at_pc(&mut self) -> u16 {
        if self.pc + 1 >= VM_CODE_SIZE {
            self.error = 5;
            self.halted = true;
            return 0;
        }
        let hi = self.code[self.pc] as u16;
        let lo = self.code[self.pc + 1] as u16;
        self.pc += 2;
        (hi << 8) | lo
    }

    fn step(&mut self) {
        if self.halted || self.pc >= VM_CODE_SIZE {
            self.halted = true;
            return;
        }

        let opcode = self.code[self.pc];
        self.pc += 1;

        match opcode {
            OP_PUSH => {
                let val = self.code[self.pc];
                self.pc += 1;
                self.push(val);
            }
            OP_PUSH16 => {
                let addr = self.read_u16_at_pc();
                self.push((addr >> 8) as u8);
                self.push(addr as u8);
            }
            OP_POP => { self.pop(); }
            OP_DUP => {
                let val = self.peek();
                self.push(val);
            }
            OP_SWAP => {
                let a = self.pop();
                let b = self.pop();
                self.push(a);
                self.push(b);
            }
            OP_OVER => {
                if self.sp < 2 { self.error = 2; self.halted = true; return; }
                let val = self.stack[self.sp - 2];
                self.push(val);
            }
            OP_ROT => {
                let c = self.pop();
                let b = self.pop();
                let a = self.pop();
                self.push(b);
                self.push(c);
                self.push(a);
            }
            OP_ADD => {
                let a = self.pop();
                let b = self.pop();
                self.push(b.wrapping_add(a));
            }
            OP_SUB => {
                let a = self.pop();
                let b = self.pop();
                self.push(b.wrapping_sub(a));
            }
            OP_MUL => {
                let a = self.pop();
                let b = self.pop();
                self.push(b.wrapping_mul(a));
            }
            OP_XOR => {
                let a = self.pop();
                let b = self.pop();
                self.push(b ^ a);
            }
            OP_AND => {
                let a = self.pop();
                let b = self.pop();
                self.push(b & a);
            }
            OP_OR => {
                let a = self.pop();
                let b = self.pop();
                self.push(b | a);
            }
            OP_NOT => {
                let a = self.pop();
                self.push(!a);
            }
            OP_SHL => {
                let amt = self.pop() & 7;
                let val = self.pop();
                self.push(val << amt);
            }
            OP_SHR => {
                let amt = self.pop() & 7;
                let val = self.pop();
                self.push(val >> amt);
            }
            OP_ROTL => {
                let amt = (self.pop() & 7) as u32;
                let val = self.pop();
                self.push((val as u8).rotate_left(amt));
            }
            OP_ROTR => {
                let amt = (self.pop() & 7) as u32;
                let val = self.pop();
                self.push((val as u8).rotate_right(amt));
            }
            OP_JMP => {
                let addr = self.read_u16_at_pc();
                self.pc = addr as usize;
            }
            OP_JZ => {
                let addr = self.read_u16_at_pc();
                let val = self.pop();
                if val == 0 { self.pc = addr as usize; }
            }
            OP_JNZ => {
                let addr = self.read_u16_at_pc();
                let val = self.pop();
                if val != 0 { self.pc = addr as usize; }
            }
            OP_CALL => {
                let addr = self.read_u16_at_pc();
                if self.csp >= 64 { self.error = 3; self.halted = true; return; }
                self.call_stack[self.csp] = self.pc as u16;
                self.csp += 1;
                self.pc = addr as usize;
            }
            OP_RET => {
                if self.csp == 0 { self.error = 4; self.halted = true; return; }
                self.csp -= 1;
                self.pc = self.call_stack[self.csp] as usize;
            }
            OP_SBOX => {
                let a = self.pop();
                let hi = SBOX[((a >> 4) & 0xF) as usize];
                let lo = SBOX[(a & 0xF) as usize];
                self.push((hi << 4) | lo);
            }
            OP_SBOXI => {
                let a = self.pop();
                let hi = SBOX_INV[((a >> 4) & 0xF) as usize];
                let lo = SBOX_INV[(a & 0xF) as usize];
                self.push((hi << 4) | lo);
            }
            OP_PERM => {
                if self.sp < 4 { self.error = 2; self.halted = true; return; }
                let b3 = self.pop() as u32;
                let b2 = self.pop() as u32;
                let b1 = self.pop() as u32;
                let b0 = self.pop() as u32;
                let val = (b0 << 24) | (b1 << 16) | (b2 << 8) | b3;
                let result = apply_pbox_32(val, &PBOX);
                self.push((result >> 24) as u8);
                self.push((result >> 16) as u8);
                self.push((result >> 8) as u8);
                self.push(result as u8);
            }
            OP_PERMI => {
                if self.sp < 4 { self.error = 2; self.halted = true; return; }
                let b3 = self.pop() as u32;
                let b2 = self.pop() as u32;
                let b1 = self.pop() as u32;
                let b0 = self.pop() as u32;
                let val = (b0 << 24) | (b1 << 16) | (b2 << 8) | b3;
                // Compute inverse P-box
                let mut pbox_inv = [0u8; 32];
                for i in 0..32 { pbox_inv[PBOX[i] as usize] = i as u8; }
                let result = apply_pbox_32(val, &pbox_inv);
                self.push((result >> 24) as u8);
                self.push((result >> 16) as u8);
                self.push((result >> 8) as u8);
                self.push(result as u8);
            }
            OP_MIX => {
                let round_idx = self.pop() as usize & 0xF;
                if self.sp < 4 { self.error = 2; self.halted = true; return; }
                let b3 = self.pop();
                let b2 = self.pop();
                let b1 = self.pop();
                let b0 = self.pop();
                // Apply S-box to each nibble of all 4 bytes
                let mut bytes = [b0, b1, b2, b3];
                for b in bytes.iter_mut() {
                    let hi = SBOX[((*b >> 4) & 0xF) as usize];
                    let lo = SBOX[(*b & 0xF) as usize];
                    *b = (hi << 4) | lo;
                }
                // Apply P-box
                let val = (bytes[0] as u32) << 24
                    | (bytes[1] as u32) << 16
                    | (bytes[2] as u32) << 8
                    | bytes[3] as u32;
                let permuted = apply_pbox_32(val, &PBOX);
                // XOR with round key (copy to avoid borrow issue)
                let rk = self.round_keys[round_idx];
                self.push(((permuted >> 24) as u8) ^ rk[0]);
                self.push(((permuted >> 16) as u8) ^ rk[1]);
                self.push(((permuted >> 8) as u8) ^ rk[2]);
                self.push((permuted as u8) ^ rk[3]);
            }
            OP_RKEY => {
                let idx = (self.code[self.pc] & 0xF) as usize;
                self.pc += 1;
                let rk = self.round_keys[idx];
                self.push(rk[0]);
                self.push(rk[1]);
                self.push(rk[2]);
                self.push(rk[3]);
            }
            OP_LOAD => {
                let addr = self.read_u16_at_pc() as usize;
                if addr < VM_MEM_SIZE {
                    self.push(self.mem[addr]);
                } else {
                    self.push(0);
                }
            }
            OP_STORE => {
                let addr = self.read_u16_at_pc() as usize;
                let val = self.pop();
                if addr < VM_MEM_SIZE {
                    self.mem[addr] = val;
                }
            }
            OP_MMOD => {
                let addr = self.read_u16_at_pc() as usize;
                let val = self.pop();
                if addr < VM_CODE_SIZE {
                    self.code[addr] = val;
                }
            }
            OP_CRC => {
                let a = self.pop();
                self.push(a.wrapping_mul(0x9E).wrapping_add(0x37));
            }
            OP_IN => { self.push(0); }
            OP_OUT => {
                let val = self.pop();
                self.output.push(val);
            }
            OP_HALT => { self.halted = true; }
            OP_NOP => {}
            OP_TRAP => {
                // Skip over embedded string
                let len = self.code[self.pc] as usize;
                self.pc += 1 + len;
            }
            OP_DBG => {}
            OP_RND => {
                self.rng_state = self.rng_state.wrapping_mul(1103515245).wrapping_add(12345);
                self.push((self.rng_state >> 16) as u8);
            }
            OP_ENV => { self.push(0); }
            _ => {
                self.error = 5;
                self.halted = true;
            }
        }
    }

    /// Run the VM until halt or max_steps
    pub fn run(&mut self) {
        while !self.halted && self.steps < self.max_steps {
            self.step();
            self.steps += 1;
        }
    }

    /// Get the output buffer
    pub fn get_output(&self) -> &[u8] {
        &self.output
    }

    /// Get the display buffer (memory 0x100-0x1FF)
    pub fn get_display_buffer(&self) -> &[u8] {
        &self.mem[0x100..0x200]
    }

    /// Check if VM completed successfully
    pub fn is_ok(&self) -> bool {
        self.halted && self.error == 0
    }
}
