@echo off
setlocal enabledelayedexpansion

REM Try to find PowerShell 7 (pwsh) first
set "PWSH_FOUND=0"
for %%X in (pwsh.exe) do (
    set "PWSH_TEST="
    for %%Y in ("%%~$PATH:X") do set "PWSH_TEST=%%~Y"
    if defined PWSH_TEST (
        set "PWSH=pwsh.exe"
        set "PWSH_FOUND=1"
    )
)

REM If PowerShell 7 not found, use default PowerShell
if "!PWSH_FOUND!"=="0" (
    echo PowerShell 7 not found, using default PowerShell
    set "PWSH=powershell.exe"
)

REM Run the script with elevated privileges
!PWSH! -Command "if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { Start-Process '!PWSH!' -ArgumentList '-ExecutionPolicy Bypass -NoExit -File \".\scripts\cursor_resetter.ps1\"' -Verb RunAs } else { & '!PWSH!' -ExecutionPolicy Bypass -NoExit -File '.\scripts\cursor_resetter.ps1' }"