"""API路由模块。"""

from fastapi import APIRouter

from .auth import router as auth_router

router = APIRouter()

# 注册认证路由
router.include_router(auth_router)


@router.get("/health")
async def health_check() -> dict:
    """健康检查接口。

    Returns:
        健康状态信息
    """
    return {"status": "ok", "message": "服务运行正常"}
