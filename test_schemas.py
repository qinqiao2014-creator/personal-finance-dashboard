import os
import sys

# 添加backend/app到Python路径
app_dir = os.path.join(os.path.dirname(__file__), 'backend', 'app')
if app_dir not in sys.path:
    sys.path.append(app_dir)
    
"""
测试Pydantic模式验证功能
"""
from schemas.user import UserCreate, UserLogin
from schemas.asset import AssetCreate, AssetType

def test_user_validation():
    """测试用户数据验证"""
    print("🧪 测试用户数据验证...")
    
    # 测试有效数据
    try:
        valid_user = UserCreate(
            username="john_doe",
            email="john@example.com",
            password="secure123"
        )
        print("✅ 有效用户数据验证通过")
    except Exception as e:
        print(f"❌ 有效用户数据验证失败: {e}")
    
    # 测试无效数据
    try:
        invalid_user = UserCreate(
            username="jo",  # 太短
            email="invalid-email",  # 无效邮箱
            password="123"  # 太短
        )
        print("❌ 无效用户数据应该被拒绝但通过了")
    except Exception as e:
        print(f"✅ 无效用户数据正确被拒绝: {e}")

def test_asset_validation():
    """测试资产数据验证"""
    print("\n🧪 测试资产数据验证...")
    
    # 测试有效数据
    try:
        valid_asset = AssetCreate(
            name="我的股票",
            type=AssetType.STOCK,
            amount=10000.0,
            description="腾讯股票投资"
        )
        print("✅ 有效资产数据验证通过")
    except Exception as e:
        print(f"❌ 有效资产数据验证失败: {e}")
    
    # 测试无效数据
    try:
        invalid_asset = AssetCreate(
            name="",  # 空名称
            type=AssetType.STOCK,
            amount=-100,  # 负数
            description="测试"
        )
        print("❌ 无效资产数据应该被拒绝但通过了")
    except Exception as e:
        print(f"✅ 无效资产数据正确被拒绝: {e}")

if __name__ == "__main__":
    test_user_validation()
    test_asset_validation()
    print("\n🎉 测试完成！")