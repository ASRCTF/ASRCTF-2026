final_funcs = ""
string = "Nope, no flag here"
for i in range(len(string)):
    temp = f"""
    int func_{i}(char input){{
        if ('{string[i]}' == input){{
            return 0;
        }}
        return 1;
    }}
    """
    final_funcs += temp + "\n"

print(final_funcs)
