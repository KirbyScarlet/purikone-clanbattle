##

import importlib
from nonebot.log import logger

try:
    from .official import *
except ImportError as e:
    logger.warning("未找到官方适配器\n" + str(e))
from .onebotv11 import *