import os
import logging
import logging.config
from .setting import LOG_DIR
from .log import LOGCONFIG as logconfig

os.makedirs(LOG_DIR, exist_ok=True)

logging.config.dictConfig(logconfig)