from pydantic import BaseModel, EmailStr, Field

# PUBLIC_INTERFACE
class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="Password min length 8")
    full_name: str | None = Field(None, description="Optional full name")

# PUBLIC_INTERFACE
class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str

# PUBLIC_INTERFACE
class UserPublic(BaseModel):
    """Public user view for API responses."""
    id: int
    email: EmailStr
    full_name: str | None
    is_verified: bool
    allow_analytics: bool
    private_account: bool

    class Config:
        from_attributes = True

# PUBLIC_INTERFACE
class UserUpdate(BaseModel):
    """Schema for profile updates and privacy settings."""
    full_name: str | None = None
    allow_analytics: bool | None = None
    private_account: bool | None = None

# PUBLIC_INTERFACE
class TokenResponse(BaseModel):
    """Access token response payload."""
    access_token: str
    token_type: str = "bearer"
