#include <stdlib.h>
#include <stdio.h>
#include <string.h>


    int func_0(char input){
        if ('N' == input){
            return 0;
        }
        return 1;
    }
    

    int func_1(char input){
        if ('o' == input){
            return 0;
        }
        return 1;
    }
    

    int func_2(char input){
        if ('p' == input){
            return 0;
        }
        return 1;
    }
    

    int func_3(char input){
        if ('e' == input){
            return 0;
        }
        return 1;
    }
    

    int func_4(char input){
        if (',' == input){
            return 0;
        }
        return 1;
    }
    

    int func_5(char input){
        if (' ' == input){
            return 0;
        }
        return 1;
    }
    

    int func_6(char input){
        if ('n' == input){
            return 0;
        }
        return 1;
    }
    

    int func_7(char input){
        if ('o' == input){
            return 0;
        }
        return 1;
    }
    

    int func_8(char input){
        if (' ' == input){
            return 0;
        }
        return 1;
    }
    

    int func_9(char input){
        if ('f' == input){
            return 0;
        }
        return 1;
    }
    

    int func_10(char input){
        if ('l' == input){
            return 0;
        }
        return 1;
    }
    

    int func_11(char input){
        if ('a' == input){
            return 0;
        }
        return 1;
    }
    

    int func_12(char input){
        if ('g' == input){
            return 0;
        }
        return 1;
    }
    

    int func_13(char input){
        if (' ' == input){
            return 0;
        }
        return 1;
    }
    

    int func_14(char input){
        if ('h' == input){
            return 0;
        }
        return 1;
    }
    

    int func_15(char input){
        if ('e' == input){
            return 0;
        }
        return 1;
    }
    

    int func_16(char input){
        if ('r' == input){
            return 0;
        }
        return 1;
    }
    

    int func_17(char input){
        if ('e' == input){
            return 0;
        }
        return 1;
    }
    

int main(){
    char inp[19];
    printf(">");
    
    int (*functions[])(char) = {
        func_0, func_1, func_2, func_3, func_4, func_5, 
        func_6, func_7, func_8, func_9, func_10, func_11, 
        func_12, func_13, func_14, func_15, func_16, func_17
    };
    int num_funcs = sizeof(functions) / sizeof(functions[0]);

    fgets(inp, sizeof(inp), stdin);
    inp[strcspn(inp, "\n")] = '\0';
    if (strlen(inp) != 18){
        return 0;
    }

    for (int i=0; i<num_funcs; i++){
        if (functions[i](inp[i]) != 0){
            return 0;
        }
    }
    printf("you already the knew the flag ain't here lmao");
    return 0;
}
