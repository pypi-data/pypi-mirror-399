from colorama import Fore, init
init(autoreset=True)

ASCII_ART = f"""{Fore.GREEN}
                             _____       
___  _______    ________ ___/ ____\\__.__.
\\  \\/ /\\__  \\  /  ___/  |  \\   __<   |  |
 \\   /  / __ \\_\\___ \\|  |  /|  |  \\___  |
  \\_/  (____  /____  >____/ |__|  / ____|
            \\/     \\/             \\/     
"""

def main():
    # ASCII LOGO
    print(ASCII_ART)

    # ABOUT SECTION
    print(f"{Fore.LIGHTCYAN_EX}💫 ABOUT VASU\n")

    print(f"{Fore.WHITE}• Created with 💚 by {Fore.LIGHTGREEN_EX}Vasu{Fore.WHITE}.")
    print(f"{Fore.WHITE}• {Fore.LIGHTMAGENTA_EX}vasufy{Fore.WHITE} simply means "
          f"{Fore.LIGHTYELLOW_EX}'Vasu things'{Fore.WHITE}.")
    print(f"{Fore.WHITE}• Random ideas, clean logic, fun experiments — all simplified ✨")
    print(f"{Fore.WHITE}• Built when curiosity wins over sleep 😴 → 💻")
    print(f"{Fore.WHITE}• Not perfect. Not fancy. Just fun codes 🤍")
    print(f"{Fore.WHITE}• If it works — celebrate 🎉 | If it breaks — learn & laugh 😄\n")

    # ASSLI FOOTER
    print(f"{Fore.LIGHTGREEN_EX}✨ Vasufy — vasu things, simplified")
    print(f"{Fore.LIGHTCYAN_EX}💡 Made with curiosity, not pressure 😄")
    print(f"{Fore.GREEN}📨 Telegram channel: {Fore.YELLOW}@vasufy {Fore.LIGHTGREEN_EX}(say hi 👋😄)")
if __name__ == "__main__":
    main()
