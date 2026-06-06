import os
import stat
import time

def dec_1(data):
    decrypted = ""
    for i in range(0, len(data), 4):
        chunk = data[i:i+4]
        if len(chunk) == 4:
            original_chunk = chunk[1] + chunk[3] + chunk[2] + chunk[0]
            decrypted += original_chunk
        else:
            decrypted += chunk
    return decrypted

def dec_2(data_bytes, key):
    res = bytearray()
    for i, b in enumerate(data_bytes):
        res.append(b ^ key[i % len(key)])
    return res

def spawn_prog(data, filename):
    with open(filename, "wb") as file:
        file.write(bytes.fromhex(data))
        if os.name == "posix":
            st = os.stat(filename)
            os.chmod(filename, st.st_mode | stat.S_IEXEC)
        else:
            print("This program only works on UNIX based systems")


def del_th(data, start_idx, procs, filename):
    bin_list = os.listdir()
    if "golden_titus_1" in bin_list and "golden_titus_2" in bin_list:
        procs *= 5 
    elif "golden_titus_1" in bin_list or "golden_titus_2" in bin_list:
        procs *= 3

    if filename in bin_list:
        os.remove(filename)
    else:
        return start_idx

    for i in range(procs):
        clean_hex = data[start_idx][len(str(start_idx+1))+1:]
        try:
            with open("whelp", "wb") as file:
                file.write(bytes.fromhex(clean_hex))
            
            if os.name == "posix":
                st = os.stat("whelp")
                os.chmod("whelp", st.st_mode | stat.S_IEXEC)
                time.sleep(1) 
                os.remove("whelp")
                time.sleep(0.5)
            else:
                print("This program only works on UNIX based systems.")
        except Exception as e:
            pass
        start_idx += 1
    return start_idx

def del_bm(data, start_idx, filename):
    bin_list = set(os.listdir())  

    has_titus1 = "golden_titus_1" in bin_list
    has_titus2 = "golden_titus_2" in bin_list
    has_brood2 = "twilight_broodmother_2" in bin_list
    has_brood1 = "twilight_broodmother_1" in bin_list

    if has_titus1 and has_titus2 and has_brood2 and has_brood1:
        hatchling_range = range(55, 58) 
        loop_count = 3
    elif (has_titus1 and has_titus2) or (has_titus1 and has_brood2) or (has_titus2 and has_brood2):
        hatchling_range = range(55, 59) 
        loop_count = 4
    elif has_titus1 or has_titus2:
        hatchling_range = range(55, 60) 
        loop_count = 5
    else:
        hatchling_range = range(55, 56) 
        loop_count = 2

    if filename in bin_list:
        os.remove(filename)
        
        for i in hatchling_range:
            file_to_write = f"twilight_hatchling_{i-54}"
            clean_hex = data[i][len(str(i))+1:] 
            
            with open(file_to_write, "wb") as file:
                file.write(bytes.fromhex(clean_hex))
                
            if os.name == 'posix':
                st = os.stat(file_to_write)
                os.chmod(file_to_write, st.st_mode | stat.S_IEXEC)
            else:
                return start_idx

        for i in range(1, loop_count + 1):
            time.sleep(0.5)
            start_idx = del_th(data, start_idx, 1, f"twilight_hatchling_{i}")
            
    return start_idx


    

if __name__ == "__main__":
    key = b"FF"
    with open("data.txt", "r") as file:
        hex_data = file.read().strip()
    
    encrypted_bytes = bytes.fromhex(hex_data)
    
    un_xored_bytes = dec_2(encrypted_bytes, key)
    
    un_xored_str = un_xored_bytes.decode('latin-1')
    original_text = dec_1(un_xored_str)
    chunks = original_text.split("END:")
    idx = 0
    spawn_prog(chunks[60][2:], "golden_titus_1")
    spawn_prog(chunks[61][2:], "golden_titus_2")
    spawn_prog(chunks[62][2:], "twilight_broodmother_1")
    spawn_prog(chunks[63][2:], "twilight_broodmother_2")
    spawn_prog(chunks[64][2:], "golden_twilight_hatchling_1")
    spawn_prog(chunks[65][2:], "golden_twilight_hatchling_2")
    for i in range(1,3):
        start_idx = del_th(chunks, idx, 2, f"golden_twilight_hatchling_{i}")
        idx = start_idx
    for i in range(1,3):
        start_idx = del_bm(chunks, idx, f"twilight_broodmother_{i}")
        idx = start_idx
    targets = ["golden_titus_1", "golden_titus_2", "stuntdrake"]

    for target in targets:
        try:
            os.remove(target)
        except FileNotFoundError:

            pass

