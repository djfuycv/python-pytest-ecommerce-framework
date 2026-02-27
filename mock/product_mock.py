# mock/product_mock.py
from utils.log_util import logger


class ProductMockData:
    """商品模块的 Mock 数据中心"""

    # 1. 商品列表数据
    PRODUCT_LIST = [
        {"id": 1001, "name": "iPhone 15 Pro", "price": 7999, "stock": 100},
        {"id": 1002, "name": "MacBook Air M2", "price": 9499, "stock": 50},
        {"id": 1003, "name": "AirPods Pro 2", "price": 1899, "stock": 200}
    ]

    # 2. 商品详情数据模板
    @staticmethod
    def get_detail_mock(product_id):
        return {
            "id": int(product_id),
            "name": f"Product_{product_id}_Name",
            "price": 99.9 * int(product_id),
            "description": "这是一个非常棒的商品",
            "stock": 1000
        }

    # 3. 模拟业务逻辑判断 (核心！)
    @staticmethod
    def check_product_logic(product_id):
        """
        模拟后端的业务校验逻辑
        返回：(code, msg, data)
        """
        # 场景 A: 商品不存在
        if product_id == "9999":
            logger.warning(f"[Mock Logic] 商品 {product_id} 不存在")
            return 404, "product not found", None

        # 场景 B: ID 格式错误
        if not product_id or not str(product_id).isdigit():
            logger.warning(f"[Mock Logic] 商品 ID 格式错误：{product_id}")
            return 400, "invalid id format", None

        # 场景 C: 正常
        return 200, "success", ProductMockData.get_detail_mock(product_id)