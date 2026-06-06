import os
import random
import struct

def crc16(data: bytes) -> int:
    # CRC-16 (Modbus/ARC style)
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF

def generate():
    decoy_flags = [
        "ASRCTF{forensics_is_not_always_about_hex_dumps_rabbit_hole}",
        "ASRCTF{n0t_th3_fl4g_y0u_4r3_l00k1ng_f0r_s0rry}",
        "ASRCTF{buffer_align_anomalies_are_not_exploits_here}",
        "ASRCTF{k33p_s34rch1ng_n3xp_l3v3l_d3c0y}",
        "ASRCTF{nice_hex_carving_but_try_harder_decoy_flag}"
    ]

    # File magic and global header
    # Magic: 'ORRY' (Orrery), Version: 1, Source: Capture Node 7
    magic = b"ORRY"
    global_header = struct.pack(">4sBBI", magic, 1, 7, 0) # Header size = 10 bytes
    
    dist_dir = os.path.join(os.path.dirname(__file__), "..", "dist")
    os.makedirs(dist_dir, exist_ok=True)
    out_path = os.path.join(dist_dir, "debris_log.bin")
    
    # Target size: 5,242,939 bytes
    target_size = 5242939
    
    with open(out_path, "wb") as f:
        f.write(global_header)
        current_size = len(global_header)
        
        seq = 0
        
        # Stop normal generation when we are close to the target size
        # to guarantee the padding frame fits perfectly.
        while current_size < target_size - 1000:
            choice = random.random()
            
            # Frame structure:
            # Sync (2 bytes: \xFA\xCE)
            # Type (1 byte)
            # Seq (4 bytes, Big-Endian)
            # Len (2 bytes, Big-Endian)
            # Data (N bytes)
            # CRC-16 (2 bytes, Big-Endian, calculated over Type + Seq + Len + Data)
            sync = b"\xFA\xCE"
            
            if choice < 0.25:
                # Type 1: Raw Binary Telemetry Frame (22 bytes payload)
                # Floats: pitch, yaw, roll, velocity, temperature, plus status flags (2 bytes)
                frame_type = 1
                payload = struct.pack(
                    ">fffffH",
                    random.uniform(-180.0, 180.0),
                    random.uniform(-180.0, 180.0),
                    random.uniform(-180.0, 180.0),
                    random.uniform(100.0, 5000.0),
                    random.uniform(20.0, 85.0),
                    random.randint(0, 0xFFFF)
                )
            elif choice < 0.50:
                # Type 2: Standard Text Log Frame
                frame_type = 2
                subsystem = random.choice(["EJECTOR", "THRUSTER", "COMMS", "POWER", "LIFE_SUPPORT", "THERMAL"])
                level = random.choice(["INFO", "WARNING", "DEBUG"])
                msg = f"[{level}] Subsystem {subsystem} reports state {random.choice(['NOMINAL', 'DEGRADED', 'STABLE', 'STANDBY'])} - Temp: {random.uniform(20.0, 85.0):.2f}C"
                payload = msg.encode('utf-8')
            elif choice < 0.70:
                # Type 3: High-Entropy Encrypted Payload Block (Compression/Encryption Hints)
                # IV (16 bytes) + Encrypted data length (4 bytes) + random payload (64 to 256 bytes) + Auth Tag (16 bytes)
                frame_type = 3
                enc_len = random.randint(64, 256)
                payload_data = os.urandom(enc_len)
                iv = os.urandom(16)
                tag = os.urandom(16)
                payload = struct.pack(
                    f">16sI{enc_len}s16s",
                    iv,
                    enc_len,
                    payload_data,
                    tag
                )
            elif choice < 0.85:
                # Type 4: Decoy Flag Signal
                frame_type = 4
                flag = random.choice(decoy_flags)
                msg = f"ALERT_CACHE: signature=DEC_SIG_{random.randint(100, 999)} data_cache={flag}"
                payload = msg.encode('utf-8')
            else:
                # Type 5: Corrupted Archive Fragment / Binwalk decoy
                # Embeds a realistic PKZIP Local File Header signature to trip foremost/binwalk
                frame_type = 5
                zip_header = b"\x50\x4B\x03\x04" # PK\x03\x04
                version = b"\x14\x00"            # version 2.0
                flags = b"\x00\x00"              # no flags
                compression = b"\x08\x00"        # deflated
                mod_time = b"\x21\x2f"
                mod_date = b"\x6f\x52"
                crc32 = b"\xef\xbe\xad\xde"      # decoy CRC-32
                comp_size = struct.pack("<I", random.randint(128, 512))
                uncomp_size = struct.pack("<I", random.randint(512, 1024))
                filename = b"comms_archive_payload.bin"
                filename_len = struct.pack("<H", len(filename))
                extra_len = b"\x00\x00"
                
                payload = zip_header + version + flags + compression + mod_time + mod_date + crc32 + comp_size + uncomp_size + filename_len + extra_len + filename + os.urandom(64)
                
            payload_len = len(payload)
            header_to_checksum = struct.pack(">BHI", frame_type, payload_len, seq)
            crc = crc16(header_to_checksum + payload)
            
            # Sync (2) + Type (1) + Len (2) + Seq (4) + Payload (N) + CRC (2)
            frame_bytes = sync + header_to_checksum + payload + struct.pack(">H", crc)
            
            f.write(frame_bytes)
            current_size += len(frame_bytes)
            seq += 1
            
        # Perfect padding alignment to reach exactly 5,242,939 bytes
        # Using a valid Type 0xFF (Padding Frame) structure
        rem = target_size - current_size
        if rem >= 11:
            sync = b"\xFA\xCE"
            frame_type = 255 # Padding Frame
            payload_len = rem - 11
            payload = b"\x00" * payload_len
            header_to_checksum = struct.pack(">BHI", frame_type, payload_len, seq)
            crc = crc16(header_to_checksum + payload)
            
            padding_frame = sync + header_to_checksum + payload + struct.pack(">H", crc)
            f.write(padding_frame)
            current_size += len(padding_frame)
            
    print(f"Generated structured decoy binary capture with size: {os.path.getsize(out_path)} bytes.")

if __name__ == "__main__":
    generate()
