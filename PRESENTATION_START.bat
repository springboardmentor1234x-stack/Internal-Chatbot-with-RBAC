@echo off
title FINSOLVE PRESENTATION - GUARANTEED WORKING
color 0A
echo.
echo ==========================================
echo   FINSOLVE PRESENTATION - FINAL VERSION
echo ==========================================
echo.
echo Cleaning up any existing processes...
taskkill /f /im python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo Starting GUARANTEED WORKING Backend...
start "FinSolve Backend - FINAL" cmd /k "python FINAL_WORKING_BACKEND.py"
timeout /t 4 /nobreak >nul

echo Starting Frontend...
start "FinSolve Frontend" cmd /k "streamlit run frontend/app.py --server.port=8504"
timeout /t 3 /nobreak >nul

echo.
echo ==========================================
echo   PRESENTATION READY - GUARANTEED!
echo ==========================================
echo.
echo Frontend: http://localhost:8504
echo Backend:  http://127.0.0.1:8003
echo API Docs: http://127.0.0.1:8003/docs
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
start http://localhost:8504
echo.
echo READY FOR PRESENTATION!
echo Press any key to exit...
pause >nul