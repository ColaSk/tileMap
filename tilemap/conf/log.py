import os
from .setting import LOG_DIR

simple_format = '[%(asctime)s: %(levelname)s/%(processName)s (%(filename)s:%(funcName)s:%(lineno)d)] %(message)s'

LOGCONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': simple_format
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'simple',
            'filename': os.path.join(LOG_DIR, "tile.log"),
            'when': 'midnight',
            'backupCount': 10,
            'encoding': 'utf-8'
        }
    },
    'root': {
        'handlers': ['console', 'default'],
        'level': 'DEBUG'
    }
}
