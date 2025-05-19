# Cursor Dribbler

![Cursor Dribbler Splash](assets/splash.png)

A simple tool to check Cursor editor account information, subscription status, usage statistics, and reset machine id.

## Features

- View account email
- Check subscription type (Free, Pro, Team, etc.)
- See remaining trial days (if applicable)
- View usage statistics for Fast Response and Slow Response
- Run Cursor Resetter with a simple menu option

## Requirements

- Windows operating system
- Cursor Editor installed and logged in
- PowerShell (script will attempt to use PowerShell 7 if available, otherwise falls back to Windows PowerShell)

## Usage

### Running the Python script

1. Make sure you have Python installed
2. Install the required packages:
   ```
   pip install -r src/requirements.txt
   ```
3. Run the main script:
   ```
   python src/main.py
   ```

### Building the executable

1. Make sure you have Python installed
2. Either:
   - Run the setup script:
     ```
     python src/setup.py
     ```
   - Or run the batch file:
     ```
     build.bat
     ```
3. This will install the required packages and build the executable
4. Find the executable in the `dist` folder

### Running the executable

1. Download the executable from the `dist` folder
2. Double-click to run it
3. From the menu, select an option:
   - Option 1: Run Cursor Resetter
   - Option 0: Exit
4. The program will automatically display your account information
5. Press Enter when prompted to continue or exit

## License

This project is licensed under the MIT License.