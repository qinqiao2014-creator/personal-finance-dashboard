from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# 资产基础模式
class AssetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="我的储蓄账户")
    category_code: str = Field(..., description="资产分类代码", example="equity.stock.cn_a")
    amount: float = Field(..., gt=0, description="资产金额必须大于0", example=10000.50)
    description: Optional[str] = Field(None, max_length=500, example="工商银行定期存款")

# 创建资产请求
class AssetCreate(AssetBase):
    class Config:
        json_schema_extra = {
            "example": {
                "name": "招商银行A股",
                "category_code": "equity.stock.cn_a",
                "amount": 50000.0,
                "description": "A股股票投资"
            }
        }

# 资产响应
class AssetResponse(AssetBase):
    id: int
    owner_id: int
    category_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # 分类详细信息
    category: Optional[dict] = None
    
    class Config:
        from_attributes = True

# 资产更新请求
class AssetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, example="更新后的资产名")
    category_code: Optional[str] = Field(None, description="资产分类代码", example="fixed_income.deposit")
    amount: Optional[float] = Field(None, gt=0, example=15000.0)
    description: Optional[str] = Field(None, max_length=500, example="更新后的描述")

# 资产统计响应
class AssetSummary(BaseModel):
    total_assets: float = Field(..., example=250000.0)
    assets_by_type: dict = Field(..., example={"equity.stock (股票)": 200000.0, "fixed_income.deposit (银行存款)": 50000.0})
    asset_count: int = Field(..., example=5)

# 资产列表响应
class AssetListResponse(BaseModel):
    total: int
    items: list[AssetResponse]