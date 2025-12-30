from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import jwt, JWTError

app = FastAPI(
    title="Fintech Internal RBAC Chatbot",
    description="Role-Based Access Control for Fintech Data",
    version="1.0.0"
)

SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

PERMISSION_MAP = {
    "admin": ["view_policy", "view_salary", "search", "manage_users"],
    "finance_manager": ["view_policy", "view_salary", "search"],
    "hr_manager": ["view_policy", "view_salary", "search"],
    "intern": ["view_policy", "search"]
}

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user_role(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        if role is None:
            raise HTTPException(status_code=401, detail="Invalid token: Role missing")
        return role
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

def require_permission(required_perm: str):
    def decorator(role: str = Depends(get_current_user_role)):
        user_perms = PERMISSION_MAP.get(role.lower(), [])
        if required_perm not in user_perms:
            raise HTTPException(
                status_code=403, 
                detail=f"Access Denied: Missing {required_perm} permission"
            )
        return True
    return decorator

@app.get("/")
def read_root():
    return {"project": "Fintech RBAC Chatbot", "status": "Online"}

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username.lower()
    if "admin" in username:
        role = "admin"
    elif "finance" in username:
        role = "finance_manager"
    elif "hr" in username:
        role = "hr_manager"
    else:
        role = "intern"
        
    access_token = create_access_token(data={"sub": form_data.username, "role": role})
    return {"access_token": access_token, "token_type": "bearer", "role": role}

@app.get("/search")
async def search_documents(authorized: bool = Depends(require_permission("search"))):
    return {"message": "Success! You have permission to search documents."}

@app.get("/salary-data")
async def view_salary(authorized: bool = Depends(require_permission("view_salary"))):
    return {"message": "Confidential financial/salary data accessed."}

@app.get("/system-settings")
async def admin_only_endpoint(authorized: bool = Depends(require_permission("manage_users"))):
    return {"message": "Welcome Admin. You have full system access."}

@app.post("/refresh")
async def refresh(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        new_access_token = create_access_token(data={"sub": username, "role": "intern"}) 
        return {"access_token": new_access_token, "token_type": "bearer"}
    except:
        raise HTTPException(status_code=401, detail="Invalid refresh token")