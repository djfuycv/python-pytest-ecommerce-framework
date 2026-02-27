import pytest
import yaml
import os
from api.product_api import ProductApi
from utils.log_util import logger

# ================= 配置区域 =================
# 定位数据文件路径 (自动适配不同操作系统)
data_path = os.path.join(os.path.dirname(__file__), "../data/product_data.yaml")

# 加载 YAML 数据
try:
    with open(data_path, "r", encoding="utf-8") as f:
        raw_data = yaml.safe_load(f)
        # 确保获取的是 product_cases 列表
        test_data = raw_data.get('product_cases', [])
        if not test_data:
            logger.error(f"⚠️ 警告：{data_path} 中未找到 'product_cases' 数据！")
except FileNotFoundError:
    logger.error(f"❌ 错误：找不到数据文件 {data_path}")
    test_data = []
except Exception as e:
    logger.error(f"❌ 错误：读取 YAML 失败 - {str(e)}")
    test_data = []


# ===========================================

class TestProduct:
    """商品模块自动化测试类"""

    # 🌟 核心亮点：依赖 login_token fixture
    # Pytest 会自动从 conftest.py 查找并执行 login_token
    # 这意味着：整个测试会话只登录一次，所有商品用例复用这个 Token
    @pytest.fixture(autouse=True)
    def setup(self, login_token):
        """
        前置处理：每个用例执行前运行
        :param login_token: 由 conftest.py 提供的全局 Token
        """
        self.api = ProductApi()
        self.token = login_token

        # 简单校验 Token 是否存在
        if not self.token:
            logger.error("❌ 前置条件失败：未获取到有效的 Token，跳过商品测试！")
            pytest.skip("Token 缺失")

        logger.info(f"✅ 商品用例前置完成：Token 已就绪 ({self.token[:15]}...)")

    # 🚀 数据驱动：参数化测试
    # ids=lambda x: x['case_name'] 让测试报告显示中文用例名，而不是枯燥的参数
    @pytest.mark.parametrize("case", test_data, ids=lambda x: x['case_name'])
    def test_product_scenarios(self, case):
        """
        通用商品测试入口
        根据 YAML 中的 case_type 或直接通过字段判断执行哪个接口
        """
        case_name = case.get('case_name', 'Unknown')
        product_id = case.get('product_id')
        exp_code = case.get('expected_code')
        exp_msg = case.get('expected_msg')

        logger.info(f"🧪 开始执行用例：[{case_name}]")
        logger.info(f"   输入：product_id={product_id}")

        # --- 1. 动作 (Action)：调用 API ---
        # 逻辑判断：如果有 product_id，测详情；如果没有（或为空字符串），测列表
        # 你也可以在 YAML 里加一个 'action': 'detail' 字段来更明确地控制
        if product_id is None or product_id == "":
            # 测试获取列表
            logger.info("   -> 调用接口：get_product_list")
            resp = self.api.get_product_list(token=self.token)
        else:
            # 测试获取详情
            logger.info(f"   -> 调用接口：get_product_detail (id={product_id})")
            resp = self.api.get_product_detail(product_id=product_id, token=self.token)

        # --- 2. 断言 (Assertion)：验证结果 ---

        # 2.1 断言状态码
        assert resp['code'] == exp_code, \
            f"❌ 状态码不符！期望: {exp_code}, 实际: {resp['code']}"

        # 2.2 断言错误消息 (如果预期有消息)
        if exp_msg:
            assert exp_msg in resp.get('msg', ''), \
                f"❌ 消息不符！期望包含 '{exp_msg}', 实际: '{resp.get('msg')}'"

        # 2.3 进阶断言：根据成功/失败做不同检查
        if exp_code == 200:
            # 成功场景：检查数据结构
            assert resp.get('data') is not None, "✅ 成功时 data 不应为空"

            if isinstance(resp['data'], list):
                # 列表检查
                assert len(resp['data']) > 0, "✅ 商品列表不应为空"
                logger.info(f"   ✅ 列表校验通过：共 {len(resp['data'])} 个商品")

            elif isinstance(resp['data'], dict):
                # 详情检查
                assert 'id' in resp['data'], "✅ 详情应包含 id 字段"
                assert 'name' in resp['data'], "✅ 详情应包含 name 字段"
                logger.info(f"   ✅ 详情校验通过：商品名={resp['data'].get('name')}")
        else:
            # 失败场景：检查 data 是否为空或 None
            # 这是一个很好的安全校验，防止报错时还返回了脏数据
            if resp.get('data'):
                logger.warning(f"   ⚠️ 警告：错误状态下返回了 data: {resp['data']}")

        logger.info(f"🎉 用例 [{case_name}] 执行通过!\n")

    # --- 扩展用例：创建商品 (可选) ---
    def test_create_product(self):
        """单独测试创建商品，不参数化，演示普通写法"""
        logger.info("🧪 执行用例：创建新商品")

        new_name = "Test_Product_Auto"
        new_price = 99.9

        resp = self.api.create_product(name=new_name, price=new_price, token=self.token)

        assert resp['code'] == 201, "创建商品应返回 201"
        assert resp['data']['name'] == new_name, "返回的商品名应与输入一致"
        logger.info("✅ 创建商品测试通过")