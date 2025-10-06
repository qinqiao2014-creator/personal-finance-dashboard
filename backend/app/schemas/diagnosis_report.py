from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime

class AdjustmentAdvice(BaseModel):
    category: str
    category_name: str
    action: str
    amount: float
    current_percent: float
    suggested_percent: float
    reason: str

class DiagnosisReportCreate(BaseModel):
    health_score: float
    total_amount: float
    user_allocation: Dict[str, float]
    merrill_suggestion: Dict[str, float]
    adjustment_advice: List[AdjustmentAdvice]
    economic_phase: str = "recovery"

class DiagnosisReportResponse(BaseModel):
    id: int
    title: str
    health_score: float
    total_amount: float
    user_allocation: Dict[str, float]
    merrill_suggestion: Dict[str, float]
    adjustment_advice: List[Dict[str, Any]]
    economic_phase: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class DiagnosisReportList(BaseModel):
    reports: List[DiagnosisReportResponse]