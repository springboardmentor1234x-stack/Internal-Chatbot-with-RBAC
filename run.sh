#!/bin/bash
# Quick Start Script for Secure RAG Chatbot

echo "🚀 Starting Secure RAG Chatbot..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 setup.py"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo "${GREEN}✓ Virtual environment activated${NC}"

# Start Backend
echo ""
echo "${BLUE}Starting Backend Server...${NC}"
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "Waiting for backend to initialize..."
sleep 5

# Start Frontend
echo ""
echo "${BLUE}Starting Frontend Server...${NC}"
cd frontend
streamlit run app.py --server.port 8501 &
FRONTEND_PID=$!
cd ..

echo ""
echo "${GREEN}✓ Both servers started!${NC}"
echo ""
echo "📡 Backend API:  http://localhost:8000"
echo "🎨 Frontend UI:  http://localhost:8501"
echo "📚 API Docs:     http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Trap Ctrl+C and kill both processes
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

# Wait for processes
wait
