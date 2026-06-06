#!/usr/bin/env python3
"""
Solaris VM Local TCP Bridge
Accepts TCP connections on port 1337 and handles the full VM protocol:
  1. Print banner
  2. Read instruction count from client
  3. Read bytecode payload from client
  4. Spawn chal.exe with piped stdin/stdout
  5. Forward chal.exe stdout → client socket byte-by-byte (to handle INPUT> prompts)
  6. Forward client input → chal.exe stdin when INPUT> is detected
"""
import socket
import subprocess
import threading
import sys
import os
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

BANNER = (
    b"+----------------------------------------------------------+\n"
    b"|      Solaris Space Station - Telemetry Uplink JIT v9     |\n"
    b"|      Orbital Relay Station 9 - Operational Network       |\n"
    b"+----------------------------------------------------------+\n"
    b"\n"
    b"ORS-9 Uplink established. Secure sandbox initialized.\n"
    b"Submit optimized sensor telemetry bytecode to calibrate thrusters.\n"
    b"\n"
)


def recv_line(sock):
    """Receive bytes from socket until newline."""
    buf = b""
    while True:
        ch = sock.recv(1)
        if not ch:
            return buf
        buf += ch
        if ch == b"\n":
            return buf


def recv_exact(sock, n):
    """Receive exactly n bytes from socket."""
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            return buf
        buf += chunk
    return buf


def handle_client(client_socket):
    """Handle a single TCP client connection with the full VM protocol."""
    addr = client_socket.getpeername()
    print(f"[*] Client connected from {addr}")
    sys.stdout.flush()

    proc = None
    try:
        # --- Step 1: Send banner ---
        client_socket.sendall(BANNER)
        client_socket.sendall(b"Enter Telemetry Bytecode count: ")

        # --- Step 2: Read instruction count ---
        count_line = recv_line(client_socket)
        if not count_line:
            print(f"[-] Client {addr}: No count received, closing.")
            sys.stdout.flush()
            return

        try:
            count = int(count_line.strip())
        except ValueError:
            client_socket.sendall(b"ORS-9: [ERROR] Invalid instruction count.\n")
            return

        if count <= 0 or count > 512:
            client_socket.sendall(b"ORS-9: [ERROR] Instruction count must be between 1 and 512.\n")
            return

        # --- Step 3: Read bytecode payload ---
        inst_size = 12
        total_bytes = count * inst_size
        client_socket.sendall(f"Send {total_bytes} bytes of bytecode payload:\n".encode())

        payload = recv_exact(client_socket, total_bytes)
        if len(payload) < total_bytes:
            client_socket.sendall(b"\nORS-9: [ERROR] Bytecode transmission interrupted.\n")
            return

        # --- Step 4: Spawn chal binary ---
        chal_path = os.path.join(SCRIPT_DIR, "chal")
        if os.name == 'nt' or not os.path.exists(chal_path):
            chal_path = os.path.join(SCRIPT_DIR, "chal.exe")

        if not os.path.exists(chal_path):
            client_socket.sendall(b"ORS-9: [ERROR] Telemetry VM binary not found.\n")
            return

        proc = subprocess.Popen(
            [chal_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=SCRIPT_DIR,
            bufsize=0
        )

        # Feed initial data to binary
        proc.stdin.write(f"{count}\n".encode())
        proc.stdin.write(payload)
        proc.stdin.flush()

        # --- Step 5: Interactive I/O loop ---
        # Read byte-by-byte from chal stdout, forward to socket.
        # When we see "INPUT>", read a line from the socket and forward to chal stdin.
        # Use a thread so we can enforce a timeout (chal may hang after exploit).
        import queue
        output_queue = queue.Queue()
        
        def reader_thread():
            try:
                while True:
                    char = proc.stdout.read(1)
                    if not char:
                        output_queue.put(None)
                        break
                    output_queue.put(char)
            except Exception:
                output_queue.put(None)
        
        reader = threading.Thread(target=reader_thread, daemon=True)
        reader.start()
        
        buf = b""
        while True:
            try:
                char = output_queue.get(timeout=3)
            except queue.Empty:
                # No output for 3 seconds — chal is likely hung
                break
            
            if char is None:
                break

            # Forward byte to client immediately
            try:
                client_socket.sendall(char)
            except Exception:
                break

            buf += char

            if char == b"\n":
                buf = b""
            elif buf.endswith(b"INPUT>"):
                # Wait for client to send a line of input
                user_input = recv_line(client_socket)
                if not user_input:
                    break
                try:
                    proc.stdin.write(user_input)
                    proc.stdin.flush()
                except Exception:
                    break
                buf = b""

        # Kill the process if still running (may hang after exploit)
        if proc.poll() is None:
            try:
                proc.kill()
            except Exception:
                pass
        proc.wait()
        # Read stderr for diagnostics
        try:
            stderr_data = proc.stderr.read()
            if stderr_data:
                print(f"[*] Client {addr}: chal stderr: {stderr_data.decode(errors='ignore')}")
        except Exception:
            pass
        print(f"[*] Client {addr}: chal exited with code {proc.returncode}")
        sys.stdout.flush()

    except Exception as e:
        print(f"[-] Client {addr}: Exception: {e}")
        sys.stdout.flush()
    finally:
        if proc and proc.poll() is None:
            try:
                proc.kill()
            except Exception:
                pass
        try:
            client_socket.close()
        except Exception:
            pass


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("127.0.0.1", 1337))
    except Exception as e:
        print(f"[ERROR] Could not bind to port 1337: {e}")
        sys.exit(1)

    s.listen(10)
    print("==================================================")
    print("   Solaris VM Local TCP Bridge Active on Port 1337 ")
    print("==================================================")
    print("[*] Listening on 127.0.0.1:1337...")
    print("[*] Press Ctrl+C to stop.")
    sys.stdout.flush()

    try:
        while True:
            client_sock, addr = s.accept()
            threading.Thread(target=handle_client, args=(client_sock,), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[*] Stopping TCP bridge...")
    finally:
        s.close()


if __name__ == "__main__":
    main()
