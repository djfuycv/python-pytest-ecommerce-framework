import os
from dotenv import load_dotenv

load_dotenv()

class EnvConfig:
    def __init__(self):
        self.env = os.getenv("AUTO_ENV", "test")
        self.BASE_URL = os.getenv("TEST_BASE_URL", "https://httpbin.org")
        self.TIMEOUT = 10
        self.HEADERS = {"Content-Type": "application/json"}

config = EnvConfig()