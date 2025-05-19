from utils import print_logo, print_menu
from account_info import display_account_info
from resetter import run_cursor_resetter
from constants import EMOJI
from colorama import Fore, Style

def main():
    print_logo()
    while True:
        display_account_info()
        print_menu()

        try:
            choice = input(f"\n{EMOJI['ARROW']} {Fore.CYAN}Enter your choice (0-1): {Style.RESET_ALL}")

            if choice == "1":
                run_cursor_resetter()
                input(f"\n{Fore.GREEN}Press Enter to return to menu...{Style.RESET_ALL}")
            elif choice == "0":
                print(f"\n{Fore.CYAN}Goodbye!{Style.RESET_ALL}")
                break
            else:
                print(f"\n{Fore.RED}{EMOJI['ERROR']} Invalid choice. Please try again.{Style.RESET_ALL}")
                input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n{Fore.CYAN}Goodbye!{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Error: {str(e)}{Style.RESET_ALL}")
            input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
