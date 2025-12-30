@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    
    
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username}) # New function
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "token_type": "bearer"
    }