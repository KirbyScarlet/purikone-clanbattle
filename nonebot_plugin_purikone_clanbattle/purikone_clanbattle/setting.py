# 修改默认设置

__all__  = ['settings']

from argparse import Namespace
from nonebot.adapters import Message
import re

from utils import sint
from utils.sqliteapi import (
    group_server,
    group_check,

)


SETTING_HELP = """\
命令格式：
  设置 d1 10e
  设置 d 10e 11e 12e 13e 14e
"""

async def settings_parser(msg: Message):
    n = msg.extract_plain_text().split()
    res = {
        "chapter": "",
        "bossid": 0,
        "maxhp": []
    }
    if re.match(r"[a-eA-E][12345]", n[0]) and len(n) == 2:
        res["chapter"] = n[0][0]
        res["bossid"] = n[0][1]
        res["maxhp"].append(sint(n[1]))
    elif re.match(r"[12345]", n[0]) and len(n) == 6:
        res["chapter"] = n[0][0]
        res["bossid"] = 0
        res["maxhp"] = n[1:]
    else:
        return None
    return Namespace(**res)

async def setting(group_id: str, msg: Namespace):
    res = []
    server = await group_server(group_id)
    for num in msg.maxhp:
        if sint.check(num):
            continue
        else:
            return [{"text":"数字输入格式错误"}]
    
