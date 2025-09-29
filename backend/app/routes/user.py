from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User as UserModel
from app.schemas import user as user_schemas
from app.auth import get_current_user

router = APIRouter(prefix="/users", tags=["用户管理"])

@router.get("/me", response_model=user_schemas.UserResponse)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    """获取当前用户信息（需要认证）"""
    return current_user

@router.get("/{user_id}", response_model=user_schemas.UserResponse)
async def read_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """获取指定用户信息（需要认证）"""
    # 如果用户查看自己的信息，直接返回
    if current_user.id == user_id:
        return current_user

    # 权限检查：只有管理员可以访问
    if current_user.role == "admin":
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        return db_user
        
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="没有权限访问其他用户信息"
    )

@router.get("/summary/users", response_model=user_schemas.UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=10, description="每页记录数"),
    role: Optional[user_schemas.UserRole] = Query(None, description="按用户类型过滤"), 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> user_schemas.UserListResponse:
    """查询所有用户（仅管理员）"""
    # 权限检查：只有管理员可以访问
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问其他用户信息"  
        )
    
    # 基础查询
    query = db.query(UserModel)
    
    # 过滤条件
    if role:
        query = query.filter(UserModel.role == role)    
    
    # 总数
    total = query.count()
    # 分页查询
    users = query.order_by(UserModel.created_at.desc()).offset(skip).limit(limit).all()
    
    return user_schemas.UserListResponse(total=total, items=users)