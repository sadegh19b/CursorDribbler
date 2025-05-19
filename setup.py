import os
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    packages = ['pyinstaller', 'colorama', 'requests', 'pillow']
    subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages)
    print("Packages installed successfully!")

def convert_png_to_ico():
    """Convert PNG logo to ICO format"""
    try:
        from PIL import Image
        
        # Check if the logo file exists
        if os.path.exists('logo-512.png'):
            print("Converting logo to ICO format...")
            img = Image.open('logo-512.png')
            icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            img.save('logo.ico', sizes=icon_sizes)
            print("Logo converted successfully!")
            return True
        else:
            print("Logo file not found: logo-512.png")
            return False
    except ImportError:
        print("Could not import PIL. Icon conversion skipped.")
        return False
    except Exception as e:
        print(f"Error converting logo: {str(e)}")
        return False

def build_exe():
    """Build executable using PyInstaller"""
    print("Building executable...")
    
    # Convert logo to ICO if possible
    has_icon = convert_png_to_ico()
    icon_path = 'logo.ico' if has_icon else 'NONE'
    
    # Build the standard version
    print("\n1. Building standard version...")
    cmd_simple = [
        'pyinstaller',
        '--onefile',  # Create a single executable file
        '--console',  # Show console window
        '--name=CursorDribbler',  # Name of the executable
        f'--icon={icon_path}',  # Use the created icon or NONE
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