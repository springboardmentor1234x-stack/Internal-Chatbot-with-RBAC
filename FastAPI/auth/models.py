from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., description="Username", example="intern_user")
    password: str = Field(..., description="Password", example="intern123")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "intern_user",
                    "password": "intern123"
                },
                {
                    "username": "finance_user",
                    "password": "finance123"
                },
                {
                    "username": "admin_user",
                    "password": "admin123"
                }
            ]
        }
    }


class LoginResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry in seconds")


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="JWT refresh token")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry in seconds")


class UserInfo(BaseModel):
    username: str
    role: str