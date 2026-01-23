# 🚀 FinSolve in VS Code - Complete Guide

## 🎯 QUICK START IN VS CODE

### Method 1: Using F5 (Debug/Run)
1. **Open VS Code** in this project folder
2. **Press F5** or go to Run → Start Debugging
3. **Select**: "🚀 Run FinSolve (Full App)"
4. **Wait 10 seconds** for both services to start
5. **Browser opens automatically** at http://localhost:8501

### Method 2: Using VS Code Terminal
```bash
# In VS Code terminal, run:
python run_in_vscode.py
```

### Method 3: Separate Terminals (Recommended for Development)
1. **Terminal 1**: `python backend_only.py`
2. **Terminal 2**: `python frontend_only.py`

## 🔧 VS CODE FEATURES ADDED

### Debug Configurations (F5 Menu)
- **🚀 Run FinSolve (Full App)** - Starts both backend and frontend
- **🔧 Backend Only** - Just the API server
- **🎨 Frontend Only** - Just the Streamlit app
- **🔍 Debug Backend** - Backend with debugging enabled

### Tasks (Ctrl+Shift+P → "Tasks: Run Task")
- **🚀 Start FinSolve Backend** - Backend in new terminal
- **🎨 Start FinSolve Frontend** - Frontend in new terminal
- **🔧 Install Dependencies** - Install all required packages
- **🧪 Test Backend Connection** - Check if backend is running

### VS Code Settings
- ✅ Python interpreter configured
- ✅ Terminal settings optimized
- ✅ File associations set up
- ✅ Exclude unnecessary files

## 📍 ACCESS INFORMATION

**URLs:**
- **Frontend**: http://localhost:8501
- **Backend**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs

**Login:**
- **Username**: `admin`
- **Password**: `password123`

## 🎭 DEVELOPMENT WORKFLOW IN VS CODE

### For Daily Development:
1. **Open VS Code** in project folder
2. **Press Ctrl+Shift+P** → "Tasks: Run Task"
3. **Select**: "🚀 Start FinSolve Backend"
4. **Open new terminal** (Ctrl+Shift+`)
5. **Run**: `python frontend_only.py`
6. **Start coding!**

### For Debugging:
1. **Press F5**
2. **Select**: "🔍 Debug Backend"
3. **Set breakpoints** in your code
4. **Test API endpoints** with debugging

### For Testing:
1. **Press Ctrl+Shift+P** → "Tasks: Run Task"
2. **Select**: "🧪 Test Backend Connection"
3. **Check output** for connection status

## 🔍 TROUBLESHOOTING IN VS CODE

### Problem: "Module not found"
**Solution:**
1. **Press Ctrl+Shift+P** → "Tasks: Run Task"
2. **Select**: "🔧 Install Dependencies"
3. **Wait for installation** to complete

### Problem: "Port already in use"
**Solution:**
1. **Press Ctrl+C** in all terminals
2. **Close all terminals** (trash can icon)
3. **Start again** with F5

### Problem: "Python interpreter not found"
**Solution:**
1. **Press Ctrl+Shift+P** → "Python: Select Interpreter"
2. **Choose your Python installation**
3. **Restart VS Code**

## 📁 VS CODE PROJECT STRUCTURE

```
FinSolve-Internal-Chatbot/
├── .vscode/
│   ├── launch.json          # ← F5 debug configurations
│   ├── tasks.json           # ← Task definitions
│   └── settings.json        # ← VS Code settings
├── run_in_vscode.py         # ← Main VS Code runner
├── backend_only.py          # ← Backend only
├── frontend_only.py         # ← Frontend only
├── app/
│   ├── main.py             # ← FastAPI backend
│   ├── routes.py           # ← API endpoints
│   └── ...
├── frontend/
│   └── app.py              # ← Streamlit frontend
└── VS_CODE_GUIDE.md        # ← This guide
```

## ⚡ KEYBOARD SHORTCUTS

- **F5** - Start debugging (run full app)
- **Ctrl+F5** - Run without debugging
- **Ctrl+Shift+P** - Command palette (access tasks)
- **Ctrl+Shift+`** - New terminal
- **Ctrl+C** - Stop running process

## 🎯 QUICK COMMANDS

```bash
# Install dependencies
python -m pip install fastapi uvicorn streamlit requests pyjwt passlib[bcrypt]

# Run full application
python run_in_vscode.py

# Run backend only
python backend_only.py

# Run frontend only
python frontend_only.py

# Test connection
python -c "import requests; print(requests.get('http://127.0.0.1:8000/health').json())"
```

## ✅ VS CODE READY!

Your FinSolve project is now fully configured for VS Code development!

**Just press F5 and select "🚀 Run FinSolve (Full App)" to get started!**