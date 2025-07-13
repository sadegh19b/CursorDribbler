import os
import json
import requests
import sqlite3
import platform
import re
from colorama import Fore, Style, init
from config import Config
from constants import EMOJI

init()

def get_paths():
    """Get Cursor paths based on OS"""
    system = platform.system()
    if system == "Windows":
        appdata = os.getenv("APPDATA")
        return {
            'storage_path': os.path.join(appdata, "Cursor", "User", "globalStorage", "storage.json"),
            'sqlite_path': os.path.join(appdata, "Cursor", "User", "globalStorage", "state.vscdb"),
            'session_path': os.path.join(appdata, "Cursor", "Session Storage")
        }
    elif system == "Darwin":  # macOS
        return {
            'storage_path': os.path.abspath(os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage/storage.json")),
            'sqlite_path': os.path.abspath(os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage/state.vscdb")),
            'session_path': os.path.expanduser("~/Library/Application Support/Cursor/Session Storage")
        }
    elif system == "Linux":
        home = os.path.expanduser("~")
        config_base = os.path.join(home, ".config")
        cursor_dir = None
        possible_paths = [
            os.path.join(config_base, "Cursor"),
            os.path.join(config_base, "cursor")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                cursor_dir = path
                break
        if not cursor_dir:
            return None
        return {
            'storage_path': os.path.abspath(os.path.join(cursor_dir, "User/globalStorage/storage.json")),
            'sqlite_path': os.path.abspath(os.path.join(cursor_dir, "User/globalStorage/state.vscdb")),
            'session_path': os.path.join(cursor_dir, "Session Storage")
        }
    return None

def get_token():
    """Get Cursor token"""
    paths = get_paths()
    if not paths:
        return None
    # Try to get token from storage.json
    if os.path.exists(paths['storage_path']):
        try:
            with open(paths['storage_path'], 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'cursorAuth/accessToken' in data:
                    return data['cursorAuth/accessToken']
                for key in data:
                    if 'token' in key.lower() and isinstance(data[key], str) and len(data[key]) > 20:
                        return data[key]
        except:
            pass
    # Try to get token from sqlite
    if 'sqlite_path' in paths and os.path.exists(paths['sqlite_path']):
        try:
            conn = sqlite3.connect(paths['sqlite_path'])
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM ItemTable WHERE key LIKE '%token%'")
            rows = cursor.fetchall()
            conn.close()
            for row in rows:
                try:
                    value = row[0]
                    if isinstance(value, str) and len(value) > 20:
                        return value
                    data = json.loads(value)
                    if isinstance(data, dict) and 'token' in data:
                        return data['token']
                except:
                    continue
        except:
            pass
    # Try to get token from session files
    if os.path.exists(paths['session_path']):
        try:
            for file in os.listdir(paths['session_path']):
                if file.endswith('.log'):
                    file_path = os.path.join(paths['session_path'], file)
                    try:
                        with open(file_path, 'rb') as f:
                            content = f.read().decode('utf-8', errors='ignore')
                            token_match = re.search(r'"token":"([^"]+)"', content)
                            if token_match:
                                return token_match.group(1)
                    except:
                        continue
        except:
            pass
    return None

def get_email(storage_path, sqlite_path=None):
    """Get email from storage.json or sqlite database"""
    if os.path.exists(storage_path):
        try:
            with open(storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'cursorAuth/cachedEmail' in data:
                    return data['cursorAuth/cachedEmail']
                for key in data:
                    if 'email' in key.lower() and isinstance(data[key], str) and '@' in data[key]:
                        return data[key]
        except:
            pass
    if sqlite_path and os.path.exists(sqlite_path):
        try:
            conn = sqlite3.connect(sqlite_path)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM ItemTable WHERE key LIKE '%email%' OR key LIKE '%cursorAuth%'")
            rows = cursor.fetchall()
            conn.close()
            for row in rows:
                try:
                    value = row[0]
                    if isinstance(value, str) and '@' in value:
                        return value
                    try:
                        data = json.loads(value)
                        if isinstance(data, dict):
                            if 'email' in data:
                                return data['email']
                            if 'cachedEmail' in data:
                                return data['cachedEmail']
                    except:
                        pass
                except:
                    continue
        except:
            pass
    return None

def get_subscription_info(token):
    """Get subscription info"""
    url = "https://api2.cursor.sh/auth/full_stripe_profile"
    headers = Config.BASE_HEADERS.copy()
    headers.update({"Authorization": f"Bearer {token}"})
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except:
        return None

def format_subscription_type(subscription_data):
    """Format subscription type"""
    if not subscription_data:
        return f"{EMOJI['BASIC']} Free"
    if "membershipType" in subscription_data:
        membership_type = subscription_data.get("membershipType", "").lower()
        subscription_status = subscription_data.get("subscriptionStatus", "").lower()
        
        # Format membership type with proper capitalization
        if membership_type == "pro":
            formatted_type = "Pro"
        elif membership_type == "free_trial":
            formatted_type = "Free Trial"
        elif membership_type == "pro_trial":
            formatted_type = "Pro Trial"
        elif membership_type == "team":
            formatted_type = "Team"
        elif membership_type == "enterprise":
            formatted_type = "Enterprise"
        else:
            # Convert snake_case to Title Case (e.g., free_trial → Free Trial)
            formatted_type = " ".join(word.capitalize() for word in membership_type.split("_"))
        
        # Add proper emoji based on active status
        if subscription_status == "active":
            return f"{EMOJI['PREMIUM']} {formatted_type}"
        elif subscription_status:
            return f"{EMOJI['WARNING']} {formatted_type} ({subscription_status.capitalize()})"
        else:
            return f"{EMOJI['WARNING']} {formatted_type}"
            
    return f"{EMOJI['BASIC']} Free"

def display_account_info():
    print(f"\n{Fore.CYAN}{EMOJI['INFO']} Account Info:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'─' * 50}{Style.RESET_ALL}")
    paths = get_paths()
    if not paths:
        print(f"{Fore.RED}{EMOJI['ERROR']} Configuration not found.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'─' * 50}{Style.RESET_ALL}")
        return
    token = get_token()
    if not token:
        print(f"{Fore.RED}{EMOJI['ERROR']} Token not found. Please login to Cursor first.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'─' * 50}{Style.RESET_ALL}")
        return
    email = get_email(paths['storage_path'], paths.get('sqlite_path'))
    if email:
        print(f"{EMOJI['USER']} Email: {Fore.GREEN}{email}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}{EMOJI['WARNING']} Email not found{Style.RESET_ALL}")
    subscription_info = get_subscription_info(token)
    if subscription_info:
        if not email and 'customer' in subscription_info and 'email' in subscription_info['customer']:
            email = subscription_info['customer']['email']
            print(f"{EMOJI['USER']} Email: {Fore.GREEN}{email}{Style.RESET_ALL}")
        subscription_type = format_subscription_type(subscription_info)
        print(f"{EMOJI['SUBSCRIPTION']} Subscription: {Fore.GREEN}{subscription_type}{Style.RESET_ALL}")
        days_remaining = subscription_info.get("daysRemainingOnTrial")
        if days_remaining is not None and days_remaining > 0:
            print(f"⏱️ Remaining Pro Trial: {Fore.WHITE}{days_remaining} days{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}{EMOJI['WARNING']} Subscription information not found{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'─' * 50}{Style.RESET_ALL}")
