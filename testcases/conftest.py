import pytest
from utils.log_util import logger

@pytest.fixture(scope="session")
def global_setup():
    logger.info("=== 🚀 测试会话开始 (Session Start) ===")
    yield
    logger.info("=== 🏁 测试会话结束 (Session End) ===")