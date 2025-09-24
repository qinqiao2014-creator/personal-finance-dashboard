import sys
import os
# 获取当前脚本的目录（即 test_models.py 所在的目录）
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取 backend 目录的路径
backend_dir = os.path.join(current_dir, 'backend')
# 将 backend 目录添加到 Python 搜索路径中
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.database import engine, Base
from app.models.user import User
from app.models.asset import Asset, AssetType

def test_models():
    print("创建数据表...")
    Base.metadata.create_all(bind=engine)
    print("数据表创建成功！")
    
    # 测试枚举类型
    print("\n资产类型枚举:")
    for asset_type in AssetType:
        print(f"  {asset_type.value}: {asset_type}")
    
    print("\n模型定义完成！")

if __name__ == "__main__":
    test_models()