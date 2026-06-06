from ff3 import FF3Cipher

flag = "ASRCTF{1_H4t3_S33_b3hW4_y4NgS}"

key_text = "ASRCTFISSOFUNBRO"
key_hex = key_text.encode().hex()

tweak_text = "PLEASEGIVEFLAG"
tweak_hex = tweak_text[:7].encode().hex() 

alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}_"

c = FF3Cipher.withCustomAlphabet(key_hex, tweak_hex, alphabet)

ct = c.encrypt(flag)

print(f"Ciphertext: {ct}")

dt = c.decrypt(ct)
print(f"Decrypted:  {dt}")
