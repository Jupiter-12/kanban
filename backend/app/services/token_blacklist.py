"""令牌黑名单服务模块。

使用内存存储实现简单的令牌黑名单，用于使JWT令牌失效。
生产环境建议使用Redis等持久化存储。
"""

import threading
from datetime import datetime, timezone
from typing import Dict, Optional

from ..config import settings


class TokenBlacklist:
    """令牌黑名单管理类。

    使用内存字典存储已失效的令牌JTI（JWT ID）。
    定期清理过期的黑名单条目以节省内存。
    """

    def __init__(self):
        """初始化黑名单存储。"""
        self._blacklist: Dict[str, datetime] = {}
        self._lock = threading.Lock()

    def add(self, jti: str, exp: Optional[datetime] = None) -> None:
        """将令牌添加到黑名单。

        Args:
            jti: JWT ID（令牌唯一标识）
            exp: 令牌过期时间，用于自动清理
        """
        with self._lock:
            # 如果没有提供过期时间，使用默认过期时间
            if exp is None:
                from datetime import timedelta
                exp = datetime.now(timezone.utc) + timedelta(
                    minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
                )
            self._blacklist[jti] = exp
            # 每次添加时清理过期条目
            self._cleanup()

    def is_blacklisted(self, jti: str) -> bool:
        """检查令牌是否在黑名单中。

        Args:
            jti: JWT ID

        Returns:
            如果令牌在黑名单中返回True
        """
        with self._lock:
            return jti in self._blacklist

    def _cleanup(self) -> None:
        """清理过期的黑名单条目。"""
        now = datetime.now(timezone.utc)
        expired_jtis = [
            jti for jti, exp in self._blacklist.items()
            if exp < now
        ]
        for jti in expired_jtis:
            del self._blacklist[jti]


# 全局黑名单实例
token_blacklist = TokenBlacklist()
