#!/usr/bin/env python3
"""
开发环境一键初始化脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base  # 添加engine和Base
from app.models import User
from app.utils.init_data import init_asset_categories, create_test_assets
from app.auth.security import hash_password  # 添加导入

def main():
    """主初始化函数"""
    # 先创建数据库表
    print("🗃️ 创建数据库表...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("🚀 开始初始化开发环境...")
        
        # 1. 初始化分类体系
        print("📊 初始化资产分类体系...")
        category_count = init_asset_categories(db)
        print(f"   ✅ 创建了 {category_count} 个分类")
        
        # 2. 获取或创建测试用户
        user = db.query(User).first()
        if not user:
            user = User(
                username="testuser",
                email="test@example.com", 
                hashed_password=hash_password("test123"),  # ✅ 添加逗号
                role="user"
            )
            db.add(user)
            db.commit()  # 提交用户创建
            db.refresh(user)
            print("   ✅ 创建测试用户")
        
        # 3. 创建测试资产
        print("💾 创建测试资产数据...")
        asset_count = create_test_assets(db, user.id)
        print(f"   ✅ 创建了 {asset_count} 个测试资产")
        
        print("🎉 开发环境初始化完成！")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()