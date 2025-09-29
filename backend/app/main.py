from fastapi import FastAPI
from .database import engine, Base
from fastapi.middleware.cors import CORSMiddleware

# 统一导入方式
from app.auth import auth as auth_router
from app.routes import user as user_router  
from app.routes import asset as asset_router
from app.routes import categories as categories_router
# 暂时注释掉analytics，等后续开发
# from app.routes import analytics as analytics_router

from . import models  # 这行很重要，用于让SQLAlchemy发现所有模型

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 初始化FastAPI应用
app = FastAPI(title="个人资产管理系统API", version="0.1.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                   "http://127.0.0.1:5173",
                   "https://pc.tail4461b.ts.net", 
                   "https://100.80.154.12:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 统一挂载路由（使用导入的变量名）
app.include_router(auth_router.router)
app.include_router(user_router.router)  
app.include_router(asset_router.router)
app.include_router(categories_router.router)
# 暂时注释掉analytics
# app.include_router(analytics_router.router, prefix="/api/analytics", tags=["analytics"])

# 一个最简单的根端点，用于测试服务器是否存活
@app.get("/")
def read_root():
    return {"message": "Personal Finance API Server is Running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}