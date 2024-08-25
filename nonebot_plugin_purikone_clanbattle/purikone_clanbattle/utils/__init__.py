##

import re
from decimal import Decimal
import aiosqlite
import pathlib
from nonebot.adapters import Bot, Event
from nonebot.rule import Rule

import asyncio

from .config import purikone_config

from . import sqliteapi

__all__ = [
    "dbclient",
    "sint",
    "check_bot"
]

###########################
# 中文习惯的伤害值转换

SINT_NUMBER = re.compile(r"([0-9]\.?[0-9]*)k?w?e?")
SINT_HELP = """\
数字格式：
  数字，数字k，数字w，数字e
  23000000，2300w，2.3kw，0.23e"""

class sint:
    __doc__ = SINT_HELP
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
        if value == "":
            self.value = 0
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

