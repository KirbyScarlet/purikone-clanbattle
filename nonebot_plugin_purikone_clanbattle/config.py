# 配置项

from pydantic import BaseModel
from nonebot import get_driver

class Config(BaseModel):
    purikone_clanbattle_bots: list[str] = []

    class Config:
        extra = "ignore"

purikone_config = Config.parse_obj(get_driver().config)

