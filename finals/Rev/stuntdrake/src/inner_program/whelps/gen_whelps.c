#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>

void gen_whelp(char *eqn, int idx) {
    FILE *fptr;
    char bin_name[32];
    char filename[32];
    char contents[512];
    char compile_cmd[128];
    char run_cmd[64];
    char del_cmd[100];

    snprintf(bin_name, sizeof(bin_name), "whelp_%d", idx + 1);
    snprintf(filename, sizeof(filename), "whelp_%d.c", idx + 1);
    
    snprintf(contents, sizeof(contents), 
             "#include <unistd.h>\nchar eqn[600] = \"%s\";\nint main(){ sleep(2); return 0; }", 
             eqn);

    fptr = fopen(filename, "w");
    if (fptr == NULL) return;
    fprintf(fptr, "%s", contents);
    fclose(fptr);

    snprintf(compile_cmd, sizeof(compile_cmd), "gcc %s -o %s -s", filename, bin_name);
    system(compile_cmd);
    sleep(0.1);
    snprintf(del_cmd, sizeof(del_cmd), "rm -rf %s", filename);
    system(del_cmd);

}

int main(){
    FILE  *fptr;
    char line[500];
    int i=0;

    fptr = fopen("eqn.txt", "r");
    if (fptr == NULL){
        printf("eqn.txt file not found");
        return 0;
    }
    while (fgets(line, sizeof(line), fptr)){
        line[strcspn(line, "\n")] = 0;
        if (strlen(line)>0){
            printf("Spawning whelp %d with eqn: %s\n", i+1, line);
            gen_whelp(line, i);
            i++;
        }
    }
    fclose(fptr);
    return 0;
}
