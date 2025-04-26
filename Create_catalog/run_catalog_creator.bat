@echo off
echo Mias Moda Catalog Creator
echo ========================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo pip is not installed
    echo Please install pip and try again
    pause
    exit /b 1
)

REM Install dependencies if not already installed
echo Installing dependencies...
pip install -r requirements.txt

REM Create directories if they don't exist
if not exist "product_pictures" mkdir product_pictures
if not exist "new_catalog" mkdir new_catalog

REM Run the catalog creator
echo.
echo Running catalog creator...
python catalog_creator.py

echo.
echo Done! Check the new_catalog folder for results.
pause
