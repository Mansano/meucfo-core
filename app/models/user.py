# app/models/user.py

from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None
    document: Optional[str] = None
    type: Optional[str] = "PF"

class UserCreate(UserBase):
    password: str
    password_confirmation: str
    
    @model_validator(mode='after')
    def passwords_match(self):
        if self.password != self.password_confirmation:
            raise ValueError('As senhas não coincidem')
        return self
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('A senha deve ter pelo menos 8 caracteres')
        # Adicione mais validações de força se necessário
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserInDB(UserBase):
    id: int
    password: str
    profile: int = 1  # 1=User, 2=Admin
    created_at: datetime
    last_login: Optional[datetime] = None
    
    @property
    def is_admin(self) -> bool:
        return self.profile == 2
        
    @property
    def is_approved(self) -> bool:
        return True # Frontend não tem is_approved, auto-aprova
    
    class Config:
        from_attributes = True

class UserResponse(UserInDB):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    is_admin: Optional[bool] = False
