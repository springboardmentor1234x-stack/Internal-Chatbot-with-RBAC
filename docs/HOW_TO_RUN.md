# 🚀 How to Run FinSolve Internal Chatbot

## Method 1: Automatic Startup (Recommended)

### Option A: Using Python Script
```bash
python start_app.py
```

### Option B: Using Batch File (Windows)
```bash
start_app.bat
```

## Method 2: Manual Startup

### Step 1: Start Backend
Open **Terminal 1** and run:
```bash
python simple_backend.py
```
Wait until you see: `Uvicorn running on http://127.0.0.1:8000`

### Step 2: Start Frontend
Open **Terminal 2** and run:
```bash
streamlit run frontend/app.py --server.port=8501
```
Wait until you see: `You can now view your Streamlit app in your browser.`

### Step 3: Open Browser
Go to: http://localhost:8501

## 🔑 Test Accounts
All accounts use password: `password123`

- **admin** → C-Level access (all documents)
- **employee** → General employee access
- **finance_user** → Finance department access
- **marketing_user** → Marketing department access
- **hr_user** → HR department access
- **engineering_user** → Engineering department access

## 🔧 Troubleshooting

### "Cannot connect to backend server"
- Make sure backend is running on port 8000
- Check: http://127.0.0.1:8000/health

### "Port already in use"
- Kill existing processes:
  ```bash
  # Kill Streamlit
  taskkill /f /im python.exe
  
  # Or find specific process
  netstat -ano | findstr :8501
  taskkill /f /pid [PID_NUMBER]
  ```

### Missing Dependencies
```bash
pip install fastapi uvicorn streamlit requests pydantic python-multipart pyjwt passlib[bcrypt] python-dotenv
```

## 📍 URLs
- **Frontend**: http://localhost:8501
- **Backend**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health