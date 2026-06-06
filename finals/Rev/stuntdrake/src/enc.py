import random



with open("flag.txt", "r") as f:
    flag = f.read().strip()
    print(flag)

for i in range(len(flag)):
    print(i, flag[i])

ops = ["+", "-"]
to_write = []
for _ in range(55):
    chosen = []
    eqn = ""
    flag_idx_eqn = ""
    for _ in range(len(flag)):
        rand_idx = random.randint(0, len(flag)-1)
        op = random.choice(ops)
        part = str(ord(flag[rand_idx].strip())) + op.strip()
        flag_idx_eqn += f"c[{rand_idx}]" + op.strip()
        eqn += part
    eqn = eqn[:-1]
    res = eval(eqn)
    flag_idx_eqn = flag_idx_eqn[:-1] + "=" + str(res)
    print(flag_idx_eqn)
    to_write.append(flag_idx_eqn)
with open("eqn.txt", "w") as f:
    for line in to_write:
        f.write(line + "\n")




