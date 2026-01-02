@echo off
REM ControlGit GitHub CLI Installation Script
REM This script checks if GitHub CLI (gh) is installed
REM If not, it installs Chocolatey (if needed) and then installs gh

REM Check for permissions
net session >nul 2>&1
if %errorLevel% == 0 (goto :admin) else (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process -FilePath '%0' -Verb RunAs"
    exit /b
)

:admin
REM Your administrative commands go below this line
setlocal enabledelayedexpansion

echo.
echo ============================================================
echo ControlGit - GitHub CLI Installation
echo ============================================================
echo.

REM Check if gh is already installed
echo Checking for GitHub CLI (gh)...
where gh >nul 2>nul
if %errorlevel% equ 0 (
    echo [OK] GitHub CLI is already installed
    echo.
    goto end
)

echo [INFO] GitHub CLI not found, attempting installation...
echo.

REM Check if Chocolatey is installed
echo Checking for Chocolatey...
where choco >nul 2>nul
if %errorlevel% equ 0 (
    echo [OK] Chocolatey is installed
    goto install_gh
)

REM Chocolatey not found, try to install it
echo [INFO] Chocolatey not found, attempting to install...
echo.

REM Install Chocolatey
echo Installing Chocolatey...
powershell -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" && set "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Chocolatey
    echo Please install manually from: https://chocolatey.org/install
    echo.
    goto end
)

echo [OK] Chocolatey installed successfully
echo.

:install_gh
REM Install GitHub CLI
echo Installing GitHub CLI (gh)...
choco install gh -y

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo [SUCCESS] GitHub CLI installed successfully!
    echo ============================================================
    echo.
    echo Next step: Run 'gh auth login' to authenticate with GitHub
    echo.
) else (
    echo.
    echo [ERROR] Failed to install GitHub CLI
    echo Please install manually from: https://cli.github.com
    echo.
)

:end
endlocal
