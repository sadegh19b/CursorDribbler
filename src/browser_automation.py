import random
import string
import time
import pyperclip
from DrissionPage import ChromiumPage, ChromiumOptions
from colorama import Fore, Style
from constants import EMOJI
import re
import os
import requests
import signal
import sys
from utils import get_default_browser_path as utils_get_default_browser_path

_chrome_process_ids = []

def cleanup_chrome_processes():
    """Clean only Chrome processes launched by this script"""
    global _chrome_process_ids
    
    if not _chrome_process_ids:
        print("\nNo Chrome processes to clean...")
        return
        
    print("\nCleaning Chrome processes launched by this script...")
    try:
        if os.name == 'nt':
            for pid in _chrome_process_ids:
                try:
                    os.system(f'taskkill /F /PID {pid} /T 2>nul')
                except:
                    pass
        else:
            for pid in _chrome_process_ids:
                try:
                    os.kill(pid, signal.SIGTERM)
                except:
                    pass
        _chrome_process_ids = []  # Reset the list after cleanup
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Error cleaning up processes: {str(e)}{Style.RESET_ALL}")

def signal_handler(signum, frame):
    """Handle Ctrl+C signal"""
    print(f"\n{Fore.CYAN}Exit signal received, shutting down...{Style.RESET_ALL}")
    cleanup_chrome_processes()
    os._exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def generate_password(length=12):
    """Generate a random password"""
    return ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=length))

def random_string(length=8):
    """Generate a random string"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_name():
    """Generate a random name"""
    fnames = ["John", "Arthur", "David", "Michael", "William", "James", "Robert", "Charles", "Joseph", "Thomas"]
    lnames = ["Shelby", "Smith", "Johnson", "Williams", "Silva", "Jones", "Garcia", "Miller", "Rodriguez", "Davis"]

    return {'first_name': random.choice(fnames), 'last_name': random.choice(lnames)}

def get_random_user():
    """Generate a random username"""
    randomUserApi = "https://randomuser.me/api/"
    try:
        response = requests.get(randomUserApi)
        data = response.json()
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Error on random user: {str(e)}{Style.RESET_ALL}")
    
    return {
        'first_name': data['results'][0]['name']['first'] if data['results'][0]['name']['first'] else random_name()['first_name'],
        'last_name': data['results'][0]['name']['last'] if data['results'][0]['name']['last'] else random_name()['last_name'],
        'username': data['results'][0]['login']['username'] if data['results'][0]['login']['username'] else random_string(),
        'password': generate_password(),
    }

def manual_interaction(page):
    """Keep browser open for manual interaction"""
    print(f"\n{Fore.YELLOW}Browser window will remain open for manual interaction.{Style.RESET_ALL}")
    input(f"{Fore.YELLOW}Press Enter to return to menu...{Style.RESET_ALL}")
    return False

def get_random_wait_time():
    """
    Get random wait time
    Returns:
        float: Random wait time
    """
    return random.uniform(0.1, 0.8)

def get_browser(url):
    """Setup browser driver"""
    global _chrome_process_ids
    
    try:
        browser_type = 'chrome'
        browser_path = utils_get_default_browser_path(browser_type)
        
        if not browser_path or not os.path.exists(browser_path):
            print(f"{Fore.YELLOW}⚠️  Chrome browser not found. Trying to find Edge browser...{Style.RESET_ALL}")
            browser_type = 'edge'
            browser_path = utils_get_default_browser_path(browser_type)

        if not browser_path or not os.path.exists(browser_path):
            print(f"{Fore.YELLOW}⚠️  Edge browser not found. Trying to find Brave browser...{Style.RESET_ALL}")
            browser_type = 'brave'
            browser_path = utils_get_default_browser_path(browser_type)

        if not browser_path or not os.path.exists(browser_path):
            print(f"{Fore.RED}{EMOJI['ERROR']} Could not find a supported browser (Chrome, Edge, or Brave).{Style.RESET_ALL}")
            raise Exception("No supported browser found.")

        co = ChromiumOptions()
        co.set_browser_path(browser_path)
        co.set_argument("--incognito")

        if sys.platform == "linux":
            co.set_argument("--no-sandbox")
            
        co.auto_port()
        co.headless(False)
        
        print(f"{Fore.CYAN}🌐 Using {browser_type} browser from: {browser_path}{Style.RESET_ALL}")
        
        try:
            extension_path = os.path.join(os.getcwd(), "turnstilePatch")
            if os.path.exists(extension_path):
                co.set_argument("--allow-extensions-in-incognito")
                co.add_extension(extension_path)
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Error loading extension: {str(e)}{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}🚀 Starting browser...{Style.RESET_ALL}")
        
        before_pids = []
        try:
            import psutil
            browser_process_names = {
                'chrome': ['chrome', 'chromium'],
                'edge': ['msedge', 'edge'],
                'firefox': ['firefox'],
                'brave': ['brave', 'brave-browser']
            }
            process_names = browser_process_names.get(browser_type, ['chrome'])
            before_pids = [p.pid for p in psutil.process_iter() if any(name in p.name().lower() for name in process_names)]
        except ImportError:
            print(f"{Fore.YELLOW}psutil not installed. Cannot track browser processes for cleanup. Please run 'pip install psutil'{Style.RESET_ALL}")
        except Exception:
            pass
            
        page = ChromiumPage(addr_or_opts=co)
        
        time.sleep(1)
        
        try:
            import psutil
            process_names = browser_process_names.get(browser_type, ['chrome'])
            after_pids = [p.pid for p in psutil.process_iter() if any(name in p.name().lower() for name in process_names)]
            new_pids = [pid for pid in after_pids if pid not in before_pids]
            _chrome_process_ids.extend(new_pids)
            
            if _chrome_process_ids:
                print(f"Tracking {len(_chrome_process_ids)} new {browser_type} process(es).")
            else:
                print(f"{Fore.YELLOW}Warning: Could not detect new {browser_type} processes to track.{Style.RESET_ALL}")
        except ImportError:
            pass
        except Exception as e:
            print(f"Could not track {browser_type} processes due to an error: {e}")

        page.get(url)

        return page

    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Error setting up browser: {str(e)}{Style.RESET_ALL}")
        raise

def create_temp_email():
    """Create a temporary email using tmail.dark2web.com"""
    print(f"\n{Fore.CYAN}{EMOJI['BROWSER']} Opening private browser session...{Style.RESET_ALL}")
    
    try:
        # Get a new browser page
        print(f"{Fore.CYAN}Navigating to tmail.dark2web.com...{Style.RESET_ALL}")
        page = get_browser("https://tmail.dark2web.com")

        domains = ["competition.tel", "ministre.rocks"]
        
        # Wait for page to load
        time.sleep(3)

        # First click on Copy button to check if in domains list
        print(f"\n{Fore.CYAN}Looking for Copy button...{Style.RESET_ALL}")
        try:
            copy_button = page.ele('tag:div@text():Copy')
            if copy_button:
                copy_button.click(by_js=True)
                print(f"{Fore.GREEN}The temp email copied in clipboard: {pyperclip.paste()}{Style.RESET_ALL}")
                if pyperclip.paste().split('@')[1] not in domains:
                    print(f"{Fore.RED}{EMOJI['ERROR']} The temp email is not in domains list{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}The temp email copied in clipboard: {pyperclip.paste()}{Style.RESET_ALL}")
                    return True
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} Could not find Copy button{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Error on Copy button: {str(e)}{Style.RESET_ALL}")

        method = input(f"{Fore.CYAN}Choose get temp email method one or method two? (1 or 2)(default 1): {Style.RESET_ALL}") or "1"
        if method == "1":
            while True:
                print(f"\n{Fore.CYAN}Looking for Delete button...{Style.RESET_ALL}")
                try:
                    delete_button = page.ele('tag:div@text():Delete')
                    if delete_button:
                        delete_button.click(by_js=True)
                        print(f"{Fore.GREEN}The temp email deleted to get new one{Style.RESET_ALL}")

                        time.sleep(get_random_wait_time())

                        print(f"\n{Fore.CYAN}Looking for Copy button...{Style.RESET_ALL}")
                        try:
                            copy_button = page.ele('tag:div@text():Copy')
                            if copy_button:
                                copy_button.click(by_js=True)
                                print(f"{Fore.GREEN}The temp email copied in clipboard: {pyperclip.paste()}{Style.RESET_ALL}")
                                if pyperclip.paste().split('@')[1] not in domains:
                                    print(f"{Fore.RED}{EMOJI['ERROR']} The temp email is not in domains list{Style.RESET_ALL}")
                                    time.sleep(get_random_wait_time())
                                    continue
                                else:
                                    print(f"{Fore.GREEN}The temp email copied in clipboard: {pyperclip.paste()}{Style.RESET_ALL}")
                                    break
                            else:
                                print(f"{Fore.RED}{EMOJI['ERROR']} Could not find Copy button{Style.RESET_ALL}")
                        except Exception as e:
                            print(f"{Fore.RED}{EMOJI['ERROR']} Error on Copy button: {str(e)}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}{EMOJI['ERROR']} Could not find Delete button{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}{EMOJI['ERROR']} Error on Delete button: {str(e)}{Style.RESET_ALL}")
        elif method == "2":
            print(f"{Fore.CYAN}Looking for New button...{Style.RESET_ALL}")
            try:
                new_button = page.ele('tag:div@text():New')
                if new_button:
                    #print(f"{Fore.GREEN}Found New button with selector: {new_button}{Style.RESET_ALL}")
                    new_button.click(by_js=True)
                else:
                    print(f"{Fore.RED}{EMOJI['ERROR']} Could not find New button{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} Error on new button: {str(e)}{Style.RESET_ALL}")
                return manual_interaction(page)
            
            # Generate random user
            user = get_random_user()
            print(f"\n{Fore.CYAN}Generating random username: {user['username']}{Style.RESET_ALL}")
            
            time.sleep(get_random_wait_time())
            
            # Try to fill username field
            print(f"\n{Fore.CYAN}Looking for username field...{Style.RESET_ALL}")
            try:
                username_field = page.ele('tag:input@name=user')
                if username_field:
                    username = user['username']
                    #print(f"{Fore.GREEN}Found username field with selector: {username_field}{Style.RESET_ALL}")
                    page.run_js(f'Livewire.find(document.querySelector(\'input[name="user"]\').closest(\'[wire\\\\:id]\').getAttribute(\'wire:id\')).set("user", "{username}");')
                    print(f"{Fore.GREEN}Filled username field: {username}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}{EMOJI['ERROR']} Could not find username field{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} Error on username field: {str(e)}{Style.RESET_ALL}")
                return manual_interaction(page)
            
            time.sleep(get_random_wait_time())
            
            selected_domain = random.choice(domains)
            print(f"\n{Fore.CYAN}Selecting domain: {selected_domain}{Style.RESET_ALL}")
            
            # Try to find and click domain dropdown
            print(f"{Fore.CYAN}Looking for domain dropdown...{Style.RESET_ALL}")
            try:
                domain_dropdown = page.ele('tag:input@name=domain')
                if domain_dropdown:
                    #print(f"{Fore.GREEN}Found domain dropdown with selector: {domain_dropdown}{Style.RESET_ALL}")
                    domain_dropdown.parent().click(by_js=True)
                    print(f"{Fore.GREEN}Clicked domain dropdown{Style.RESET_ALL}")
                else:
                    # Try with placeholder attribute
                    domain_dropdown = page.ele('tag:input@placeholder=Select Domain')
                    if domain_dropdown:
                        #print(f"{Fore.GREEN}Found domain dropdown with placeholder selector: {domain_dropdown}{Style.RESET_ALL}")
                        domain_dropdown.click()
                        print(f"{Fore.GREEN}Clicked domain dropdown{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}{EMOJI['ERROR']} Could not find domain dropdown{Style.RESET_ALL}")
                
                time.sleep(1)
                
                # Try to select domain
                print(f"{Fore.CYAN}Looking for domain option: {selected_domain}{Style.RESET_ALL}")
                try:
                    # Try direct selector
                    domain_option = page.ele(f'tag:a@text():{selected_domain}')
                    if domain_option:
                        #print(f"{Fore.GREEN}Found domain option with selector: {domain_option}{Style.RESET_ALL}")
                        domain_option.click(by_js=True)
                        print(f"{Fore.GREEN}Selected domain {selected_domain}{Style.RESET_ALL}")
                    else:
                        # Try with parent navigation
                        domain_option = domain_dropdown.parent().parent().ele(f'tag:a@text():{selected_domain}')
                        if domain_option:
                            domain_option.click()
                            print(f"{Fore.GREEN}Selected domain {selected_domain} via parent navigation{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.YELLOW}Could not find domain option, trying JavaScript selection{Style.RESET_ALL}")
                            # Try JavaScript selection
                            script = f"""
                            var options = document.querySelectorAll('a');
                            for(var i = 0; i < options.length; i++) {{
                                if(options[i].textContent.includes('{selected_domain}')) {{
                                    options[i].click();
                                    return true;
                                }}
                            }}
                            return false;
                            """
                            result = page.run_js(script)
                            if result:
                                print(f"{Fore.GREEN}Selected domain {selected_domain} via JavaScript{Style.RESET_ALL}")
                            else:
                                print(f"{Fore.RED}{EMOJI['ERROR']} Could not select domain{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}{EMOJI['ERROR']} Error selecting domain: {str(e)}{Style.RESET_ALL}")
                    return manual_interaction(page)
            except Exception as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} Error on domain dropdown: {str(e)}{Style.RESET_ALL}")
                return manual_interaction(page)

            time.sleep(get_random_wait_time())
            
            # Try to find and click Create button
            print(f"\n{Fore.CYAN}Looking for Create button...{Style.RESET_ALL}")
            try:
                create_button = page.ele('tag:input@value=Create')
                if create_button:
                    #print(f"{Fore.GREEN}Found Create button with selector: {create_button}{Style.RESET_ALL}")
                    create_button.click(by_js=True)
                    print(f"{Fore.GREEN}Clicked Create button{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}{EMOJI['ERROR']} Could not find Create button{Style.RESET_ALL}")
                    return manual_interaction(page)
            except Exception as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} Error on Create button: {str(e)}{Style.RESET_ALL}")

            time.sleep(3)

            # Click on Copy button
            print(f"\n{Fore.CYAN}Looking for Copy button...{Style.RESET_ALL}")
            try:
                copy_button = page.ele('tag:div@text():Copy')
                if copy_button:
                    #print(f"{Fore.GREEN}Found Copy button with selector: {copy_button}{Style.RESET_ALL}")
                    copy_button.click(by_js=True)
                    print(f"{Fore.GREEN}The temp email copied in clipboard: {pyperclip.paste()}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}{EMOJI['ERROR']} Could not find Copy button{Style.RESET_ALL}")
                    return manual_interaction(page)
            except Exception as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} Error on Copy button: {str(e)}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}{EMOJI['ERROR']} Invalid method{Style.RESET_ALL}")

        return True
    
    except Exception as e:
        print(f"\n{Fore.RED}{EMOJI['ERROR']} Error: {str(e)}{Style.RESET_ALL}")
        return False 

def create_cursor_account():
    """Create a Cursor account"""
    print(f"\n{Fore.CYAN}{EMOJI['BROWSER']} Opening private browser session...{Style.RESET_ALL}")
    
    # Get email from user
    while True:
        email = input(f"{Fore.CYAN}\nPlease enter your email: {Style.RESET_ALL}")
        if not email:
            print(f"{Fore.RED}{EMOJI['ERROR']} Email is required{Style.RESET_ALL}")
            continue
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            print(f"{Fore.RED}{EMOJI['ERROR']} Invalid email{Style.RESET_ALL}")
            continue
        else:
            break

    # Get cursor login url from user
    while True:
        cursor_login_url = input(f"{Fore.CYAN}\nPlease enter your cursor login url (Right Click to Sign In button on Cursor app and copy url address then paste it here): {Style.RESET_ALL}")
        if not cursor_login_url:
            print(f"{Fore.RED}{EMOJI['ERROR']} Cursor login url is required{Style.RESET_ALL}")
            continue
        elif not re.match(r'^https://(www\.)?cursor\.com/loginDeepControl', cursor_login_url):
            print(f"{Fore.RED}{EMOJI['ERROR']} Invalid cursor login url{Style.RESET_ALL}")
            continue
        else:
            break

    try:
        # Get a new browser page
        print(f"{Fore.CYAN}\nNavigating to Cursor login page...{Style.RESET_ALL}")
        page = get_browser(cursor_login_url)
        
        # Wait for page to load
        time.sleep(get_random_wait_time())

        # Click on sign in button
        sign_up_button = page.ele('tag:a@class=rt-Text BrandedLink rt-reset')
        if sign_up_button:
            sign_up_button.click(by_js=True)
            print(f"{Fore.GREEN}Clicked sign up button{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}{EMOJI['ERROR']} Could not find sign up button{Style.RESET_ALL}")
            return manual_interaction(page)
    
        time.sleep(3)

        # Generate random user information
        user = get_random_user()
        
        print(f"\n{Fore.GREEN}{EMOJI['BASIC']} Generated account information:{Style.RESET_ALL}")
        print(f"First Name: {user['first_name']}")
        print(f"Last Name: {user['last_name']}")
        print(f"Email: {email}")
        print(f"Password: {user['password']}")
        
        # Fill signup form
        print(f"{Fore.CYAN}\nFilling signup form...{Style.RESET_ALL}")
        
        # Fill first name
        first_name_input = page.ele("@name=first_name")
        if first_name_input:
            first_name_input.input(user['first_name'])
            time.sleep(get_random_wait_time())
        
        # Fill last name
        last_name_input = page.ele("@name=last_name")
        if last_name_input:
            last_name_input.input(user['last_name'])
            time.sleep(get_random_wait_time())
        
        # Fill email
        email_input = page.ele("@name=email")
        if email_input:
            email_input.input(email)
            time.sleep(get_random_wait_time())
        
        # Click submit button
        submit_button = page.ele("@type=submit")
        if submit_button:
            submit_button.click()
            time.sleep(get_random_wait_time())
        
        print(f"{Fore.GREEN}Form submitted successfully{Style.RESET_ALL}")
        
        # Wait for password field
        time.sleep(3)
        
        # Fill password
        print(f"{Fore.CYAN}\nSetting password...{Style.RESET_ALL}")
        password_input = page.ele("@name=password")
        if password_input:
            password_input.input(user['password'])
            time.sleep(get_random_wait_time())
            
            # Click submit button
            submit_button = page.ele("@type=submit")
            if submit_button:
                submit_button.click()
                time.sleep(get_random_wait_time())
        
        # Save account information in cursor_accounts.txt
        with open('cursor_accounts.txt', 'a', encoding='utf-8') as f:
            f.write(f"Email: {email} | Password: {user['password']} | Created at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        print(f"\n{Fore.GREEN}{EMOJI['SUCCESS']} Account information saved to cursor_accounts.txt{Style.RESET_ALL}")
        
        # Wait for manual verification code input
        print(f"\n{Fore.YELLOW}Please check the email for verification code and enter it manually.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}The browser will remain open for continue steps with manual interaction.{Style.RESET_ALL}")
        return True
        
    except Exception as e:
        print(f"\n{Fore.RED}{EMOJI['ERROR']} Error: {str(e)}{Style.RESET_ALL}")
        return False