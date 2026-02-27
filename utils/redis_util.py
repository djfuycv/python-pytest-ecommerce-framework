from utils.log_util import logger

# 用字典模拟 Redis 数据库
mock_redis_db = {}

class MockRedisUtil:
    def set_token(self, username, token, expire=3600):
        key = f"user_token:{username}"
        mock_redis_db[key] = token
        logger.info(f"[Mock Redis] SET {key} = {token[:10]}...")

    def get_token(self, username):
        key = f"user_token:{username}"
        token = mock_redis_db.get(key)
        if token:
            logger.info(f"[Mock Redis] HIT {key}")
            return token
        logger.warning(f"[Mock Redis] MISS {key}")
        return None

redis_util = MockRedisUtil()