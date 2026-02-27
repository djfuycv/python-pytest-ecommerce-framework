import requests
from config.env_config import config
from utils.log_util import logger


class RequestUtil:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = config.BASE_URL

    def send(self, method, url, data=None, token=None):
        full_url = f"{self.base_url}{url}"
        headers = config.HEADERS.copy()
        if token:
            headers["Authorization"] = f"Bearer {token}"

        logger.info(f"【请求】{method} {full_url} | Data: {data}")
        try:
            resp = self.session.request(method, full_url, json=data, headers=headers, timeout=config.TIMEOUT)
            resp.raise_for_status()
            logger.info(f"【响应】Status: {resp.status_code}")
            return resp.json()
        except Exception as e:
            logger.error(f"【异常】{str(e)}")
            raise e