@echo off
title AI Resume Studio
cd /d %~dp0

if not exist venv (
    echo Please run setup.bat first.
    pause
    exit /b
)

call venv\Scripts\activate
echo Starting AI Resume Studio...
streamlit run app.py
pause