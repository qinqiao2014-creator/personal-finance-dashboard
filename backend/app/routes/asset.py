from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.database import get_db
from app.models import Asset, AssetCategory, User
from app.auth import get_current_user
from app.schemas.asset import AssetCreate, AssetUpdate, AssetResponse, AssetListResponse, AssetSummary

router = APIRouter(prefix="/assets", tags=["资产管理"])

@router.get("", response_model=AssetListResponse)
async def get_assets(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="每页记录数"),
    category_code: Optional[str] = Query(None, description="按分类代码过滤"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AssetListResponse:
    """获取当前用户的资产列表"""
    query = db.query(Asset).filter(Asset.owner_id == current_user.id)
    
    if category_code:
        query = query.join(Asset.primary_category).filter(AssetCategory.code == category_code)
    
    total = query.count()
    assets = query.order_by(Asset.created_at.desc()).offset(skip).limit(limit).all()
    
    # 构建包含分类信息的响应
    response_assets = []
    for asset in assets:
        asset_data = {
            "id": asset.id,
            "name": asset.name,
            "amount": asset.amount,
            "description": asset.description,
            "created_at": asset.created_at,
            "updated_at": asset.updated_at,
            "owner_id": asset.owner_id
        }
        
        if asset.primary_category:
            asset_data["category_code"] = asset.primary_category.code
            asset_data["category_name"] = asset.primary_category.name
            asset_data["category"] = {
                "code": asset.primary_category.code,
                "name": asset.primary_category.name,
                "level": asset.primary_category.level
            }
        
        response_assets.append(asset_data)
    
    return AssetListResponse(total=total, items=response_assets)

@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """根据ID获取特定资产详情"""
    asset = db.query(Asset).filter(
        Asset.id == asset_id, 
        Asset.owner_id == current_user.id
    ).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "ASSET_NOT_FOUND", "message": "资产不存在"}
        )
    
    asset_data = {
        "id": asset.id,
        "name": asset.name,
        "amount": asset.amount,
        "description": asset.description,
        "created_at": asset.created_at,
        "updated_at": asset.updated_at,
        "owner_id": asset.owner_id
    }
    
    if asset.primary_category:
        asset_data["category_code"] = asset.primary_category.code
        asset_data["category_name"] = asset.primary_category.name
        asset_data["category"] = {
            "code": asset.primary_category.code,
            "name": asset.primary_category.name,
            "level": asset.primary_category.level
        }
    
    return asset_data

@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_data: AssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新资产"""
    # 验证分类代码是否存在
    category = db.query(AssetCategory).filter(AssetCategory.code == asset_data.category_code).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "INVALID_CATEGORY", "message": f"无效的资产分类: {asset_data.category_code}"}
        )
    
    # 创建资产并绑定分类
    asset = Asset(
        name=asset_data.name,
        amount=asset_data.amount,
        description=asset_data.description,
        owner_id=current_user.id,
        primary_category_id=category.id  # 正确绑定分类ID
    )
    
    db.add(asset)
    db.commit()
    db.refresh(asset)
    
    # 返回包含分类信息的响应
    return {
        "id": asset.id,
        "name": asset.name,
        "amount": asset.amount,
        "description": asset.description,
        "created_at": asset.created_at,
        "updated_at": asset.updated_at,
        "owner_id": asset.owner_id,
        "category_code": category.code,
        "category_name": category.name
    }

@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新资产信息"""
    asset = db.query(Asset).filter(
        Asset.id == asset_id, 
        Asset.owner_id == current_user.id
    ).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资产不存在"
        )
    
    # 如果更新了分类，需要验证新的分类代码
    if asset_data.category_code and asset_data.category_code != (asset.primary_category.code if asset.primary_category else None):
        category = db.query(AssetCategory).filter(AssetCategory.code == asset_data.category_code).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的资产分类: {asset_data.category_code}"
            )
        asset.primary_category_id = category.id
    
    # 更新字段
    update_data = asset_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field != "category_code":  # 分类已单独处理
            setattr(asset, field, value)
    
    db.commit()
    db.refresh(asset)
    
    # 返回包含分类信息的响应
    asset_data = {
        "id": asset.id,
        "name": asset.name,
        "amount": asset.amount,
        "description": asset.description,
        "created_at": asset.created_at,
        "updated_at": asset.updated_at,
        "owner_id": asset.owner_id
    }
    
    if asset.primary_category:
        asset_data["category_code"] = asset.primary_category.code
        asset_data["category_name"] = asset.primary_category.name
        asset_data["category"] = {
            "code": asset.primary_category.code,
            "name": asset.primary_category.name,
            "level": asset.primary_category.level
        }
    
    return asset_data

@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除资产"""
    asset = db.query(Asset).filter(
        Asset.id == asset_id, 
        Asset.owner_id == current_user.id
    ).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资产不存在"
        )
    
    db.delete(asset)
    db.commit()
    
    return None

@router.get("/summary/total", response_model=AssetSummary)
async def get_assets_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取资产统计摘要"""
    # 总资产价值
    total_value = db.query(func.sum(Asset.amount)).filter(
        Asset.owner_id == current_user.id
    ).scalar() or 0.0

    # 按分类统计（使用分类代码）
    assets_by_category_result = db.query(
        AssetCategory.code,
        AssetCategory.name, 
        func.sum(Asset.amount).label("total_amount")
    ).join(Asset.primary_category).filter(
        Asset.owner_id == current_user.id
    ).group_by(AssetCategory.code, AssetCategory.name).all()
    
    # 修复：正确解包三元组 (code, name, total_amount)
    assets_by_category = {
        f"{code} ({name})": total_amount for code, name, total_amount in assets_by_category_result
    }
    
    # 资产数量
    asset_count = db.query(Asset).filter(Asset.owner_id == current_user.id).count()
    
    return AssetSummary(
        total_assets=total_value,
        assets_by_type=assets_by_category,  # 保持字段名兼容性
        asset_count=asset_count
    )