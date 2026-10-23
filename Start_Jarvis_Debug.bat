@echo off
cd /d "%~dp0"
title Jarvis Debug Console
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start_Jarvis.ps1" -DebugConsole
pause
