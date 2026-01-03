# 🚀 Pull Request Guide for FinSolve Internal Chatbot

## 📋 **Step-by-Step Pull Request Process**

### **Step 1: Create a Feature Branch**

```bash
# Make sure you're on main branch
git checkout main
git pull origin main

# Create a new feature branch
git checkout -b feature/your-feature-name

# Example:
git checkout -b feature/improve-authentication
git checkout -b fix/frontend-styling
git checkout -b docs/update-readme
```

### **Step 2: Make Your Changes**

1. **Edit files** in VS Code
2. **Test your changes** locally:
   ```bash
   python run.py
   ```
3. **Run tests**:
   ```bash
   python scripts/test_auth.py
   ```

### **Step 3: Format and Clean Code**

```bash
# Format code with black (if installed)
black app/ frontend/

# Or just ensure main files are clean
python -m py_compile app/main.py
python -m py_compile app/auth_utils.py
python -m py_compile frontend/app.py
```

### **Step 4: Commit Your Changes**

```bash
# Add files
git add .

# Commit with descriptive message
git commit -m "feat: improve authentication system"

# Examples of good commit messages:
git commit -m "fix: resolve login endpoint issue"
git commit -m "docs: update README with new features"
git commit -m "refactor: clean up RAG pipeline code"
```

### **Step 5: Push to GitHub**

```bash
# Push your feature branch
git push origin feature/your-feature-name

# Example:
git push origin feature/improve-authentication
```

### **Step 6: Create Pull Request on GitHub**

1. **Go to your GitHub repository**
2. **Click "Compare & pull request"** (appears after push)
3. **Fill out the PR template**:
   - **Title**: Clear, descriptive title
   - **Description**: What changes you made and why
   - **Testing**: How you tested the changes

### **Step 7: Wait for CI and Review**

- **CI will run automatically** (simplified version)
- **Address any feedback** from reviewers
- **Make additional commits** if needed

## 🎯 **Quick Commands for Common Scenarios**

### **Scenario 1: Fix a Bug**
```bash
git checkout -b fix/login-bug
# Make your fixes
git add .
git commit -m "fix: resolve login authentication issue"
git push origin fix/login-bug
# Create PR on GitHub
```

### **Scenario 2: Add New Feature**
```bash
git checkout -b feature/new-role-system
# Add your feature
git add .
git commit -m "feat: add new role-based permissions"
git push origin feature/new-role-system
# Create PR on GitHub
```

### **Scenario 3: Update Documentation**
```bash
git checkout -b docs/update-setup-guide
# Update docs
git add .
git commit -m "docs: improve setup instructions"
git push origin docs/update-setup-guide
# Create PR on GitHub
```

## 📝 **Pull Request Template**

When creating a PR, use this template:

```markdown
## 📋 Description
Brief description of what this PR does.

## 🔄 Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## 🧪 Testing
- [ ] I have tested this locally
- [ ] Backend starts without errors
- [ ] Frontend loads correctly
- [ ] Authentication works
- [ ] Tests pass

## 📸 Screenshots (if applicable)
Add screenshots to help explain your changes.

## 📋 Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] My changes generate no new warnings
```

## 🚨 **Troubleshooting Common Issues**

### **Issue: CI Fails with Linting Errors**
```bash
# Format your code
black app/ frontend/

# Or fix manually and commit again
git add .
git commit -m "fix: resolve linting issues"
git push origin your-branch-name
```

### **Issue: Merge Conflicts**
```bash
# Update your branch with latest main
git checkout main
git pull origin main
git checkout your-branch-name
git merge main

# Resolve conflicts in VS Code
# Then commit the merge
git add .
git commit -m "resolve merge conflicts"
git push origin your-branch-name
```

### **Issue: Need to Update PR**
```bash
# Make more changes
git add .
git commit -m "address review feedback"
git push origin your-branch-name
# PR updates automatically
```

## 🎉 **After PR is Merged**

```bash
# Switch back to main
git checkout main

# Pull the latest changes
git pull origin main

# Delete your feature branch (optional)
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

## 💡 **Best Practices**

1. **Keep PRs small** - Easier to review
2. **Write clear commit messages** - Helps reviewers understand changes
3. **Test locally first** - Ensure everything works
4. **Update documentation** - If you change functionality
5. **Respond to feedback** - Address reviewer comments promptly

## 🔗 **Useful Git Commands**

```bash
# Check current branch
git branch

# See what files changed
git status

# See what changes you made
git diff

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo all changes to a file
git checkout -- filename.py

# See commit history
git log --oneline
```

---

**Happy Contributing! 🚀**