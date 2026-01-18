@echo off
title FinSolve Presentation Setup
color 0A
echo.
echo ========================================
echo   FINSOLVE PRESENTATION STARTUP
echo ========================================
echo.
echo Killing any existing processes...
taskkill /f /im python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo Starting Backend Server...
start "FinSolve Backend" cmd /k "python presentation_ready_backend.py"
timeout /t 4 /nobreak >nul

echo Starting Frontend...
start "FinSolve Frontend" cmd /k "streamlit run frontend/app.py --server.port=8502"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   PRESENTATION READY!
echo ========================================
echo.
echo Frontend: http://localhost:8502
echo Backend:  http://127.0.0.1:8001
echo API Docs: http://127.0.0.1:8001/docs
echo.
echo Test Accounts (password: password123):
echo   admin        - Full Access
echo   finance_user - Finance Access  
echo   marketing_user - Marketing Access
echo   hr_user      - HR Access
echo   engineering_user - Engineering Access
echo   employee     - Basic Access
echo.
echo Opening browser...
start http://localhost:8502
echo.
echo READY FOR PRESENTATION!
echo Press any key to exit...
pause >nul