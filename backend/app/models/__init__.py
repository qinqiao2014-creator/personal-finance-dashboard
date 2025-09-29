from .user import User
from .asset import Asset
from .asset_category import AssetCategory
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from app.database import Base

#未来开发多对多关系
# asset_category_mapping = Table(
#     'asset_category_mapping',
#     Base.metadata,
#     Column('asset_id', Integer, ForeignKey('assets.id'), primary_key=True),
#     Column('category_id', Integer, ForeignKey('asset_categories.id'), primary_key=True)
# )

__all__ = ["User", "Asset", "AssetCategory"]