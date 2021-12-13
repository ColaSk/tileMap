import os
from .setting import LOG_DIR

simple_format = '[%(asctime)s: %(levelname)s/%(processName)s (%(filename)s:%(funcName)s:%(lineno)d)] %(message)s'

def get_log_config(level='INFO', logfile=None):
    
    if not logfile:
        logfile = os.path.join(LOG_DIR, "tile.log")

    if not os.path.isabs(logfile):
        logfile = os.path.abspath(logfile)

    return {
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
                'filename': logfile,
                'when': 'midnight',
                'backupCount': 10,
                'encoding': 'utf-8'
            }
        },
        'root': {
            'handlers': ['console', 'default'],
            'level': level
        }
    }
