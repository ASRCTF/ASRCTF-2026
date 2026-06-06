from ff3 import FF3Cipher
ct = "Vu}fm4HZcc7NCIVLERh16zyazi8ZlX"
key_text = "ASRCTFISSOFUNBRO"
key_hex = key_text.encode().hex()

tweak_text = "PLEASEGIVEFLAG"
tweak_hex = tweak_text[:7].encode().hex() 

alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}_"
c = FF3Cipher.withCustomAlphabet(key_hex, tweak_hex, alphabet)

print("Flag:", c.decrypt(ct))

