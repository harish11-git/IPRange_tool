@echo off
setlocal

:: --- Configuration ---
set "TICKET=MC-4093"
set "INPUT_FILE=IP_RANGE.txt"
set "OUTPUT_FILE=IP_RANGE_OUTPUT.xml"
set "SCRIPT=cidr_to_regex.py"

:: Override ticket from command line if provided:  cidr_to_regex.bat MC-5001
if not "%~1"=="" set "TICKET=%~1"

:: Check input file exists
if not exist "%INPUT_FILE%" (
    echo ERROR: %INPUT_FILE% not found in current directory.
    echo Create %INPUT_FILE% with one CIDR per line, e.g.:
    echo     37.186.35.0/24
    echo     37.186.36.0/24
    exit /b 1
)

:: Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    exit /b 1
)

echo ============================================
echo   CIDR to Regex XML Converter
echo ============================================
echo   Ticket  : %TICKET%
echo   Input   : %INPUT_FILE%
echo   Output  : %OUTPUT_FILE%
echo ============================================
echo.

:: Run the Python script and display + save output
python "%~dp0%SCRIPT%" -t %TICKET% -f "%INPUT_FILE%" > "%OUTPUT_FILE%"

:: Show the output on screen as well
type "%OUTPUT_FILE%"

echo.
echo ============================================
echo   Output saved to: %OUTPUT_FILE%
echo ============================================

endlocal
