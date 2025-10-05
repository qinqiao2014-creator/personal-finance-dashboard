import sys
import os

# 添加backend目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)  # 假设脚本放在backend目录下
sys.path.insert(0, backend_dir)

from datetime import datetime, timezone
from app.database import SessionLocal
from app.models import Asset, AssetHistory, AssetCategory


def create_future_asset():
    """创建未来日期的测试资产"""
    db = SessionLocal()
    
    try:
        print("🔍 连接数据库...")
        
        # 获取股票分类
        category = db.query(AssetCategory).filter(AssetCategory.code == 'equity.stock.cn_a').first()
        if not category:
            print("❌ 找不到股票分类，请先确保分类数据存在")
            return
        
        print(f"✅ 找到分类: {category.name}")
        
        # 设置未来日期（2025年10月6日）
        future_date = datetime(2025, 10, 6, 10, 0, 0, tzinfo=timezone.utc)
        
        # 创建资产
        asset = Asset(
            name="未来测试股票",
            amount=50000.0,
            description="2025年10月6日的测试资产",
            owner_id=3,  # 替换为您的用户ID
            primary_category_id=category.id,
            created_at=future_date,
            updated_at=future_date
        )
        
        db.add(asset)
        db.commit()
        db.refresh(asset)
        
        print(f"✅ 创建资产成功，ID: {asset.id}")
        
        # 创建历史记录
        history = AssetHistory(
            asset_id=asset.id,
            amount=50000.0,
            effective_date=future_date,
            change_type='create'
        )
        
        db.add(history)
        db.commit()
        
        print("✅ 创建历史记录成功")
        print(f"📅 资产创建时间: {future_date}")
        print(f"💰 资产金额: 50000.0")
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()



def check_categories():
    """检查所有资产分类"""
    db = SessionLocal()
    
    try:
        print("🔍 检查资产分类...")
        
        categories = db.query(AssetCategory).all()
        
        if not categories:
            print("❌ 没有任何资产分类，需要先初始化分类数据")
            return
        
        print(f"✅ 找到 {len(categories)} 个资产分类:")
        for category in categories:
            print(f"  - 代码: {category.code}, 名称: {category.name}, ID: {category.id}")
            
        # 显示前几个可用的分类代码
        print("\n📋 可用的分类代码示例:")
        for category in categories[:5]:  # 显示前5个
            print(f"  - {category.code}")
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_categories()
    # create_future_asset()