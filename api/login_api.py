from utils.request_util import RequestUtil
from utils.redis_util import redis_util
from utils.db_util import db_util
from utils.log_util import logger


class LoginApi:
    def __init__(self):
        self.req = RequestUtil()

    def login(self, username, password):
        logger.info(f"收到登录请求：用户={username}, 密码长度={len(password)}")

        # 1. 【核心修改】即使 Redis 有 Token，只要用户传了密码，就必须验证密码！
        # 防止“一旦登录过，输错密码也成功”的逻辑漏洞
        user_info = db_util.query_user(username)

        if not user_info:
            return {"code": 404, "msg": "user not found", "data": None}

        if user_info['password'] != password:
            # 密码错误：DB 失败次数 +1
            db_util.update_fail_count(username, increment=True)
            return {"code": 401, "msg": "password error", "data": None}

        # 2. 密码验证通过，生成/获取 Token
        # 先看看 Redis 有没有，有就直接用（单点登录特性），没有就新生成
        cached_token = redis_util.get_token(username)
        if cached_token:
            token = cached_token
            logger.info("复用现有 Token")
        else:
            token = f"token_{username}_8888"
            redis_util.set_token(username, token)
            logger.info("生成新 Token")

        # 3. 登录成功：重置失败次数
        db_util.update_fail_count(username, increment=False)

        # 4. 模拟调用外部接口
        self.req.send("POST", "/post", data={"login": "success"})

        return {"code": 200, "msg": "success", "data": {"token": token}}