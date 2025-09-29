from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum 
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum


# # 资产类型枚举
# class AssetType(str, enum.Enum):
#     STOCK = "stock"          # 股票
#     FUND = "fund"            # 基金
#     BANK = "bank"            # 银行存款
#     CRYPTO = "crypto"        # 加密货币
#     INSURANCE = "insurance"  # 保险
#     REAL_ESTATE = "real_estate"  # 房地产
#     OTHER = "other"          # 其他 

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # 资产名称
    # type = Column(Enum(AssetType), nullable=False)  # 资产类型
    # type = Column(String(50), nullable=False) #过渡期保留，资产类型
    amount = Column(Float, nullable=False)  # 资产金额      
    description = Column(String(500), nullable=True)  # 描述
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 外键关联到资产种类
    primary_category_id = Column(Integer, ForeignKey("asset_categories.id"))
    primary_category = relationship("AssetCategory", back_populates="assets_primary")

    # 外键关联到用户
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="assets")
    
    def __repr__(self):
        return f"<Asset(id={self.id}, name={self.name}, type={self.type}, value={self.amount})>"