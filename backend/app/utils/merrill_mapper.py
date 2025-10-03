from typing import Dict, List
from sqlalchemy.orm import Session
from app.models import Asset, AssetCategory

class MerrillAllocationMapper:
    """美林时钟资产配置分析引擎"""
    
    # 美林时钟各阶段的标准配置建议
    MERRILL_STANDARD_SUGGESTIONS = {
        "recovery": {"equity": 0.60, "bond": 0.20, "commodity": 0.10, "cash": 0.10},
        "overheat": {"equity": 0.30, "bond": 0.20, "commodity": 0.40, "cash": 0.10},
        "stagflation": {"equity": 0.10, "bond": 0.10, "commodity": 0.70, "cash": 0.10},
        "recession": {"equity": 0.20, "bond": 0.50, "commodity": 0.20, "cash": 0.10}
    }
    
    # 资产分类到美林大类的动态映射规则
    MAPPING_RULES = {
        # 加密货币 - 动态权重映射
        "alternative.crypto": {
            "recovery": {"equity": 0.6, "commodity": 0.3, "cash": 0.1, "bond": 0.0},
            "overheat": {"equity": 0.4, "commodity": 0.5, "cash": 0.1, "bond": 0.0},
            "stagflation": {"equity": 0.1, "commodity": 0.7, "cash": 0.2, "bond": 0.0},
            "recession": {"equity": 0.3, "commodity": 0.5, "cash": 0.1, "bond": 0.1}
        },
        # 黄金 - 主要商品属性，但在不同阶段略有变化
        "physical.gold": {
            "recovery": {"equity": 0.1, "commodity": 0.9, "cash": 0.0, "bond": 0.0},
            "overheat": {"equity": 0.0, "commodity": 1.0, "cash": 0.0, "bond": 0.0},
            "stagflation": {"equity": 0.0, "commodity": 1.0, "cash": 0.0, "bond": 0.0},
            "recession": {"equity": 0.2, "commodity": 0.8, "cash": 0.0, "bond": 0.0}
        },
        # 房地产 - 商品属性为主
        "physical.real_estate": {
            "recovery": {"equity": 0.3, "commodity": 0.7, "cash": 0.0, "bond": 0.0},
            "overheat": {"equity": 0.2, "commodity": 0.8, "cash": 0.0, "bond": 0.0},
            "stagflation": {"equity": 0.1, "commodity": 0.9, "cash": 0.0, "bond": 0.0},
            "recession": {"equity": 0.2, "commodity": 0.8, "cash": 0.0, "bond": 0.0}
        }
    }
    
    # 默认映射规则（用于没有特殊规则的资产）
    DEFAULT_MAPPING = {
        "equity": {"equity": 1.0, "commodity": 0.0, "cash": 0.0, "bond": 0.0},
        "fixed_income": {"equity": 0.0, "commodity": 0.0, "cash": 0.0, "bond": 1.0},
        "cash": {"equity": 0.0, "commodity": 0.0, "cash": 1.0, "bond": 0.0},
        "physical": {"equity": 0.0, "commodity": 1.0, "cash": 0.0, "bond": 0.0},
        "alternative": {"equity": 0.5, "commodity": 0.5, "cash": 0.0, "bond": 0.0},
        "insurance": {"equity": 0.0, "commodity": 0.0, "cash": 0.0, "bond": 1.0}  # 保险归为债券类
    }
    
    def __init__(self, db: Session):
        self.db = db
        self._category_cache = {}
    
    def _get_category_full_path(self, category_id: int) -> str:
        """获取分类的完整路径代码"""
        if category_id in self._category_cache:
            return self._category_cache[category_id]
        
        category = self.db.query(AssetCategory).filter(AssetCategory.id == category_id).first()
        if not category:
            return ""
        
        # 构建完整路径 (如: equity.stock.cn_a)
        path_codes = []
        current = category
        while current:
            path_codes.insert(0, current.code)
            if current.parent_id:
                current = self.db.query(AssetCategory).filter(AssetCategory.id == current.parent_id).first()
            else:
                current = None
        
        full_path = ".".join(path_codes)
        self._category_cache[category_id] = full_path
        return full_path
    
    def _get_mapping_weights(self, category_path: str, phase: str) -> Dict[str, float]:
        """获取指定分类在特定阶段的映射权重"""
        # 优先使用精确匹配的动态映射规则
        if category_path in self.MAPPING_RULES and phase in self.MAPPING_RULES[category_path]:
            return self.MAPPING_RULES[category_path][phase].copy()
        
        # 使用一级分类的默认映射
        first_level = category_path.split('.')[0] if '.' in category_path else category_path
        if first_level in self.DEFAULT_MAPPING:
            return self.DEFAULT_MAPPING[first_level].copy()
        
        # 兜底映射
        return {"equity": 0.0, "commodity": 0.0, "cash": 0.0, "bond": 1.0}
    
    def analyze_user_allocation(self, assets: List[Asset], phase: str = "recovery") -> Dict:
        """分析用户资产配置"""
        total_amount = sum(asset.amount for asset in assets)
        if total_amount == 0:
            return self._get_empty_analysis(phase)
        
        # 初始化美林四大类金额
        merrill_allocation = {"equity": 0.0, "commodity": 0.0, "cash": 0.0, "bond": 0.0}
        
        # 对每个资产进行映射计算
        for asset in assets:
            category_path = self._get_category_full_path(asset.primary_category_id)
            weights = self._get_mapping_weights(category_path, phase)
            
            # 按权重分配到美林四大类
            for merrill_class, weight in weights.items():
                merrill_allocation[merrill_class] += asset.amount * weight
        
        # 计算比例
        user_allocation = {
            class_name: amount / total_amount 
            for class_name, amount in merrill_allocation.items()
        }
        
        # 获取美林建议配置
        merrill_suggestion = self.MERRILL_STANDARD_SUGGESTIONS.get(phase, self.MERRILL_STANDARD_SUGGESTIONS["recovery"])
        
        # 生成调整建议
        adjustment_advice = self._generate_adjustment_advice(
            user_allocation, merrill_suggestion, total_amount
        )
        
        # 计算健康度评分
        health_score = self._calculate_health_score(user_allocation, merrill_suggestion)
        
        return {
            "user_allocation": user_allocation,
            "merrill_suggestion": merrill_suggestion,
            "adjustment_advice": adjustment_advice,
            "health_score": health_score,
            "total_amount": total_amount
        }
    
    def _generate_adjustment_advice(self, user_alloc: Dict, suggestion: Dict, total_amount: float) -> List[Dict]:
        """生成调整建议"""
        advice = []
        threshold = 0.05  # 5%的偏差阈值
        
        for class_name in user_alloc.keys():
            diff = user_alloc[class_name] - suggestion[class_name]
            if abs(diff) > threshold:
                action = "decrease" if diff > 0 else "increase"
                amount = abs(diff) * total_amount
                
                # 根据资产大类给出具体建议
                category_names = {
                    "equity": "权益类资产",
                    "bond": "债券类资产", 
                    "commodity": "商品类资产",
                    "cash": "现金类资产"
                }
                
                advice.append({
                    "category": class_name,
                    "category_name": category_names.get(class_name, class_name),
                    "action": action,
                    "amount": round(amount, 2),
                    "current_percent": round(user_alloc[class_name] * 100, 1),
                    "suggested_percent": round(suggestion[class_name] * 100, 1),
                    "reason": f"当前配置{round(user_alloc[class_name] * 100, 1)}%，当前周期基准{round(suggestion[class_name] * 100, 1)}%"
                })
        
        return advice
    
    def _calculate_health_score(self, user_alloc: Dict, suggestion: Dict) -> float:
        """计算配置健康度评分 (0-100分)"""
        total_diff = 0
        for class_name in user_alloc.keys():
            diff = abs(user_alloc[class_name] - suggestion[class_name])
            total_diff += diff
        
        # 差异越小分数越高，最大差异为2（100%偏差），所以用(1 - total_diff/2)计算比例
        score = max(0, (1 - total_diff / 2) * 100)
        return round(score, 1)
    
    def _get_empty_analysis(self, phase: str) -> Dict:
        """返回空资产的分析结果"""
        return {
            "user_allocation": {"equity": 0.0, "commodity": 0.0, "cash": 0.0, "bond": 0.0},
            "merrill_suggestion": self.MERRILL_STANDARD_SUGGESTIONS.get(phase, self.MERRILL_STANDARD_SUGGESTIONS["recovery"]),
            "adjustment_advice": [],
            "health_score": 0.0,
            "total_amount": 0
        }