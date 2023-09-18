@echo off
REM Check if pip is installed
pip --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pip...
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    if %errorlevel% neq 0 (
        echo Failed to install pip. Exiting...
        exit /b 1
    )
    echo Pip installed successfully.
)

REM Check if the serial package is installed
pip show pyserial > nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pyserial...
    pip install pyserial
    if %errorlevel% neq 0 (
        echo Failed to install pyserial. Exiting...
        exit /b 1
    )
    echo pyserial installed successfully.
)

REM Check if tkinter package is installed
python -c "import tkinter" > nul 2>&1
if %errorlevel% neq 0 (
    echo Installing tkinter...
    pip install tk
    if %errorlevel% neq 0 (
        echo Failed to install tkinter. Exiting...
        exit /b 1
    )
    echo tkinter installed successfully.
)

REM Run channelTest.py
echo Running channelTest.py...
python ./data/channelTest.py