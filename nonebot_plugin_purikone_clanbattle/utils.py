##

import re
from decimal import Decimal
import aiosqlite
import asyncio
import pathlib
from nonebot.adapters import Bot, Event
from nonebot.rule import Rule

import asyncio

from .config import purikone_config

__all__ = [
    "dbclient",
    "sint",
    "check_bot"
]

###########################
# 数据库连接

if not pathlib.Path("data/purikone").exists():
    pathlib.Path("data/purikone").mkdir(parents=True, exist_ok=True)

DB_PATH = "data/purikone/purikone_clanbattle.db"

dbclient = asyncio.run(aiosqlite.connect(DB_PATH).__aenter__())

###########################
# 中文习惯的伤害值转换

SINT_NUMBER = re.compile(r"([0-9]\.?[0-9]*)k?w?e?")

class sint:
    def __init__(self, value: int|float|str):
        self.value = None
        if isinstance(value, int):
            self.value = value
        if isinstance(value, str):
            if r:=SINT_NUMBER.fullmatch(value):
                num = Decimal(r.groups()[0])
                if "k" in value:
                    num *= Decimal("1000")
                if "w" in value:
                    num *= Decimal("10000")
                if "e" in value:
                    num *= Decimal("100000000")
                self.value = int(num)
        if self.value is None:
            raise ValueError("输入的数字有误")
    def __add__(self, other: int|float|str):
        if isinstance(other, (int, float)):
            return self.value + other
        elif isinstance(other, sint):
            return self.value + other.value
        elif isinstance(other, str):
            return self.value + _sint(other)
    def __sub__(self, other: int|float|str):
        return self.value - other.value
    def __int__(self):
        return self.value
    def __set__(self, instance, value: int|float|str):
        self.value = _sint(value)
    def __get__(self, instance, owner):
        return self.value

def _sint(value: str) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        if r:=SINT_NUMBER.fullmatch(value):
            num = Decimal(r.groups()[0])
            if "k" in value:
                num *= Decimal("1000")
            if "w" in value:
                num *= Decimal("10000")
            if "e" in value:
                num *= Decimal("100000000")
            return int(num)
    raise ValueError("输入的数字有误")

###########################
# 只允许特定的bot开启会战

async def _check_bot(bot: Bot):
    return bot.self_id in purikone_config.purikone_clanbattle_bots

check_bot = Rule(_check_bot)

