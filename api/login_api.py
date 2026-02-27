from utils.request_util import RequestUtil
from utils.redis_util import redis_util
from utils.db_util import db_util
from mock.login_mock import login_mock
from config.env_config import config
from utils.log_util import logger


class LoginApi:
    def __init__(self):
        self.req = RequestUtil()
        self.db = login_mock if config.IS_MOCK else db_util
        self.redis = login_mock if config.IS_MOCK else redis_util
        # 【修改点1】修复URL拼接：移除BASE_URL末尾的/，避免生成//post
        self.base_url = config.BASE_URL.rstrip("/")

    def login(self, username, password):

        logger.info(f"收到登录请求：用户={username}, 密码长度={len(password)}")

        # 【新增】密码长度校验（超长密码返回400）
        if len(password) > 50:
            logger.warning(f"⚠️ 密码长度超限：{len(password)}字符（最大50）")
            return {"code": 400, "msg": "密码长度超出限制", "data": None}

        # 原有登录逻辑（完全保留）
        user_info = self.db.query_user(username)
        if not user_info:
            return {"code": 404, "msg": "user not found", "data": None}

        if user_info['password'] != password:
            self.db.update_fail_count(username, increment=True)
            return {"code": 401, "msg": "password error", "data": None}

        # 【补充点1】原有框架遗漏：账号锁定判断（匹配Mock中的locked状态）
        if user_info.get("status") == "locked":
            return {"code": 403, "msg": "account locked", "data": None}

        cached_token = self.redis.get_token(username)
        if cached_token:
            token = cached_token
            logger.info("复用现有 Token")
        else:
            token = f"token_{username}_8888"
            self.redis.set_token(username, token)
            logger.info("生成新 Token")

        self.db.update_fail_count(username, increment=False)

        # 【修改点2】修复URL拼接：明确拼接完整URL，新增异常捕获（不影响登录核心）
        try:
            full_url = f"{self.base_url}/post"
            self.req.send("POST", full_url, data={"login": "success"})
        except Exception as e:
            # 仅打印警告，不阻断登录逻辑
            logger.warning(f"外部接口调用失败（不影响登录）：{str(e)[:100]}")

        return {"code": 200, "msg": "success", "data": {"token": token}}