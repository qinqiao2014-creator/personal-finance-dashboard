from sqlalchemy.orm import Session
from app.models import AssetCategory, Asset, User

# 完整的分类体系数据
CATEGORIES_DATA = [
    # Level 1: 大类资产
    {"code": "equity", "name": "权益类", "level": 1, "is_common": False},
    {"code": "fixed_income", "name": "固定收益类", "level": 1, "is_common": False},
    {"code": "cash", "name": "现金类", "level": 1, "is_common": False},
    {"code": "insurance", "name": "保险类", "level": 1, "is_common": False},
    {"code": "physical", "name": "实物资产", "level": 1, "is_common": False},
    {"code": "alternative", "name": "另类投资", "level": 1, "is_common": False},
    
    # Level 2: 权益类子类
    {"code": "equity.stock", "name": "股票", "level": 2, "parent_code": "equity", "is_common": True},
    {"code": "equity.fund", "name": "基金", "level": 2, "parent_code": "equity", "is_common": True},
    {"code": "equity.derivatives", "name": "衍生品", "level": 2, "parent_code": "equity", "is_common": False},
    
    # Level 3: 股票细类
    {"code": "equity.stock.cn_a", "name": "A股股票", "level": 3, "parent_code": "equity.stock", "is_common": False},
    {"code": "equity.stock.hk", "name": "港股股票", "level": 3, "parent_code": "equity.stock", "is_common": False},
    {"code": "equity.stock.us", "name": "美股股票", "level": 3, "parent_code": "equity.stock", "is_common": False},
    
    # Level 2: 固定收益类子类
    {"code": "fixed_income.bond", "name": "债券", "level": 2, "parent_code": "fixed_income", "is_common": False},
    {"code": "fixed_income.deposit", "name": "银行存款", "level": 2, "parent_code": "fixed_income", "is_common": True},
    {"code": "fixed_income.wealth_mgmt", "name": "银行理财", "level": 2, "parent_code": "fixed_income", "is_common": False},
    {"code": "fixed_income.national_debt", "name": "国债", "level": 2, "parent_code": "fixed_income", "is_common": False},
    
    # Level 2: 保险类子类
    {"code": "insurance.life", "name": "保险", "level": 2, "parent_code": "insurance", "is_common": True},
    {"code": "insurance.health", "name": "健康保险", "level": 2, "parent_code": "insurance", "is_common": False},
    {"code": "insurance.property", "name": "财产保险", "level": 2, "parent_code": "insurance", "is_common": False},
    
    # Level 2: 实物资产子类
    {"code": "physical.real_estate", "name": "房地产", "level": 2, "parent_code": "physical", "is_common": True},
    {"code": "physical.gold", "name": "黄金", "level": 2, "parent_code": "physical", "is_common": False},
    {"code": "physical.collectibles", "name": "收藏品", "level": 2, "parent_code": "physical", "is_common": False},
    
    # Level 2: 另类投资子类
    {"code": "alternative.crypto", "name": "加密货币", "level": 2, "parent_code": "alternative", "is_common": True},
    {"code": "alternative.private_equity", "name": "私募股权", "level": 2, "parent_code": "alternative", "is_common": False},
    {"code": "alternative.other", "name": "其他", "level": 2, "parent_code": "alternative", "is_common": True},
    
    # Level 2: 现金类子类
    {"code": "cash.savings", "name": "活期存款", "level": 2, "parent_code": "cash", "is_common": False},
    {"code": "cash.money_fund", "name": "货币基金", "level": 2, "parent_code": "cash", "is_common": False},
]

def init_asset_categories(db: Session):
    """初始化资产分类体系"""
    # 清空现有分类
    db.query(AssetCategory).delete()
    
    category_map = {}
    
    # 第一遍创建所有分类
    for cat_data in CATEGORIES_DATA:
        category = AssetCategory(
            code=cat_data["code"],
            name=cat_data["name"],
            level=cat_data["level"],
            is_common=cat_data.get("is_common", False)
        )
        db.add(category)
        db.flush()
        category_map[cat_data["code"]] = category
    
    # 第二遍设置父子关系
    for cat_data in CATEGORIES_DATA:
        if "parent_code" in cat_data:
            category_map[cat_data["code"]].parent_id = category_map[cat_data["parent_code"]].id
    
    db.commit()
    return len(CATEGORIES_DATA)

def create_test_assets(db: Session, user_id: int):
    """创建测试资产数据（使用新的分类系统）"""
    # 清空现有资产
    db.query(Asset).filter(Asset.owner_id == user_id).delete()
    
    # 获取分类映射
    categories = {cat.code: cat for cat in db.query(AssetCategory).all()}
    
    # 测试数据（使用具体分类代码）
    test_assets_data = [
        {"name": "招商银行A股", "category_code": "equity.stock.cn_a", "amount": 50000},
        {"name": "腾讯控股港股", "category_code": "equity.stock.hk", "amount": 100000},
        {"name": "苹果公司美股", "category_code": "equity.stock.us", "amount": 80000},
        {"name": "沪深300指数基金", "category_code": "equity.fund", "amount": 150000},
        {"name": "银行定期存款", "category_code": "fixed_income.deposit", "amount": 200000},
        {"name": "国债投资", "category_code": "fixed_income.national_debt", "amount": 100000},
        {"name": "比特币", "category_code": "alternative.crypto", "amount": 50000},
        {"name": "北京住宅房产", "category_code": "physical.real_estate", "amount": 5000000},
        {"name": "黄金投资", "category_code": "physical.gold", "amount": 30000},
        {"name": "重疾保险", "category_code": "insurance.life", "amount": 50000},
    ]
    
    for asset_data in test_assets_data:
        category = categories.get(asset_data["category_code"])
        if category:
            asset = Asset(
                name=asset_data["name"],
                amount=asset_data["amount"],
                primary_category_id=category.id,
                owner_id=user_id
            )
            db.add(asset)
    
    db.commit()
    return len(test_assets_data)