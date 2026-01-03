import logging
import datetime

# 自定义Formatter，支持微秒
class MicrosecondFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = datetime.datetime.fromtimestamp(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            s = ct.isoformat(sep=' ', timespec='microseconds')
        return s

# 创建日志记录器
logger = logging.getLogger('tmutils_logger')
logger.setLevel(logging.DEBUG)

# 创建控制台处理器
console_handler = logging.StreamHandler()
formatter = MicrosecondFormatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S.%f'
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# 日志封装函数
def debug(msg: str, *args, stacklevel=2, **kwargs):
    logger.debug(msg, *args, stacklevel=stacklevel, **kwargs)

def info(msg: str, *args, stacklevel=2, **kwargs):
    logger.info(msg, *args, stacklevel=stacklevel, **kwargs)

def warning(msg: str, *args, stacklevel=2, **kwargs):
    logger.warning(msg, *args, stacklevel=stacklevel, **kwargs)

def error(msg: str, *args, stacklevel=2, **kwargs):
    logger.error(msg, *args, stacklevel=stacklevel, **kwargs)
