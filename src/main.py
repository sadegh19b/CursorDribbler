from utils import print_logo, print_menu
from account_info import display_account_info
from resetter import run_cursor_resetter
from browser_automation import create_cursor_account
from temp_mail_sites import display_temp_email_sites
from constants import EMOJI, APP_NAME, VERSION
from colorama import Fore, Style
import os

def main():
    # Set console title with version
    os.system(f"title {APP_NAME} {VERSION}")
    
    print_logo()
    while True:
        display_account_info()
        print_menu()

        try:
            choice = input(f"\n{EMOJI['ARROW']} {Fore.CYAN}Enter your choice (0-3): {Style.RESET_ALL}")

            if choice == "1":
                run_cursor_resetter()
                input(f"\n{Fore.GREEN}{EMOJI['BACK']} Press Enter to return to menu...{Style.RESET_ALL}")
            elif choice == "2":
                create_cursor_account()
                input(f"\n{Fore.GREEN}{EMOJI['BACK']} Press Enter to return to menu...{Style.RESET_ALL}")
            elif choice == "3":
                display_temp_email_sites()
                input(f"\n{Fore.GREEN}{EMOJI['BACK']} Press Enter to return to menu...{Style.RESET_ALL}")
            elif choice == "0":
                print(f"\n{Fore.CYAN}Goodbye!{Style.RESET_ALL}")
                break
            else:
                print(f"\n{Fore.RED}{EMOJI['ERROR']} Invalid choice. Please try again.{Style.RESET_ALL}")
                input(f"\n{Fore.GREEN}{EMOJI['BACK']} Press Enter to continue...{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n{Fore.CYAN}Goodbye!{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Error: {str(e)}{Style.RESET_ALL}")
            input(f"\n{Fore.GREEN}{EMOJI['BACK']} Press Enter to continue...{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
