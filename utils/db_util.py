from utils.log_util import logger

# 用列表模拟 users 表
# 结构：{'username': str, 'password': str, 'fail_count': int}
mock_users_db = [
    {"username": "admin", "password": "123456", "fail_count": 0},
    {"username": "user1", "password": "123456", "fail_count": 0}
]

class MockDBUtil:
    def query_user(self, username):
        for user in mock_users_db:
            if user['username'] == username:
                logger.info(f"[Mock DB] Query User: {username}, FailCount: {user['fail_count']}")
                return user
        logger.warning(f"[Mock DB] User Not Found: {username}")
        return None

    def update_fail_count(self, username, increment=True):
        for user in mock_users_db:
            if user['username'] == username:
                if increment:
                    user['fail_count'] += 1
                    logger.info(f"[Mock DB] Update FailCount +1: {username} -> {user['fail_count']}")
                else:
                    user['fail_count'] = 0
                    logger.info(f"[Mock DB] Reset FailCount: {username} -> 0")
                return True
        return False

db_util = MockDBUtil()