from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.database import get_db
from app.models.asset import Asset, AssetType
from app.models.user import User
from app.schemas.asset import AssetCreate, AssetResponse, AssetUpdate, AssetListResponse, AssetSummary
from app.routes.auth import get_current_user

router = APIRouter(prefix="/assets", tags=["资产管理"])

@router.get("", response_model=AssetListResponse)
def get_assets(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=10, description="每页记录数"),
    type: Optional[AssetType] = Query(None, description="按资产类型过滤"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
)-> AssetListResponse:
    """
    获取当前用户的资产列表
    """
    query = db.query(Asset).filter(Asset.owner_id == current_user.id)
    
    if type:
        query = query.filter(Asset.type == type)
    
    total = query.count()
    assets = query.order_by(Asset.created_at.desc()).offset(skip).limit(limit).all()
    
    return AssetListResponse(total=total, items=assets)

@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    根据ID获取特定资产详情
    """
    asset = db.query(Asset).filter(
        Asset.id == asset_id, 
        Asset.owner_id == current_user.id
    ).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "ASSET_NOT_FOUND", "message": "资产不存在"}
        )
    
    return asset

#创建新增资产
@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(
    asset_data: AssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新资产
    """
    # 创建资产
    asset = Asset(
        name=asset_data.name,
        type=asset_data.type,
        amount=asset_data.amount,
        description=asset_data.description,
        owner_id=current_user.id
    )
    
    db.add(asset)
    db.commit()
    db.refresh(asset)
    
    return asset

@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新资产信息
    """
    asset = db.query(Asset).filter(
        Asset.id == asset_id, 
        Asset.owner_id == current_user.id
    ).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资产不存在"
        )
    
    # 更新字段
    update_data = asset_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(asset, field, value)
    
    db.commit()
    db.refresh(asset)
    
    return asset

@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除资产
    """
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
def get_assets_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取资产统计摘要
    """
    # 总资产价值
    total_value = db.query(func.sum(Asset.amount)).filter(
        Asset.owner_id == current_user.id
    ).scalar() or 0.0

    # 按类型分类统计
    assets_by_type_result = db.query(
        Asset.type, 
        func.sum(Asset.amount).label("total_amount")
    ).filter(
        Asset.owner_id == current_user.id
    ).group_by(Asset.type).all()
    
    assets_by_type = {asset_type.value: total_amount for asset_type, total_amount in assets_by_type_result}
    
    # 资产数量
    asset_count = db.query(Asset).filter(Asset.owner_id == current_user.id).count()
    
    return AssetSummary(
        total_assets=total_value,
        assets_by_type=assets_by_type,
        asset_count=asset_count
    )