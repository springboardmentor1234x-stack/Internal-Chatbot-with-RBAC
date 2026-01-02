@echo off
title FinSolve Internal Chatbot
color 0A

echo.
echo ========================================
echo    FinSolve Internal Chatbot
echo ========================================
echo.
echo Starting both Backend and Frontend...
echo.
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:8501
echo API Docs: http://127.0.0.1:8000/docs
echo.
echo Press Ctrl+C to stop both services
echo ========================================
echo.

REM Start backend in background
echo Starting Backend...
start "FinSolve Backend" /min cmd /c "python app/main.py"

REM Wait a few seconds for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend in foreground
echo Starting Frontend...
streamlit run frontend/app.py --server.port=8501

REM If we get here, frontend was closed
echo.
echo Frontend closed. Backend may still be running.
echo Check Task Manager if needed.
pause