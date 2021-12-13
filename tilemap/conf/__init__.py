import os
import logging
import logging.config
from .setting import LOG_DIR
from .log import get_log_config

logconfig = get_log_config('DEBUG')
os.makedirs(LOG_DIR, exist_ok=True)

logging.config.dictConfig(logconfig)