@echo off
echo ========================================
echo    FinSolve Fixed System Startup
echo ========================================
echo.

echo 1. Testing system first...
python test_fixed_system.py

echo.
echo 2. If tests passed, starting backend...
echo    Backend will run on http://127.0.0.1:8000
echo.

cd app
start "FinSolve Backend" cmd /k "python main.py"

echo 3. Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo 4. Starting frontend...
echo    Frontend will run on http://localhost:8501
echo.

cd ..\frontend
start "FinSolve Frontend" cmd /k "streamlit run app.py"

echo.
echo ========================================
echo    System Started Successfully!
echo ========================================
echo.
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:8501
echo.
echo Test accounts (password: password123):
echo - admin (C-Level access)
echo - finance_user (Finance access)  
echo - marketing_user (Marketing access)
echo - hr_user (HR access)
echo - engineering_user (Engineering access)
echo - employee (General access)
echo.
echo Press any key to exit...
pause > nul