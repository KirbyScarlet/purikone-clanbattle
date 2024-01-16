# 预约表

from argparse import Namespace
from nonebot.adapters import Message
from utils.sqliteapi import (
    reserve_boss,
    cancel_reserve,
    get_step
)
import re

RESERVE_HELP = """\
命令格式：
  预约 [阶段] [周目] 首领编号
  预约表
例：
  预约 4
    预约下一个4号首领
  预约 23-4
    预约23周目4号首领
  预约 e4
    预约e阶段第一个4号首领"""

async def reserve_parser(msg: Message):
    m = "".join(msg.extract_plain_text())
    if m in "12345":
        return Namespace(turn=0, bossid=int(m))
    elif re.match(r"\d+-[12345]", m):
        return Namespace(turn=int(m.split("-")[0]), bossid=int(m.split("-")[1]))
    elif re.match(r"[a-eA-E][12345]", m):
        turn = await get_step(m[0])
        return Namespace(turn=turn+1, bossid=int(m[-1]))
    else:
        return None
    
async def reserve(group_id: str, user_id: str, msg: Namespace):
    res = []
    