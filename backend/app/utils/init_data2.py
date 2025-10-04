from sqlalchemy.orm import Session
from app.models import AssetCategory, Asset, User

# 完整的分类体系数据
CATEGORIES_DATA = [
        # ========== Level 1 : 大类资产 ==========
    {"code": "equity",       "name": "权益类",   "level": 1, "is_common": False},
    {"code": "fixed_income", "name": "固定收益类", "level": 1, "is_common": False},
    {"code": "cash",         "name": "现金类",    "level": 1, "is_common": False},
    {"code": "insurance",    "name": "保险资产",  "level": 1, "is_common": True},
    {"code": "physical",     "name": "实物资产",  "level": 1, "is_common": False},
    {"code": "derivatives",  "name": "衍生品（纯合约）",   "level": 1, "is_common": False},
    {"code": "alternative", "name": "另类投资", "level": 1, "is_common": False},

    # ========== Level 2 : 权益类 ==========
    {"code": "equity.stock",      "name": "股票",        "level": 2, "parent_code": "equity", "is_common": True},
    {"code": "equity.fund",       "name": "基金",        "level": 2, "parent_code": "equity", "is_common": True},
    {"code": "equity.derivatives","name": "权益衍生品",  "level": 2, "parent_code": "equity", "is_common": False},

    # ========== Level 3 : 股票细分 ==========
    {"code": "equity.stock.cn_a", "name": "A股股票", "level": 3, "parent_code": "equity.stock", "is_common": False},
    {"code": "equity.stock.hk",   "name": "港股股票", "level": 3, "parent_code": "equity.stock", "is_common": False},
    {"code": "equity.stock.us",   "name": "美股股票", "level": 3, "parent_code": "equity.stock", "is_common": False},

    # ========== Level 3 : 权益衍生品（股票/股指相关） ==========
    {"code": "equity.derivatives.cn_etf_options",   "name": "中国ETF期权",  "level": 3, "parent_code": "equity.derivatives", "is_common": True},
    {"code": "equity.derivatives.cn_index_futures", "name": "中国股指期货",  "level": 3, "parent_code": "equity.derivatives", "is_common": False},
    {"code": "equity.derivatives.cn_index_options", "name": "中国股指期权","level": 3, "parent_code": "equity.derivatives", "is_common": False},
    {"code": "equity.derivatives.us_options",       "name": "美股期权",   "level": 3, "parent_code": "equity.derivatives", "is_common": True},
    {"code": "equity.derivatives.us_futures",       "name": "美股指数期货",  "level": 3, "parent_code": "equity.derivatives", "is_common": False},
    {"code": "equity.derivatives.hk_warrants",      "name": "港股涡轮/权证",    "level": 3, "parent_code": "equity.derivatives", "is_common": False},
    {"code": "equity.derivatives.hk_cbbc",          "name": "港股牛熊证",   "level": 3, "parent_code": "equity.derivatives", "is_common": False},
    {"code": "equity.derivatives.cfd",              "name": "个股差价合约(CFD)",  "level": 3, "parent_code": "equity.derivatives", "is_common": False},

    # ========== Level 2 : 固定收益 ==========
    {"code": "fixed_income.bond",          "name": "债券/债券基金",        "level": 2, "parent_code": "fixed_income", "is_common": True},
    {"code": "fixed_income.wealth_mgmt",   "name": "银行理财",    "level": 2, "parent_code": "fixed_income", "is_common": True},
    {"code": "fixed_income.national_debt", "name": "国债",        "level": 2, "parent_code": "fixed_income", "is_common": False},

    # ========== Level 2 : 保险资产 ==========
    {"code": "insurance.annuity",       "name": "年金险（累积期）", "level": 2, "parent_code": "insurance", "is_common": False},
    {"code": "insurance.enterprise",    "name": "企业年金",         "level": 2, "parent_code": "insurance", "is_common": False},
    {"code": "insurance.whole_life",    "name": "增额终身寿",       "level": 2, "parent_code": "insurance", "is_common": True},
    {"code": "insurance.pension",       "name": "个人养老金",       "level": 2, "parent_code": "insurance", "is_common": False},
    {"code": "insurance.ul",            "name": "万能险",           "level": 2, "parent_code": "insurance", "is_common": False},
    {"code": "insurance.vul",           "name": "投连险",           "level": 2, "parent_code": "insurance", "is_common": False},

    # ========== Level 2 : 实物资产 ==========
    {"code": "physical.real_estate", "name": "房地产", "level": 2, "parent_code": "physical", "is_common": False},
    {"code": "physical.gold",        "name": "黄金/黄金ETF",   "level": 2, "parent_code": "physical", "is_common": True},
    {"code": "physical.car",         "name": "汽车",   "level": 2, "parent_code": "physical", "is_common": False},
    {"code": "physical.collectibles","name": "收藏品(古董/画/玉石)","level": 2, "parent_code": "physical", "is_common": False},

    # ========== Level 2 : 衍生品（纯合约） ==========
    {"code": "derivatives.commodity", "name": "商品衍生品", "level": 2, "parent_code": "derivatives", "is_common": False},
    {"code": "derivatives.rate",      "name": "利率衍生品", "level": 2, "parent_code": "derivatives", "is_common": False},
    {"code": "derivatives.fx",        "name": "汇率衍生品", "level": 2, "parent_code": "derivatives", "is_common": False},
    {"code": "derivatives.crypto",    "name": "加密衍生品", "level": 2, "parent_code": "derivatives", "is_common": False},

    # ========== Level 3 : 商品衍生品 ==========
    {"code": "derivatives.commodity.cn_futures", "name": "中国商品期货", "level": 3, "parent_code": "derivatives.commodity", "is_common": True},
    {"code": "derivatives.commodity.us_futures", "name": "美股商品期货", "level": 3, "parent_code": "derivatives.commodity", "is_common": False},

    # ========== Level 3 : 利率衍生品 ==========
    {"code": "derivatives.rate.bond_futures", "name": "国债期货", "level": 3, "parent_code": "derivatives.rate", "is_common": False},

    # ========== Level 3 : 汇率衍生品 ==========
    {"code": "derivatives.fx.cny_futures", "name": "人民币期货/期权", "level": 3, "parent_code": "derivatives.fx", "is_common": False},

    # ========== Level 3 : 加密衍生品 ==========
    {"code": "derivatives.crypto.futures", "name": "加密期货/永续", "level": 3, "parent_code": "derivatives.crypto", "is_common": False},

    # ========== Level 2 : 现金类 ==========
    {"code": "cash.money_fund", "name": "货币基金", "level": 2, "parent_code": "cash", "is_common": True},
    {"code": "cash.deposit",    "name": "银行存款", "level": 2, "parent_code": "cash", "is_common": True},

    # ========== Level 3 : 银行存款细分 ==========
    {"code": "cash.deposit.demand", "name": "活期存款",   "level": 3, "parent_code": "cash.deposit", "is_common": False},
    {"code": "cash.deposit.time",   "name": "定期存款",   "level": 3, "parent_code": "cash.deposit", "is_common": False},
    {"code": "cash.deposit.call",   "name": "通知存款",   "level": 3, "parent_code": "cash.deposit", "is_common": False},
    {"code": "cash.deposit.struct", "name": "结构性存款", "level": 3, "parent_code": "cash.deposit", "is_common": False},
    {"code": "cash.deposit.cd",     "name": "大额存单",   "level": 3, "parent_code": "cash.deposit", "is_common": False},
    {"code": "cash.deposit.housing_fund", "name": "住房公积金", "level": 3, "parent_code": "cash.deposit", "is_common": False},

    # ========== Level 2 : 另类投资子类 ==========
    {"code": "alternative.reits",       "name": "公募REITs",     "level": 2, "parent_code": "alternative", "is_common": True},
    {"code": "alternative.private_equity", "name": "私募股权",  "level": 2, "parent_code": "alternative", "is_common": False},
    {"code": "alternative.crypto",      "name": "加密货币",      "level": 2, "parent_code": "alternative", "is_common": True},
    {"code": "alternative.other",       "name": "其他",          "level": 2, "parent_code": "alternative", "is_common": False},
    {"code": "alternative.hedge_fund", "name": "对冲基金", "level": 2, "parent_code": "alternative", "is_common": False},
    {"code": "alternative.venture_capital", "name": "风险投资", "level": 2, "parent_code": "alternative", "is_common": False},
    {"code": "alternative.art_finance", "name": "艺术金融", "level": 2, "parent_code": "alternative", "is_common": False},
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