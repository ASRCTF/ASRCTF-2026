#!/usr/bin/env python3
import random
import time
import re
# pretty print
from pyfiglet import Figlet
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


chances = True
money = 0

def isolate():
    for _ in range(69):
        print("\n")

def banner():
    console = Console()
    ascii_art = r"""
  ___ ___                     .___                          __                       
 /   |   \   ____ _____     __| _/________ _______ ________/  |_  ___________  ______
/    ~    \_/ __ \\__  \   / __ |/ ____/  |  \__  \\_  __ \   __\/ __ \_  __ \/  ___/
\    Y    /\  ___/ / __ \_/ /_/ < <_|  |  |  // __ \|  | \/|  | \  ___/|  | \/\___ \ 
 \___|_  /  \___  >____  /\____ |\__   |____/(____  /__|   |__|  \___  >__|  /____  >
       \/       \/     \/      \/   |__|          \/                 \/           \/ 
.____                 .__                                                            
|    |    ____   ____ |__| ____                                                      
|    |   /  _ \ / ___\|  |/    \                                                     
|    |__(  <_> ) /_/  >  |   |  \                                                    
|_______ \____/\___  /|__|___|  /                                                    
        \/    /_____/         \/   
"""
    console.print(Text(ascii_art, style="bold #00FF00 on black"))

def menu():
    console = Console()
    lines = [
        "┃       [1] - Login       ┃",
        "┃       [2] - Exit        ┃"
    ]

    top = "┏" + "━" * 25 + "┓"
    bottom = "┗" + "━" * 25 + "┛"

    console.print(Text(top, style="orange1"))
    for line in lines:
        console.print(Text(line, style="orange1"))
    console.print(Text(bottom, style="orange1"))

def login():
    isolate()
    console = Console()
    lines = [
        "┃       [*] Our security system is flawless! We've been hacked 0 times!      ┃"
    ]
    top = "┏" + "━" * 76 + "┓"
    bottom = "┗" + "━" * 76 + "┛"
    console.print(Text(top, style="green1"))
    for line in lines:
        console.print(Text(line, style="green1"))
    console.print(Text(bottom, style="green1"))
    loginid = console.input("[bold blue]LoginID[/bold blue]> ")
    password = console.input("[bold blue]Password[/bold blue]> ")
    if loginid == "bob" and password == "123":
        user()
    else:
        default(loginid)

def default(username):
    isolate()
    global loginid
    console = Console()
    check = False
    while not check:
        console.print(r"""[bold dark_orange]
 ____ ___                                                  
|    |   \______ ___________  ___________     ____   ____  
|    |   /  ___// __ \_  __ \ \____ \__  \   / ___\_/ __ \ 
|    |  /\___ \\  ___/|  | \/ |  |_> > __ \_/ /_/  >  ___/ 
|______//____  >\___  >__|    |   __(____  /\___  / \___  >
             \/     \/        |__|       \//_____/      \/ 
        [/bold dark_orange]""")
        console.print(f"[bold blue]Welcome {username}![/bold blue]")
        lines = [
            "┃       [1] - Deposit            ┃",
            "┃       [2] - Tell me a joke     ┃",
            "┃       [3] - Exit               ┃"
        ]
        top = "┏" + "━" * 32 + "┓"
        bottom = "┗" + "━" * 32 + "┛"
        console.print(Text(top, style="orange1"))
        for line in lines:
            console.print(Text(line, style="orange1"))
        console.print(Text(bottom, style="orange1"))
        choice = console.input("[bold blue]> [/bold blue]")
        if choice == "1":
            isolate()
            ascii_art = r"""
_______________________________ ________ __________     _____  _______      _____  
\_   _____/\______   \______   \\_____  \\______   \   /  |  | \   _  \    /  |  | 
 |    __)_  |       _/|       _/ /   |   \|       _/  /   |  |_/  /_\  \  /   |  |_
 |        \ |    |   \|    |   \/    |    \    |   \ /    ^   /\  \_/   \/    ^   /
/_______  / |____|_  /|____|_  /\_______  /____|_  / \____   |  \_____  /\____   | 
        \/         \/        \/         \/       \/       |__|        \/      |__| 
"""

            console.print(ascii_art, style="bold red", markup=False)
            console.print("[bold red][!] Sorry, this function isn't available")
            input()
            isolate()
        elif choice == "2":
            isolate()
            console.print("[bold red][!] What kind of prata is sold at Changi Airport?[/bold red]")
            guess = console.input("[bold blue]> [/bold blue]")
            if guess.strip().lower() == "plain":
                console.print("[bold red][!] You've heard this joke before... haven't you?[/bold red]")
                with open("flag.txt","r") as file:
                    exit(0)
            console.print("[bold red][!] Plain! [/bold red]")
            input()
            isolate()
        else:
            console.print("[bold orange1][(:] Have a nice day![/bold orange1]")
            exit(0)

def user():
    isolate()
    global money
    console = Console()
    check = False 
    isolate()
    money = 0
    while not check:
        console.print(r"""[bold dark_orange]
 ____ ___                                                  
|    |   \______ ___________  ___________     ____   ____  
|    |   /  ___// __ \_  __ \ \____ \__  \   / ___\_/ __ \ 
|    |  /\___ \\  ___/|  | \/ |  |_> > __ \_/ /_/  >  ___/ 
|______//____  >\___  >__|    |   __(____  /\___  / \___  >
             \/     \/        |__|       \//_____/      \/ 
        [/bold dark_orange]""")
        console.print(f"[bold blue]Welcome Bob![/bold blue]")
        lines = [
            "┃       [1] - Deposit money      ┃",
            "┃       [2] - Shop               ┃",
            "┃       [3] - Exit               ┃"
        ]
        top = "┏" + "━" * 32 + "┓"
        bottom = "┗" + "━" * 32 + "┛"
        console.print(Text(top, style="orange1"))
        for line in lines:
            console.print(Text(line, style="orange1"))
        console.print(Text(bottom, style="orange1"))
        choice = console.input("[bold blue]> [/bold blue]")
        if choice == "1":
            money = earn(money)
        elif choice == "2":
            money = shop(money)
        else:
            console.print("[bold orange1][(:] Have a nice day![/bold orange1]")
            exit(0)

def earn(amt):
    global chances
    earned = amt
    stop = False
    isolate()
    if not chances:
        return console.print(f"[bold red][!] You have no more roll chances left![/bold red]")
    times = 0
    lines = [
        "┃       [?] You've entered the secret casino!      ┃"
    ]
    top = "┏" + "━" * 50 + "┓"
    bottom = "┗" + "━" * 50 + "┛"
    console.print(Text(top, style="green1"))
    for line in lines:
        console.print(Text(line, style="green1"))
    console.print(Text(bottom, style="green1"))
    print(r"""
...................................................................................=***=............
..................................................................................+*+***#...........
..................................................................................******#:..........
............:-------------------------------------------------------------------..:*###*:...........
...........--=+*#***********************************************************#*+--:..:=:.............
...........--+#=::::::::::::::::::+#*::::::::::::::::::-##-::::::::::::::::::+#+--...-..............
...........--+*::................:-#=:................::+*::................::*+--...-..............
...........--+*.                  :#-.                 .+*.                  .*+--...-..............
...........--+*.                  :#-                   +*.                  .*+--...-..............
...........--+*.  :+++++++++++=.. :#-  .-+++++++++++=.  +*. .:++++++++++++.  .*+--------............
...........--+*.  -*###########:. :#-  .+*##########*.  +*. .=*##########%:  .*+----=-+--...........
...........--+*.  -*###########:. :#-  .+*##########*.  +*. .=*##########%:  .*+----+=+--...........
...........--+*.  -*###%#*###%=.  :#-  .+*###%######:.  +*. .=*###%#*####-.  .*+----+=+--...........
...........--+*.  :++*%*#####=..  :#-  .=++##*####%:.   +*. .-++*#*#####=..  .*+---------...........
...........--+*.   .=########.    :#-     +*######=     +*.   .=*######*..   .*+---------...........
...........--+*.   .+*#####%:.    :#-     +#######.     +*.   .++######:     .*+---------...........
...........--+*.   .+*######.     :#-     +######*.     +*.   .+*######.     .*+---------...........
...........--+*.   ..........     :#-     .........     +*.   ..........     .*+--:.................
...........--+*...................:#=...................+*...................:*+--..................
...........--+*:::::::::::::::::::-#=:::::::::::::::::::**::::::::::::::::::::#+--..................
...........--+##-::::::::::::::::=###+:::::::::::::::::*###-::::::::::::::::=#*+--..................
............--=+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=--...................
.............:-----------------------------------------------------------------:.................... 
    """)
    console.print(f"[bold blue]Enter 'roll' to get a random amount from 1 to 1,000,000,000,000[/bold blue]")
    console.print(f"[bold blue]You'll get to roll 4 times before you're out of chances![/bold blue]")
    console.print(f"[bold blue]You ain't gettin' another chance to roll after leaving this place![/bold blue]")
    console.print(f"[bold green1]Heh, good luck![/bold green1]")
    while not stop:
        verification = console.input("[bold blue]> [/bold blue]> ")
        if verification.lower() == "roll":
            if times != 4:
                won = random.randint(1,1000000000000)
                console.print(f"[bold green1] You've earned ${won} [/bold green1]")
                earned += won
                msg = f"You now have ${earned}"
                padding = 4
                width = len(msg) + padding
                top = "┏" + "━" * (width+padding)+ "┓"
                bottom = "┗" + "━" * (width+padding) + "┛"
                lines = [f"┃  {msg.center(width)}  ┃"]
                console.print(Text(top, style="green1"))
                for line in lines:
                    console.print(Text(line, style="green1"))
                console.print(Text(bottom, style="green1"))
                times += 1
            else:
                console.print(f"[bold red][!] You have no more roll chances left![/bold red]")
                chances = False
                return earned
        else:
            chances = False
            console.print(f"[bold red][!] Wrong input! You have no more roll chances left![/bold red]")
            return earned
            

def shop(amt):
    value = amt
    isolate()
    console.print(Text(f"[*] You currently have ${value} \n", style="green1"))
    items = [
    "┃       [1] - Flag ($4,000,000,000,000)      ┃",
    "┃       [2] - Coffee ($2)                    ┃",
    "┃       [3] - Exit                           ┃"
    ]   
    top = "┏" + "━" * 44 + "┓"
    bottom = "┗" + "━" * 44 + "┛"
    console.print(Text(top, style="orange1"))
    for line in items:
        console.print(Text(line, style="orange1"))
    console.print(Text(bottom, style="orange1"))
    choice = console.input("[bold blue]> [/bold blue]")
    try:
        if choice == "1":
            if int(value) > 4000000000000:
                with open("flag.txt", "r") as f:
                    print(f.read().rstrip())
                    print("You got lucky, huh")
            else:
                console.print(Text("Insufficient value!", style="red"))
                return value
        elif choice == "2":
            if int(value) > 2:
                console.print(Text("You've earned a coffee!", style="green"))
                print(r'''           
                       (
                        )     (
                 ___...(-------)-....___
             .-""       )    (          ""-.
       .-'``'|-._             )         _.-|
      /  .--.|   `""---...........---""`   |
     /  /    |                             |
     |  |    |                             |
      \  \   |                             |
       `\ `\ |                             |
         `\ `|                             |
         _/ /\                             /
        (__/  \                           /
     _..---""` \                         /`""---.._
  .-'           \                       /          '-.
 :               `-.__             __.-'              :
 :                  ) ""---...---"" (                 :
  '._               `"--...___...--"`              _.'
    \""--..__                              __..--""/
     '._     """----.....______.....----"""     _.'
        `""--..,,_____            _____,,..--""`
                      `"""----"""`
                    ''')
                return (value - 2)
            else:
                console.print(Text("Insufficient value!", style="red"))
                value -= 2
                console.print(Text(f"[*] You currently have ${value} \n", style="green1"))
                return value
        else:
            return value
    except TypeError:
        one_bullet()

def one_bullet():
    console = Console()
    isolate()
    msg = f"[!] Prove youerself worthy"
    padding = 4
    width = len(msg) + padding
    top = "┏" + "━" * (width+padding)+ "┓"
    bottom = "┗" + "━" * (width+padding) + "┛"
    lines = [f"┃  {msg.center(width)}  ┃"]
    console.print(Text(top, style="red"))
    for line in lines:
        console.print(Text(line, style="red"))
    console.print(Text(bottom, style="red"))
    console.print(r"""[blue]

                              ...                                                         ...-++.   
                             .**+*+:......................                         ...:-+++++++++.  
                          ... :*+==============+++++++++++++=====================================:  
                     ..  .++:.=+++*%######**********:::::::-***********++++++*****++++++*******++*..
                 .=++++:.=+**=+**=+****##*=====-----*++++++=--=*-------------------------=*=======*:
                       .+**++****-+=:::::::::::-----##======--=--------------------===============*:
                       .-+=*****+--:....-=----------#+%%###+------------------:-======------:::::.. 
                    .:++++++*++++-#+****************%+%#**#*+================++.                    
               .====++++-:-===+-+=%-----=*++++++++==%+%##*#*=--:-::----::---=+.                     
              .+#*****+*:::-=+**+**+--------========#+##***+-----------------                       
              .=+*####******#*****+++++++===========*#####+.                                        
              .=+****###***=++=-=*++:::.............:*+==-.                                         
             .:==*#******#**=+*+*+=.   ............ .=....                                          
            .-+==+#*++++++#***+=*+*++++++++++++**++**#---:                                          
          ..====++*#*+++==+##*=++++#####:..:-+*=+**++====:                                          
          .====+++++##*++++##***+. ..:*+.    ..++=.                                                 
        .:=====+++++++***+*##%*+.     -*.      .*.                                                  
       .:=+++*++++*********###%+.      =+.     .+.                                                  
      .:=+++++++*+****##*****##+.       .--....-=.                                                  
      .++++++++**+***##*=.  .. :=.      .:+**#*-.                                                   
     .=+=+*+*+*+*****#*:.       .=----+##**+=..                                                     
     -+++*++#*+*****##*.           .:---:..                                                         
   ..+*+++==*******###-.                                                                            
   .:+++**+*#****#*###:.                                                                            
   .+*+**********####*..                                                                            
  ..+++**********####*.                                                                             
  .=*+*********#*#####.                                                                             
 .:++++********###*###.                                                                             
 .++++++*+******######:.                                                                            
.-+==+++++++*****#####-.                                                                            
:++=++++++********####+.                                                                            
.:=++**********++====:.                                                                             
                              
    [/blue]""")
    console.print("[green1]Note from the previous developer:[/green1]")
    print('\n')
    items = [
    "┃To those that have made it this far,                                                      ┃",
    "┃                                                                                          ┃",
    "┃It must be done. The company has foolishly decided to pay us developers poorly as they    ┃",
    "┃prefer the weight of dolla' bills in their own lined pockets. Since none of the other poor┃",
    "┃souls at the company have any idea to read or write code (heck, they don't even have this ┃",
    "┃source code), as an act of revenge. I've made this account just so you can take a shot at ┃",
    "┃them. So if you have something you wanna know hidden in the system files, go on, take the ┃",
    "┃shot. If you succeed, your efforts just might be highly rewarded.                         ┃",
    "┃                                                                                          ┃",
    "┃Yours sincerely,                                                                          ┃",
    "┃'Bob'                                                                                     ┃",
    ]   
    top = "┏" + "━" * 90 + "┓"
    bottom = "┗" + "━" * 90 + "┛"
    console.print(Text(top, style="green1"))
    for line in items:
        console.print(Text(line, style="green1"))
    console.print(Text(bottom, style="green1"))
    user_trial = console.input("[bold blue]Take your shot> [/bold blue]")
    banned = "import|chr|os|sys|system|builtin|exec|eval|subprocess|pty|popen|read|get_data|globals|[|]|k|interact|open|getattr|flag"
    test = lambda word: re.compile(f"({word})", re.IGNORECASE).search
    try:
        console.print("[bold blue][*] Let's see if your shot missed[bold blue]")
        time.sleep(2)
        console.print("[bold blue][*]...[bold blue]")
        time.sleep(1.5)
        groups = [user_trial[i:i+3] for i in range(0, len(user_trial), 3)]
        stripped_groups = [num.lstrip('0') or '0' for num in groups]
        bullet = [chr(int(num)) for num in stripped_groups]
        check = test(banned)(''.join(bullet).replace("__", ""))
        if check:
            console.print("[bold red][!] A faulty bullet... We don't want that [/bold red]")
            exit(0)
        else:
            console.print("[bold blue][*]..[bold blue]")
            time.sleep(1)
            clean_bullet = ''.join(bullet)
            console.print("[bold blue][*].[bold blue]")
            time.sleep(0.5)
            eval(clean_bullet)
    except Exception as e:
        console.print("[bold red][!] A miss. Truly unfortunate. [/bold red]")
        exit(0)
    

if __name__ == "__main__":
    console = Console()
    while (1):
        isolate()
        banner()
        menu()
        choice = console.input("[bold blue]> [/bold blue]")
        if choice == "1":
            login()
        elif choice == "2":
            console.print("[bold orange1][(:] Have a nice day![/bold orange1]")
            exit(0)
        else:
            exit(0)
