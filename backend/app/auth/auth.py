from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import or_
from jose import jwt, JWTError
from datetime import datetime, timedelta
import logging

# 使用绝对导入
from app.database import get_db
from app.models import User
from app.schemas import user as user_schemas
from app.auth.security import hash_password, verify_password, create_access_token, SECRET_KEY, ALGORITHM

# 设置日志记录器
logger = logging.getLogger(__name__)

# OAuth2方案配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# 创建一个路由管理器，所有路径都会自动加前缀 `/auth`
router = APIRouter(prefix="/auth", tags=["认证接口"])

@router.post("/register", response_model=user_schemas.UserResponse)
async def register_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    """
    # 1. 检查用户名是否已存在
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已被注册")
    
    # 2. 检查邮箱是否已存在
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被注册")
    
    # 3. 哈希密码
    hashed_password_str = hash_password(user.password)
    
    # 4. 创建新用户
    db_user = User(
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

@router.post("/login", response_model=user_schemas.UserLoginResponse)
async def login_user(user: user_schemas.UserLogin, db: Session = Depends(get_db)):
    """
    用户登录接口 - 支持用户名或邮箱登录
    """
    try:
        # 添加详细的调试信息
        print(f"=== 登录调试信息 ===")
        print(f"请求数据 - username: '{user.username}', email: '{user.email}'")
        print(f"邮箱长度: {len(user.email) if user.email else 'None'}")
        print(f"邮箱类型: {type(user.email)}")
        # 1. 根据用户名或邮箱查找用户
        if user.username:
            # 使用用户名登录
            db_user = db.query(User).filter(User.username == user.username).first()
            login_type = "用户名"
            identifier = user.username
            print(f"使用用户名查找: '{user.username}'")
        else:
            # 使用邮箱登录
            db_user = db.query(User).filter(User.email == user.email).first()
            login_type = "邮箱"
            identifier = user.email
            print(f"使用邮箱查找: '{user.email}'")
        
         # 打印查询结果和所有用户对比
        if db_user:
            print(f"✅ 找到用户: ID={db_user.id}, 用户名='{db_user.username}', 邮箱='{db_user.email}'")
        else:
            print(f"❌ 未找到用户")
            # 打印数据库中所有用户用于对比
            all_users = db.query(User).all()
            print("📋 数据库中的所有用户:")
            for u in all_users:
                print(f"  - 用户名: '{u.username}', 邮箱: '{u.email}'")


        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"{login_type} {identifier} 不存在"
            )
        
        # 2. 验证密码
        if not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="密码错误"
            )
        
        # 3. 生成JWT令牌
        access_token = create_access_token(data={"sub": str(db_user.id)})
        
        # 4. 返回令牌和用户信息
        userloginresponse = user_schemas.UserLoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_schemas.UserLoginResponseBase(
                id=db_user.id,
                role=db_user.role,
                username=db_user.username,
                email=db_user.email
            )
        )

        logger.info(f"用户登录成功: {db_user.username} (ID: {db_user.id})")
        return userloginresponse
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登录过程错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系统内部错误，请稍后重试"
        )

@router.post("/token", response_model=user_schemas.Token)
async def login_for_swagger(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    专门为Swagger UI的Authorize按钮提供的登录端点
    注意：Swagger的OAuth2表单只支持用户名，不支持双通道登录
    """
    # 尝试用用户名查找用户
    db_user = db.query(User).filter(User.username == form_data.username).first()
    
    # 如果用户名没找到，尝试用邮箱查找（扩展Swagger支持）
    if not db_user:
        db_user = db.query(User).filter(User.email == form_data.username).first()
    
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名/邮箱或密码错误")
    
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

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
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    return user