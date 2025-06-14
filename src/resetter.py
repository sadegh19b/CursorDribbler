import os
import sys
import json
import subprocess
import ctypes
import uuid
import secrets
import time
import sqlite3
import shutil
import winreg
import stat
import random

from colorama import Fore, Style, init
from constants import EMOJI

# Initialize colorama
init(autoreset=True)

# --- Print Helpers (adapted to use colorama) ---

def print_info(message):
    print(f"{Fore.GREEN}[Info]{Style.RESET_ALL} {message}")

def print_success(message):
    print(f"{Fore.GREEN}[Success]{Style.RESET_ALL} {message}")

def print_error(message):
    print(f"{Fore.RED}[Error]{Style.RESET_ALL} {message}")

def print_warning(message):
    print(f"{Fore.YELLOW}[Warning]{Style.RESET_ALL} {message}")

def print_debug(message):
    print(f"{Fore.BLUE}[Debug]{Style.RESET_ALL} {message}")

def print_question(message):
    return input(f"{Fore.YELLOW}[Question]{Style.RESET_ALL} {message}")

# --- Core Logic Functions ---

def is_admin():
    """Checks if the script is running with administrator privileges on Windows."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Re-runs this script with administrator privileges on Windows."""
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

def clear_vscdb_telemetry_data(base_path, backup_dir):
    """Clears specific telemetry data from the state.vscdb SQLite database."""
    print("")
    print_info("Attempting to clear specific telemetry data from state.vscdb...")

    if not shutil.which("sqlite3"):
        print_error("sqlite3 command is not available in your PATH.")
        print_warning("Please install SQLite3 and ensure it's in your system's PATH to use this feature.")
        return

    db_file = os.path.join(base_path, "globalStorage", "state.vscdb")

    if not os.path.exists(db_file):
        print_warning(f"Database file not found, skipping: {db_file}")
        return

    try:
        filename = os.path.basename(db_file)
        backup_name = f"{filename}.backup_{time.strftime('%Y%m%d_%H%M%S')}"
        backup_path = os.path.join(backup_dir, backup_name)
        print_info("Backing up database file...")
        shutil.copy(db_file, backup_path)
        print_success(f"Database file backed up: {backup_path}")
    except Exception as e:
        print_error(f"Failed to back up database file: {db_file} {e}")
        print_warning("Proceeding without a backup.")

    keys_to_delete = [
        'telemetry.firstSessionDate',
        'telemetry.lastSessionDate',
        'telemetry.currentSessionDate',
        'cursorAuth/accessToken',
        'cursorAuth/refreshToken',
        'cursorAuth/cachedEmail',
        'cursorAuth/cachedSignUpType',
        'cursorAuth/onboardingDate',
        'cursorAuth/stripeMembershipType',
        'aiCodeTrackingStartTime',
        'aiCodeTrackingLines',
        'aicontext.personalContext',
        'anysphere.cursor-always-local',
    ]

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        placeholders = ', '.join('?' for _ in keys_to_delete)
        sql_query = f"DELETE FROM itemTable WHERE key IN ({placeholders});"
        print_debug(f"Executing SQL query: {sql_query.replace('?', '%s') % tuple(f'{k}' for k in keys_to_delete)}")
        
        cursor.execute(sql_query, keys_to_delete)
        conn.commit()
        print_success(f"Successfully cleared telemetry data from {db_file}")
    except sqlite3.Error as e:
        print_error(f"An error occurred while executing sqlite3 query: {e}")
        print_error(f"Failed to clear telemetry data from {db_file}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def cursor_initialization(base_path, backup_dir):
    """Handles the initial cleanup process for Cursor files and directories."""
    print("")
    print_info("Executing Cursor initialization cleanup...")

    state_db_file = os.path.join(base_path, "globalStorage", "state.vscdb")
    state_db_backup_file = os.path.join(base_path, "globalStorage", "state.vscdb.backup")
    folder_to_clean_contents = os.path.join(base_path, "History")
    folder_to_delete_completely = os.path.join(base_path, "workspaceStorage")

    print_debug(f"Base path: {base_path}")

    if os.path.exists(state_db_file):
        print("")
        print(f"{Fore.YELLOW}[Question]{Style.RESET_ALL} How do you want to handle '{state_db_file}'?")
        print("1) Delete the file (recommended for a full reset)")
        print("2) Clean specific telemetry data from the file")
        print("3) Skip (Press Enter or any other key to skip)")
        choice = input("Please enter your choice (1, 2, or 3): ")

        if choice == "1":
            print_info("Deleting state database file and its backup...")
            files_to_delete = [state_db_file, state_db_backup_file]
            for file in files_to_delete:
                if os.path.exists(file):
                    try:
                        filename = os.path.basename(file)
                        backup_name = f"{filename}.backup_{time.strftime('%Y%m%d_%H%M%S')}"
                        backup_path = os.path.join(backup_dir, backup_name)
                        print_info(f"Backing up file: {file}")
                        shutil.copy(file, backup_path)
                        print_success(f"File backed up: {backup_path}")
                        
                        os.remove(file)
                        print_success(f"File deleted: {file}")
                    except Exception as e:
                        print_error(f"Failed to handle file: {file} {e}")
        elif choice == "2":
            clear_vscdb_telemetry_data(base_path, backup_dir)
            if os.path.exists(state_db_backup_file):
                print_info(f"Removing old backup file: {state_db_backup_file}")
                try:
                    os.remove(state_db_backup_file)
                    print_success("Old backup file removed.")
                except Exception as e:
                    print_error(f"Failed to remove old backup file: {e}")
        else:
            print_warning(f"Action on '{state_db_file}' skipped by user.")
    else:
        print_warning(f"State database file not found, skipping associated actions: {state_db_file}")

    print("")

    if os.path.exists(folder_to_clean_contents):
        confirmation = print_question(f"Do you want to clear the contents of this folder? '{folder_to_clean_contents}' (y/n): ")
        if confirmation.lower() == 'y':
            try:
                for item in os.listdir(folder_to_clean_contents):
                    item_path = os.path.join(folder_to_clean_contents, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
                print_success(f"Folder contents cleared: {folder_to_clean_contents}")
            except Exception as e:
                print_error(f"Failed to clear folder contents: {folder_to_clean_contents} {e}")
        else:
            print_warning(f"Cleanup of folder skipped by user: {folder_to_clean_contents}")
    else:
        print_warning(f"Folder does not exist, skipping cleanup: {folder_to_clean_contents}")

    print("")

    if os.path.exists(folder_to_delete_completely):
        confirmation = print_question(f"Do you want to delete this folder and all its contents? '{folder_to_delete_completely}' (y/n): ")
        if confirmation.lower() == 'y':
            try:
                shutil.rmtree(folder_to_delete_completely)
                print_success(f"Folder deleted: {folder_to_delete_completely}")
            except Exception as e:
                print_error(f"Failed to delete folder: {folder_to_delete_completely} {e}")
        else:
            print_warning(f"Deletion of folder skipped by user: {folder_to_delete_completely}")
    else:
        print_warning(f"Folder does not exist, skipping deletion: {folder_to_delete_completely}")

    print_info("Cursor initialization cleanup completed.")
    print("")

def get_cursor_version():
    """Reads and displays the installed Cursor version from package.json."""
    print("")
    try:
        possible_paths = [
            os.path.join(os.getenv('LOCALAPPDATA'), 'Programs', 'cursor', 'resources', 'app', 'package.json'),
            os.path.join(os.getenv('LOCALAPPDATA'), 'cursor', 'resources', 'app', 'package.json')
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    package_json = json.load(f)
                    version = package_json.get('version')
                    if version:
                        print_info(f"Current installed Cursor version: v{version}")
                        return version
        
        print_warning("Unable to detect Cursor version.")
        print_warning("Please ensure Cursor is correctly installed.")
        return None
    except Exception as e:
        print_error(f"Failed to get Cursor version: {e}")
        return None

def close_cursor_process(process_name):
    """Checks for and closes the specified Cursor process."""
    process_name_exe = f"{process_name}.exe"
    max_retries = 5
    wait_time = 1

    try:
        result = subprocess.run(['tasklist', '/FI', f'IMAGENAME eq {process_name_exe}'], capture_output=True, text=True, check=True)
        if process_name_exe in result.stdout:
            print_warning(f"Found {process_name} is running.")
            print_warning(f"Trying to close {process_name}...")
            
            subprocess.run(['taskkill', '/F', '/IM', process_name_exe], check=True, capture_output=True)
            
            for i in range(max_retries):
                result = subprocess.run(['tasklist', '/FI', f'IMAGENAME eq {process_name_exe}'], capture_output=True, text=True)
                if process_name_exe not in result.stdout:
                    print_info(f"{process_name} has been successfully closed.")
                    return
                
                print_warning(f"Waiting for process to close, trying {i+1}/{max_retries}...")
                time.sleep(wait_time)
            
            print_error(f"Unable to close {process_name} after {max_retries} attempts.")
            print_error("Please close the cursor process manually and try again.")
            input("Press Enter to exit")
            sys.exit(1)
    except FileNotFoundError:
        print_warning("tasklist/taskkill command not found. Skipping process check.")
    except subprocess.CalledProcessError:
         pass

def get_random_hex(length):
    """Generates a random hexadecimal string of the specified length in bytes."""
    return secrets.token_hex(length)

def new_standard_machine_id():
    """Generates a new standard v4 UUID."""
    return str(uuid.uuid4())

def update_machine_guid(backup_dir):
    """Updates the MachineGuid in the Windows Registry."""
    print_info("Updating MachineGuid in registry...")
    try:
        registry_path = r"SOFTWARE\Microsoft\Cryptography"
        original_guid = ""
        backup_file = None

        try:
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, registry_path)
            
            try:
                original_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
                print_info("Current registry value:")
                print(f"HKEY_LOCAL_MACHINE\\{registry_path}")
                print(f"    MachineGuid    REG_SZ    {original_guid}")
            except FileNotFoundError:
                print_warning("MachineGuid value does not exist, creating new value")
            
            winreg.CloseKey(key)

        except Exception as e:
            print_warning(f"Failed to get MachineGuid: {e}")

        if original_guid:
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir, exist_ok=True)
            
            backup_file = os.path.join(backup_dir, f"MachineGuid_{time.strftime('%Y%m%d_%H%M%S')}.reg")
            try:
                result = subprocess.run(['reg', 'export', f'HKEY_LOCAL_MACHINE\\{registry_path}', backup_file, '/y'], capture_output=True, text=True)
                if result.returncode == 0:
                    print_info(f"Registry item backed up to: {backup_file}")
                else:
                    print_warning(f"Backup creation failed: {result.stderr}")
                    backup_file = None
            except Exception as e:
                print_warning(f"Backup creation failed: {e}")
                backup_file = None

        new_guid = str(uuid.uuid4())
        
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "MachineGuid", 0, winreg.REG_SZ, new_guid)
        winreg.CloseKey(key)

        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_READ)
        verify_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
        winreg.CloseKey(key)

        if verify_guid != new_guid:
            raise Exception(f"Registry verification failed: updated value ({verify_guid}) does not match expected value ({new_guid})")
        
        print_success("Registry updated successfully:")
        print(f"HKEY_LOCAL_MACHINE\\{registry_path}")
        print(f"    MachineGuid    REG_SZ    {new_guid}")
        return True

    except Exception as e:
        print_error(f"Registry operation failed: {e}")
        if backup_file and os.path.exists(backup_file):
            print_warning("Restoring from backup...")
            try:
                result = subprocess.run(['reg', 'import', backup_file], capture_output=True, text=True)
                if result.returncode == 0:
                    print_success("Backup restored successfully")
                else:
                    print_error(f"Backup restore failed, please manually import backup file: {backup_file}")
                    print_error(f"REG IMPORT log: {result.stdout} {result.stderr}")

            except Exception as import_e:
                print_error(f"Backup restore failed with exception: {import_e}")
        return False

def show_manual_update_guide(updater_path):
    """Displays a manual guide for disabling automatic updates."""
    username = os.getlogin()
    print("")
    print_warning("Automatic settings failed, please try manual operation:")
    print_warning("Manual disable update steps:")
    print("1. Open PowerShell as administrator")
    print("2. Copy and paste the following commands:")
    print(f"{Fore.BLUE}Command 1 - Delete existing directory (if exist):{Style.RESET_ALL}")
    print(f"Remove-Item -Path \"{updater_path}\" -Force -Recurse -ErrorAction SilentlyContinue")
    print("")
    print(f"{Fore.BLUE}Command 2 - Create blocking file:{Style.RESET_ALL}")
    print(f"New-Item -Path \"{updater_path}\" -ItemType File -Force | Out-Null")
    print("")
    print(f"{Fore.BLUE}Command 3 - Set read-only attribute:{Style.RESET_ALL}")
    print(f"Set-ItemProperty -Path \"{updater_path}\" -Name IsReadOnly -Value $true")
    print("")
    print(f"{Fore.BLUE}Command 4 - Set permissions (optional):{Style.RESET_ALL}")
    print(f"icacls \"{updater_path}\" /inheritance:r /grant:r \"`$($env:USERNAME):(R)\"")

def disable_auto_update():
    """Disables Cursor's automatic update feature."""
    print("")
    print_info("Processing automatic update...")
    updater_path = os.path.join(os.getenv('LOCALAPPDATA'), 'cursor-updater')

    try:
        if os.path.exists(updater_path):
            if os.path.isfile(updater_path):
                print_info("Update blocking file already exists, no need to block again.")
                return
            elif os.path.isdir(updater_path):
                try:
                    shutil.rmtree(updater_path)
                    print_success("Successfully deleted cursor-updater directory.")
                except Exception as e:
                    print_error(f"Failed to delete cursor-updater directory: {e}")
                    show_manual_update_guide(updater_path)
                    return

        try:
            with open(updater_path, 'w') as f: pass
            print_success("Successfully created blocking file.")
        except Exception as e:
            print_error(f"Failed to create blocking file: {e}")
            show_manual_update_guide(updater_path)
            return

        try:
            os.chmod(updater_path, stat.S_IREAD)
            username = os.getlogin()
            result = subprocess.run(['icacls', updater_path, '/inheritance:r', '/grant:r', f'{username}:(R)'], check=True, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"icacls command failed: {result.stderr}")
            print_success("Successfully set file permissions.")
        except Exception as e:
            print_error(f"Failed to set file permissions: {e}")
            show_manual_update_guide(updater_path)
            return

        print_success("Successfully disabled automatic update.")
    except Exception as e:
        print_error(f"Unknown error: {e}")
        show_manual_update_guide(updater_path)

def _main_logic():
    """The main logic for the Cursor resetter script."""
    if sys.platform != "win32":
        print_error("This script is intended to run on Windows only.")
        sys.exit(1)

    if not is_admin():
        print_error("Please run this script as administrator.")
        print_info("Attempting to relaunch with administrator privileges...")
        run_as_admin()
        sys.exit(99)  # Special exit code for relaunch

    sys.stdout.reconfigure(encoding='utf-8')
    os.system('cls' if os.name == 'nt' else 'clear')

    print(f"""{Fore.CYAN}
    ██████╗██╗   ██╗██████╗ ███████╗ ██████╗ ██████╗ 
   ██╔════╝██║   ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗
   ██║     ██║   ██║██████╔╝███████╗██║   ██║██████╔╝
   ██║     ██║   ██║██╔══██╗╚════██║██║   ██║██╔══██╗
   ╚██████╗╚██████╔╝██║  ██║███████║╚██████╔╝██║  ██║
    ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝
{Style.RESET_ALL}""")
    print(f"{Fore.BLUE}================================{Style.RESET_ALL}")
    print(f"{Fore.GREEN}   Cursor Device ID Resetter          {Style.RESET_ALL}")
    print(f"{Fore.BLUE}================================{Style.RESET_ALL}")
    print("")

    get_cursor_version()

    print("")
    print_warning("Supported Version: Cursor 1.0.x")
    print("")

    print_info("Checking Cursor process...")
    close_cursor_process("Cursor")
    close_cursor_process("cursor")
    
    appdata_path = os.getenv('APPDATA')
    base_path = os.path.join(appdata_path, 'Cursor', 'User')
    storage_file = os.path.join(base_path, 'globalStorage', 'storage.json')
    backup_dir = os.path.join(base_path, 'globalStorage', 'backups')
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir, exist_ok=True)
    
    cursor_initialization(base_path, backup_dir)

    if os.path.exists(storage_file):
        print_info("Backing up configuration file...")
        backup_name = f"storage.json.backup_{time.strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(storage_file, os.path.join(backup_dir, backup_name))
    else:
        print_error(f"Configuration file not found: {storage_file}")
        print_warning("Please install and run Cursor once before using this script.")
        input("Press Enter to exit")
        sys.exit(1)

    print_info("Generating new ID...")
    mac_machine_id = new_standard_machine_id()
    uuid_val = str(uuid.uuid4())
    prefix_hex = "auth0|user_".encode('utf-8').hex()
    random_part = get_random_hex(32)
    machine_id = f"{prefix_hex}{random_part}"
    sqm_id = f"{{{str(uuid.uuid4()).upper()}}}"

    print_info("Updating configuration...")
    original_content = ""
    try:
        with open(storage_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
            config = json.loads(original_content)

        config['telemetry.machineId'] = machine_id
        config['telemetry.macMachineId'] = mac_machine_id
        config['telemetry.devDeviceId'] = uuid_val
        config['telemetry.sqmId'] = sqm_id

        updated_json = json.dumps(config, indent=4)
        with open(storage_file, 'w', encoding='utf-8') as f:
            f.write(updated_json)
        
        print_success("Configuration file updated successfully.")
    except Exception as e:
        print_error(f"Failed to process JSON: {e}")
        if original_content:
            with open(storage_file, 'w', encoding='utf-8') as f:
                f.write(original_content)
        input("Press Enter to exit")
        sys.exit(1)

    update_machine_guid(backup_dir)

    print("")
    print_info("Configuration updated:")
    print_debug(f"machineId: {machine_id}")
    print_debug(f"macMachineId: {mac_machine_id}")
    print_debug(f"devDeviceId: {uuid_val}")
    print_debug(f"sqmId: {sqm_id}")
    
    print("")
    print_info("File structure:")
    print(f"{Fore.BLUE}{base_path}{Style.RESET_ALL}")
    print("├── globalStorage")
    print("│   ├── storage.json (modified)")
    print("│   └── backups")
    
    backup_files = os.listdir(backup_dir)
    if backup_files:
        for file in backup_files:
            print(f"│       └── {file}")
    else:
        print("│       └── (empty)")

    print("")
    print_info("Please restart Cursor to apply the new configuration.")
    print("")
    
    choice = print_question("Do you want to disable Cursor automatic update?\n0) No - Keep default settings (Press Enter)\n1) Yes - Disable automatic update\nPlease enter the option (0): ")

    if choice == "1":
        disable_auto_update()
    else:
        print_info("Keeping default settings, no changes made.")

    print("")
    input("Press Enter to exit")
    sys.exit(0)

def run_cursor_resetter():
    """Runs the main resetter logic and handles exit codes."""
    print(f"\n{Fore.CYAN}{EMOJI['RUN']} Running Cursor Resetter...{Style.RESET_ALL}")
    
    try:
        _main_logic()
    except SystemExit as e:
        if e.code == 0:
            print(f"\n{Fore.GREEN}{EMOJI['SUCCESS']} Cursor Resetter executed successfully!{Style.RESET_ALL}")
            return True
        elif e.code == 99:
            print(f"\n{Fore.YELLOW}{EMOJI['WARNING']} Relaunching with administrator privileges...{Style.RESET_ALL}")
            return True
        else:
            print(f"\n{Fore.RED}{EMOJI['ERROR']} Cursor Resetter exited with error code: {e.code}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"\n{Fore.RED}{EMOJI['ERROR']} Failed to run Cursor Resetter: {str(e)}{Style.RESET_ALL}")
        return False

if __name__ == "__main__":
    _main_logic()
