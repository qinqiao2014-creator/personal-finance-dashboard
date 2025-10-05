from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func,text
from typing import List, Optional
from app.database import get_db
from app.models import Asset, AssetCategory, User, AssetHistory
from app.auth import get_current_user
from app.schemas.asset import AssetCreate, AssetUpdate, AssetResponse, AssetListResponse, AssetSummary,AllocationAnalysis
from datetime import datetime, timedelta,timezone
import random
from app.utils.merrill_mapper import MerrillAllocationMapper



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
    # 使用 joinedload 加载关联关系
    from sqlalchemy.orm import joinedload
    
    query = db.query(Asset).options(
        joinedload(Asset.primary_category),
        joinedload(Asset.history_records)  # 加载历史记录
    ).filter(Asset.owner_id == current_user.id)
    
    if category_code:
        query = query.join(Asset.primary_category).filter(AssetCategory.code == category_code)
    
    total = query.count()
    assets = query.order_by(Asset.created_at.desc()).offset(skip).limit(limit).all()
    
    # 构建包含分类信息和历史记录的响应
    response_assets = []
    for asset in assets:
        asset_data = {
            "id": asset.id,
            "name": asset.name,
            "amount": asset.amount,
            "description": asset.description,
            "created_at": asset.created_at,
            "updated_at": asset.updated_at,
            "owner_id": asset.owner_id,
            "history_records": [
                {
                    "id": history.id,
                    "asset_id": history.asset_id,
                    "amount": history.amount,
                    "effective_date": history.effective_date,
                    "change_type": history.change_type
                }
                for history in asset.history_records
            ] if asset.history_records else []
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
    from sqlalchemy.orm import joinedload
    
    asset = db.query(Asset).options(
        joinedload(Asset.primary_category),
        joinedload(Asset.history_records)  # 加载历史记录
    ).filter(
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
        "owner_id": asset.owner_id,
        "history_records": [
            {
                "id": history.id,
                "asset_id": history.asset_id,
                "amount": history.amount,
                "effective_date": history.effective_date,
                "change_type": history.change_type
            }
            for history in asset.history_records
        ] if asset.history_records else []
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

# 在创建资产时也添加历史记录调试
@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(    
    asset_data: AssetCreate,
    test_date: Optional[str] = None,  # 隐藏参数，不暴露在文档中
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    """创建新资产"""
    from sqlalchemy.orm import joinedload
    
    # 验证分类代码是否存在
    category = db.query(AssetCategory).filter(AssetCategory.code == asset_data.category_code).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "INVALID_CATEGORY", "message": f"无效的资产分类: {asset_data.category_code}"}
        )
    

        # 只有在有test_date时才手动设置日期
    # 创建资产 - 根据是否有test_date决定是否手动设置日期
    if test_date:
        try:
            created_at = datetime.strptime(test_date, "%Y-%m-%d").replace(
                hour=10, minute=0, second=0, tzinfo=timezone.utc
            )
            # 有test_date时手动设置日期
            asset = Asset(
                name=asset_data.name,
                amount=asset_data.amount,
                description=asset_data.description,
                owner_id=current_user.id,
                primary_category_id=category.id,
                created_at=created_at,
                updated_at=created_at
            )
        except ValueError:
            # 日期格式错误，回退到自动生成
            asset = Asset(
                name=asset_data.name,
                amount=asset_data.amount,
                description=asset_data.description,
                owner_id=current_user.id,
                primary_category_id=category.id
            )
    else:
        # 没有test_date时，使用模型默认值
        asset = Asset(
            name=asset_data.name,
            amount=asset_data.amount,
            description=asset_data.description,
            owner_id=current_user.id,
            primary_category_id=category.id
        )
    
    
    db.add(asset)
    db.commit()
    db.refresh(asset)
    
    # 创建资产历史记录
    print(f"📝 创建资产初始历史记录: {asset.amount}")
    history = AssetHistory(
        asset_id=asset.id,
        amount=asset.amount,
        effective_date=asset.created_at,
        change_type='create'
    )
    db.add(history)
    db.commit()
    
    # 重新加载关联关系
    asset = db.query(Asset).options(
        joinedload(Asset.primary_category),
        joinedload(Asset.history_records)
    ).filter(Asset.id == asset.id).first()
    
    # 返回包含分类信息和历史记录的响应
    return {
        "id": asset.id,
        "name": asset.name,
        "amount": asset.amount,
        "description": asset.description,
        "created_at": asset.created_at,
        "updated_at": asset.updated_at,
        "owner_id": asset.owner_id,
        "category_code": category.code,
        "category_name": category.name,
        "history_records": [
            {
                "id": history.id,
                "asset_id": history.asset_id,
                "amount": history.amount,
                "effective_date": history.effective_date,
                "change_type": history.change_type
            }
            for history in asset.history_records
        ] if asset.history_records else []
    }


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    test_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新资产信息"""
    from sqlalchemy.orm import joinedload
    
    asset = db.query(Asset).options(
        joinedload(Asset.primary_category),
        joinedload(Asset.history_records)
    ).filter(
        Asset.id == asset_id, 
        Asset.owner_id == current_user.id
    ).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资产不存在"
        )
    
    # 记录旧金额用于历史记录
    old_amount = asset.amount


     # 处理测试日期
    if test_date:
        try:
            updated_at = datetime.strptime(test_date, "%Y-%m-%d").replace(
                hour=10, minute=0, second=0, tzinfo=timezone.utc
            )
            # 有test_date时手动设置updated_at
            asset.updated_at = updated_at
        except ValueError:
            # 日期格式错误，让模型自动更新
            pass
    
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
    
    # 如果金额发生变化，记录历史
    if 'amount' in update_data and update_data['amount'] != old_amount:
        print(f"💰 记录资产历史: {old_amount} -> {update_data['amount']}")

        # 确定历史记录的时间
        effective_date = asset.updated_at if test_date else datetime.now(timezone.utc)

        history = AssetHistory(
            asset_id=asset.id,
            amount=update_data['amount'],
            effective_date=effective_date , # 使用正确的时间
            change_type='update'
        )
        db.add(history)
        # 立即提交历史记录
        db.commit()
        print("✅ 历史记录已创建")
    
    # 提交资产更新
    db.commit()
    db.refresh(asset)
    
    # 重新加载关联关系
    db.refresh(asset, ['primary_category', 'history_records'])
    
    # 构建响应数据
    asset_data = {
        "id": asset.id,
        "name": asset.name,
        "amount": asset.amount,
        "description": asset.description,
        "created_at": asset.created_at,
        "updated_at": asset.updated_at,
        "owner_id": asset.owner_id,
        "history_records": [
            {
                "id": history.id,
                "asset_id": history.asset_id,
                "amount": history.amount,
                "effective_date": history.effective_date,
                "change_type": history.change_type
            }
            for history in asset.history_records
        ] if asset.history_records else []
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
    """基于资产历史记录的精确趋势计算"""
    
    cumulative_query = text("""
        WITH RECURSIVE date_series(date) AS (
            SELECT date(:start_date)
            UNION ALL
            SELECT date(date, '+1 day')
            FROM date_series
            WHERE date < date('now', '+7 days')
        ),
        -- 获取每个资产在每个日期的有效金额
        daily_asset_values AS (
            SELECT 
                ds.date,
                ah.asset_id,
                ah.amount,
                ROW_NUMBER() OVER (PARTITION BY ds.date, ah.asset_id ORDER BY ah.effective_date DESC) as rn
            FROM date_series ds
            CROSS JOIN asset_histories ah
            INNER JOIN assets a ON ah.asset_id = a.id
            WHERE a.owner_id = :user_id
            AND date(ah.effective_date) <= ds.date
        )
        SELECT 
            ds.date,
            COALESCE(SUM(dav.amount), 0) as cumulative_value
        FROM date_series ds
        LEFT JOIN daily_asset_values dav ON ds.date = dav.date AND dav.rn = 1
        GROUP BY ds.date
        ORDER BY ds.date
    """)
    
    result = db.execute(cumulative_query, {
        'user_id': current_user.id,
        'start_date': from_date.date()
    }).fetchall()
    
    trend_data = [{"date": str(row.date), "value": float(row.cumulative_value)} for row in result]
    
    print(f"📊 基于历史记录生成 {len(trend_data)} 个数据点")
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


#美林时钟相关
@router.get("/merrill/allocation-analysis", response_model=AllocationAnalysis)
async def get_allocation_analysis(
    phase: str = "recovery",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户资产配置分析报告
    - phase: 美林时钟阶段 (recovery, overheat, stagflation, recession)
    """
    # 参数验证
    valid_phases = ["recovery", "overheat", "stagflation", "recession"]
    if phase not in valid_phases:
        phase = "recovery"
    
    try:
        # 获取用户所有资产
        assets = db.query(Asset).filter(Asset.owner_id == current_user.id).all()
        
        # 使用美林映射器进行分析
        mapper = MerrillAllocationMapper(db)
        analysis_result = mapper.analyze_user_allocation(assets, phase)
        
        # 保存诊断报告到数据库
        from datetime import datetime
        from app.models.diagnosis_report import DiagnosisReport
        
        title = f"资产诊断报告 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        report = DiagnosisReport(
            user_id=current_user.id,
            title=title,
            health_score=analysis_result["health_score"],
            total_amount=analysis_result["total_amount"],
            user_allocation=analysis_result["user_allocation"],
            merrill_suggestion=analysis_result["merrill_suggestion"],
            adjustment_advice=analysis_result["adjustment_advice"],
            economic_phase=phase
        )


        
        db.add(report)
        db.commit()
        db.refresh(report)
        
        # 在返回结果中添加报告ID
        analysis_result_dict = analysis_result
        analysis_result_dict["report_id"] = report.id
        analysis_result_dict["economic_phase"] = phase
        
        return analysis_result_dict
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"资产配置分析失败: {str(e)}"
        )
    
@router.get("/{asset_id}/history", response_model=List[dict])
async def get_asset_history(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取资产的历史记录"""
    # 验证资产所有权
    asset = db.query(Asset).filter(
        Asset.id == asset_id, 
        Asset.owner_id == current_user.id
    ).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资产不存在"
        )
    
    # 查询历史记录
    history_records = db.query(AssetHistory).filter(
        AssetHistory.asset_id == asset_id
    ).order_by(AssetHistory.effective_date.desc()).all()
    
    return [
        {
            "id": record.id,
            "asset_id": record.asset_id,
            "amount": record.amount,
            "effective_date": record.effective_date,
            "change_type": record.change_type
        }
        for record in history_records
    ]