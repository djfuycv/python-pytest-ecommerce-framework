# test_login_simple.py（纯本地、无依赖、保证能跑）
import sys
import os
# 把项目根目录加入Python路径（避免导入报错）
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.login_api import LoginApi
from utils.log_util import logger

# 直接实例化登录接口
api = LoginApi()

def test_login_success():
    """测试：正确密码登录"""
    resp = api.login("test_user", "test_pass_123")
    assert resp["code"] == 200, f"正确密码登录失败！响应：{resp}"
    assert resp["msg"] == "success", f"正确密码登录提示语错误！响应：{resp}"
    logger.info("✅ 正确密码登录测试通过")

def test_login_fail_wrong_pwd():
    """测试：错误密码登录"""
    resp = api.login("test_user", "wrong_pass_123")
    assert resp["code"] == 401, f"错误密码登录失败！响应：{resp}"
    assert resp["msg"] == "password error", f"错误密码登录提示语错误！响应：{resp}"
    logger.info("✅ 错误密码登录测试通过")

def test_login_fail_user_not_exist():
    """测试：用户不存在"""
    resp = api.login("not_exist_user", "any_pass")
    assert resp["code"] == 404, f"用户不存在登录失败！响应：{resp}"
    assert resp["msg"] == "user not found", f"用户不存在登录提示语错误！响应：{resp}"
    logger.info("✅ 用户不存在登录测试通过")


def test_login_fail_locked_user():
    """测试：锁定账号登录"""
    resp = api.login("locked_user", "test_pass_456")
    assert resp["code"] == 403, f"锁定账号登录失败！响应：{resp}"
    assert "locked" in resp["msg"], f"锁定账号提示语错误！响应：{resp}"
    logger.info("✅ 锁定账号登录测试通过")

def test_login_token_reuse():
    """测试：Token复用（登录成功后再次登录复用Token）"""
    # 第一次登录生成Token
    resp1 = api.login("test_user", "test_pass_123")
    token1 = resp1["data"]["token"]
    # 第二次登录复用Token
    resp2 = api.login("test_user", "test_pass_123")
    token2 = resp2["data"]["token"]
    assert token1 == token2, f"Token未复用！第一次：{token1}，第二次：{token2}"
    logger.info("✅ Token复用测试通过")
# 直接执行测试（不用pytest，避免筛选问题）
if __name__ == "__main__":
    try:
        test_login_success()
        test_login_fail_wrong_pwd()
        test_login_fail_user_not_exist()
        print("\n🎉 所有核心登录测试通过！")
    except AssertionError as e:
        print(f"\n❌ 测试失败：{e}")
    except Exception as e:
        print(f"\n❌ 代码报错：{e}")