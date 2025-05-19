import os
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    packages = ['pyinstaller', 'colorama', 'requests']
    subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages)
    print("Packages installed successfully!")

def build_exe():
    """Build executable using PyInstaller"""
    print("Building executable...")
    
    # Build the standard version
    print("\n1. Building standard version...")
    cmd_simple = [
        'pyinstaller',
        '--onefile',  # Create a single executable file
        '--console',  # Show console window
        '--name=CursorDribbler',  # Name of the executable
        '--icon=NONE',  # No icon
        '--add-data=constants.py;.',  # Add necessary data files
        '--add-data=cursor_resetter.ps1;.',  # Add PowerShell script directly to executable
        'main.py'  # Script to convert
    ]
    
    subprocess.check_call(cmd_simple)
    print("Standard version built successfully!")
    print("You can find the executable in the 'dist' folder:")
    print("- CursorDribbler.exe (Standard version)")

if __name__ == "__main__":
    install_requirements()
    build_exe() 