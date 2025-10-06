from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class DiagnosisReport(Base):
    __tablename__ = "diagnosis_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    health_score = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    user_allocation = Column(JSON, nullable=False)
    merrill_suggestion = Column(JSON, nullable=False)
    adjustment_advice = Column(JSON, nullable=False)
    economic_phase = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 如果不是FastAPI + Pydantic 的 from_attributes=True 这个框架，就需要手动to_dict
    # def to_dict(self):
    #     return {
    #         "id": self.id,
    #         "title": self.title,
    #         "health_score": self.health_score,
    #         "total_amount": self.total_amount,
    #         "user_allocation": self.user_allocation,
    #         "merrill_suggestion": self.merrill_suggestion,
    #         "adjustment_advice": self.adjustment_advice,
    #         "economic_phase": self.economic_phase,
    #         "created_at": self.created_at.isoformat() if self.created_at else None
        # }