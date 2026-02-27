import pytest
from api.product_api import ProductApi
from mock.product_mock import ProductMockData
from config.env_config import config
from utils.log_util import logger

# 测试数据（复用数据驱动思路，简化版）
test_product_data = [
    # 用例名称, product_id, token, exp_code, exp_msg
    ("查询存在商品-正常在售", "product_001", "mock_token_123", 200, "success"),
    ("查询存在商品-已售罄", "product_002", "mock_token_123", 200, "success（商品已售罄）"),
    ("查询不存在商品", "product_999", "mock_token_123", 404, "商品不存在"),
    ("获取商品列表", "", "mock_token_123", 200, "success"),  # 列表接口无product_id
    ("创建商品-正常创建", "test_create", 99.9, "mock_token_123", 201, "created")  # 创建商品
]


class TestProduct:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """前置：初始化API + 重置Mock数据"""
        self.api = ProductApi()
        ProductMockData.reset_mock_data()  # 重置Mock
        self.mock_token = "mock_token_123"  # 模拟登录Token
        logger.info(f"🔧 商品测试前置完成：Mock模式={config.IS_MOCK}")
        yield

    # 1. 测试商品详情接口
    @pytest.mark.parametrize("case_name, product_id, token, exp_code, exp_msg", [
        test_product_data[0], test_product_data[1], test_product_data[2]
    ])
    def test_get_product_detail(self, case_name, product_id, token, exp_code, exp_msg):
        logger.info(f"🧪 执行用例：{case_name}")

        # 调用接口
        resp = self.api.get_product_detail(product_id, token)

        # 核心断言（复用登录模块的断言逻辑）
        assert resp["code"] == exp_code, f"{case_name} - Code错误：期望{exp_code}, 实际{resp['code']}"
        assert exp_msg in resp["msg"], f"{case_name} - Msg错误：期望{exp_msg}, 实际{resp['msg']}"

        # 额外断言：存在商品时返回数据
        if exp_code == 200 and product_id != "":
            assert resp["data"]["product_id"] == product_id, "商品ID不匹配"
        logger.info(f"✅ 用例通过：{case_name}\n")

    # 2. 测试商品列表接口
    def test_get_product_list(self):
        case_name = "获取商品列表"
        logger.info(f"🧪 执行用例：{case_name}")

        resp = self.api.get_product_list(self.mock_token)

        # 断言
        assert resp["code"] == 200, f"{case_name} - Code错误"
        assert resp["msg"] == "success", f"{case_name} - Msg错误"
        assert len(resp["data"]) == len(ProductMockData.PRODUCT_LIST), "商品列表长度不匹配"
        logger.info(f"✅ 用例通过：{case_name}\n")

    # 3. 测试创建商品接口
    def test_create_product(self):
        case_name = "创建商品-正常创建"
        logger.info(f"🧪 执行用例：{case_name}")

        # 调用创建接口
        resp = self.api.create_product("新测试商品", 199.9, self.mock_token)

        # 断言
        assert resp["code"] == 201, f"{case_name} - Code错误"
        assert resp["msg"] == "created", f"{case_name} - Msg错误"
        assert resp["data"]["name"] == "新测试商品", "商品名称不匹配"
        assert resp["data"]["price"] == 199.9, "商品价格不匹配"
        logger.info(f"✅ 用例通过：{case_name}\n")


# 执行配置（适配低版本pytest）
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])