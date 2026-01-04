# Pull Request Guide - FinSolve Internal Chatbot

## 📋 Pre-submission Checklist

Before creating a pull request, ensure you have completed the following:

### ✅ Code Quality
- [ ] Code is formatted with `black --line-length 88`
- [ ] No linting errors from `flake8`
- [ ] All imports are working correctly
- [ ] No syntax errors or undefined variables

### ✅ Testing
- [ ] Backend starts without errors (`python app/main.py`)
- [ ] Frontend loads successfully (`streamlit run frontend/app.py`)
- [ ] Authentication works with test accounts
- [ ] Chat functionality responds correctly
- [ ] Role-based access control is working

### ✅ Documentation
- [ ] Code changes are documented
- [ ] README.md is updated if needed
- [ ] New features are explained

## 🚀 How to Create a Pull Request

### 1. Format Your Code
```bash
# Install black if not already installed
pip install black

# Format all Python files
black . --line-length 88

# Check for linting issues
pip install flake8
flake8 . --max-line-length=88
```

### 2. Test Your Changes
```bash
# Test backend
python app/main.py

# Test frontend (in another terminal)
streamlit run frontend/app.py

# Test authentication
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password123"
```

### 3. Commit Your Changes
```bash
git add .
git commit -m "feat: describe your changes

- Bullet point 1
- Bullet point 2
- Bullet point 3"
```

### 4. Push and Create PR
```bash
git push origin your-branch-name
```

Then go to GitHub and create a pull request with:
- Clear title describing the change
- Detailed description of what was changed
- Screenshots if UI changes were made
- Reference to any issues being fixed

## 🔧 Common Issues and Solutions

### Black Formatting Issues
```bash
# Fix common formatting issues
black . --line-length 88
```

### Import Errors
```bash
# Test imports
python -c "import sys; sys.path.append('app'); import main"
```

### Authentication Issues
- Ensure `passlib[bcrypt]` is installed
- Check that JWT tokens are properly configured
- Verify database connections

### Frontend Issues
- Ensure Streamlit is installed: `pip install streamlit`
- Check backend is running on port 8000
- Verify CORS is properly configured

## 📝 Commit Message Format

Use conventional commits:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for formatting changes
- `refactor:` for code refactoring
- `test:` for adding tests

Example:
```
feat: add role-based document viewer

- Added document viewer with role-based access control
- Enhanced UI with expandable document sections
- Improved security by hiding sensitive test credentials
- Fixed authentication flow with proper JWT handling
```

## 🎯 Review Criteria

Your PR will be reviewed for:
- Code quality and formatting
- Functionality and testing
- Security best practices
- Documentation completeness
- Performance considerations

## 🆘 Getting Help

If you encounter issues:
1. Check the CI pipeline logs
2. Run tests locally first
3. Review this guide
4. Ask for help in the PR comments