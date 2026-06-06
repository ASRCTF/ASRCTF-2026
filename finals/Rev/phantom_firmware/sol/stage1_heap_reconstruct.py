#!/usr/bin/env python3
"""
Stage 1 Solution: Heap Reconstruction from LiME Memory Dump

Extracts the ARM64 binary and config file from the fragmented heap
in the LiME-format memory dump.

Usage: python stage1_heap_reconstruct.py memdump.lime

Author: nmluan (solution script)
"""

import struct
import sys
import os

LIME_MAGIC = 0x4C694D45
LIME_HEADER_SIZE = 32
CHUNK_HEADER_SIZE = 16

# Fragment header: seq_num (2) + total_frags (2) + total_size (4) = 8 bytes
FRAG_HEADER_SIZE = 8


def parse_lime_segments(filepath):
    """Parse LiME format memory dump and return segments."""
    segments = []
    with open(filepath, 'rb') as f:
        while True:
            header = f.read(LIME_HEADER_SIZE)
            if len(header) < LIME_HEADER_SIZE:
                break
            
            magic, version, start, end, reserved = struct.unpack('<IIQQ8s', header)
            if magic != LIME_MAGIC:
                print(f"[!] Bad magic at offset {f.tell() - LIME_HEADER_SIZE}: 0x{magic:08X}")
                break
            
            size = end - start + 1
            data = f.read(size)
            segments.append({
                'start': start,
                'end': end,
                'size': size,
                'data': data
            })
            print(f"[+] Segment: 0x{start:016X} - 0x{end:016X} ({size / 1024 / 1024:.1f} MB)")
    
    return segments


def find_heap_chunks(data, base_addr):
    """
    Scan memory for heap chunks containing fragment headers.
    A fragment header has: seq_num (uint16), total_frags (uint16), total_size (uint32)
    We look for plausible values: seq_num < 32, total_frags < 32, 1024 < total_size < 1MB
    """
    fragments = []
    
    for offset in range(0, len(data) - CHUNK_HEADER_SIZE - FRAG_HEADER_SIZE, 16):
        # Check chunk header
        prev_size, size_flags = struct.unpack_from('<QQ', data, offset)
        chunk_size = size_flags & ~0x7  # Mask out flags
        
        # Plausible chunk size: 32 bytes to 64KB
        if chunk_size < 32 or chunk_size > 65536:
            continue
        
        # Check fragment header after chunk header
        frag_offset = offset + CHUNK_HEADER_SIZE
        if frag_offset + FRAG_HEADER_SIZE > len(data):
            continue
        
        seq_num, total_frags, total_size = struct.unpack_from('<HHI', data, frag_offset)
        
        # Plausible fragment: seq < total, total reasonable, size reasonable
        if (seq_num < total_frags and 
            total_frags >= 2 and total_frags <= 16 and
            total_size >= 512 and total_size <= 1048576):
            
            # Extract fragment data (skip chunk header + fragment header)
            data_offset = frag_offset + FRAG_HEADER_SIZE
            
            # Calculate the exact size of this fragment based on total_size and total_frags
            base_frag_size = total_size // total_frags
            remainder = total_size % total_frags
            actual_frag_size = base_frag_size + (1 if seq_num < remainder else 0)
            
            if actual_frag_size <= 0 or data_offset + actual_frag_size > len(data):
                continue
            
            frag_data = data[data_offset:data_offset + actual_frag_size]
            
            fragments.append({
                'addr': base_addr + offset,
                'seq': seq_num,
                'total': total_frags,
                'total_size': total_size,
                'data': frag_data,
                'chunk_size': chunk_size
            })
    
    return fragments


def reassemble_fragments(fragments):
    """Group fragments by total_frags+total_size and reassemble."""
    groups = {}
    for frag in fragments:
        key = (frag['total'], frag['total_size'])
        if key not in groups:
            groups[key] = []
        groups[key].append(frag)
    
    results = []
    for (total, total_size), frags in groups.items():
        # Sort by sequence number
        frags.sort(key=lambda f: f['seq'])
        
        # Check completeness
        seq_nums = [f['seq'] for f in frags]
        expected = list(range(total))
        
        if seq_nums == expected:
            # Reassemble
            data = b''.join(f['data'] for f in frags)
            # Trim to total_size
            data = data[:total_size]
            results.append({
                'total_size': total_size,
                'fragments': total,
                'data': data
            })
            print(f"[+] Reassembled artifact: {total_size} bytes from {total} fragments")
        else:
            print(f"[!] Incomplete artifact ({total} frags expected, got {len(frags)}): seqs={seq_nums}")
    
    return results


def identify_artifact(data):
    """Identify what type of artifact the reassembled data is."""
    if data[:4] == b'\x7fELF':
        return 'ELF binary'
    elif b'# Orbital Relay' in data[:200]:
        return 'Configuration file'
    elif data[:4] == b'FWUP':
        return 'Firmware update (FAKE/HONEYPOT)'
    else:
        return 'Unknown'


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <memdump.lime>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    print(f"=== Stage 1: Heap Reconstruction ===\n")
    print(f"[*] Parsing {filepath}...")
    
    segments = parse_lime_segments(filepath)
    print(f"[+] Found {len(segments)} segments\n")
    
    # Scan all segments for heap chunks
    all_fragments = []
    for seg in segments:
        frags = find_heap_chunks(seg['data'], seg['start'])
        all_fragments.extend(frags)
        print(f"[+] Found {len(frags)} fragment candidates in segment 0x{seg['start']:016X}")
    
    print(f"\n[*] Total fragments found: {len(all_fragments)}")
    
    # Reassemble
    artifacts = reassemble_fragments(all_fragments)
    
    print(f"\n[*] Extracted {len(artifacts)} artifacts:")
    output_dir = os.path.splitext(filepath)[0] + "_extracted"
    os.makedirs(output_dir, exist_ok=True)
    
    for i, artifact in enumerate(artifacts):
        artifact_type = identify_artifact(artifact['data'])
        
        if artifact_type == 'ELF binary':
            filename = "firmware_loader.elf"
        elif artifact_type == 'Configuration file':
            filename = "relay_config.txt"
        else:
            filename = f"artifact_{i}.bin"
        
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'wb') as f:
            f.write(artifact['data'])
        
        print(f"  [{i}] {artifact_type}: {len(artifact['data'])} bytes -> {output_path}")
    
    print(f"\n[+] Stage 1 complete! Artifacts extracted to {output_dir}/")


if __name__ == '__main__':
    main()
