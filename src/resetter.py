import os
import subprocess
import sys
import shutil
import pathlib
from colorama import Fore, Style
from constants import EMOJI

def run_cursor_resetter():
    print(f"\n{Fore.CYAN}{EMOJI['RUN']} Running Cursor Resetter...{Style.RESET_ALL}")
    
    # Get the path to the bundled ps1 file
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        base_path = sys._MEIPASS
        ps_script_path = os.path.join(base_path, "scripts", "cursor_resetter.ps1")
    else:
        # Running as script
        base_path = os.path.dirname(os.path.abspath(__file__))
        root_dir = pathlib.Path(base_path).parent
        ps_script_path = os.path.join(root_dir, "scripts", "cursor_resetter.ps1")
    
    # Check if the script exists
    if not os.path.exists(ps_script_path):
        print(f"{Fore.RED}{EMOJI['ERROR']} cursor_resetter.ps1 not found at: {ps_script_path}{Style.RESET_ALL}")
        return False
    
    try:
        # Check for PowerShell 7 (pwsh) first, then fall back to regular PowerShell
        pwsh_path = shutil.which("pwsh")
        powershell_exe = "pwsh" if pwsh_path else "powershell"
        
        # Check if we have admin privileges
        admin_check = subprocess.run([
            powershell_exe, 
            "-Command", 
            "([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)"
        ], capture_output=True, text=True)
        
        is_admin = admin_check.stdout.strip().lower() == "true"
        
        if not is_admin:
            print(f"{Fore.YELLOW}{EMOJI['WARNING']} Requesting administrator privileges...{Style.RESET_ALL}")
            # If not admin, we need to use Start-Process with RunAs verb
            subprocess.run([
                powershell_exe,
                "-Command",
                f"Start-Process '{powershell_exe}' -ArgumentList '-ExecutionPolicy Bypass -File \"{ps_script_path}\"' -Verb RunAs"
            ], check=True)
        else:
            # If already admin, run the script directly in the current window
            print(f"{Fore.CYAN}{EMOJI['INFO']} Running script with current privileges...{Style.RESET_ALL}")
            result = subprocess.run([
                powershell_exe,
                "-ExecutionPolicy", "Bypass",
                "-File", ps_script_path
            ], check=True, capture_output=False)
        
        print(f"\n{Fore.GREEN}{EMOJI['SUCCESS']} Cursor Resetter executed successfully!{Style.RESET_ALL}")
        return True
    except subprocess.SubprocessError as e:
        print(f"\n{Fore.RED}{EMOJI['ERROR']} Failed to run Cursor Resetter: {str(e)}{Style.RESET_ALL}")
        return False

if __name__ == "__main__":
    print("Starting Cursor Resetter...")
    run_cursor_resetter()
