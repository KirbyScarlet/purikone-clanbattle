# 配置项

from pydantic import BaseModel
from typing import Mapping
from nonebot import get_driver, get_plugin_config

class Config(BaseModel):
    purikone_clanbattle_bots: list[str] = []
    purikone_clanbattle_bots_blacklist: list[str] = []
    purikone_clanbattle_prefix: str = "/"
    purikone_clanbattle_storage: str = "sqlite3"
    purikone_clanbattle_storage_path: str = "./data/purikone_clanbattle.db"
    purikone_clanbattle_settings: Mapping[str, list] = {}

    class Config:
        extra = "ignore"

purikone_config = get_plugin_config(Config)

