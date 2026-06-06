#!/usr/bin/env python3
import sys
import os
import signal
import subprocess

def setup_timeout(seconds: int):
    # Safe signal handling for cross-platform compatibility (Windows vs Linux)
    if hasattr(signal, 'SIGALRM'):
        signal.signal(signal.SIGALRM, lambda s, f: sys.exit(0))
        signal.alarm(seconds)

def main():
    setup_timeout(60) # 60 second timeout for the telemetry routine

    print("+----------------------------------------------------------+")
    print("|      Solaris Space Station - Telemetry Uplink JIT v9     |")
    print("|      Orbital Relay Station 9 - Operational Network       |")
    print("+----------------------------------------------------------+")
    print("")
    print("ORS-9 Uplink established. Secure sandbox initialized.")
    print("Submit optimized sensor telemetry bytecode to calibrate thrusters.")
    print("")
    sys.stdout.flush()

    try:
        # 1. Read bytecode count
        sys.stdout.write("Enter Telemetry Bytecode count: ")
        sys.stdout.flush()
        count_line = sys.stdin.readline()
        if not count_line:
            return
        
        try:
            count = int(count_line.strip())
        except ValueError:
            print("ORS-9: [ERROR] Invalid instruction count.")
            sys.stdout.flush()
            return

        if count <= 0 or count > 512:
            print("ORS-9: [ERROR] Instruction count must be between 1 and 512.")
            sys.stdout.flush()
            return

        # 2. Calculate bytes to read
        # Each Instruction is 12 bytes packed: op(1) + dst(1) + src1(1) + src2(1) + imm(8)
        inst_size = 12
        total_bytes = count * inst_size

        sys.stdout.write(f"Send {total_bytes} bytes of bytecode payload:\n")
        sys.stdout.flush()

        # 3. Read exact payload bytes from stdin
        payload = b""
        while len(payload) < total_bytes:
            chunk = sys.stdin.buffer.read(total_bytes - len(payload))
            if not chunk:
                print("\nORS-9: [ERROR] Bytecode transmission interrupted.")
                sys.stdout.flush()
                return
            payload += chunk

        # 4. Start the binary process
        # Determine paths (handle .exe on Windows for local testing)
        dir_path = os.path.dirname(os.path.abspath(__file__))
        chal_path = os.path.join(dir_path, "chal")
        if os.name == 'nt' or not os.path.exists(chal_path):
            chal_path = os.path.join(dir_path, "chal.exe")

        if not os.path.exists(chal_path):
            print("ORS-9: [ERROR] Telemetry VM binary not found. Please compile the binary.")
            sys.stdout.flush()
            return

        # Start process with piped stdin/stdout
        proc = subprocess.Popen(
            [chal_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0
        )

        # Pipe the initial data to binary (instruction count + newline + payload)
        proc.stdin.write(f"{count}\n".encode())
        proc.stdin.write(payload)
        proc.stdin.flush()

        # 5. Interactive loop for VM inputs / outputs
        # We read from binary output and pipe to user, and vice versa
        while True:
            # Read byte-by-byte until we get a newline or 'INPUT>'
            buf = b""
            while True:
                char = proc.stdout.read(1)
                if not char:
                    break
                buf += char
                if char == b"\n" or buf.endswith(b"INPUT>"):
                    break
            
            if not buf:
                break
            
            sys.stdout.buffer.write(buf)
            sys.stdout.flush()

            # If the binary is waiting for input (indicated by "INPUT>" in buf)
            if b"INPUT>" in buf:
                # Read input from user and send to binary
                user_input = sys.stdin.readline()
                if not user_input:
                    break
                proc.stdin.write(user_input.encode())
                proc.stdin.flush()

        proc.wait()
    except Exception as e:
        print(f"\nORS-9: [CRITICAL TELEMETRY EXCEPTION] {e}")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
