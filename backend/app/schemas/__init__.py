# 解决循环导入问题
from typing import Optional
from .user import UserResponse

# 导出所有模式
from .user import (
    UserBase, UserCreate, UserLogin, UserResponse, 
    UserUpdate, UserInDB, Token, TokenData, UserRole,UserListResponse,UserLoginResponse,UserLoginResponseBase
)

from .asset import (
    AssetBase, AssetCreate, AssetResponse, 
    AssetUpdate, AssetSummary, AssetWithOwnerResponse, AssetType
)

# 更新AssetWithOwnerResponse中的类型
from .asset import AssetWithOwnerResponse as AssetWithOwnerResponseOriginal

# 重新定义以避免循环导入
class AssetWithOwnerResponse(AssetWithOwnerResponseOriginal):
    owner: Optional[UserResponse] = None

__all__ = [
    # User schemas
    'UserBase', 'UserCreate', 'UserLogin', 'UserResponse',
    'UserUpdate', 'UserInDB', 'Token', 'TokenData', 'UserRole',"UserListResponse","UserLoginResponse","UserLoginResponseBase",
    
    # Asset schemas
    'AssetBase', 'AssetCreate', 'AssetResponse', 
    'AssetUpdate', 'AssetSummary', 'AssetWithOwnerResponse', 'AssetType'
]