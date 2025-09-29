from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class AssetCategory(Base):
    __tablename__ = "asset_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    level = Column(Integer, default=1)
    parent_id = Column(Integer, ForeignKey("asset_categories.id"))
    sort_order = Column(Integer, default=0)
    is_common = Column(Boolean, default=False)  # 是否为常用选项
    attributes = Column(JSON, default=dict)
    
    parent = relationship("AssetCategory", remote_side=[id], backref="children")
    
       # 添加与Asset的关系
    assets_primary = relationship("Asset", back_populates="primary_category")
    
    def __repr__(self):
        return f"<AssetCategory {self.code}: {self.name}>"