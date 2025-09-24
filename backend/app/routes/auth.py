from fastapi import APIRouter, HTTPException, Depends, status
import logging
from sqlalchemy.orm import Session
from .. import schemas, models
from ..database import get_db 
from ..auth import hash_password ,verify_password  # 导入哈希工具
from datetime import datetime, timedelta
from jose import jwt
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import JWTError



# JWT配置 - 需要添加到您的配置中
SECRET_KEY = "dev-secret-key-change-before-production"  # 开发环境使用，生产前请更改
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 设置日志记录器
logger = logging.getLogger(__name__)

#创建JWT访问令牌
def create_access_token(data: dict):
    """
    创建JWT访问令牌
    """
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"JWT令牌生成失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="令牌生成失败"
        )



# 创建一个路由管理器，所有路径都会自动加前缀 `/auth`
router = APIRouter(prefix="/auth", tags=["认证接口"])

@router.post("/register", response_model=schemas.UserResponse)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    """
    # 1. 检查用户名是否已存在
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已被注册")
    
    # 2. 检查邮箱是否已存在
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被注册")
    
    # 3. 哈希密码
    hashed_password_str = hash_password(user.password)
    
    # 4. 创建新用户
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password_str,
        role=user.role
    )
    
    # 5. 保存到数据库
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # 6. 返回创建的用户信息（不包含密码）
    return db_user

#json入口
@router.post("/login")
async def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    用户登录接口
    """
    try:
        # 1. 查找用户
        db_user = db.query(models.User).filter(
            models.User.username == user.username).first()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"  # 模糊提示增强安全性
            )
        
        # 2. 验证密码
        if not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 3. 生成JWT令牌
        access_token = create_access_token(data={"sub":str(db_user.id)})
        
        # 4. 返回令牌
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role":db_user.role,
            "user_id": db_user.id,
            "username": db_user.username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登录过程错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统内部错误，请稍后重试"
        )

#表单token
@router.post("/token",response_model=schemas.Token)
async def login_for_swagger(form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    """
    专门为Swagger UI的Authorize按钮提供的登录端点
    """
    # 复用现有的登录逻辑，但使用表单数据
    db_user = db.query(models.User).filter(
        models.User.username == form_data.username
    ).first()
    
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# OAuth2方案配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    获取当前用户的依赖项
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码JWT令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 从数据库获取用户信息
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    return user

