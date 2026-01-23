# 🚀 FinSolve Internal Chatbot - PERMANENT USAGE GUIDE

## 🎯 GUARANTEED TO WORK EVERY TIME

This guide ensures your project works permanently, even after restarting your computer.

## 📋 ONE-TIME SETUP (Do this once)

### Step 1: Run Setup
```bash
python SETUP_PROJECT.py
```

### Step 2: Verify Installation
The setup script will:
- ✅ Install all required packages
- ✅ Check all project files
- ✅ Test imports
- ✅ Create desktop shortcut (optional)

## 🚀 DAILY USAGE (Every time you want to run the project)

### Method 1: Batch File (EASIEST)
```bash
# Double-click this file:
START_PROJECT.bat
```

### Method 2: Python Script
```bash
python start_project.py
```

### Method 3: Manual (if needed)
```bash
# Terminal 1: Backend
python app/main.py

# Terminal 2: Frontend
streamlit run frontend/app.py --server.port=8501
```

## 📍 ACCESS INFORMATION

**URLs:**
- **Frontend**: http://localhost:8501
- **Backend**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs

**Login Credentials:**
- **Username**: `admin`
- **Password**: `password123`

**Other Test Accounts:**
- `finance_user` / `password123` - Finance access
- `marketing_user` / `password123` - Marketing access
- `hr_user` / `password123` - HR access
- `engineering_user` / `password123` - Engineering access
- `employee` / `password123` - Basic access

## 🔧 TROUBLESHOOTING

### Problem: "Cannot connect to backend server"
**Solution:**
1. Close all browser tabs
2. Run `START_PROJECT.bat` again
3. Wait 10 seconds before opening browser

### Problem: "Port already in use"
**Solution:**
1. Close all command prompt windows
2. Run `START_PROJECT.bat` (it will clean up automatically)

### Problem: "Module not found"
**Solution:**
```bash
python SETUP_PROJECT.py
```

### Problem: "Permission denied"
**Solution:**
1. Run Command Prompt as Administrator
2. Navigate to project folder
3. Run `START_PROJECT.bat`

## 📁 PROJECT STRUCTURE

```
FinSolve-Internal-Chatbot/
├── START_PROJECT.bat          # ← Main startup file
├── start_project.py           # ← Alternative startup
├── SETUP_PROJECT.py           # ← One-time setup
├── app/
│   ├── main.py               # ← Fixed backend
│   ├── database.py           # ← User database
│   ├── auth_utils.py         # ← Authentication
│   ├── routes.py             # ← API routes
│   └── rag_pipeline_simple_working.py  # ← RAG system
├── frontend/
│   └── app.py                # ← Streamlit frontend
└── data/                     # ← Document storage
```

## ✅ PERMANENT FEATURES

### 🔐 Authentication System
- JWT-based login/logout
- Role-based access control
- Session management
- Password hashing

### 🤖 RAG Pipeline
- Document retrieval
- AI-powered responses
- Accuracy scoring
- Source citations

### 👥 User Roles
- **C-Level**: Full access to all documents
- **Finance**: Financial reports only
- **Marketing**: Marketing data only
- **HR**: Employee policies only
- **Engineering**: Technical documentation only
- **Employee**: Basic company information only

### 📊 Analytics
- Chat history
- Usage statistics
- Accuracy metrics
- Performance tracking

## 🎭 DEMO SCENARIOS

### Scenario 1: Financial Query (Admin)
1. Login as `admin`
2. Ask: "What are our Q4 financial results?"
3. Shows: Financial data with high accuracy

### Scenario 2: Role Restriction (Employee)
1. Login as `employee`
2. Ask: "What are our financial results?"
3. Shows: Access denied message

### Scenario 3: HR Query (HR User)
1. Login as `hr_user`
2. Ask: "What are the employee benefits?"
3. Shows: HR policy information

## 🚀 SUBMISSION READY

Your project includes:
- ✅ Complete working backend
- ✅ Professional frontend interface
- ✅ Role-based access control
- ✅ AI-powered chat system
- ✅ Comprehensive documentation
- ✅ Easy startup process
- ✅ Permanent configuration

## 📞 SUPPORT

If you encounter any issues:
1. Run `SETUP_PROJECT.py` first
2. Try `START_PROJECT.bat`
3. Check the troubleshooting section above

---

## 🎉 YOUR PROJECT IS PERMANENTLY READY!

**Just run `START_PROJECT.bat` anytime you want to use your project!**