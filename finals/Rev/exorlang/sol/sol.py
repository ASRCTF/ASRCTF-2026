from collections import defaultdict

with open("challenge.bfx", "r") as f:
    program = f.read()

def run(program):
    tape = defaultdict(int)
    ptr = 0
    ip = 0
    output = ""

    bracket_map = {}
    stack = []

    for i, c in enumerate(program):
        if c == "[":
            stack.append(i)
        elif c == "]":
            j = stack.pop()
            bracket_map[i] = j
            bracket_map[j] = i

    while ip < len(program):
        op = program[ip]

        if op == ">":
            ptr += 1

        elif op == "<":
            ptr -= 1

        elif op == "+":
            tape[ptr] = (tape[ptr] + 1) & 0xFF

        elif op == "-":
            tape[ptr] = (tape[ptr] - 1) & 0xFF

        elif op == ".":
            output += chr(tape[ptr])

        elif op == ",":
            pass

        elif op == "[":
            if tape[ptr] == 0:
                ip = bracket_map[ip]

        elif op == "]":
            if tape[ptr] != 0:
                ip = bracket_map[ip]

        # Custom instruction
        elif op == "@":
            tape[ptr] ^= tape[0]

        ip += 1

    return output

enc = run(program)

# Notice that the first byte is the key itself (it is itself when XORed with itself (= 0)), so recover the key from cell_0 manually.
key = 55

flag = "".join(chr(ord(c) ^ key) for c in enc[1:])

print(flag)
