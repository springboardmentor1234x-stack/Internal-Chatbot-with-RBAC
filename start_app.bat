@echo off
echo ========================================
echo FinSolve Internal Chatbot Startup
echo ========================================
echo.
echo Starting Backend Server...
start "Backend" cmd /k "python simple_backend.py"
echo.
echo Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak >nul
echo.
echo Starting Frontend...
start "Frontend" cmd /k "streamlit run frontend/app.py --server.port=8501"
echo.
echo ========================================
echo Services Started!
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:8501
echo API Docs: http://127.0.0.1:8000/docs
echo ========================================
echo.
echo Press any key to exit...
pause >nul