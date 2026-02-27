import logging
import os
from datetime import datetime


class LogUtil:
    def __init__(self):
        self.logger = logging.getLogger("EcomTest")
        self.logger.setLevel(logging.INFO)

        log_dir = "log"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = os.path.join(log_dir, f"run_{datetime.now().strftime('%Y%m%d')}.log")

        fh = logging.FileHandler(log_file, encoding='utf-8')
        ch = logging.StreamHandler()

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        if not self.logger.handlers:
            self.logger.addHandler(fh)
            self.logger.addHandler(ch)

    def info(self, msg):
        self.logger.info(msg)

    def error(self, msg):
        self.logger.error(msg)

    def warning(self, msg):
        self.logger.warning(msg)


logger = LogUtil()