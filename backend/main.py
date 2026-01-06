"""看板系统后端入口文件。"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as api_router


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

    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(api_router, prefix="/api")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
