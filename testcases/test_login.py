import pytest
import yaml
import os
from api.login_api import LoginApi
from utils.db_util import db_util
from utils.log_util import logger

# 加载并处理数据
data_path = os.path.join(os.path.dirname(__file__), "../data/test_data.yaml")
with open(data_path, "r", encoding="utf-8") as f:
    raw_data = yaml.safe_load(f)['login_cases']


def process_data(cases):
    processed = []
    for c in cases:
        new_c = c.copy()
        if new_c.get('password_type') == 'long_1000':
            new_c['password'] = 'a' * 1000
            new_c.pop('password_type')
        processed.append(new_c)
    return processed


test_data = process_data(raw_data)


class TestLogin:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.api = LoginApi()

    @pytest.mark.parametrize("case", test_data, ids=lambda x: x['case_name'])
    def test_login_scenarios(self, case):
        username = case['username']
        password = case['password']
        exp_code = case['expected_code']
        exp_msg = case['expected_msg']
        check_db = case.get('check_db', False)

        logger.info(f"🧪 执行用例：{case['case_name']}")

        # 1. 前置：记录失败次数 (如果需要)
        pre_count = None
        if check_db:
            user = db_util.query_user(username)
            if user: pre_count = user['fail_count']

        # 2. 调用接口
        resp = self.api.login(username, password)

        # 3. 断言状态码和消息
        assert resp['code'] == exp_code, f"Code 错误：期望 {exp_code}, 实际 {resp['code']}"
        assert exp_msg in resp.get('msg', ""), f"Msg 错误：期望 {exp_msg}"

        # 4. 安全断言
        if case.get('sensitive_check') and len(password) > 5:
            assert password not in str(resp), "⚠️ 安全漏洞：明文密码泄露!"

        # 5. DB 一致性校验 (核心亮点)
        if check_db and pre_count is not None:
            user = db_util.query_user(username)
            assert user['fail_count'] == pre_count + 1, f"DB 校验失败：期望 {pre_count + 1}, 实际 {user['fail_count']}"
            logger.info(f"✅ DB 校验通过：FailCount {pre_count} -> {user['fail_count']}")

        logger.info(f"✅ 用例通过：{case['case_name']}\n")