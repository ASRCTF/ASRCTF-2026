import os

def convert_bin_to_hex(filename, spec_char):
    with open("hexes.txt", "a") as out_file:
        with open(filename, "rb") as f:
            binary_hex = f.read().hex()
            if spec_char == None:
                out_file.write(f"{str(binary_hex)}\n")
            else:
                out_file.write(spec_char + str(binary_hex))
        os.remove(filename)
        out_file.write("END:")
def four_char_rotation(data):
    encrypted = ""
    for i in range(0, len(data), 4):
        chunk = data[i:i+4]
        if len(chunk) == 4:
            new_chunk = chunk[3] + chunk[0] + chunk[2] + chunk[1]
            encrypted += new_chunk
        else:
            encrypted += chunk
    return encrypted

def xor_each_byte(data, key):
    res = []
    for i, char in enumerate(data):
        res.append(ord(char) ^ key[i % len(key)])
    return res

if __name__ == "__main__":
    for i in range(55):
        convert_bin_to_hex(f"whelp_{i+1}", f"{i+1}:")
    for i in range(55, 60):
        convert_bin_to_hex(f"twilight_hatchling_{i-54}", f"{i+1}:")
    key = b"FF"
    with open("hexes.txt", "r") as f:
        data = f.read().strip()
    enc1 = four_char_rotation(data)
    enc_final = xor_each_byte(enc1, key)
    hex_output = "".join(f"{b:02x}" for b in enc_final)
    with open('data.txt', 'w') as file:
        file.write(hex_output)

