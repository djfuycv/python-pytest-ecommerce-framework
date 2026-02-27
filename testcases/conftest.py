
import pytest
from api.login_api import LoginApi
from utils.log_util import logger


@pytest.fixture(scope="session")
def login_token():
    """
    全局登录 Fixture
    整个测试会话只执行一次，返回 Token 供其他用例使用
    """
    logger.info("=== 🚀 全局前置：登录获取 Token ===")
    api = LoginApi()

    # 调用登录接口 (使用硬编码的测试账号，或者从 YAML 读)
    resp = api.login("admin", "123456")

    if resp['code'] == 200:
        token = resp['data']['token']
        logger.info(f"Token 获取成功：{token}")
        yield token
    else:
        logger.error(f"登录失败：{resp}")
        pytest.fail("全局登录失败，无法继续测试商品模块")