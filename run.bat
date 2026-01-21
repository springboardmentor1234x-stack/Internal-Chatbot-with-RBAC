@echo off
echo Starting Secure RAG Chatbot...
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Could not activate virtual environment
    echo Please ensure venv exists by running: python -m venv venv
    pause
    exit /b 1
)

echo Starting Backend Server...
start "Backend" cmd /k "call %CD%\venv\Scripts\activate.bat && cd module_4_backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 5 /nobreak

echo Starting Frontend Server...
start "Frontend" cmd /k "call %CD%\venv\Scripts\activate.bat && cd module_6_frontend && streamlit run app.py --server.port 8501"

echo.
echo Both servers started!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:8501
echo.
