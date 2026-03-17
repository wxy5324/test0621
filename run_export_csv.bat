@echo off
chcp 65001 >nul
set SCRIPT_DIR=%~dp0
python "%SCRIPT_DIR%src\main\python\export_csv.py" %*
