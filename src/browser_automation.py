import random
import string
import time
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
    print(f"\n{Fore.YELLOW}{EMOJI['BROWSER']} Browser window will remain open for manual interaction.{Style.RESET_ALL}")
    input(f"{Fore.YELLOW}{EMOJI['BACK']} Press Enter to return to menu...{Style.RESET_ALL}")
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
    global _browser_process_ids
    
    try:
        browser_type = 'chrome'
        browser_path = utils_get_default_browser_path(browser_type)

        if not browser_path or not os.path.exists(browser_path):
            print(f"{Fore.YELLOW}{EMOJI['WARNING']}  Chrome browser not found. Trying to find Edge browser...{Style.RESET_ALL}")
            browser_type = 'edge'
            browser_path = utils_get_default_browser_path(browser_type)

        if not browser_path or not os.path.exists(browser_path):
            print(f"{Fore.YELLOW}{EMOJI['WARNING']}  Edge browser not found. Trying to find Brave browser...{Style.RESET_ALL}")
            browser_type = 'brave'
            browser_path = utils_get_default_browser_path(browser_type)

        if not browser_path or not os.path.exists(browser_path):
            print(f"{Fore.RED}{EMOJI['ERROR']} Could not find a supported browser (Chrome, Edge, or Brave).{Style.RESET_ALL}")
            raise Exception("No supported browser found.")

        print(f"{Fore.CYAN}{EMOJI['BROWSER']} Using {browser_type} browser from: {browser_path}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{EMOJI['RUN']} Starting browser...{Style.RESET_ALL}")
        
        before_pids = []
        try:
            import psutil
            browser_process_names = {
                'chrome': ['chrome', 'chromium'],
                'edge': ['msedge', 'edge'],
                'brave': ['brave', 'brave-browser']
            }
            process_names = browser_process_names.get(browser_type, ['chrome'])
            before_pids = [p.pid for p in psutil.process_iter() if any(name in p.name().lower() for name in process_names)]
        except ImportError:
            print(f"{Fore.YELLOW}{EMOJI['WARNING']} psutil not installed. Cannot track browser processes for cleanup. Please run 'pip install psutil'{Style.RESET_ALL}")
        except Exception:
            pass

        co = ChromiumOptions()
        co.set_browser_path(browser_path)
        co.set_argument("--incognito")

        if sys.platform == "linux":
            co.set_argument("--no-sandbox")
            
        co.auto_port()
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
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} Could not detect new {browser_type} processes to track.{Style.RESET_ALL}")
        except ImportError:
            pass
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} Could not track {browser_type} processes due to an error: {e}{Style.RESET_ALL}")

        page.get(url)

        return page

    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} Error setting up browser: {str(e)}{Style.RESET_ALL}")
        raise

def create_cursor_account():
    """Create a Cursor account"""    
    # Get email from user
    while True:
        email = input(f"{Fore.CYAN}\n{EMOJI['EMAIL']} Please enter your email: {Style.RESET_ALL}")
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
        cursor_login_url = input(f"{Fore.CYAN}\n{EMOJI['BROWSER']} Please enter your cursor login url (Right Click to Sign In button on Cursor app and copy url address then paste it here): {Style.RESET_ALL}")
        if not cursor_login_url:
            print(f"{Fore.RED}{EMOJI['ERROR']} Cursor login url is required{Style.RESET_ALL}")
            continue
        elif not re.match(r'^https://(www\.)?cursor\.com/loginDeepControl', cursor_login_url):
            print(f"{Fore.RED}{EMOJI['ERROR']} Invalid cursor login url{Style.RESET_ALL}")
            continue
        else:
            break

    print(f"\n{Fore.CYAN}{EMOJI['BROWSER']} Opening private browser session...{Style.RESET_ALL}")

    try:
        # Get a new browser page
        print(f"{Fore.CYAN}\n{EMOJI['BROWSER']} Navigating to Cursor login page...{Style.RESET_ALL}")
        page = get_browser(cursor_login_url)
        
        # Wait for page to load
        time.sleep(get_random_wait_time())

        # Click on sign in button
        sign_up_button = page.ele('tag:a@class=rt-Text BrandedLink rt-reset')
        if sign_up_button:
            sign_up_button.click(by_js=True)
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Clicked sign up button{Style.RESET_ALL}")
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
        print(f"{Fore.CYAN}\n{EMOJI['FORM']} Filling signup form...{Style.RESET_ALL}")
        
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
        
        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Form submitted successfully{Style.RESET_ALL}")
        
        # Wait for password field
        time.sleep(3)
        
        # Fill password
        print(f"{Fore.CYAN}\n{EMOJI['FORM']} Setting password...{Style.RESET_ALL}")
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
            f.write(f"Name: {user['first_name']} {user['last_name']} | Email: {email} | Password: {user['password']} | Created at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        print(f"\n{Fore.GREEN}{EMOJI['SUCCESS']} Account information saved to cursor_accounts.txt{Style.RESET_ALL}")
        
        # Wait for manual verification code input
        print(f"\n{Fore.YELLOW}{EMOJI['WARNING']} Please check the email for verification code and enter it manually.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{EMOJI['WARNING']} The browser will remain open for continue steps with manual interaction.{Style.RESET_ALL}")
        return True
        
    except Exception as e:
        print(f"\n{Fore.RED}{EMOJI['ERROR']} Error: {str(e)}{Style.RESET_ALL}")
        return False