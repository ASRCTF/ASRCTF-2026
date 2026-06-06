const vm = require("vm");

const art = String.raw`
     \                  ###########                  /
      \                  #########                  /
       \                                           /
        \                                         /
         \                                       /
          \                                     /
           \                                   /
            \_________________________________/
            |                                 |
            |                                 |
            |                                 |
            |            _________            |
            |           |         |           |
            |           |   ___   |           |
            |           I  |___|  |           |
            |           |         |           |
            |           |         |           |
            |           |        _|           |
            |           |       |#|           |  ;,
    -- ___  |           |         |           |   ;\'
    H*/   \ |           |         |      _____|    .,\`
    */     )|           I         |     \_____\     ;\'
    /___.,';|           |         |     \\     \     ."\'
    |     ; |___________|_________|______\\     \      ;:
    | ._,'  /                             \\     \      .
    |,'    /                               \\     \
    ||    /                                 \\_____\
    ||   /                                   \_____|
    ||  /              ___________                \
    || /              / =====o    |                \
    ||/              /  |   /-\   |                 \
    //              /   |         |                  \
   //              /    |   ____  |______             \
  //              /    (O) |    | |      \             \
 //              /         |____| |  0    \             \
//              /          o----  |________\             \
/              /                  |     |  |              \
              /                   |        |               \
             /                    |        |              
            /                     |        |
`;

const sandbox = {
    Math,
    Date,
    JSON,
    String,
    Number,
    Boolean,
    Array,
    Object,
    console: {
        log: (...args) => {
            process.stdout.write(args.join(" ") + "\n");
        }
    }
};

Object.freeze(sandbox);

process.stdout.write(art + "\n");
process.stdout.write("Welcome to my NodeJS Jail\n");
process.stdout.write("You will be stuck here for all of eternity unless u figure out how to escape\n");
process.stdout.write("> ");

process.stdin.once("data", (chunk) => {
    const input = chunk.toString().split("\n")[0].trim();
    console.log(input);

    try {
        if (/[a-zA-Z`'"]/i.test(input)) {
            process.stdout.write("Blocked letters\n");
            process.exit(1);
        }

        const context = vm.createContext(sandbox);
        const result = vm.runInContext(input, context, { timeout: 3000 });
        process.stdout.write("Result: " + result + "\n");
    } catch (err) {
        process.stdout.write("Error: " + err.message + "\n");
    }

    process.exit(0);
});