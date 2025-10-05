"""
资产分类数据迁移工具 - 最终优化版本
"""

import sys
import os
import argparse
from pathlib import Path

# 修复Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import AssetCategory, Asset

# 导入新分类数据
try:
    init_data2_path = current_dir / "init_data2.py"
    with open(init_data2_path, 'r', encoding='utf-8') as f:
        content = f.read()
    exec_globals = {}
    exec(content, exec_globals)
    NEW_CATEGORIES_DATA = exec_globals['CATEGORIES_DATA']
    print(f"✅ 成功导入 {len(NEW_CATEGORIES_DATA)} 个新分类")
except Exception as e:
    print(f"❌ 导入新分类数据失败: {e}")
    sys.exit(1)

class CategoryMigrator:
    """最终优化的迁移工具"""
    
    def __init__(self, db: Session):
        self.db = db
        self.migration_report = {
            "total_assets": 0,
            "migrated_assets": 0,
            "failed_assets": 0,
            "new_categories_created": 0,
            "category_mapping": {}
        }
        
        # 优化的关键词映射
        self.keyword_mapping = {
            # 股票关键词 - 精确匹配
            '招商银行A股': 'a_stock',
            '腾讯控股港股': 'hk_stock',
            '苹果公司美股': 'us_stock',
            '特斯拉': 'us_stock',
            
            # 股票通用关键词
            'A股': 'a_stock', 
            '港股': 'hk_stock',
            '美股': 'us_stock',
            '股票': 'stock',
            '股': 'stock',
            
            # 基金关键词
            '货币基金': 'money_market_fund',
            '指数基金': 'fund',
            '基金': 'fund',
            'ETF': 'fund',
            
            # 债券关键词
            '债券': 'bond',
            '国债': 'bond',
            '债': 'bond',
            
            # 存款关键词
            '大额存单': 'large_deposit_certificate',
            '定期存款': 'time_deposit',
            '活期存款': 'demand_deposit',
            '存款': 'demand_deposit',
            '储蓄': 'demand_deposit',
            
            # 银行关键词 - 默认到活期存款
            '工商银行': 'demand_deposit',
            '微众银行': 'demand_deposit',
            '网商银行': 'demand_deposit',
            '招商银行': 'demand_deposit',
            '中信银行': 'demand_deposit',
            '汇丰银行': 'demand_deposit',
            '建设银行': 'demand_deposit',
            '公司账户': 'demand_deposit',
            '银行': 'demand_deposit',
            
            # 理财关键词
            '小金库': 'wealth_management',
            '银行理财': 'wealth_management',
            '理财': 'wealth_management',
            
            # 保险关键词
            '增额寿': 'increasing_whole_life',
            '重疾保险': 'insurance',
            '保险': 'insurance',
            
            # 房地产关键词
            '北京住宅房产': 'real_estate',
            '房产': 'real_estate',
            '房地产': 'real_estate',
            '住宅': 'real_estate',
            
            # 黄金关键词
            '黄金投资': 'gold',
            '黄金': 'gold',
            
            # 加密货币关键词
            '比特币': 'crypto',
            
            # 衍生品关键词
            '期权': 'us_stock_options',
            '期货': 'commodity_futures_cn',
            '衍生品': 'derivatives',
            
            # 其他平台
            '长桥': 'stock',
        }

    def execute_migration(self, dry_run: bool = True) -> dict:
        """执行数据迁移"""
        print("🚀 开始资产分类数据迁移 - 最终优化版本...")
        print(f"📊 模式: {'试运行（不修改数据）' if dry_run else '实际执行'}")

        try:
            # 1. 分析当前状态
            current_stats = self._analyze_current_state()
            print(f"📈 当前状态: {current_stats['asset_count']}个资产")

            if dry_run:
                # 试运行：显示优化映射计划
                mapping_plan = self._analyze_optimized_mapping_plan()
                return {
                    "status": "dry_run_completed",
                    "message": "试运行完成，未修改任何数据",
                    "current_stats": current_stats,
                    "new_categories_count": len(NEW_CATEGORIES_DATA),
                    "mapping_plan": mapping_plan
                }

            # 2. 执行实际迁移
            return self._execute_actual_migration()

        except Exception as e:
            print(f"❌ 迁移失败: {e}")
            try:
                self.db.rollback()
            except:
                pass
            return {"status": "failed", "error": str(e)}

    def _analyze_current_state(self) -> dict:
        """分析当前数据库状态"""
        asset_count = self.db.query(Asset).count()
        return {
            "asset_count": asset_count,
        }

    def _analyze_optimized_mapping_plan(self) -> dict:
        """分析优化映射计划"""
        print("📋 分析优化分类映射计划...")
        
        # 获取当前所有资产
        assets = self.db.query(Asset).all()
        mapping_plan = {}
        
        for asset in assets:
            current_category = asset.primary_category
            current_category_name = current_category.name if current_category else "无分类"
            current_category_code = current_category.code if current_category else None
            
            # 基于资产名称优化查找新分类
            new_category_code = self._find_optimized_category(asset.name)
            
            mapping_plan[asset.id] = {
                "asset_name": asset.name,
                "current_category": f"{current_category_name}",
                "planned_new_category_code": new_category_code,
                "mapping_reason": self._get_mapping_reason(asset.name, new_category_code)
            }
            
            print(f"  📍 {asset.name}")
            print(f"     当前: {current_category_name}")
            print(f"     计划: {new_category_code}")
            print(f"     原因: {mapping_plan[asset.id]['mapping_reason']}")
            print()
        
        return mapping_plan

    def _find_optimized_category(self, asset_name: str) -> str:
        """基于资产名称优化查找分类"""
        # 首先尝试精确匹配完整名称
        if asset_name in self.keyword_mapping:
            return self.keyword_mapping[asset_name]
        
        # 然后按优先级匹配关键词
        asset_name_lower = asset_name.lower()
        for keyword, category_code in self.keyword_mapping.items():
            if keyword in asset_name_lower:
                return category_code
        
        # 默认映射到活期存款
        return "demand_deposit"

    def _get_mapping_reason(self, asset_name: str, category_code: str) -> str:
        """获取映射原因说明"""
        # 检查精确匹配
        if asset_name in self.keyword_mapping and self.keyword_mapping[asset_name] == category_code:
            return "精确匹配资产名称"
        
        asset_name_lower = asset_name.lower()
        for keyword, mapped_code in self.keyword_mapping.items():
            if keyword in asset_name_lower and mapped_code == category_code:
                return f"匹配关键词: '{keyword}'"
        
        return "默认映射到活期存款"

    def _execute_actual_migration(self) -> dict:
        """执行实际迁移"""
        print("🔄 开始实际数据迁移...")

        try:
            # 1. 备份当前资产数据
            assets_before = self.db.query(Asset).all()
            self.migration_report["total_assets"] = len(assets_before)
            
            # 2. 获取或重建分类体系
            new_categories = self._get_or_rebuild_categories()
            
            # 3. 优化迁移资产分类关系
            self._optimized_migrate_asset_categories(assets_before, new_categories)
            
            # 4. 验证迁移结果
            validation_result = self._validate_migration(assets_before)
            
            print("✅ 数据迁移成功完成！")
            return {
                "status": "success",
                "message": "优化迁移成功",
                "report": self.migration_report,
                "validation": validation_result
            }

        except Exception as e:
            self.db.rollback()
            raise e

    def _get_or_rebuild_categories(self) -> dict:
        """获取或重建分类体系"""
        print("📁 检查分类体系...")
        
        current_category_count = self.db.query(AssetCategory).count()
        
        if current_category_count == len(NEW_CATEGORIES_DATA):
            print("✅ 分类体系已是最新，无需重建")
            categories = self.db.query(AssetCategory).all()
            return {cat.code: cat for cat in categories}
        else:
            print("🔄 重建分类体系...")
            self.db.query(AssetCategory).delete()
            
            for cat_data in NEW_CATEGORIES_DATA:
                category = AssetCategory(
                    code=cat_data["code"],
                    name=cat_data["name"],
                    level=cat_data["level"],
                    is_common=cat_data.get("is_common", False)
                )
                self.db.add(category)
            
            self.db.commit()
            
            categories = self.db.query(AssetCategory).all()
            category_map = {cat.code: cat for cat in categories}
            
            for cat_data in NEW_CATEGORIES_DATA:
                if "parent_code" in cat_data:
                    category = category_map.get(cat_data["code"])
                    parent = category_map.get(cat_data["parent_code"])
                    if category and parent:
                        category.parent_id = parent.id
            
            self.db.commit()
            
            self.migration_report["new_categories_created"] = len(NEW_CATEGORIES_DATA)
            print(f"📁 创建了 {len(NEW_CATEGORIES_DATA)} 个新分类")
            
            return category_map

    def _optimized_migrate_asset_categories(self, assets: list, new_categories: dict):
        """优化迁移资产分类关系"""
        print("🔄 优化迁移资产分类关系...")
        
        success_count = 0
        failed_count = 0
        
        for asset in assets:
            try:
                new_category_code = self._find_optimized_category(asset.name)
                new_category = new_categories.get(new_category_code)
                
                if new_category:
                    asset.primary_category_id = new_category.id
                    success_count += 1
                    
                    self.migration_report["category_mapping"][asset.id] = {
                        "asset_name": asset.name,
                        "new_category": new_category.name,
                        "new_category_code": new_category_code
                    }
                    
                    print(f"  ✅ {asset.name} → {new_category.name}")
                else:
                    print(f"  ⚠️  {asset.name}: 未找到对应分类 {new_category_code}")
                    failed_count += 1
                    
            except Exception as e:
                print(f"  ❌ {asset.name}: 迁移失败 - {e}")
                failed_count += 1
        
        self.db.commit()
        
        self.migration_report["migrated_assets"] = success_count
        self.migration_report["failed_assets"] = failed_count
        
        print(f"📊 资产迁移结果: {success_count}成功, {failed_count}失败")

    def _validate_migration(self, original_assets: list) -> dict:
        """验证迁移结果"""
        print("🔍 验证迁移结果...")
        
        assets_after = self.db.query(Asset).all()
        count_preserved = len(original_assets) == len(assets_after)
        assets_with_category = sum(1 for asset in assets_after if asset.primary_category_id is not None)
        
        print(f"📊 验证结果:")
        print(f"  - 资产数量: {'✅ 保持完好' if count_preserved else '❌ 数据丢失'}")
        print(f"  - 有分类资产: {assets_with_category}/{len(assets_after)}")
        
        print(f"\n📋 最终映射结果:")
        migrated_assets = self.db.query(Asset).join(Asset.primary_category).limit(10).all()
        for i, asset in enumerate(migrated_assets):
            category_name = asset.primary_category.name if asset.primary_category else "无分类"
            print(f"  {i+1}. {asset.name} → {category_name}")
        
        return {
            "assets_before": len(original_assets),
            "assets_after": len(assets_after),
            "assets_preserved": count_preserved,
            "assets_with_category": assets_with_category,
        }


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='资产分类数据迁移工具 - 最终优化版本')
    parser.add_argument('--execute', action='store_true', help='实际执行迁移（默认试运行）')
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    print("=" * 60)
    print("🏦 资产分类数据迁移工具 - 最终优化版本")
    print("📂 基于精确匹配的优化映射")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        migrator = CategoryMigrator(db)
        result = migrator.execute_migration(dry_run=dry_run)
        
        print("\n📊 迁移结果:")
        print(f"状态: {result.get('status', 'unknown')}")
        print(f"消息: {result.get('message', '无详细信息')}")
        
        if not dry_run:
            print("\n🎉 迁移完成！请检查以下关键分类是否正确:")
            print("  - 股票类资产 → 权益类/股票")
            print("  - 银行存款 → 现金类/银行存款") 
            print("  - 基金 → 权益类/基金")
            print("  - 保险 → 保险资产")
            print("  - 房地产 → 实物资产/房地产")
            
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()

# # 在 backend 目录下执行
# cd F:\code\personal-finance-dashboard\backend

# # 试运行
# python app/utils/migrate_categories.py 

# # 实际执行
# python app/utils/migrate_categories.py --execute

# 如果未来数据继续变化 改成 init_data3.py即可