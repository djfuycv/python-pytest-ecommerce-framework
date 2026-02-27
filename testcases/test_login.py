import pytest
from api.login_api import LoginApi
from utils.data_util import data_util  # 复用统一的数据工具
from mock.login_mock import login_mock  # 导入Mock工具
from config.env_config import config  # 导入环境配置
from utils.log_util import logger

# 【修改点1】修复：补充缺失的db_util导入（否则db_tool会报错）
try:
    from utils.db_util import db_util
except ImportError:
    # 兼容：如果没有真实db_util，直接用login_mock兜底
    db_util = login_mock

# 核心优化1：复用data_util加载/处理数据（保留原有逻辑，仅简化筛选）
def load_filtered_login_cases():
    """加载登录用例：关闭环境筛选，返回所有用例（适配低版本pytest）"""
    all_cases = data_util.load_login_cases()
    # 核心修改：强制返回所有用例，不做任何筛选
    filtered_cases = all_cases
    # 日志更新：明确说明关闭筛选
    logger.info(f"✅ 加载登录用例：共{len(all_cases)}条，关闭环境筛选后可执行{len(filtered_cases)}条")
    return filtered_cases
test_data = load_filtered_login_cases()

class TestLogin:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """前置：初始化接口 + 重置Mock数据；后置：无（按需添加）"""
        self.api = LoginApi()
        # 仅Mock模式下重置数据，避免真实环境误操作
        if config.IS_MOCK:
            login_mock.reset_mock_data()
        logger.info(f"🔧 测试前置完成：Mock模式={config.IS_MOCK}，环境={config.env}")
        yield  # 用例执行后执行后置逻辑
        # 可选：后置清理（比如删除临时用户）
        # if config.IS_MOCK:
        #     login_mock.del_temp_user("temp_user")

    @pytest.mark.parametrize("case", test_data, ids=lambda x: x['case_name'])
    # 【修改点3】修复：移除P0标记筛选（避免命令行-m P0导致用例跳过）
    def test_login_scenarios(self, case):
        # 核心优化2：简化变量读取（保持原有逻辑）
        username = case['username']
        password = case['password']
        exp_code = case['expected_code']
        exp_msg = case['expected_msg']
        check_db = case.get('check_db', False)
        sensitive_check = case.get('sensitive_check', False)

        logger.info(f"🧪 执行用例：{case['case_name']}")

        # 1. 前置：预置Mock数据（比如指定失败次数）+ 记录失败次数
        pre_count = None
        # 核心优化3：适配Mock/真实环境的DB操作（保留原有逻辑）
        db_tool = login_mock if config.IS_MOCK else db_util

        if check_db:
            # 预置失败次数（从YAML读取fail_count_before）
            if config.IS_MOCK and case.get("fail_count_before") is not None:
                user = db_tool.query_user(username)
                if user:
                    # 【关键修改】直接访问全局变量，而非login_mock实例
                    from mock.login_mock import MOCK_USER_DB
                    MOCK_USER_DB[username]["fail_count"] = case["fail_count_before"]
                    logger.info(f"📝 预置Mock失败次数：{username} → {case['fail_count_before']}")
            # 记录前置失败次数（Mock/真实环境通用）
            user = db_tool.query_user(username)
            if user:
                pre_count = user['fail_count']
                logger.info(f"📊 前置失败次数：{username} → {pre_count}")

        # 2. 核心：调用登录接口（无需修改，LoginApi已适配Mock）
        resp = self.api.login(username, password)

        # 3. 基础断言（保留原有逻辑）
        assert resp['code'] == exp_code, \
            f"Code 错误：期望 {exp_code}, 实际 {resp['code']}"
        assert exp_msg in resp.get('msg', ""), \
            f"Msg 错误：期望包含「{exp_msg}」, 实际「{resp.get('msg', '')}」"

        # 4. 安全断言（保留原有逻辑）
        if sensitive_check and len(password) > 5:
            assert password not in str(resp), \
                f"⚠️ 安全漏洞：明文密码({password[:5]}...)泄露在响应中!"

        # 5. DB一致性校验（核心优化：适配Mock/真实环境）
        if check_db and pre_count is not None:
            user = db_tool.query_user(username)
            # 计算预期失败次数（密码错误+1，正确重置为0）
            expected_count = pre_count + 1 if resp['code'] != 200 else 0
            assert user['fail_count'] == expected_count, \
                f"DB 校验失败：期望 {expected_count}, 实际 {user['fail_count']}"
            logger.info(f"✅ DB 校验通过：FailCount {pre_count} → {user['fail_count']}")

        # 6. 新增：账号状态断言（从YAML读取expected_status）
        if case.get("expected_status"):
            user = db_tool.query_user(username)
            assert user['status'] == case["expected_status"], \
                f"状态校验失败：期望 {case['expected_status']}, 实际 {user['status']}"
            logger.info(f"✅ 状态校验通过：{username} → {user['status']}")

        logger.info(f"✅ 用例通过：{case['case_name']}\n")

# 【修改点4】修复：调整pytest执行配置，关闭标记筛选
if __name__ == "__main__":
    # 运行所有用例，不按标记筛选（解决deselected问题）
    pytest.main([
        __file__,
        "-v",  # 详细日志
        # "--no-marker-expr",  # 关闭标记筛选
        "--tb=short"  # 简化错误栈
    ])