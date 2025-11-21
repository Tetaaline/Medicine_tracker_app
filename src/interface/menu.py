#Importing colorama for colored output in the terminal
from colorama import Fore, Style
#Function to print colored headerin the terminal
def print_header(title):
    print('\n' + Fore.LIGHTBLUE_EX + '='*60 + Style.RESET_ALL)
    print(Fore.LIGHTYELLOW_EX + title + Style.RESET_ALL)
    print(Fore.LIGHTBLUE_EX + '='*60 + Style.RESET_ALL)

