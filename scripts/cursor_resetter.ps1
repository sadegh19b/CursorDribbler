# Set output encoding to UTF-8
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Color definitions
$RED = "`e[31m"
$GREEN = "`e[32m"
$YELLOW = "`e[33m"
$BLUE = "`e[34m"
$NC = "`e[0m"

# Add this function after color definitions
function Clear-VscdbTelemetryData {
    param($basePath)

    Write-Host ""
    Write-Host "$GREEN[Info]$NC Attempting to clear specific telemetry data from state.vscdb..."

    # Check if sqlite3 is available
    $sqliteAvailable = Get-Command sqlite3 -ErrorAction SilentlyContinue
    if (-not $sqliteAvailable) {
        Write-Host "$RED[Error]$NC sqlite3 command is not available in your PATH."
        Write-Host "$YELLOW[Tip]$NC Please install SQLite3 and ensure it's in your system's PATH to use this feature."
        return
    }

    $dbFile = Join-Path -Path $basePath -ChildPath "globalStorage\state.vscdb"

    if (-not (Test-Path $dbFile)) {
        Write-Host "$YELLOW[Warning]$NC Database file not found, skipping: $dbFile"
        return
    }

    # Backup file before modification
    try {
        $filename = Split-Path -Path $dbFile -Leaf
        $backupName = "$filename.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Write-Host "$GREEN[Info]$NC Backing up database file..."
        Copy-Item -Path $dbFile -Destination "$BACKUP_DIR\$backupName" -Force
        Write-Host "$GREEN[Success]$NC Database file backed up: $BACKUP_DIR\$backupName"
    } catch {
        Write-Host "$RED[Error]$NC Failed to back up database file: $dbFile $($_.Exception.Message)"
        Write-Host "$YELLOW[Warning]$NC Proceeding without a backup."
    }
    
    $keysToDelete = @(
        'telemetry.firstSessionDate',
        'telemetry.lastSessionDate',
        'telemetry.currentSessionDate',
        'cursorAuth/onboardingDate',
        'aiCodeTrackingStartTime',
        'aiCodeTrackingLines'
    )

    $keyList = $keysToDelete | ForEach-Object { "'$_'" } | Join-String -Separator ', '
    $sqlQuery = "DELETE FROM itemTable WHERE key IN ($keyList);"

    Write-Host "$BLUE[Debug]$NC Executing SQL query: $sqlQuery"

    try {
        $process = Start-Process -FilePath "sqlite3" -ArgumentList @("`"$dbFile`"", $sqlQuery) -Wait -NoNewWindow -PassThru
        
        if ($process.ExitCode -eq 0) {
            Write-Host "$GREEN[Success]$NC Successfully cleared telemetry data from $dbFile"
        } else {
            Write-Host "$RED[Error]$NC sqlite3 command failed with exit code $($process.ExitCode)."
            Write-Host "$RED[Error]$NC Failed to clear telemetry data from $dbFile"
        }
    }
    catch {
        Write-Host "$RED[Error]$NC An error occurred while executing sqlite3: $($_.Exception.Message)"
    }
}

# Configuration file paths
$STORAGE_FILE = "$env:APPDATA\Cursor\User\globalStorage\storage.json"
$BACKUP_DIR = "$env:APPDATA\Cursor\User\globalStorage\backups"

# Add Cursor initialization function
function Cursor-Initialization {
    Write-Host ""
    Write-Host "$GREEN[Info]$NC Executing Cursor initialization cleanup..."
    $BASE_PATH = "$env:APPDATA\Cursor\User"

    $stateDbFile = Join-Path -Path $BASE_PATH -ChildPath "globalStorage\state.vscdb"
    $stateDbBackupFile = Join-Path -Path $BASE_PATH -ChildPath "globalStorage\state.vscdb.backup"
    
    $folderToCleanContents = Join-Path -Path $BASE_PATH -ChildPath "History"
    $folderToDeleteCompletely = Join-Path -Path $BASE_PATH -ChildPath "workspaceStorage"

    Write-Host "$BLUE[Debug]$NC Base path: $BASE_PATH"

    # Handle state.vscdb
    if (Test-Path $stateDbFile) {
        Write-Host ""
        Write-Host "$YELLOW[Question]$NC How do you want to handle '$stateDbFile'?"
        Write-Host "1) Delete the file (recommended for a full reset)"
        Write-Host "2) Clean specific telemetry data from the file"
        Write-Host "3) Skip (Press Enter or any other key to skip)"
        $choice = Read-Host "Please enter your choice (1, 2, or 3)"

        if ($choice -eq "1") {
            Write-Host "$GREEN[Info]$NC Deleting state database file and its backup..."
            $filesToDelete = @($stateDbFile, $stateDbBackupFile)
            foreach ($file in $filesToDelete) {
                if (Test-Path $file) {
                    try {
                        $filename = Split-Path -Path $file -Leaf
                        $backupName = "$filename.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
                        Write-Host "$GREEN[Info]$NC Backing up file: $file"
                        Copy-Item -Path $file -Destination "$BACKUP_DIR\$backupName" -Force
                        Write-Host "$GREEN[Success]$NC File backed up: $BACKUP_DIR\$backupName"

                        Remove-Item -Path $file -Force -ErrorAction Stop
                        Write-Host "$GREEN[Success]$NC File deleted: $file"
                    } catch {
                        Write-Host "$RED[Error]$NC Failed to handle file: $file $($_.Exception.Message)"
                    }
                }
            }
        } elseif ($choice -eq "2") {
            Clear-VscdbTelemetryData -basePath $BASE_PATH
            if (Test-Path $stateDbBackupFile) {
                Write-Host "$GREEN[Info]$NC Removing old backup file: $stateDbBackupFile"
                try {
                    Remove-Item -Path $stateDbBackupFile -Force -ErrorAction Stop
                    Write-Host "$GREEN[Success]$NC Old backup file removed."
                } catch {
                    Write-Host "$RED[Error]$NC Failed to remove old backup file: $($_.Exception.Message)"
                }
            }
        } else {
            Write-Host "$YELLOW[Info]$NC Action on '$stateDbFile' skipped by user."
        }
    } else {
        Write-Host "$YELLOW[Warning]$NC State database file not found, skipping associated actions: $stateDbFile"
    }

    Write-Host ""

    # Clean contents of specified folder
    Write-Host "$BLUE[Debug]$NC Checking folder to clean contents: $folderToCleanContents"
    if (Test-Path $folderToCleanContents) {
        $confirmation = Read-Host -Prompt "$YELLOW[Question]$NC Do you want to clear the contents of this folder? '$folderToCleanContents' (y/n)"
        if ($confirmation -eq 'y') {
            try {
                # Get subitems to delete to avoid deleting History folder itself
                Get-ChildItem -Path $folderToCleanContents -Recurse | Remove-Item -Recurse -Force -ErrorAction Stop
                Write-Host "$GREEN[Success]$NC Folder contents cleared: $folderToCleanContents"
            }
            catch {
                Write-Host "$RED[Error]$NC Failed to clear folder contents: $folderToCleanContents $($_.Exception.Message)"
            }
        } else {
            Write-Host "$YELLOW[Info]$NC Cleanup of folder skipped by user: $folderToCleanContents"
        }
    } else {
        Write-Host "$YELLOW[Warning]$NC Folder does not exist, skipping cleanup: $folderToCleanContents"
    }

    Write-Host ""

    # Delete specified folder and its contents
    Write-Host "$BLUE[Debug]$NC Checking folder to delete: $folderToDeleteCompletely"
    if (Test-Path $folderToDeleteCompletely) {
        $confirmation = Read-Host -Prompt "$YELLOW[Question]$NC Do you want to delete this folder and all its contents? '$folderToDeleteCompletely' (y/n)"
        if ($confirmation -eq 'y') {
            try {
                Remove-Item -Path $folderToDeleteCompletely -Recurse -Force -ErrorAction Stop
                Write-Host "$GREEN[Success]$NC Folder deleted: $folderToDeleteCompletely"
            }
            catch {
                Write-Host "$RED[Error]$NC Failed to delete folder: $folderToDeleteCompletely $($_.Exception.Message)"
            }
        } else {
            Write-Host "$YELLOW[Info]$NC Deletion of folder skipped by user: $folderToDeleteCompletely"
        }
    } else {
        Write-Host "$YELLOW[Warning]$NC Folder does not exist, skipping deletion: $folderToDeleteCompletely"
    }

    Write-Host "$GREEN[Info]$NC Cursor initialization cleanup completed."
    Write-Host "" # Add empty line for better output formatting
}

# Check for administrator privileges
function Test-Administrator {
    $user = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($user)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Administrator)) {
    Write-Host "$RED[Error]$NC Please run this script as administrator"
    Write-Host "Please right-click the script and select 'Run as administrator'"
    Read-Host "Press Enter to exit"
    exit 1
}

# Display Logo
Clear-Host
Write-Host @"

    ██████╗██╗   ██╗██████╗ ███████╗ ██████╗ ██████╗ 
   ██╔════╝██║   ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗
   ██║     ██║   ██║██████╔╝███████╗██║   ██║██████╔╝
   ██║     ██║   ██║██╔══██╗╚════██║██║   ██║██╔══██╗
   ╚██████╗╚██████╔╝██║  ██║███████║╚██████╔╝██║  ██║
    ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝

"@
Write-Host "$BLUE================================$NC"
Write-Host "$GREEN   Cursor Device ID Resetter          $NC"
Write-Host "$BLUE================================$NC"
Write-Host ""

# Get and display Cursor version
function Get-CursorVersion {
    try {
        # Main detection path
        $packagePath = "$env:LOCALAPPDATA\Programs\cursor\resources\app\package.json"
        
        if (Test-Path $packagePath) {
            $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
            if ($packageJson.version) {
                Write-Host "$GREEN[Info]$NC Current installed Cursor version: v$($packageJson.version)"
                return $packageJson.version
            }
        }

        # Alternative path detection
        $altPath = "$env:LOCALAPPDATA\cursor\resources\app\package.json"
        if (Test-Path $altPath) {
            $packageJson = Get-Content $altPath -Raw | ConvertFrom-Json
            if ($packageJson.version) {
                Write-Host "$GREEN[Info]$NC Current installed Cursor version: v$($packageJson.version)"
                return $packageJson.version
            }
        }

        Write-Host "$YELLOW[Warning]$NC Unable to detect Cursor version"
        Write-Host "$YELLOW[Tip]$NC Please ensure Cursor is correctly installed"
        return $null
    }
    catch {
        Write-Host "$RED[Error]$NC Failed to get Cursor version: $_"
        return $null
    }
}

# Get and display version information
$cursorVersion = Get-CursorVersion
Write-Host ""

Write-Host "$YELLOW[Supported Version]$NC Cursor 1.0.x"
Write-Host ""

# Check and close Cursor process
Write-Host "$GREEN[Info]$NC Checking Cursor process..."

function Get-ProcessDetails {
    param($processName)
    Write-Host "$BLUE[Debug]$NC Getting $processName process details:"
    Get-WmiObject Win32_Process -Filter "name='$processName'" | 
        Select-Object ProcessId, ExecutablePath, CommandLine | 
        Format-List
}

# Define maximum retries and wait time
$MAX_RETRIES = 5
$WAIT_TIME = 1

# Handle process closing
function Close-CursorProcess {
    param($processName)
    
    $process = Get-Process -Name $processName -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "$YELLOW[Warning]$NC Found $processName is running"
        Get-ProcessDetails $processName
        
        Write-Host "$YELLOW[Warning]$NC Trying to close $processName..."
        Stop-Process -Name $processName -Force
        
        $retryCount = 0
        while ($retryCount -lt $MAX_RETRIES) {
            $process = Get-Process -Name $processName -ErrorAction SilentlyContinue
            if (-not $process) { break }
            
            $retryCount++
            if ($retryCount -ge $MAX_RETRIES) {
                Write-Host "$RED[Error]$NC Unable to close $processName after $MAX_RETRIES attempts"
                Get-ProcessDetails $processName
                Write-Host "$RED[Error]$NC Please close the cursor process manually and try again"
                Read-Host "Press Enter to exit"
                exit 1
            }
            Write-Host "$YELLOW[Warning]$NC Waiting for process to close, trying $retryCount/$MAX_RETRIES..."
            Start-Sleep -Seconds $WAIT_TIME
        }
        Write-Host "$GREEN[Info]$NC $processName has been successfully closed"
    }
}

# Create backup directory
if (-not (Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR | Out-Null
}

# Close all Cursor processes
Close-CursorProcess "Cursor"
Close-CursorProcess "cursor"

# Execute Cursor initialization cleanup
Cursor-Initialization

# Backup existing configuration
if (Test-Path $STORAGE_FILE) {
    Write-Host "$GREEN[Info]$NC Backing up configuration file..."
    $backupName = "storage.json.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $STORAGE_FILE "$BACKUP_DIR\$backupName"
}

# Generate new ID
Write-Host "$GREEN[Info]$NC Generating new ID..."

# Add this function after color definitions
function Get-RandomHex {
    param (
        [int]$length
    )
    
    $bytes = New-Object byte[] ($length)
    $rng = [System.Security.Cryptography.RNGCryptoServiceProvider]::new()
    $rng.GetBytes($bytes)
    $hexString = [System.BitConverter]::ToString($bytes) -replace '-',''
    $rng.Dispose()
    return $hexString
}

# Improve ID generation function
function New-StandardMachineId {
    $template = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"
    $result = $template -replace '[xy]', {
        param($match)
        $r = [Random]::new().Next(16)
        $v = if ($match.Value -eq "x") { $r } else { ($r -band 0x3) -bor 0x8 }
        return $v.ToString("x")
    }
    return $result
}

# Use new function when generating ID
$MAC_MACHINE_ID = New-StandardMachineId
$UUID = [System.Guid]::NewGuid().ToString()
# Convert auth0|user_ to byte array hexadecimal
$prefixBytes = [System.Text.Encoding]::UTF8.GetBytes("auth0|user_")
$prefixHex = -join ($prefixBytes | ForEach-Object { '{0:x2}' -f $_ })
# Generate 32 bytes (64 hexadecimal characters) as random part of machineId
$randomPart = Get-RandomHex -length 32
$MACHINE_ID = "$prefixHex$randomPart"
$SQM_ID = "{$([System.Guid]::NewGuid().ToString().ToUpper())}"

# Add permission check before Update-MachineGuid function
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "$RED[Error]$NC Please run this script with administrator privileges"
    Start-Process powershell "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

function Update-MachineGuid {
    try {
        # Check if registry path exists, if not create it
        $registryPath = "HKLM:\SOFTWARE\Microsoft\Cryptography"
        if (-not (Test-Path $registryPath)) {
            Write-Host "$YELLOW[Warning]$NC Registry path does not exist: $registryPath, creating..."
            New-Item -Path $registryPath -Force | Out-Null
            Write-Host "$GREEN[Info]$NC Registry path created successfully"
        }

        # Get current MachineGuid, if not exist use empty string as default value
        $originalGuid = ""
        try {
            $currentGuid = Get-ItemProperty -Path $registryPath -Name MachineGuid -ErrorAction SilentlyContinue
            if ($currentGuid) {
                $originalGuid = $currentGuid.MachineGuid
                Write-Host "$GREEN[Info]$NC Current registry value:"
                Write-Host "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography" 
                Write-Host "    MachineGuid    REG_SZ    $originalGuid"
            } else {
                Write-Host "$YELLOW[Warning]$NC MachineGuid value does not exist, creating new value"
            }
        } catch {
            Write-Host "$YELLOW[Warning]$NC Failed to get MachineGuid: $($_.Exception.Message)"
        }

        # Create backup directory (if not exist)
        if (-not (Test-Path $BACKUP_DIR)) {
            New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
        }

        # Create backup file (only when original value exists)
        if ($originalGuid) {
            $backupFile = "$BACKUP_DIR\MachineGuid_$(Get-Date -Format 'yyyyMMdd_HHmmss').reg"
            $backupResult = Start-Process "reg.exe" -ArgumentList "export", "`"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography`"", "`"$backupFile`"" -NoNewWindow -Wait -PassThru
            
            if ($backupResult.ExitCode -eq 0) {
                Write-Host "$GREEN[Info]$NC Registry item backed up to: $backupFile"
            } else {
                Write-Host "$YELLOW[Warning]$NC Backup creation failed, continuing..."
            }
        }

        # Generate new GUID
        $newGuid = [System.Guid]::NewGuid().ToString()

        # Update or create registry value
        Set-ItemProperty -Path $registryPath -Name MachineGuid -Value $newGuid -Force -ErrorAction Stop
        
        # Verify update
        $verifyGuid = (Get-ItemProperty -Path $registryPath -Name MachineGuid -ErrorAction Stop).MachineGuid
        if ($verifyGuid -ne $newGuid) {
            throw "Registry verification failed: updated value ($verifyGuid) does not match expected value ($newGuid)"
        }

        Write-Host "$GREEN[Info]$NC Registry updated successfully:"
        Write-Host "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography"
        Write-Host "    MachineGuid    REG_SZ    $newGuid"
        return $true
    }
    catch {
        Write-Host "$RED[Error]$NC Registry operation failed: $($_.Exception.Message)"
        
        # Try to restore backup (if exist)
        if (($backupFile -ne $null) -and (Test-Path $backupFile)) {
            Write-Host "$YELLOW[Info]$NC Restoring from backup..."
            $restoreResult = Start-Process "reg.exe" -ArgumentList "import", "`"$backupFile`"" -NoNewWindow -Wait -PassThru
            
            if ($restoreResult.ExitCode -eq 0) {
                Write-Host "$GREEN[Info]$NC Backup restored successfully"
            } else {
                Write-Host "$RED[Error]$NC Backup restore failed, please manually import backup file: $backupFile"
            }
        } else {
            Write-Host "$YELLOW[Warning]$NC Backup file not found or backup creation failed, cannot be automatically restored"
        }
        return $false
    }
}

# Create or update configuration file
Write-Host "$GREEN[Info]$NC Updating configuration..."

try {
    # Check if configuration file exists
    if (-not (Test-Path $STORAGE_FILE)) {
        Write-Host "$RED[Error]$NC Configuration file not found: $STORAGE_FILE"
        Write-Host "$YELLOW[Tip]$NC Please install and run Cursor once before using this script"
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Read existing configuration file
    try {
        $originalContent = Get-Content $STORAGE_FILE -Raw -Encoding UTF8
        
        # Convert JSON string to PowerShell object
        $config = $originalContent | ConvertFrom-Json 

        # Backup current values
        $oldValues = @{
            'machineId' = $config.'telemetry.machineId'
            'macMachineId' = $config.'telemetry.macMachineId'
            'devDeviceId' = $config.'telemetry.devDeviceId'
            'sqmId' = $config.'telemetry.sqmId'
        }

        # Update specific values
        $config.'telemetry.machineId' = $MACHINE_ID
        $config.'telemetry.macMachineId' = $MAC_MACHINE_ID
        $config.'telemetry.devDeviceId' = $UUID
        $config.'telemetry.sqmId' = $SQM_ID

        # Convert updated object back to JSON and save
        $updatedJson = $config | ConvertTo-Json -Depth 10
        [System.IO.File]::WriteAllText(
            [System.IO.Path]::GetFullPath($STORAGE_FILE), 
            $updatedJson, 
            [System.Text.Encoding]::UTF8
        )
        Write-Host "$GREEN[Info]$NC Configuration file updated successfully"
    } catch {
        # If error, try to restore original content
        if ($originalContent) {
            [System.IO.File]::WriteAllText(
                [System.IO.Path]::GetFullPath($STORAGE_FILE), 
                $originalContent, 
                [System.Text.Encoding]::UTF8
            )
        }
        throw "Failed to process JSON: $_"
    }
    # Directly execute update MachineGuid, no longer ask
    Update-MachineGuid
    # Display results
    Write-Host ""
    Write-Host "$GREEN[Info]$NC Configuration updated:"
    Write-Host "$BLUE[Debug]$NC machineId: $MACHINE_ID"
    Write-Host "$BLUE[Debug]$NC macMachineId: $MAC_MACHINE_ID"
    Write-Host "$BLUE[Debug]$NC devDeviceId: $UUID"
    Write-Host "$BLUE[Debug]$NC sqmId: $SQM_ID"

    # Display file tree structure
    Write-Host ""
    Write-Host "$GREEN[Info]$NC File structure:"
    Write-Host "$BLUE$env:APPDATA\Cursor\User$NC"
    Write-Host "├── globalStorage"
    Write-Host "│   ├── storage.json (modified)"
    Write-Host "│   └── backups"

    # List backup files
    $backupFiles = Get-ChildItem "$BACKUP_DIR\*" -ErrorAction SilentlyContinue
    if ($backupFiles) {
        foreach ($file in $backupFiles) {
            Write-Host "│       └── $($file.Name)"
        }
    } else {
        Write-Host "│       └── (empty)"
    }

    # Display information
    Write-Host ""
    Write-Host "$GREEN[Info]$NC Please restart Cursor to apply the new configuration"
    Write-Host ""

    # Ask if you want to disable automatic update
    Write-Host ""
    Write-Host "$YELLOW[Question]$NC Do you want to disable Cursor automatic update?"
    Write-Host "0) No - Keep default settings (Press Enter)"
    Write-Host "1) Yes - Disable automatic update"
    $choice = Read-Host "Please enter the option (0)"

    if ($choice -eq "1") {
        Write-Host ""
        Write-Host "$GREEN[Info]$NC Processing automatic update..."
        $updaterPath = "$env:LOCALAPPDATA\cursor-updater"

        # Define manual settings tutorial
        function Show-ManualGuide {
            Write-Host ""
            Write-Host "$YELLOW[Warning]$NC Automatic settings failed, please try manual operation:"
            Write-Host "$YELLOWManual disable update steps:$NC"
            Write-Host "1. Open PowerShell as administrator"
            Write-Host "2. Copy and paste the following commands:"
            Write-Host "$BLUECommand 1 - Delete existing directory (if exist):$NC"
            Write-Host "Remove-Item -Path `"$updaterPath`" -Force -Recurse -ErrorAction SilentlyContinue"
            Write-Host ""
            Write-Host "$BLUECommand 2 - Create blocking file:$NC"
            Write-Host "New-Item -Path `"$updaterPath`" -ItemType File -Force | Out-Null"
            Write-Host ""
            Write-Host "$BLUECommand 3 - Set read-only attribute:$NC"
            Write-Host "Set-ItemProperty -Path `"$updaterPath`" -Name IsReadOnly -Value `$true"
            Write-Host ""
            Write-Host "$BLUECommand 4 - Set permissions (optional):$NC"
            Write-Host "icacls `"$updaterPath`" /inheritance:r /grant:r `"`$($env:USERNAME):(R)`""
            Write-Host ""
            Write-Host "$YELLOWVerification method:$NC"
            Write-Host "1. Run command: Get-ItemProperty `"$updaterPath`""
            Write-Host "2. Confirm IsReadOnly attribute is True"
            Write-Host "3. Run command: icacls `"$updaterPath`""
            Write-Host "4. Confirm only read permission"
            Write-Host ""
            Write-Host "$YELLOW[Tip]$NC Please restart Cursor after completion"
        }

        try {
            # Check if cursor-updater exists
            if (Test-Path $updaterPath) {
                # If it's a file, it means the update blocking file has already been created
                if ((Get-Item $updaterPath) -is [System.IO.FileInfo]) {
                    Write-Host "$GREEN[Info]$NC Update blocking file already exists, no need to block again"
                    return
                }
                # If it's a directory, try to delete
                else {
                    try {
                        Remove-Item -Path $updaterPath -Force -Recurse -ErrorAction Stop
                        Write-Host "$GREEN[Info]$NC Successfully deleted cursor-updater directory"
                    }
                    catch {
                        Write-Host "$RED[Error]$NC Failed to delete cursor-updater directory"
                        Show-ManualGuide
                        return
                    }
                }
            }

            # Create blocking file
            try {
                New-Item -Path $updaterPath -ItemType File -Force -ErrorAction Stop | Out-Null
                Write-Host "$GREEN[Info]$NC Successfully created blocking file"
            }
            catch {
                Write-Host "$RED[Error]$NC Failed to create blocking file"
                Show-ManualGuide
                return
            }

            # Set file permissions
            try {
                # Set read-only attribute
                Set-ItemProperty -Path $updaterPath -Name IsReadOnly -Value $true -ErrorAction Stop
                
                # Use icacls to set permissions
                $result = Start-Process "icacls.exe" -ArgumentList "`"$updaterPath`" /inheritance:r /grant:r `"$($env:USERNAME):(R)`"" -Wait -NoNewWindow -PassThru
                if ($result.ExitCode -ne 0) {
                    throw "icacls command failed"
                }
                
                Write-Host "$GREEN[Info]$NC Successfully set file permissions"
            }
            catch {
                Write-Host "$RED[Error]$NC Failed to set file permissions"
                Show-ManualGuide
                return
            }

            # Verify settings
            try {
                $fileInfo = Get-ItemProperty $updaterPath
                if (-not $fileInfo.IsReadOnly) {
                    Write-Host "$RED[Error]$NC Verification failed: file permissions may not have been set"
                    Show-ManualGuide
                    return
                }
            }
            catch {
                Write-Host "$RED[Error]$NC Verification failed"
                Show-ManualGuide
                return
            }

            Write-Host "$GREEN[Info]$NC Successfully disabled automatic update"
        }
        catch {
            Write-Host "$RED[Error]$NC Unknown error: $_"
            Show-ManualGuide
        }
    }
    else {
        Write-Host "$GREEN[Info]$NC Keeping default settings, no changes made"
    }

    # Retain valid registry updates
    Update-MachineGuid

} catch {
    Write-Host "$RED[Error]$NC Main operation failed: $_"
    Write-Host "$YELLOW[Attempting]$NC Using alternative method..."

    try {
        # Alternative method: Using Add-Content
        $tempFile = [System.IO.Path]::GetTempFileName()
        $config | ConvertTo-Json | Set-Content -Path $tempFile -Encoding UTF8
        Copy-Item -Path $tempFile -Destination $STORAGE_FILE -Force
        Remove-Item -Path $tempFile
        Write-Host "$GREEN[Info]$NC Successfully wrote configuration using alternative method"
    } catch {
        Write-Host "$RED[Error]$NC All attempts failed"
        Write-Host "Error details: $_"
        Write-Host "Target file: $STORAGE_FILE"
        Write-Host "Please ensure you have sufficient permissions to access this file"
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Read-Host "Press Enter to exit"
exit 0

# Modify file writing section
function Write-ConfigFile {
    param($config, $filePath)
    
    try {
        # Use UTF8 no BOM encoding
        $utf8NoBom = New-Object System.Text.UTF8Encoding $false
        $jsonContent = $config | ConvertTo-Json -Depth 10
        
        # Standardize on LF line endings
        $jsonContent = $jsonContent.Replace("`r`n", "`n")
        
        [System.IO.File]::WriteAllText(
            [System.IO.Path]::GetFullPath($filePath),
            $jsonContent,
            $utf8NoBom
        )
        
        Write-Host "$GREEN[Info]$NC Successfully wrote configuration file (UTF8 no BOM)"
    }
    catch {
        throw "Failed to write configuration file: $_"
    }
} 