from utils.request_util import RequestUtil
from utils.log_util import logger
from mock.product_mock import ProductMockData  # 引入Mock层
from config.env_config import config  # 新增：适配环境配置


class ProductApi:
    def __init__(self):
        self.req = RequestUtil()
        # 新增：标记当前是否为Mock模式（和登录API保持一致）
        self.is_mock = config.IS_MOCK

    def get_product_list(self, token):
        logger.info("【API】执行操作：获取商品列表")

        # 优化1：Mock模式下可选跳过真实请求（避免无效网络调用）
        if not self.is_mock:
            self.req.send(method="GET", url="/get", params={"page": 1}, token=token)

        # 直接返回Mock数据（核心逻辑不变）
        logger.info(f"【API】返回商品列表，共 {len(ProductMockData.PRODUCT_LIST)} 个商品")
        return {
            "code": 200,
            "msg": "success",
            "data": ProductMockData.PRODUCT_LIST
        }

    def get_product_detail(self, product_id, token):
        logger.info(f"【API】执行操作：获取商品详情 ID={product_id}")

        # 优化1：Mock模式下跳过真实请求
        if not self.is_mock:
            self.req.send(method="GET", url="/get", params={"id": product_id}, token=token)

        # 委托Mock层处理业务逻辑（核心逻辑不变）
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
        # 优化1：Mock模式下跳过真实请求
        resp = None
        if not self.is_mock:
            # 使用修复后的send方法，传data（POST body）
            resp = self.req.send(method="POST", url="/post", data=data, token=token)
            logger.info(f"【API】创建商品真实请求响应：{resp}")

        # 模拟成功创建（核心逻辑不变）
        return {
            "code": 201,
            "msg": "created",
            "data": {"id": 8888, "name": name, "price": price}
        }