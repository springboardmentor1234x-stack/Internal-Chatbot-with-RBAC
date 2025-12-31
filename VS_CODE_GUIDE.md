# 🚀 Running FinSolve Chatbot in VS Code

## 📋 Quick Start Methods

### Method 1: Using VS Code Debug/Run (Recommended)

1. **Open VS Code** in this project folder
2. **Press `F5`** or go to `Run and Debug` panel (Ctrl+Shift+D)
3. **Select configuration**:
   - `🚀 Run Backend (FastAPI)` - Starts the API server
   - `🎨 Run Frontend (Streamlit)` - Starts the web interface
   - `🔥 Run Full Application` - Starts both together
   - `⚙️ Setup Database & Vector Store` - Initialize system

### Method 2: Using VS Code Tasks

1. **Press `Ctrl+Shift+P`** (Command Palette)
2. **Type**: `Tasks: Run Task`
3. **Choose**:
   - `📦 Install Dependencies` - Install required packages
   - `🗄️ Setup Database` - Initialize database and users
   - `🚀 Start Backend` - Run FastAPI server
   - `🎨 Start Frontend` - Run Streamlit interface
   - `🔧 Initialize Vector Store` - Setup document search

### Method 3: Using Simple Python Scripts

**In VS Code Terminal:**
```bash
# Start Backend
python run_backend.py

# Start Frontend (in another terminal)
python run_frontend.py
```

### Method 4: Using VS Code Terminal

**Terminal 1 - Backend:**
```bash
python app/main.py
```

**Terminal 2 - Frontend:**
```bash
streamlit run frontend/app.py
```

## 🔧 Initial Setup (First Time Only)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Setup Database
```bash
python setup.py
```

### Step 3: (Optional) Add OpenAI API Key
Edit `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 🎯 VS Code Features Configured

### Debug Configurations
- **F5**: Quick run with debugging
- **Ctrl+F5**: Run without debugging
- **Breakpoints**: Set breakpoints in Python code
- **Variable inspection**: Hover over variables to see values

### Tasks (Ctrl+Shift+P → Tasks: Run Task)
- Install dependencies
- Setup database
- Start services
- Initialize vector store

### Extensions Recommended
- **Python** - Python language support
- **Python Debugger** - Debugging support
- **Pylance** - Advanced Python language server
- **autoDocstring** - Generate docstrings
- **GitLens** - Git integration

## 📱 Access Points

Once running:
- **Frontend UI**: http://localhost:8501
- **Backend API**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs
- **API Redoc**: http://127.0.0.1:8000/redoc

## 🔐 Test Accounts

| Username | Password | Role |
|----------|----------|------|
| `admin` | `password123` | Admin |
| `finance_user` | `password123` | Finance |
| `marketing_user` | `password123` | Marketing |
| `clevel_user` | `password123` | C-Level |

## 🐛 Debugging in VS Code

### Set Breakpoints
1. Click in the left margin next to line numbers
2. Red dots indicate breakpoints
3. Run with F5 to hit breakpoints

### Debug Backend API
1. Set breakpoints in `app/routes.py` or `app/main.py`
2. Run `🚀 Run Backend (FastAPI)` configuration
3. Make API calls from frontend or curl
4. VS Code will pause at breakpoints

### Debug Frontend
1. Set breakpoints in `frontend/app.py`
2. Run `🎨 Run Frontend (Streamlit)` configuration
3. Interact with the web interface
4. VS Code will pause at breakpoints

## 📊 VS Code Integrated Terminal

### Multiple Terminals
- **Ctrl+Shift+`**: New terminal
- **Ctrl+`**: Toggle terminal panel
- Run backend in one terminal, frontend in another

### Terminal Commands
```bash
# Check if backend is running
curl http://127.0.0.1:8000/

# Test login
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password123"

# Setup vector store
curl -X GET http://127.0.0.1:8000/api/v1/setup-vector-store
```

## 🔄 Development Workflow

### 1. Code Changes
- Edit Python files in VS Code
- Auto-reload is enabled for both backend and frontend
- Changes are reflected immediately

### 2. Testing
- Use VS Code debugger to step through code
- Set breakpoints to inspect variables
- Use integrated terminal for API testing

### 3. Git Integration
- VS Code has built-in Git support
- Use Source Control panel (Ctrl+Shift+G)
- Commit, push, pull directly from VS Code

## 🚨 Troubleshooting

### Backend Won't Start
1. Check Python interpreter (Ctrl+Shift+P → Python: Select Interpreter)
2. Ensure dependencies installed: `pip install -r requirements.txt`
3. Check terminal for error messages

### Frontend Won't Start
1. Install Streamlit: `pip install streamlit`
2. Check if port 8501 is available
3. Try running: `streamlit run frontend/app.py`

### Import Errors
1. Check PYTHONPATH in VS Code settings
2. Ensure you're in the project root directory
3. Restart VS Code Python language server

### Database Issues
1. Run setup: `python setup.py`
2. Check if `project.db` file exists
3. Delete `project.db` and run setup again

## 💡 Pro Tips

### VS Code Shortcuts
- **F5**: Start debugging
- **Ctrl+F5**: Run without debugging
- **Ctrl+Shift+`**: New terminal
- **Ctrl+Shift+P**: Command palette
- **Ctrl+Shift+D**: Debug panel

### Code Navigation
- **Ctrl+Click**: Go to definition
- **F12**: Go to definition
- **Shift+F12**: Find all references
- **Ctrl+T**: Go to symbol

### Multi-cursor Editing
- **Alt+Click**: Add cursor
- **Ctrl+Alt+↑/↓**: Add cursor above/below
- **Ctrl+D**: Select next occurrence

---

**Happy Coding! 🎉**