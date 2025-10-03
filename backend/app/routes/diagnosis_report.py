from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.diagnosis_report import DiagnosisReport
from app.models.user import User
from app.auth.auth import get_current_user

router = APIRouter(prefix="/reports", tags=["诊断报告"])

@router.get("")
async def get_user_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的所有诊断报告"""
    reports = db.query(DiagnosisReport).filter(
        DiagnosisReport.user_id == current_user.id
    ).order_by(DiagnosisReport.created_at.desc()).all()
    
    return {
        "reports": [report.to_dict() for report in reports]
    }

@router.get("/{report_id}")
async def get_report_detail(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取特定诊断报告的详细信息"""
    report = db.query(DiagnosisReport).filter(
        DiagnosisReport.id == report_id,
        DiagnosisReport.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    return report.to_dict()

@router.post("")
async def save_diagnosis_report(
    report_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """保存诊断报告"""
    from datetime import datetime
    title = f"资产诊断报告 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    report = DiagnosisReport(
        user_id=current_user.id,
        title=title,
        health_score=report_data["health_score"],
        total_amount=report_data["total_amount"],
        user_allocation=report_data["user_allocation"],
        merrill_suggestion=report_data["merrill_suggestion"],
        adjustment_advice=report_data["adjustment_advice"],
        economic_phase=report_data.get("economic_phase", "recovery")
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return {"id": report.id, "title": title, "message": "报告保存成功"}

@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除诊断报告"""
    report = db.query(DiagnosisReport).filter(
        DiagnosisReport.id == report_id,
        DiagnosisReport.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    db.delete(report)
    db.commit()
    
    return {"message": "报告删除成功"}