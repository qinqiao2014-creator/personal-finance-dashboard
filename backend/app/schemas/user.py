from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional
from datetime import datetime
from enum import Enum

# 用户角色枚举
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

# 基础用户模式
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="john_doe")
    email: EmailStr = Field(..., example="john@example.com")

# 创建用户请求（注册）
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, example="securepassword123")
    role: UserRole = Field(default="user", description="用户角色") 

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "securepassword123",
                "role": "user"
            }
        }

# 登录请求
class UserLogin(BaseModel):
    username:  Optional[str]  = Field(None, example="john_doe")
    email: Optional[str] = Field(None, example="john@example.com")
    password: str = Field(..., example="securepassword123")


    @model_validator(mode='before')
    def validate_login_identifier(cls, values):
        # 在 Pydantic V2 中，values 是原始输入数据
        if isinstance(values, dict):
            username = values.get('username')
            email = values.get('email')
            password = values.get('password')
            
            # 检查密码是否提供
            if not password:
                raise ValueError('密码是必填项')
            
            # 检查至少提供一个登录标识符
            if not username and not email:
                raise ValueError('必须提供用户名或邮箱')
            
            # 检查不能同时提供用户名和邮箱
            if username and email:
                raise ValueError('只能提供用户名或邮箱其中之一')
        
        return values

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email":"john_doe@email.com",
                "password": "securepassword123"
            }
        }


# 用户响应（返回给前端的数据）
class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True  # 允许从ORM对象转换

#用户登录响应(登录时返回给前端的数据)
class UserLoginResponseBase(BaseModel):
    id: int
    role:UserRole
    username: str
    email: str
class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str
    user:UserLoginResponseBase

    class Config:
        from_attributes = True  # 允许从ORM对象转换    

# 用户更新请求
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, example="new_username")
    email: Optional[EmailStr] = Field(None, example="new_email@example.com")
    password: Optional[str] = Field(None, min_length=6, example="newpassword123")

# 用户信息（包含敏感信息，用于内部使用）
class UserInDB(UserResponse):
    hashed_password: str

# 查询所有用户
class UserListResponse(BaseModel):
    total:int
    items:list[UserResponse]

# Token响应（登录成功后返回）
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }

# Token数据（存储在JWT中的信息）
class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None