# Cursor Dribbler

A simple tool to check Cursor AI account information, subscription status, usage statistics, and reset Cursor machine id.

## Features

- View your Cursor account email
- Check subscription type (Free, Pro, Team, etc.)
- See remaining trial days (if applicable)
- View usage statistics for Fast Response (GPT-4) and Slow Response (GPT-3.5)
- Run Cursor Resetter with a simple menu option

## Usage

### Running the executable

1. Download the executable from the `dist` folder
2. Double-click to run it
3. From the menu, select an option:
   - Option 1: Run Cursor Resetter
   - Option 0: Exit
4. The program will automatically display your account information
5. Press Enter when prompted to continue or exit

### Running the Python script

1. Make sure you have Python installed
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the main script:
   ```
   python main.py
   ```

### Building the executable yourself

1. Make sure you have Python installed
2. Either:
   - Run the setup script:
     ```
     python setup.py
     ```
   - Or run the batch file:
     ```
     build.bat
     ```
3. This will install the required packages and build the executable
4. Find the executable in the `dist` folder

## Requirements

- Windows operating system
- Cursor AI installed and logged in
- PowerShell (script will attempt to use PowerShell 7 if available, otherwise falls back to Windows PowerShell)

## License

This project is licensed under the MIT License.