# Module 6: Streamlit Frontend

## 🎯 Overview

Beautiful, interactive web interface for the Secure RAG Chatbot with role-based access control.

## ✨ Features

### 1. **User Authentication**
- Login interface with username/password
- JWT token management
- Session persistence
- Role-based welcome messages

### 2. **Chat Interface**
- Real-time message history
- Beautiful chat bubbles (user/assistant)
- Typing indicators
- Clear chat functionality
- Query input with Enter key support

### 3. **User Dashboard**
- Current role display
- Accessible departments
- Query statistics
- Logout option

### 4. **Source Viewer**
- Expandable source cards
- Document name and department
- Relevance scores
- Content previews
- Citation highlighting

### 5. **Confidence Metrics**
- Overall confidence score
- Component breakdown:
  - Retrieval quality
  - Citation coverage
  - Answer completeness
  - Source consistency
- Color-coded confidence levels

### 6. **Settings Panel**
- Switch between Basic/Advanced RAG
- Adjust top-K results (1-10)
- Toggle confidence display
- Clear conversation history

## 🗂️ File Structure

```
module_6_frontend/
├── README.md                    # This file
├── requirements.txt             # Streamlit dependencies
├── app.py                       # Main Streamlit application
├── components/
│   ├── __init__.py
│   ├── auth.py                  # Login/logout components
│   ├── chat.py                  # Chat interface
│   ├── sidebar.py               # Sidebar with user info
│   └── sources.py               # Source display components
├── utils/
│   ├── __init__.py
│   ├── api_client.py            # Backend API wrapper
│   └── session.py               # Session state management
└── assets/
    └── styles.css               # Custom CSS styling
```

## 🚀 Quick Start

### Installation

```bash
cd module_6_frontend
pip install -r requirements.txt
```

### Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Default Test Users

| Username | Password | Role |
|----------|----------|------|
| alice_finance | SecurePass123! | finance_employee |
| bob_marketing | SecurePass123! | marketing_employee |
| admin_user | AdminPass456! | admin |

## 🎨 User Interface

### Login Page
- Clean, centered login form
- Username and password inputs
- Login button with loading state
- Error message display

### Main Chat Interface
- **Left Sidebar**:
  - User profile (username, role)
  - Accessible departments
  - Query statistics
  - Settings panel
  - Logout button

- **Main Area**:
  - Chat history with scrollable view
  - Message bubbles (user/assistant)
  - Query input box
  - Send button

- **Right Panel (on query)**:
  - Confidence metrics
  - Source documents
  - Citation links

## 🔒 Security

- JWT tokens stored in session state
- Auto-logout on token expiration
- Secure password input (masked)
- HTTPS support ready

## 🎨 Styling

- Modern, clean design
- Responsive layout
- Color-coded confidence levels:
  - 🟢 Green: High confidence (>70%)
  - 🟡 Yellow: Medium (50-70%)
  - 🔴 Red: Low (<50%)
- Department badges with colors
- Smooth animations

## 📊 Features Showcase

### Basic RAG Mode
- Fast responses
- Simple prompt template
- Basic source attribution

### Advanced RAG Mode
- LLM-powered responses
- Document re-ranking
- Confidence scoring
- Enhanced citations

## 🧪 Testing

### Manual Testing Checklist

- [ ] Login with valid credentials
- [ ] Login with invalid credentials
- [ ] Send basic query
- [ ] Send advanced query
- [ ] View confidence metrics
- [ ] Expand source documents
- [ ] Switch between basic/advanced
- [ ] Adjust top-K setting
- [ ] Clear chat history
- [ ] Logout and re-login

## 🎯 Next Steps

1. ✅ Create basic Streamlit app structure
2. ✅ Implement login interface
3. ✅ Build chat UI
4. ✅ Add source viewer
5. ✅ Integrate confidence metrics
6. ✅ Add settings panel
7. ⏳ End-to-end testing
8. ⏳ UI/UX improvements

## 📚 Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Components](https://streamlit.io/components)
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

---

**Module 6: Building a beautiful, user-friendly interface for our secure RAG chatbot! 🎨**
