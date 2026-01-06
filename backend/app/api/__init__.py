"""API路由模块。"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """健康检查接口。

    Returns:
        健康状态信息
    """
    return {"status": "ok", "message": "服务运行正常"}
