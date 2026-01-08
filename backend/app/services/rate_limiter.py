"""速率限制服务模块。

提供简单的内存速率限制功能，用于防止暴力破解攻击。
生产环境建议使用Redis等持久化存储。
"""

import threading
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple


class RateLimiter:
    """速率限制器。

    基于滑动窗口算法实现的速率限制。
    """

    def __init__(
        self,
        max_attempts: int = 5,
        window_seconds: int = 300,
        lockout_seconds: int = 900,
    ):
        """初始化速率限制器。

        Args:
            max_attempts: 窗口期内最大尝试次数
            window_seconds: 窗口期时长（秒）
            lockout_seconds: 锁定时长（秒）
        """
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.lockout_seconds = lockout_seconds
        # 存储格式: {key: [(timestamp, success), ...]}
        self._attempts: Dict[str, list] = defaultdict(list)
        # 存储锁定时间: {key: lockout_until}
        self._lockouts: Dict[str, datetime] = {}
        self._lock = threading.Lock()

    def is_allowed(self, key: str) -> Tuple[bool, int]:
        """检查是否允许请求。

        Args:
            key: 限制键（如IP地址或用户名）

        Returns:
            (是否允许, 剩余等待秒数)
        """
        with self._lock:
            now = datetime.now(timezone.utc)

            # 检查是否被锁定
            if key in self._lockouts:
                lockout_until = self._lockouts[key]
                if now < lockout_until:
                    remaining = int((lockout_until - now).total_seconds())
                    return False, remaining
                else:
                    # 锁定已过期，清除
                    del self._lockouts[key]

            # 清理过期的尝试记录
            window_start = now - timedelta(seconds=self.window_seconds)
            self._attempts[key] = [
                (ts, success) for ts, success in self._attempts[key]
                if ts > window_start
            ]

            # 统计失败次数
            failed_attempts = sum(
                1 for ts, success in self._attempts[key] if not success
            )

            if failed_attempts >= self.max_attempts:
                # 触发锁定
                lockout_until = now + timedelta(seconds=self.lockout_seconds)
                self._lockouts[key] = lockout_until
                return False, self.lockout_seconds

            return True, 0

    def check_and_record_attempt(self, key: str, success: bool) -> Tuple[bool, int, int]:
        """原子性地检查速率限制并记录尝试（用于登录场景）。

        此方法将检查和记录合并为一个原子操作，避免竞态条件。

        Args:
            key: 限制键
            success: 本次尝试是否成功

        Returns:
            (是否允许本次尝试, 剩余等待秒数, 剩余尝试次数)
        """
        with self._lock:
            now = datetime.now(timezone.utc)

            # 检查是否被锁定
            if key in self._lockouts:
                lockout_until = self._lockouts[key]
                if now < lockout_until:
                    remaining = int((lockout_until - now).total_seconds())
                    return False, remaining, 0
                else:
                    # 锁定已过期，清除
                    del self._lockouts[key]

            # 清理过期的尝试记录
            window_start = now - timedelta(seconds=self.window_seconds)
            self._attempts[key] = [
                (ts, s) for ts, s in self._attempts[key]
                if ts > window_start
            ]

            # 统计当前失败次数
            failed_attempts = sum(
                1 for ts, s in self._attempts[key] if not s
            )

            # 检查是否已达到限制
            if failed_attempts >= self.max_attempts:
                # 触发锁定
                lockout_until = now + timedelta(seconds=self.lockout_seconds)
                self._lockouts[key] = lockout_until
                return False, self.lockout_seconds, 0

            # 记录本次尝试
            self._attempts[key].append((now, success))

            # 如果成功，清除该键的所有记录和锁定
            if success:
                self._attempts[key] = []
                if key in self._lockouts:
                    del self._lockouts[key]
                return True, 0, self.max_attempts

            # 计算剩余尝试次数（包含本次失败）
            new_failed_attempts = failed_attempts + 1
            remaining_attempts = max(0, self.max_attempts - new_failed_attempts)

            # 如果本次失败后达到限制，触发锁定
            if new_failed_attempts >= self.max_attempts:
                lockout_until = now + timedelta(seconds=self.lockout_seconds)
                self._lockouts[key] = lockout_until
                return True, 0, 0  # 本次允许，但已记录失败

            return True, 0, remaining_attempts

    def record_attempt(self, key: str, success: bool) -> None:
        """记录一次尝试。

        Args:
            key: 限制键
            success: 是否成功
        """
        with self._lock:
            now = datetime.now(timezone.utc)
            self._attempts[key].append((now, success))

            # 如果成功，清除该键的所有记录和锁定
            if success:
                self._attempts[key] = []
                if key in self._lockouts:
                    del self._lockouts[key]

    def get_remaining_attempts(self, key: str) -> int:
        """获取剩余尝试次数。

        Args:
            key: 限制键

        Returns:
            剩余尝试次数
        """
        with self._lock:
            now = datetime.now(timezone.utc)
            window_start = now - timedelta(seconds=self.window_seconds)

            # 统计窗口期内的失败次数
            failed_attempts = sum(
                1 for ts, success in self._attempts.get(key, [])
                if ts > window_start and not success
            )

            return max(0, self.max_attempts - failed_attempts)


# 全局登录速率限制器实例
# 5次失败后锁定15分钟
login_rate_limiter = RateLimiter(
    max_attempts=5,
    window_seconds=300,  # 5分钟窗口
    lockout_seconds=900,  # 锁定15分钟
)
