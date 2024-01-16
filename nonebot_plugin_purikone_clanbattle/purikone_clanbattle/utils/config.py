# 配置项

from pydantic import BaseModel
from nonebot import get_driver

class Config(BaseModel):
    purikone_clanbattle_bots: list[str] = []
    purikone_clanbattle_bots_blacklist: list[str] = []
    purikone_clanbattle_prefix: str = "/"
    purikone_clanbattle_storage: str = "sqlite3"
    purikone_clanbattle_storage_path: str = "./data/purikone_clanbattle.db"

    class Config:
        extra = "ignore"

purikone_config = Config.parse_obj(get_driver().config)

