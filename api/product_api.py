from utils.request_util import RequestUtil
from utils.log_util import logger
from mock.product_mock import ProductMockData  # <--- 引入 Mock 层


class ProductApi:
    def __init__(self):
        self.req = RequestUtil()

    def get_product_list(self, token):
        logger.info("【API】执行操作：获取商品列表")

        # 1. 发送真实请求 (可选，用于验证网络通断)
        self.req.send(method="GET", url="/get", params={"page": 1}, token=token)

        # 2. 直接返回 Mock 数据
        logger.info(f"【API】返回商品列表，共 {len(ProductMockData.PRODUCT_LIST)} 个商品")
        return {
            "code": 200,
            "msg": "success",
            "data": ProductMockData.PRODUCT_LIST
        }

    def get_product_detail(self, product_id, token):
        logger.info(f"【API】执行操作：获取商品详情 ID={product_id}")

        # 1. 发送真实请求 (可选)
        self.req.send(method="GET", url="/get", params={"id": product_id}, token=token)

        # 2. 委托给 Mock 层处理业务逻辑
        code, msg, data = ProductMockData.check_product_logic(product_id)

        return {
            "code": code,
            "msg": msg,
            "data": data
        }

    def create_product(self, name, price, token):
        """
        (扩展功能) 创建商品 - 模拟 POST 请求
        """
        logger.info(f"【API】执行操作：创建商品 name={name}, price={price}")

        data = {"name": name, "price": price}
        # 使用刚才修复的 send 方法，这次传 data 而不是 params
        # 注意：create_product 不需要 params，只需要 data
        resp = self.req.send(method="POST", url="/post", data=data, token=token)

        # 模拟成功创建
        return {
            "code": 201,
            "msg": "created",
            "data": {"id": 8888, "name": name, "price": price}
        }