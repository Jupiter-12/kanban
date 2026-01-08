"""看板系统后端入口文件。"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as api_router
from app.config import settings
from app.models.database import init_db

# 导入模型以确保表被创建
from app.models import user  # noqa: F401


def create_app() -> FastAPI:
    """创建并配置FastAPI应用实例。

    Returns:
        配置好的FastAPI应用实例
    """
    app = FastAPI(
        title="看板系统",
        description="看板系统后端API服务",
        version="0.1.0",
    )

    # 配置CORS - 使用配置文件中的允许来源
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(api_router, prefix="/api")

    # 初始化数据库
    init_db()

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
