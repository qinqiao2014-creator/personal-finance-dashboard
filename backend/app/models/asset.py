from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum 
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from app.database import Base

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # 资产名称
    # type = Column(Enum(AssetType), nullable=False)  # 资产类型
    # type = Column(String(50), nullable=False) #过渡期保留，资产类型
    amount = Column(Float, nullable=False)  # 资产金额      
    description = Column(String(500), nullable=True)  # 描述
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # 外键关联到资产种类
    primary_category_id = Column(Integer, ForeignKey("asset_categories.id"))
    primary_category = relationship("AssetCategory", back_populates="assets_primary")

    # 外键关联到用户
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="assets")

        # 历史记录关系
    # history_records = relationship("AssetHistory", backref="asset_rel", cascade="all, delete-orphan")

        # 1. 显式反向关系，名字保持 history_records 不变
    history_records = relationship(
        "AssetHistory",
        back_populates="asset",          # 与对面对齐
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Asset(id={self.id}, name={self.name}, type={self.type}, value={self.amount})>"
    

class AssetHistory(Base):
    __tablename__ = "asset_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    amount = Column(Float, nullable=False)
    effective_date = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    change_type = Column(String(20), nullable=False)  # 'create', 'update'
    
    # 关系
    # asset = relationship("Asset", backref="history_records")
    # 2. 取消 backref，改用 back_populates
    asset = relationship("Asset", back_populates="history_records")
    
    def __repr__(self):
        return f"<AssetHistory(id={self.id}, asset_id={self.asset_id}, amount={self.amount}, change_type={self.change_type})>"    