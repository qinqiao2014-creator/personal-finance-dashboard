
from typing import Optional
from .user import UserResponse

# 导出所有模式
from .user import (
    UserBase, UserCreate, UserLogin, UserResponse, 
    UserUpdate, UserInDB, Token, TokenData, UserRole, UserListResponse, UserLoginResponse, UserLoginResponseBase
)

from .asset import (
    AssetBase, AssetCreate, AssetResponse, 
    AssetUpdate, AssetSummary, AssetListResponse ,AssetHistoryResponse,AssetCreateList
)

from .diagnosis_report import (DiagnosisReportResponse,DiagnosisReportList,DiagnosisReportCreate)

__all__ = [
    # User schemas
    'UserBase', 'UserCreate', 'UserLogin', 'UserResponse',
    'UserUpdate', 'UserInDB', 'Token', 'TokenData', 'UserRole', 'UserListResponse', 'UserLoginResponse', 'UserLoginResponseBase',
    
    # Asset schemas
    'AssetBase', 'AssetCreate', 'AssetResponse', 
    'AssetUpdate', 'AssetSummary', 'AssetListResponse' ,"AssetHistoryResponse","AssetCreateList",

    # diagnosis_report
    "DiagnosisReportResponse","DiagnosisReportList","DiagnosisReportCreate"
]