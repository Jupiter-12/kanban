"""API路由模块。"""

from fastapi import APIRouter

from .auth import router as auth_router
from .projects import router as projects_router
from .columns import router as columns_router
from .tasks import router as tasks_router
from .users import router as users_router

router = APIRouter()

# 注册认证路由
router.include_router(auth_router)
# 注册项目路由
router.include_router(projects_router)
# 注册列路由
router.include_router(columns_router)
# 注册任务路由
router.include_router(tasks_router)
# 注册用户路由
router.include_router(users_router)


@router.get("/health")
async def health_check() -> dict:
    """健康检查接口。

    Returns:
        健康状态信息
    """
    return {"status": "ok", "message": "服务运行正常"}
