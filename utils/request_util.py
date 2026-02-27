import requests
from config.env_config import config
from utils.log_util import logger


class RequestUtil:
    def __init__(self):
        self.session = requests.Session()  # 复用Session，提升性能
        # 【优化1】移除末尾斜杠，避免URL拼接成 //get（和登录API的修复逻辑一致）
        self.base_url = config.BASE_URL.rstrip("/")

    def send(self, method, url, data=None, params=None, token=None):
        # 【优化2】URL路径补全：如果url不以/开头，自动添加（避免拼接成 httpbin.orgget）
        if not url.startswith("/"):
            url = f"/{url}"
        full_url = f"{self.base_url}{url}"

        headers = config.HEADERS.copy()
        if token:
            headers["Authorization"] = f"Bearer {token}"

        # 日志记录（保留你的清晰日志）
        log_msg = f"【请求】{method} {full_url}"
        if params: log_msg += f" | Params: {params}"
        if data: log_msg += f" | Data: {data}"
        logger.info(log_msg)

        try:
            resp = self.session.request(
                method=method.upper(),  # 兼容小写method（如 get → GET）
                url=full_url,
                json=data,
                params=params,
                headers=headers,
                timeout=config.TIMEOUT
            )
            resp.raise_for_status()  # 抛出HTTP错误（4xx/5xx）
            logger.info(f"【响应】Status: {resp.status_code} | Response: {resp.text[:200]}")  # 补充响应内容
            return resp.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"【HTTP异常】{str(e)} | 响应内容: {resp.text[:200]}")
            raise e
        except requests.exceptions.Timeout:
            logger.error(f"【超时异常】请求 {full_url} 超时（{config.TIMEOUT}s）")
            raise
        except Exception as e:
            logger.error(f"【通用异常】{str(e)}")
            raise e