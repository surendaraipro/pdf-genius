"""
Pydantic schemas for user data validation
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Schema for user creation"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        return v

class UserUpdate(BaseModel):
    """Schema for user updates"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    """Schema for user responses"""
    id: int
    subscription_tier: str
    subscription_status: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Schema for authentication tokens"""
    access_token: str
    token_type: str
    user_id: int
    email: str
    subscription_tier: str

class TokenData(BaseModel):
    """Schema for token payload"""
    sub: Optional[str] = None

class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr

class PasswordReset(BaseModel):
    """Schema for password reset"""
    token: str
    new_password: str

class SubscriptionUpdate(BaseModel):
    """Schema for subscription updates"""
    tier: str
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None

class UsageStats(BaseModel):
    """Schema for usage statistics"""
    conversions_used: int
    conversions_limit: int
    ai_questions_used: int
    ai_questions_limit: int
    subscription_tier: str
    reset_date: datetime
    
    @property
    def conversions_remaining(self) -> int:
        return max(0, self.conversions_limit - self.conversions_used)
    
    @property
    def ai_questions_remaining(self) -> int:
        return max(0, self.ai_questions_limit - self.ai_questions_used)
    
    @property
    def conversions_percentage(self) -> float:
        if self.conversions_limit == 0:
            return 0
        return (self.conversions_used / self.conversions_limit) * 100
    
    @property
    def ai_questions_percentage(self) -> float:
        if self.ai_questions_limit == 0:
            return 0
        return (self.ai_questions_used / self.ai_questions_limit) * 100

class APIKeyCreate(BaseModel):
    """Schema for API key creation"""
    name: str

class APIKeyResponse(BaseModel):
    """Schema for API key response"""
    id: int
    key: str
    name: str
    is_active: bool
    last_used: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True