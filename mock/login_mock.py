from typing import Dict, Optional, Any
from utils.log_util import logger
import copy

# -------------------------- 基础 Mock 数据（原始模板，用于重置） --------------------------
# 原始模板：避免直接修改导致数据污染，每次重置时从模板复制
MOCK_USER_DB_TEMPLATE = {
    "test_user": {
        "username": "test_user",
        "password": "test_pass_123",
        "fail_count": 0,
        "status": "active",  # active / locked / frozen
        "role": "user",  # user / admin / super_admin
        "phone": "13800138000",  # 补充真实字段
        "email": "test@example.com",  # 补充真实字段
        "last_login_time": None  # 补充登录时间字段
    },
    "locked_user": {
        "username": "locked_user",
        "password": "test_pass_456",
        "fail_count": 5,
        "status": "locked",
        "role": "user",
        "phone": "13900139000",
        "email": "locked@example.com",
        "last_login_time": "2026-02-28 10:00:00"
    },
    "admin_user": {
        "username": "admin_user",
        "password": "admin_pass_789",
        "fail_count": 0,
        "status": "active",
        "role": "admin",
        "phone": "13700137000",
        "email": "admin@example.com",
        "last_login_time": None
    },
    "frozen_user": {
        "username": "frozen_user",
        "password": "frozen_pass_000",
        "fail_count": 0,
        "status": "frozen",  # 新增冻结状态
        "role": "user",
        "phone": "13600136000",
        "email": "frozen@example.com",
        "last_login_time": None
    }
}

# 运行时 Mock 数据（每次测试前可重置）
MOCK_USER_DB = copy.deepcopy(MOCK_USER_DB_TEMPLATE)
# 模拟 Redis Token 缓存（支持过期时间）
MOCK_REDIS_TOKEN: Dict[str, Dict[str, Any]] = {}


# -------------------------- Mock 工具类（增强功能） --------------------------
class LoginMock:
    # -------------------------- 基础 DB 操作 --------------------------
    @staticmethod
    def query_user(username: str) -> Optional[Dict[str, Any]]:
        """Mock 查询用户信息（返回副本，避免外部修改原始数据）"""
        logger.info(f"[Mock DB] 查询用户: {username}")
        user = MOCK_USER_DB.get(username)
        if user:
            # 返回深拷贝，防止外部修改 Mock 数据
            return copy.deepcopy(user)
        return None

    @staticmethod
    def update_fail_count(username: str, increment: bool = True) -> bool:
        """Mock 更新失败次数（完善状态流转）"""
        user = MOCK_USER_DB.get(username)
        if not user:
            logger.warning(f"[Mock DB] 用户 {username} 不存在，更新失败次数失败")
            return False

        # 更新失败次数
        if increment:
            # 已锁定/冻结的账号，不更新失败次数
            if user["status"] in ["locked", "frozen"]:
                logger.warning(f"[Mock DB] 用户 {username} 状态为 {user['status']}，跳过失败次数更新")
                return True
            user["fail_count"] += 1
            # 失败次数 >= 5 锁定账号
            if user["fail_count"] >= 5:
                user["status"] = "locked"
                logger.warning(f"[Mock DB] 用户 {username} 失败次数达5次，账号锁定")
        else:
            # 登录成功，重置失败次数 + 恢复active状态（如果是locked）
            user["fail_count"] = 0
            if user["status"] == "locked":
                user["status"] = "active"
                logger.info(f"[Mock DB] 用户 {username} 重置失败次数，解锁账号")

        logger.info(f"[Mock DB] 用户 {username} 失败次数更新为: {user['fail_count']}, 状态: {user['status']}")
        return True

    @staticmethod
    def update_last_login_time(username: str, login_time: str) -> bool:
        """Mock 更新最后登录时间（新增实用功能）"""
        user = MOCK_USER_DB.get(username)
        if not user:
            logger.warning(f"[Mock DB] 用户 {username} 不存在，更新登录时间失败")
            return False
        user["last_login_time"] = login_time
        logger.info(f"[Mock DB] 用户 {username} 最后登录时间更新为: {login_time}")
        return True

    # -------------------------- Redis Token 操作（支持过期时间） --------------------------
    @staticmethod
    def get_token(username: str) -> Optional[str]:
        """Mock 获取 Token（校验过期时间）"""
        logger.info(f"[Mock Redis] 获取 {username} 的 Token")
        token_info = MOCK_REDIS_TOKEN.get(username)
        if not token_info:
            return None

        # 【修改点1】修复：硬编码时间改为动态判断（避免Token永远过期/不过期）
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expire_at = token_info.get("expire_at")
        if expire_at and expire_at < current_time:
            logger.warning(f"[Mock Redis] 用户 {username} 的 Token 已过期（过期时间：{expire_at}，当前时间：{current_time}）")
            del MOCK_REDIS_TOKEN[username]  # 过期自动删除
            return None

        return token_info["token"]

    @staticmethod
    def set_token(username: str, token: str, expire_at: Optional[str] = None) -> None:
        """Mock 设置 Token（支持过期时间）"""
        MOCK_REDIS_TOKEN[username] = {
            "token": token,
            "expire_at": expire_at  # None=永不过期
        }
        logger.info(f"[Mock Redis] 设置 {username} 的 Token: {token}，过期时间: {expire_at or '永不过期'}")

    @staticmethod
    def del_token(username: str) -> bool:
        """Mock 删除 Token（新增登出功能）"""
        if username in MOCK_REDIS_TOKEN:
            del MOCK_REDIS_TOKEN[username]
            logger.info(f"[Mock Redis] 删除 {username} 的 Token")
            return True
        logger.warning(f"[Mock Redis] 用户 {username} 无 Token，删除失败")
        return False

    # -------------------------- 测试辅助功能（关键：避免数据污染） --------------------------
    @staticmethod
    def reset_mock_data() -> None:
        """重置所有 Mock 数据到初始状态（测试前必备）"""
        global MOCK_USER_DB, MOCK_REDIS_TOKEN
        MOCK_USER_DB = copy.deepcopy(MOCK_USER_DB_TEMPLATE)
        MOCK_REDIS_TOKEN = {}
        logger.info("[Mock] 所有 Mock 数据已重置为初始状态")

    @staticmethod
    def add_temp_user(username: str, user_info: Dict[str, Any]) -> bool:
        """新增临时用户（用于测试自定义场景）"""
        if username in MOCK_USER_DB:
            logger.warning(f"[Mock DB] 用户 {username} 已存在，新增失败")
            return False
        # 补充默认值，避免KeyError
        default_info = {
            "password": "",
            "fail_count": 0,
            "status": "active",
            "role": "user",
            "phone": "",
            "email": "",
            "last_login_time": None
        }
        user_info = {**default_info, **user_info}
        MOCK_USER_DB[username] = user_info
        logger.info(f"[Mock DB] 新增临时用户: {username}，信息: {user_info}")
        return True

    @staticmethod
    def del_temp_user(username: str) -> bool:
        """删除临时用户（测试后清理）"""
        if username not in MOCK_USER_DB_TEMPLATE and username in MOCK_USER_DB:
            del MOCK_USER_DB[username]
            logger.info(f"[Mock DB] 删除临时用户: {username}")
            return True
        logger.warning(f"[Mock DB] {username} 不是临时用户，删除失败")
        return False


# 单例导出
login_mock = LoginMock()