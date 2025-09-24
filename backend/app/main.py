from fastapi import FastAPI
from .database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
# from . import models  # 这行很重要，用于让SQLAlchemy发现所有模型

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 初始化FastAPI应用
app = FastAPI(title="个人资产管理系统API", version="0.1.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有头
)



# 导入并挂载路由
from app.routes import auth, user , asset  # 添加user路由
app.include_router(auth.router)
app.include_router(user.router)  
app.include_router(asset.router) 

# 一个最简单的根端点，用于测试服务器是否存活
@app.get("/")
def read_root():
    return {"message": "Personal Finance API Server is Running!"}

