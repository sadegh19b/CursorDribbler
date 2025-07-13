import sys
import os
import shutil
from constants import EMOJI, APP_NAME, VERSION
from colorama import Fore, Style

def get_default_browser_path(browser_type: str) -> str:
    """Gets the default path for a browser based on the OS."""
    if sys.platform == "win32":
        paths = {
            "firefox": [
                "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe",
                os.path.join(os.path.expanduser("~"), "AppData\\Local\\Mozilla\\Firefox\\firefox.exe"),
            ],
            "chrome": [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                os.path.join(os.path.expanduser("~"), "AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"),
            ],
            "edge": [
                "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
                "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
            ],
            "brave": [
                "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
                os.path.join(os.path.expanduser("~"), "AppData\\Local\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"),
            ],
        }
        for path in paths.get(browser_type, []):
            if os.path.exists(path):
                return path
    elif sys.platform == "darwin":
        paths = {
            "firefox": "/Applications/Firefox.app/Contents/MacOS/firefox",
            "chrome": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "edge": "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "brave": "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        }
        path = paths.get(browser_type)
        if path and os.path.exists(path):
            return path
    else:
        # For Linux and other OS
        return shutil.which(browser_type)
    return None

def print_logo():
    logo = f"""
{Fore.CYAN}
 .+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+. 
(                                                                                                 )
 )                 o__ __o                                                                       ( 
(                 /v     v\                                                                       )
 )               />       <\                                                                     ( 
(              o/              o       o   \o__ __o    __o__   o__ __o    \o__ __o                )
 )            <|              <|>     <|>   |     |>  />  \   /v     v\    |     |>              ( 
(              \\             < >     < >  / \   < >  \o     />       <\  / \   < >               )
 )               \         /   |       |   \o/         v\    \         /  \o/                    ( 
(                 o       o    o       o    |           <\    o       o    |                      )
 )                <\__ __/>    <\__ __/>   / \     _\o__</    <\__ __/>   / \                    ( 
(                                                                                                 )
 )                                                                                               ( 
(                                                                                                 )
 )     o__ __o                    o     o            o            o                              ( 
(     <|     v\                 _<|>_  <|>          <|>          <|>                              )
 )    / \     <\                       / >          / >          / \                             ( 
(     \o/       \o   \o__ __o     o    \o__ __o     \o__ __o     \o/    o__  __o   \o__ __o       )
 )     |         |>   |     |>   <|>    |     v\     |     v\     |    /v      |>   |     |>     ( 
(     / \       //   / \   < >   / \   / \     <\   / \     <\   / \  />      //   / \   < >      )
 )    \o/      /     \o/         \o/   \o/      /   \o/      /   \o/  \o    o/     \o/           ( 
(      |      o       |           |     |      o     |      o     |    v\  /v __o   |             )
 )    / \  __/>      / \         / \   / \  __/>    / \  __/>    / \    <\/> __/>  / \           ( 
(                                                                                                 )
 )                                       {APP_NAME}                                         (
(                                            {VERSION}                                               ) 
 )                                            By SB                                              (
(                                                                                                 ) 
 "+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"+.+"
{Style.RESET_ALL}
"""
    print(logo)

def print_menu():
    print(f"\n{Fore.CYAN}{EMOJI['MENU']} Menu:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'─' * 50}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}1{Style.RESET_ALL}. {EMOJI['RUN']} Cursor Resetter")
    print(f"{Fore.GREEN}2{Style.RESET_ALL}. {EMOJI['ACCOUNT']} Create Cursor Account")
    print(f"{Fore.GREEN}3{Style.RESET_ALL}. {EMOJI['EMAIL']} Display Temp Email Sites")
    print(f"{Fore.GREEN}0{Style.RESET_ALL}. {EMOJI['ERROR']} Exit")
    print(f"{Fore.YELLOW}{'─' * 50}{Style.RESET_ALL}")
