from colorama import Fore, Style, init

init(autoreset=True)

RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
BLUE = Fore.BLUE
RESET = Style.RESET_ALL

def colorize(text, color):
    return f"{color}{text}{RESET}"
