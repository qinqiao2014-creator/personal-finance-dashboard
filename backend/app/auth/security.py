from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
import bcrypt as bcrypt_module  # 添加这行

# 手动设置bcrypt版本信息（修复警告）
if not hasattr(bcrypt_module, '__about__'):
    bcrypt_module.__about__ = type('obj', (object,), {'__version__': '3.2.0'})
    
# JWT配置
SECRET_KEY = "dev-secret-key-change-before-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 密码哈希配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """创建JWT访问令牌"""
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        raise Exception(f"JWT令牌生成失败: {str(e)}")