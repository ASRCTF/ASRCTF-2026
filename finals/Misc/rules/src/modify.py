#writing this shit felt like an A level 3m computing task fsr
mod_txt = ""
with open("rules.txt", "r") as file:
    for line in file:
        mod_txt += line.rstrip().lower() + '\n'

key = "ASRCTFISSOFUNBRO"
idx = 0
what_thefuck = ""
for char in mod_txt:
    try:
        if char == key[idx].lower():
            what_thefuck += char.upper()
            idx += 1
        else:
            what_thefuck += char
    except IndexError:
        what_thefuck += char.lower()

with open("RULES.txt", "w") as file:
    file.write(what_thefuck)
