@echo off
title FinSolve Internal Chatbot - PERMANENT SOLUTION
color 0A
echo.
echo ==========================================
echo   FINSOLVE INTERNAL CHATBOT
echo   PERMANENT WORKING VERSION
echo ==========================================
echo.

REM Kill any existing Python processes
echo Cleaning up existing processes...
taskkill /f /im python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start Backend
echo Starting Backend Server...
start "FinSolve Backend" cmd /k "cd /d %~dp0 && python app/main.py"
timeout /t 5 /nobreak >nul

REM Start Frontend
echo Starting Frontend...
start "FinSolve Frontend" cmd /k "cd /d %~dp0 && streamlit run frontend/app.py --server.port=8501"
timeout /t 3 /nobreak >nul

echo.
echo ==========================================
echo   PROJECT STARTED SUCCESSFULLY!
echo ==========================================
echo.
echo Frontend: http://localhost:8501
echo Backend:  http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo.
echo LOGIN CREDENTIALS:
echo   Username: admin
echo   Password: password123
echo.
echo OTHER TEST ACCOUNTS:
echo   finance_user / password123
echo   marketing_user / password123
echo   hr_user / password123
echo   engineering_user / password123
echo   employee / password123
echo.
echo Opening browser...
timeout /t 2 /nobreak >nul
start http://localhost:8501
echo.
echo PROJECT IS READY!
echo Press any key to exit this window...
pause >nul