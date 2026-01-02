# FinSolve Internal Chatbot Startup Script
# Run both backend and frontend together

Write-Host "🔥 Starting FinSolve Internal Chatbot" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Yellow
Write-Host "📍 Backend: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "📍 Frontend: http://localhost:8501" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "⏹️  Press Ctrl+C to stop both services" -ForegroundColor Yellow
Write-Host "=" * 50 -ForegroundColor Yellow

try {
    # Start backend in background job
    Write-Host "🚀 Starting Backend..." -ForegroundColor Green
    $backendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        python app/main.py
    }
    
    # Wait a bit for backend to start
    Start-Sleep -Seconds 3
    
    # Start frontend in foreground
    Write-Host "🎨 Starting Frontend..." -ForegroundColor Green
    streamlit run frontend/app.py --server.port=8501
}
catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}
finally {
    # Clean up background job
    if ($backendJob) {
        Write-Host "🛑 Stopping backend..." -ForegroundColor Yellow
        Stop-Job $backendJob -ErrorAction SilentlyContinue
        Remove-Job $backendJob -ErrorAction SilentlyContinue
    }
    Write-Host "✅ Application stopped!" -ForegroundColor Green
}