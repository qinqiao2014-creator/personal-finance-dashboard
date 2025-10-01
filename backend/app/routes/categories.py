from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AssetCategory

router = APIRouter(prefix="/categories", tags=["分类管理"])
# categories.py - 修正分类树构建逻辑
@router.get("/asset-categories")
async def get_asset_categories(db: Session = Depends(get_db)):
    """获取资产分类数据（支持常用分类和完整树形结构）"""
    
    # 获取所有分类
    all_categories = db.query(AssetCategory).order_by(AssetCategory.sort_order).all()
    
    # 构建分类树
    def build_category_tree(categories, parent_id=None):
        tree = []
        for category in categories:
            if category.parent_id == parent_id:
                node = {
                    "code": category.code,
                    "name": category.name,
                    "level": category.level,
                    "is_common": category.is_common,
                    "children": build_category_tree(categories, category.id)
                }
                tree.append(node)
        return tree
    
    # 获取常用分类（标记为常用的所有分类，不限于二级）
    common_categories = [
        {
            "code": cat.code,
            "name": cat.name,
            "is_common": True
        }
        for cat in all_categories if cat.is_common
    ]
    
    full_tree = build_category_tree(all_categories)
    
    return {
        "common_categories": common_categories,
        "full_tree": full_tree
    }

@router.get("/asset-categories/flat")
async def get_flat_categories(db: Session = Depends(get_db)):
    """获取扁平化的分类列表（用于分析模块）"""
    categories = db.query(AssetCategory).filter(AssetCategory.level == 2).all()
    return [
        {
            "code": cat.code,
            "name": cat.name,
            "parent_code": cat.parent.code if cat.parent else None,
            "parent_name": cat.parent.name if cat.parent else None
        }
        for cat in categories
    ]