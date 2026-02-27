# mock/product_mock.py
from typing import List, Dict, Tuple, Optional
from utils.log_util import logger


class ProductMockData:
    """商品Mock数据类（适配API层的调用方式）"""
    # 基础商品列表（API层直接引用）
    PRODUCT_LIST: List[Dict] = [
        {
            "product_id": "product_001",
            "name": "测试商品1",
            "price": 99.9,
            "stock": 100,
            "status": "on_sale",
            "category": "electronics"
        },
        {
            "product_id": "product_002",
            "name": "测试商品2",
            "price": 199.9,
            "stock": 0,
            "status": "out_of_stock",
            "category": "clothes"
        },
        {
            "product_id": "product_003",
            "name": "测试商品3",
            "price": 299.9,
            "stock": 50,
            "status": "on_sale",
            "category": "home"
        }
    ]

    @classmethod
    def check_product_logic(cls, product_id: str) -> Tuple[int, str, Optional[Dict]]:
        """
        委托处理商品详情业务逻辑（适配API层调用）
        返回：(code, msg, data)
        """
        logger.info(f"【Mock】校验商品逻辑：product_id={product_id}")

        # 1. 查询商品
        product = cls._query_product(product_id)
        if not product:
            return 404, "商品不存在", None

        # 2. 校验商品状态
        if product["status"] == "out_of_stock":
            return 200, "success（商品已售罄）", product
        elif product["status"] == "off_sale":
            return 200, "success（商品已下架）", product

        # 3. 正常返回
        return 200, "success", product

    @classmethod
    def _query_product(cls, product_id: str) -> Optional[Dict]:
        """内部方法：查询单个商品"""
        for p in cls.PRODUCT_LIST:
            if p["product_id"] == product_id:
                return p.copy()  # 返回副本，避免外部修改Mock数据
        return None

    @classmethod
    def reset_mock_data(cls) -> None:
        """重置Mock数据（测试前置用）"""
        # 重置PRODUCT_LIST为初始值（如果有动态修改的场景，这里补充）
        logger.info("[Mock] 商品Mock数据已重置为初始状态")