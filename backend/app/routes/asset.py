from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func,text
from typing import List, Optional
from app.database import get_db
from app.models import Asset, AssetCategory, User
from app.auth import get_current_user
from app.schemas.asset import AssetCreate, AssetUpdate, AssetResponse, AssetListResponse, AssetSummary
from datetime import datetime, timedelta
import random


TREND_MOCK = False   # True=随机模拟  False=真实数据
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

@router.get("/chart/trend", response_model=List[dict])
async def get_asset_trend(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if TREND_MOCK:
        # ===== 随机模拟 =====
        user_total = db.query(func.sum(Asset.amount)).filter(Asset.owner_id == current_user.id).scalar() or 100000
        trend_data = []
        base_date = datetime.now()
        for i in range(days, -1, -1):
            date = base_date - timedelta(days=i)
            variation = (random.random() - 0.5) * 0.05
            value = trend_data[-1]["value"] * (1 + variation) if trend_data else user_total
            trend_data.append({"date": date.strftime("%Y-%m-%d"), "value": round(value, 2)})
        return trend_data
    else:
        # ===== 真实数据 - 数据库优化方案 =====
        from_date = datetime.now() - timedelta(days=days)
        print(f"🔍 查询 {days} 天趋势数据，起始日期: {from_date.date()}")
        
        try:
            # 首选：SQL优化查询
            return await get_trend_sql_optimized(db, current_user, from_date)
        except Exception as e:
            print(f"❌ SQL优化查询失败: {e}，使用回退方案")
            # 备选：内存优化回退方案
            return await get_trend_fallback(db, current_user, from_date, days)

async def get_trend_sql_optimized(db, current_user, from_date):
    """SQL优化版本 - 首选方案"""
    cumulative_query = text("""
        WITH RECURSIVE date_series(date) AS (
            SELECT date(:start_date)
            UNION ALL
            SELECT date(date, '+1 day')
            FROM date_series
            WHERE date < date('now')
        )
        SELECT 
            ds.date,
            COALESCE((
                SELECT SUM(amount) 
                FROM assets 
                WHERE owner_id = :user_id 
                AND date(created_at) <= ds.date
            ), 0) as cumulative_value
        FROM date_series ds
        ORDER BY ds.date
    """)
    
    result = db.execute(cumulative_query, {
        'user_id': current_user.id,
        'start_date': from_date.date()
    }).fetchall()
    
    trend_data = [{"date": str(row.date), "value": float(row.cumulative_value)} for row in result]
    
    print(f"📊 SQL优化生成 {len(trend_data)} 个数据点")
    if trend_data:
        print(f"📈 金额范围: {trend_data[0]['value']} -> {trend_data[-1]['value']}")
    
    return trend_data

async def get_trend_fallback(db, current_user, from_date, days):
    """内存优化回退方案 - 备选方案"""
    # 只查询需要的字段，按日期排序
    assets = db.query(
        Asset.created_at, 
        Asset.amount
    ).filter(
        Asset.owner_id == current_user.id
    ).order_by(Asset.created_at).all()
    
    print(f"🔍 回退方案: 用户共有 {len(assets)} 条资产记录")
    
    trend_data = []
    current_date = from_date.date()
    end_date = datetime.now().date()
    
    # 使用指针优化，避免重复遍历
    asset_index = 0
    cumulative_total = 0.0
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        
        # 累加所有创建日期小于等于当前日期的资产
        while asset_index < len(assets):
            asset = assets[asset_index]
            asset_date = asset.created_at.date()
            
            if asset_date <= current_date:
                cumulative_total += asset.amount
                asset_index += 1
            else:
                break
        
        trend_data.append({
            "date": date_str,
            "value": float(cumulative_total)
        })
        
        current_date += timedelta(days=1)
    
    print(f"📊 回退方案生成 {len(trend_data)} 个数据点")
    return trend_data


# @router.get("/chart/trend", response_model=List[dict])
# async def get_asset_trend(
#     days: int = Query(30, ge=1, le=365),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     if TREND_MOCK:
#         # ===== 随机模拟 =====
#         user_total = db.query(func.sum(Asset.amount)).filter(Asset.owner_id == current_user.id).scalar() or 100000
#         trend_data = []
#         base_date = datetime.now()
#         for i in range(days, -1, -1):
#             date = base_date - timedelta(days=i)
#             variation = (random.random() - 0.5) * 0.05
#             value = trend_data[-1]["value"] * (1 + variation) if trend_data else user_total
#             trend_data.append({"date": date.strftime("%Y-%m-%d"), "value": round(value, 2)})
#         return trend_data
#     else:
#         # ===== 真实数据 - 简化但正确的累计逻辑 =====
#         from_date = datetime.now() - timedelta(days=days)
#         print("🔍 查询起始日期:", from_date.date())
        
#         # 方法1：直接计算每天的累计总额（更简单可靠）
#         # 获取所有资产的创建日期和金额
#         all_assets = db.query(
#             Asset.created_at,
#             Asset.amount
#         ).filter(
#             Asset.owner_id == current_user.id
#         ).all()
        
#         print(f"🔍 用户共有 {len(all_assets)} 条资产记录")
        
#         # 构建日期范围内的累计数据
#         trend_data = []
#         current_date = from_date.date()
#         end_date = datetime.now().date()
        
#         while current_date <= end_date:
#             date_str = current_date.strftime("%Y-%m-%d")
            
#             # 计算到当前日期为止的总资产
#             cumulative_total = 0.0
#             for asset in all_assets:
#                 asset_date = asset.created_at.date()
#                 if asset_date <= current_date:
#                     cumulative_total += asset.amount
            
#             trend_data.append({
#                 "date": date_str,
#                 "value": float(cumulative_total)
#             })
            
#             current_date += timedelta(days=1)
        
#         print(f"📊 生成的趋势数据点: {len(trend_data)}")
#         if trend_data:
#             print(f"📈 数据范围: {trend_data[0]['date']} -> {trend_data[-1]['date']}")
#             print(f"💰 金额范围: {trend_data[0]['value']} -> {trend_data[-1]['value']}")
        
#         return trend_data
