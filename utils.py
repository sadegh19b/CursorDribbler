from constants import EMOJI, APP_NAME, VERSION
from colorama import Fore, Style

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
    print(f"{Fore.GREEN}1{Style.RESET_ALL}. {EMOJI['RUN']} Run Cursor Resetter")
    print(f"{Fore.GREEN}0{Style.RESET_ALL}. {EMOJI['ERROR']} Exit")
    print(f"{Fore.YELLOW}{'─' * 50}{Style.RESET_ALL}")
