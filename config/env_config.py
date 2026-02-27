import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量（优先级：系统环境变量 > .env文件）
load_dotenv(override=True)


class EnvConfig:
    """
    环境配置类（统一管理所有环境变量）
    包含：基础URL、超时时间、请求头、Mock开关、多环境适配
    """

    def __init__(self):
        # 1. 基础环境配置（区分测试/预发/生产）
        self.env = os.getenv("AUTO_ENV", "test")  # 环境：test/pre/prod
        self._set_base_url()  # 根据环境自动设置BASE_URL

        # 2. 通用请求配置
        self.TIMEOUT = int(os.getenv("AUTO_TIMEOUT", 10))  # 超时时间（转整型）
        self.HEADERS = self._get_default_headers()  # 默认请求头

        # 3. Mock开关配置（核心：控制是否启用Mock模式）
        self.IS_MOCK = self._parse_boolean(os.getenv("AUTO_IS_MOCK", "True"))

    def _set_base_url(self):
        """根据环境自动设置BASE_URL（多环境适配）"""
        env_url_map = {
            "test": os.getenv("TEST_BASE_URL", "https://httpbin.org"),
            "pre": os.getenv("PRE_BASE_URL", "https://pre-httpbin.org"),
            "prod": os.getenv("PROD_BASE_URL", "https://prod-httpbin.org")
        }
        self.BASE_URL = env_url_map.get(self.env, env_url_map["test"])

    def _get_default_headers(self):
        """获取默认请求头（可扩展Token/认证信息）"""
        base_headers = {"Content-Type": "application/json"}
        # 可选：根据环境添加认证头（如预发/生产环境的token）
        if self.env in ["pre", "prod"]:
            base_headers["Authorization"] = os.getenv("AUTO_AUTH_TOKEN", "")
        return base_headers

    @staticmethod
    def _parse_boolean(value: str) -> bool:
        """
        安全解析布尔值（兼容多种输入：True/true/1/False/false/0）
        避免直接判断导致的类型错误
        """
        if not value:
            return False
        return value.strip().lower() in ["true", "1", "yes", "on"]


# 单例导出（全局复用，避免重复初始化）
config = EnvConfig()