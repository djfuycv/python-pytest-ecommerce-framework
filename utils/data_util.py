# utils/data_util.py
import yaml
from pathlib import Path
from typing import Dict, List, Any
from utils.log_util import logger


class DataUtil:
    """
    Data模块通用管理工具
    已实现：登录、商品模块
    待开发：订单、支付模块
    核心功能：
    1. 加载data目录下YAML文件（支持相对/绝对路径）
    2. 通用化数据校验（非空/格式/必填字段）
    3. 按模块分类加载数据 + 数据预处理
    """
    # 项目根目录（自动识别，无需硬编码）
    PROJECT_ROOT = Path(__file__).parent.parent
    # 数据目录（固定指向data文件夹）
    DATA_DIR = PROJECT_ROOT / "data"

    @classmethod
    def get_data_file_path(cls, filename: str) -> Path:
        """
        获取data目录下YAML文件的绝对路径（容错：自动补.yaml后缀）
        :param filename: 文件名（如test_login / test_product）
        :return: 完整文件路径
        """
        # 自动补充.yaml后缀
        if not filename.endswith(".yaml"):
            filename = f"{filename}.yaml"
        file_path = cls.DATA_DIR / filename

        # 校验文件是否存在
        if not file_path.exists():
            raise FileNotFoundError(f"数据文件不存在：{file_path.absolute()}")
        return file_path

    @classmethod
    def load_yaml(cls, filename: str) -> Dict[str, Any]:
        """
        通用加载YAML文件（含日志/异常处理）
        :param filename: data目录下的文件名（如test_login）
        :return: 解析后的字典数据
        """
        file_path = cls.get_data_file_path(filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}  # 空文件返回空字典
            logger.info(f"✅ 成功加载数据文件：{file_path.absolute()}")
            return data
        except yaml.YAMLError as e:
            logger.error(f"❌ YAML解析失败 {file_path}：{str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ 加载数据文件失败 {file_path}：{str(e)}")
            raise

    @classmethod
    def load_login_cases(cls) -> List[Dict[str, Any]]:
        """加载登录测试用例（已实现）"""
        raw_data = cls.load_yaml("test_login")
        login_cases = raw_data.get("login_cases", [])
        # 预处理登录数据
        return cls._process_login_data(login_cases)

    @classmethod
    def load_product_cases(cls) -> List[Dict[str, Any]]:
        """加载商品测试用例（已实现）"""
        raw_data = cls.load_yaml("test_product")
        product_cases = raw_data.get("product_cases", [])
        # 预处理商品数据
        return cls._process_product_data(product_cases)

    @classmethod
    def load_order_cases(cls) -> List[Dict[str, Any]]:
        """加载订单测试用例（待开发）"""
        logger.warning("⚠️ 订单模块数据加载功能待开发，暂返回空列表")
        return []  # 待开发：后续替换为实际加载逻辑

    @classmethod
    def load_pay_cases(cls) -> List[Dict[str, Any]]:
        """加载支付测试用例（待开发）"""
        logger.warning("⚠️ 支付模块数据加载功能待开发，暂返回空列表")
        return []  # 待开发：后续替换为实际加载逻辑

    @classmethod
    def _process_login_data(cls, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """登录数据预处理（已实现）"""
        processed = []
        for idx, case in enumerate(cases):
            # 基础校验：跳过非字典数据
            if not isinstance(case, dict):
                logger.warning(f"跳过无效登录用例（{idx + 1}）：非字典格式")
                continue

            new_case = case.copy()
            # 1. 补充默认值（避免KeyError）
            new_case.setdefault("case_name", f"登录用例_{idx + 1}")
            new_case.setdefault("username", "")
            new_case.setdefault("password", "")
            new_case.setdefault("expected_code", 200)
            new_case.setdefault("expected_msg", "success")
            new_case.setdefault("skip_cache", False)  # 是否跳过Redis缓存
            new_case.setdefault("check_db", False)  # 是否校验DB

            # 2. 生成边界值（如超长密码）
            if new_case.get("password_type") == "long_1000":
                new_case["password"] = "a" * 1000
                new_case.pop("password_type")
            elif new_case.get("password_type") == "empty":
                new_case["password"] = ""
                new_case.pop("password_type")

            processed.append(new_case)
        logger.info(f"✅ 预处理登录用例：共{len(processed)}条有效用例")
        return processed

    @classmethod
    def _process_product_data(cls, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """商品数据预处理（已实现）"""
        processed = []
        for idx, case in enumerate(cases):
            # 基础校验：跳过非字典数据
            if not isinstance(case, dict):
                logger.warning(f"跳过无效商品用例（{idx + 1}）：非字典格式")
                continue

            new_case = case.copy()
            # 1. 补充默认值（避免KeyError）
            new_case.setdefault("case_name", f"商品用例_{idx + 1}")
            new_case.setdefault("product_id", "")
            new_case.setdefault("product_name", "")
            new_case.setdefault("price", 0.0)
            new_case.setdefault("expected_code", 200)
            new_case.setdefault("expected_stock", 0)  # 预期库存
            new_case.setdefault("check_stock", False)  # 是否校验库存

            # 2. 生成边界值（如超长商品名、负数价格）
            if new_case.get("name_type") == "long_200":
                new_case["product_name"] = "商品名称超长测试" + "a" * 190
                new_case.pop("name_type")
            elif new_case.get("price_type") == "negative":
                new_case["price"] = -99.99
                new_case.pop("price_type")

            processed.append(new_case)
        logger.info(f"✅ 预处理商品用例：共{len(processed)}条有效用例")
        return processed

    @classmethod
    def _process_order_data(cls, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """订单数据预处理（待开发）"""
        logger.warning("⚠️ 订单模块数据预处理功能待开发，暂返回空列表")
        return []  # 待开发：后续补充订单数据预处理逻辑

    @classmethod
    def _process_pay_data(cls, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """支付数据预处理（待开发）"""
        logger.warning("⚠️ 支付模块数据预处理功能待开发，暂返回空列表")
        return []  # 待开发：后续补充支付数据预处理逻辑

    @classmethod
    def validate_required_fields(cls, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        通用校验必填字段（登录/商品通用，后续可扩展至订单/支付）
        :param data: 待校验数据
        :param required_fields: 必填字段列表（如["username", "password"]/["product_id"]）
        :return: 校验结果
        """
        missing_fields = [f for f in required_fields if f not in data or not data[f]]
        if missing_fields:
            logger.error(f"❌ 缺失必填字段：{missing_fields}")
            return False
        return True


# 单例导出（全局复用，避免重复初始化）
data_util = DataUtil()