# FinSolve Project Structure

## 📁 Organized Project Layout

```
finsolve-chatbot/
├── 📁 app/                          # Main application code
│   ├── main.py                      # FastAPI backend entry point
│   ├── routes.py                    # API routes and endpoints
│   ├── database.py                  # Database operations
│   ├── auth_utils.py                # Authentication utilities
│   ├── audit_logger.py              # Audit logging system
│   ├── rag_pipeline_enhanced_real.py # RAG pipeline with document access
│   ├── error_handler.py             # Error handling utilities
│   ├── chat_history_manager.py      # Chat history management
│   ├── query_optimizer.py           # Query optimization
│   ├── redis_cache.py               # Redis caching
│   └── settings.json                # Application settings
│
├── 📁 frontend/                     # Streamlit frontend
│   ├── app.py                       # Main frontend application
│   ├── app_enhanced.py              # Enhanced frontend features
│   └── error_handler_frontend.py    # Frontend error handling
│
├── 📁 data/                         # Data storage
│   ├── 📁 raw/                      # Raw documents
│   │   ├── employee_handbook.md
│   │   ├── quarterly_financial_report.md
│   │   ├── market_report_q4_2024.md
│   │   └── engineering_master_doc.md
│   ├── 📁 processed/                # Processed documents
│   └── 📁 chroma/                   # Vector database
│
├── 📁 docs/                         # Documentation
│   ├── README.md                    # Main project documentation
│   ├── HOW_TO_RUN.md               # Setup and running instructions
│   ├── AUDIT_SYSTEM_GUIDE.md       # Audit system documentation
│   ├── AUDIT_IMPLEMENTATION_SUMMARY.md # Audit implementation details
│   ├── SECURITY_ACCURACY_ENHANCEMENT_GUIDE.md # Security features
│   ├── ERROR_HANDLING_GUIDE.md     # Error handling documentation
│   ├── PRESENTATION_GUIDE.md       # Presentation instructions
│   ├── PERMANENT_USAGE_GUIDE.md    # Usage guidelines
│   └── [other documentation files]
│
├── 📁 tests/                        # Test files
│   ├── test_audit_system.py        # Audit system tests
│   ├── test_accuracy_*.py          # Accuracy testing
│   ├── test_login_*.py             # Login testing
│   ├── test_security_*.py          # Security testing
│   ├── comprehensive_test.py       # Comprehensive system tests
│   └── [other test files]
│
├── 📁 scripts/                      # Utility scripts
│   ├── start_with_audit.py         # Main startup script with audit
│   ├── start_app.py                # Basic startup script
│   ├── setup_*.py                  # Setup scripts
│   ├── run.py                      # Run script
│   ├── *.bat                       # Windows batch files
│   └── [other utility scripts]
│
├── 📁 config/                       # Configuration files
│   ├── requirements.txt            # Main dependencies
│   ├── requirements_permanent.txt  # Production dependencies
│   ├── requirements_simple.txt     # Minimal dependencies
│   └── .env                        # Environment variables
│
├── 📁 archive/                      # Archived/deprecated files
│   ├── backend_only.py             # Old backend versions
│   ├── frontend_only.py            # Old frontend versions
│   ├── debug_*.py                  # Debug scripts
│   ├── accuracy_improvements.py    # Old improvement scripts
│   └── [other deprecated files]
│
├── 📁 logs/                         # Application logs
│   ├── finsolve_detailed.log
│   └── finsolve_errors.log
│
├── 📁 .vscode/                      # VS Code settings
├── 📁 .github/                      # GitHub workflows
├── 📁 .git/                         # Git repository
│
├── project.db                       # Main SQLite database
├── audit_logs.db                    # Audit logging database
├── .gitignore                       # Git ignore rules
└── PROJECT_STRUCTURE.md             # This file
```

## 🚀 Quick Start

### 1. Main Application
```bash
# Start with audit system (recommended)
python scripts/start_with_audit.py

# Or start basic version
python scripts/start_app.py
```

### 2. Testing
```bash
# Test audit system
python tests/test_audit_system.py

# Test accuracy
python tests/test_accuracy_enhanced.py

# Comprehensive tests
python tests/comprehensive_test.py
```

### 3. Setup
```bash
# Install dependencies
pip install -r config/requirements.txt

# Setup project
python scripts/SETUP_PROJECT.py
```

## 📋 File Categories

### Core Application Files
- **Backend**: `app/main.py`, `app/routes.py`, `app/database.py`
- **Frontend**: `frontend/app.py`
- **Authentication**: `app/auth_utils.py`
- **Audit System**: `app/audit_logger.py`

### Documentation
- **User Guides**: `docs/HOW_TO_RUN.md`, `docs/PERMANENT_USAGE_GUIDE.md`
- **Technical Docs**: `docs/AUDIT_SYSTEM_GUIDE.md`, `docs/ERROR_HANDLING_GUIDE.md`
- **Implementation**: `docs/AUDIT_IMPLEMENTATION_SUMMARY.md`

### Testing & Quality
- **System Tests**: `tests/comprehensive_test.py`
- **Feature Tests**: `tests/test_audit_system.py`, `tests/test_accuracy_*.py`
- **Security Tests**: `tests/test_security_*.py`

### Configuration & Setup
- **Dependencies**: `config/requirements*.txt`
- **Environment**: `config/.env`
- **Setup Scripts**: `scripts/setup_*.py`

### Utilities & Scripts
- **Startup**: `scripts/start_with_audit.py`, `scripts/start_app.py`
- **Batch Files**: `scripts/*.bat`
- **Utilities**: `scripts/run.py`

## 🎯 Key Benefits of This Structure

### ✅ Clean Organization
- **Logical grouping** of related files
- **Easy navigation** through project structure
- **Clear separation** of concerns

### ✅ Better Development Experience
- **Quick access** to relevant files
- **Reduced clutter** in root directory
- **Intuitive folder names**

### ✅ Maintainability
- **Easy to find** specific functionality
- **Simple to add** new features
- **Clear documentation** structure

### ✅ Professional Structure
- **Industry standard** organization
- **Scalable** for future growth
- **Team-friendly** layout

## 🔧 Usage Notes

### Main Entry Points
- **Production**: `python scripts/start_with_audit.py`
- **Development**: `python scripts/start_app.py`
- **Testing**: `python tests/test_audit_system.py`

### Configuration
- **Dependencies**: Check `config/requirements.txt`
- **Environment**: Configure `config/.env`
- **Settings**: Modify `app/settings.json`

### Documentation
- **Start here**: `docs/README.md`
- **Setup guide**: `docs/HOW_TO_RUN.md`
- **Features**: `docs/AUDIT_SYSTEM_GUIDE.md`

This organized structure makes the project much more professional and easier to navigate!