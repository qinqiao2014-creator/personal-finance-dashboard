from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

# 资产类型枚举（与models/asset.py保持一致）
class AssetType(str, Enum):
    STOCK = "stock"          # 股票
    FUND = "fund"            # 基金
    BANK = "bank"            # 银行存款
    CRYPTO = "crypto"        # 加密货币
    INSURANCE = "insurance"  # 保险
    REAL_ESTATE = "real_estate"  # 房地产
    OTHER = "other"          # 其他 

# 资产基础模式
class AssetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="我的储蓄账户")
    type: AssetType
    amount: float = Field(..., gt=0, description="资产金额必须大于0", example=10000.50)
    description: Optional[str] = Field(None, max_length=500, example="工商银行定期存款")

# 创建资产请求
class AssetCreate(AssetBase):
    class Config:
        json_schema_extra = {
            "example": {
                "name": "股票",
                "type":AssetType.STOCK,
                "amount": 50000.0,
                "description": "股票市值"
            }
        }

# 资产响应
class AssetResponse(AssetBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # 允许从ORM对象转换

# 资产更新请求
class AssetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, example="更新后的资产名")
    type: Optional[AssetType] = None
    amount: Optional[float] = Field(None, gt=0, example=15000.0)
    description: Optional[str] = Field(None, max_length=500, example="更新后的描述")

# 资产统计响应
class AssetSummary(BaseModel):
    total_assets: float = Field(..., example=250000.0)
    assets_by_type: dict = Field(..., example={"bank": 50000.0, "stock": 200000.0})
    asset_count: int = Field(..., example=5)

# 资产列表响应
class AssetListResponse(BaseModel):
    total: int
    items: list[AssetResponse]

# 带用户信息的资产响应（避免循环导入，使用字符串类型）
class AssetWithOwnerResponse(AssetResponse):
    owner: Optional['UserResponse'] = None  # 会在__init__.py中解决

    class Config:
        from_attributes = True