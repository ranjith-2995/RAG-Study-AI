@echo off
title STUDY MATE AI - Backend Server
echo ============================================================
echo   STUDY MATE AI - Intelligent Study Notes Assistant
echo   Starting Backend Server on http://127.0.0.1:8000
echo ============================================================
echo.
cd /d "%~dp0"
python backend\main.py
pause

