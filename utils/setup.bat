@echo off
title AI Resume Studio Setup
echo Creating virtual environment...
python -m venv venv

echo Activating...
call venv\Scripts\activate

echo Installing packages (this may take time)...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Setup complete.
echo Now use Run App.bat to start the app.
pause